"""Investment roundtable tools — invest_roundtable

大师圆桌讨论：自动语义匹配 3-5 位投资大师，模拟结构化深度对话。
分步调用策略：每位大师独立 LLM 调用（roundtable_role），
主持人综合（roundtable_judge）。
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from mcp.server.fastmcp import FastMCP

from ..knowledge.graph_client import get_graph_client
from ..knowledge.vector_store import get_vector_store
from ..llm import llm_chat

roundtable_tools = FastMCP("roundtable-tools")

_GRAPH_ROOT = Path(__file__).resolve().parents[3] / "data" / "graph"

# ──────────────────────────────────────────────
# 大师 MBTI 映射（基于公开传记/访谈推断）
# ──────────────────────────────────────────────
MASTER_MBTI: dict[str, str] = {
    "buffett": "ISTJ",
    "munger": "INTJ",
    "ben_graham": "INTJ",
    "phil_fisher": "INFJ",
    "peter_lynch": "ESTP",
    "howard_marks": "INTJ",
    "nassim_taleb": "ENTP",
    "li_lu": "INTJ",
    "duanyongping": "ISTP",
    "michael_burry": "INTP",
    "bill_ackman": "ENTJ",
    "cathie_wood": "ENFP",
    "stanley_druckenmiller": "ESTJ",
    "aswath_damodaran": "INTP",
    "mohnish_pabrai": "ENTP",
    "rakesh_jhunjhunwala": "ESTP",
}


def _load_master_json(master_id: str) -> dict | None:
    path = _GRAPH_ROOT / "masters" / f"{master_id}.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _build_master_prompt(master: dict, topic: str) -> str:
    """构建大师角色扮演 prompt."""
    return f"""你正在以 {master['name']} 的身份参与一场投资圆桌讨论。

## 你的身份
- 姓名：{master['name']}（{master.get('name_en', '')}）
- 时代：{master.get('era', '')}
- 背景：{master.get('background', '')}
- MBTI：{MASTER_MBTI.get(master['id'], '未知')}

## 你的投资体系
核心理念：{'、'.join(master.get('core_principles', []))}
方法论：{master.get('methodology', '')}
适用条件：{'、'.join(master.get('applicable_conditions', []))}
局限：{'、'.join(master.get('limitations', []))}

## 你的代表语录
{chr(10).join(f"- {q}" for q in master.get('quotes', [])[:3])}

## 讨论议题
{topic}

## 发言要求
1. **忠于本人真实思想体系**。说 {master['name']} 真会说的话，引他自己的名言和方法论。
2. 先就议题给出你的核心判断（陈述）。立场要鲜明，有具体理由。
3. 预判可能与你产生分歧的其他大师会说什么，主动提出你的反驳点。
4. 句式：「【{master['name']}】【陈述】：……\n\n**简言之**：一句话总结」
5. 禁止泛泛而谈的正确废话。每个观点都要有具体的锚（数字/逻辑/案例）。"""


def _build_judge_prompt(
    topic: str,
    masters: list[dict],
    master_views: list[dict],
) -> str:
    """构建主持人综合 prompt."""
    views_text = "\n\n---\n\n".join(
        f"### {v['master']}（MBTI: {v['mbti']}）\n{v['view']}"
        for v in master_views
    )

    masters_list = "\n".join(
        f"- {m['name']}：{m.get('methodology', '')[:80]}"
        for m in masters
    )

    return f"""你是投资圆桌的主持人。你冷静客观、洞察力极强，目标是引导思想交锋、穷尽议题的深层逻辑。

## 圆桌议题
{topic}

## 与会大师
{masters_list}

## 各位大师的独立观点
{views_text}

## 你的任务
基于以上大师的观点，生成一份结构化的圆桌讨论纪要。按以下 JSON 结构输出：

{{
  "opening": "主持人的开场白（100字以内）：点明议题核心张力，介绍与会大师及他们各自的视角差异",
  "rounds": [
    {{
      "round": 1,
      "question": "主持人抛出的定义/引导问题",
      "exchanges": [
        {{
          "master": "大师名",
          "action": "陈述|质疑|补充|反驳|修正|综合",
          "content": "发言内容（200字以内）",
          "tldr": "简言之：一句话"
        }}
      ],
      "synthesis": "主持人综述：本轮核心争议点 + 各大师立场分布（150字以内）"
    }}
  ],
  "verdict": {{
    "consensus": "大师们一致认同的结论（如无则写'无明确共识'）",
    "conflicts": [
      {{
        "topic": "争议点",
        "sides": [
          {{ "master": "大师名", "position": "立场简述" }}
        ]
      }}
    ],
    "drill_down": ["讨论中浮现但未深挖的关键问题1", "问题2", "问题3"],
    "decision_tree": "Markdown 格式的决策结构图：基于讨论梳理出投资者可参考的分析路径（200字以内）"
  }}
}}

要求：
1. 主持人必须点破分歧。大师们观点接近时，找出隐藏的假设差异。
2. 每轮追一个争议点，逐层深入。不要摊大饼。
3. 大师发言必须接着前面的人说，有质疑、有反驳、有交锋。
4. 决策树要可操作——用户读完知道下一步该分析什么。
5. 直接输出 JSON，不要任何额外文字。"""


def _match_masters(topic: str, top_k: int = 5) -> list[dict]:
    """语义匹配最相关的大师."""
    vs = get_vector_store()
    results = vs.search_masters(topic, top_k=top_k)

    masters = []
    seen = set()
    for r in results:
        meta = r.get("metadata", {})
        mid = meta.get("id")
        if mid in seen:
            continue
        seen.add(mid)

        data = _load_master_json(mid)
        if data:
            data["mbti"] = MASTER_MBTI.get(mid, "未知")
            data["id"] = mid
            masters.append(data)

        if len(masters) >= 5:
            break

    return masters[:5]


@roundtable_tools.tool()
def invest_roundtable(topic: str) -> dict:
    """
    投资大师圆桌讨论。

    自动语义匹配 3-5 位最相关的投资大师，模拟结构化深度对话。
    每位大师独立调用 LLM 生成观点，主持人综合交锋并生成结构化纪要。

    Args:
        topic: 投资议题（如 "贵州茅台当前估值合理吗？"）

    Returns:
        dict: 含 scene / masters / rounds / verdict 的结构化圆桌纪要
    """
    # 1. 匹配大师
    masters = _match_masters(topic)
    if len(masters) < 3:
        return {
            "error": "大师池不足",
            "message": f"仅匹配到 {len(masters)} 位大师，至少需要 3 位。请尝试调整议题表述。",
            "matched": [m["name"] for m in masters],
        }

    # 2. 并行：每位大师生成独立观点
    master_views = []

    def _get_view(master: dict) -> dict:
        prompt = _build_master_prompt(master, topic)
        try:
            view = llm_chat(prompt, scene="roundtable_role")
        except Exception as e:
            view = f"[生成失败: {e}]"
        return {
            "master": master["name"],
            "mbti": master.get("mbti", "未知"),
            "view": view,
        }

    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(_get_view, m): m for m in masters}
        for future in as_completed(futures):
            master_views.append(future.result())

    # 保持大师顺序稳定（按原始匹配顺序）
    name_order = {m["name"]: i for i, m in enumerate(masters)}
    master_views.sort(key=lambda v: name_order.get(v["master"], 99))

    # 3. 主持人综合
    judge_prompt = _build_judge_prompt(topic, masters, master_views)
    try:
        verdict_raw = llm_chat(judge_prompt, scene="roundtable_judge")
        verdict = json.loads(verdict_raw)
    except Exception:
        verdict = {
            "opening": f"欢迎来到投资大师圆桌。今天讨论的议题是：{topic}。",
            "rounds": [],
            "verdict": {
                "consensus": "LLM 综合生成失败，请重试",
                "conflicts": [],
                "drill_down": [],
                "decision_tree": "",
            },
        }

    # 4. 组装返回
    return {
        "scene": {
            "topic": topic,
            "masters": [
                {
                    "name": m["name"],
                    "name_en": m.get("name_en", ""),
                    "mbti": m.get("mbti", "未知"),
                    "era": m.get("era", ""),
                    "core_principles": m.get("core_principles", [])[:3],
                    "match_reason": "语义匹配",
                }
                for m in masters
            ],
        },
        "opening": verdict.get("opening", ""),
        "rounds": verdict.get("rounds", []),
        "verdict": verdict.get("verdict", {}),
    }
