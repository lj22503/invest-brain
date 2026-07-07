# 学习辅导框架 Phase 1 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现学习辅导框架 Phase 1 — scenarios 表、Prompt 模板内置、触发判断、简单模式 10 步直接输出

**Architecture:** 新增 `coaching` 模块（prompt 模板 + 触发判断 + 情景库 CRUD + LLM 调用），作为新 handler 接入现有 orchestrator，不改动现有工具

**Tech Stack:** Python, SQLite（现有 memory.db），DeepSeek LLM（现有），skill/handler 架构（现有）

---

## 文件结构

```
src/
├── mcp_server/
│   ├── coaching/
│   │   ├── __init__.py
│   │   ├── prompts.py          # 三组 Prompt 模板
│   │   ├── trigger.py          # 简单/复杂触发判断
│   │   ├── scenario.py          # Scenario 表 CRUD
│   │   └── llm.py               # 辅导 LLM 调用（含校验逻辑）
│   └── memory/
│       └── store.py             # [修改] scenarios 表初始化 + scenario_id 列
├── skills/investment_skill/
│   ├── handlers/
│   │   └── coaching_handler.py  # [新建] 辅导 handler
│   ├── handlers/orchestrator_handler.py  # [修改] 添加 coaching intent
│   └── skill.yaml               # [修改] 添加 coaching intent 路由
```

---

## Task 1: scenarios 表 + memory store 改造

**Files:**
- Modify: `src/mcp_server/memory/store.py`

- [ ] **Step 1: 添加 scenarios 表和 scenario_id 字段**

在 `_init_db()` 方法中，`conn.commit()` 之前添加：

```python
# Scenarios table for learning coaching
cursor.execute("""
    CREATE TABLE IF NOT EXISTS scenarios (
        id TEXT PRIMARY KEY,
        trigger_event TEXT NOT NULL,
        variable_structure TEXT,
        causal_chain TEXT,
        predicted_outcome TEXT,
        actual_outcome TEXT,
        lesson TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Add scenario_id to thoughts table (for cross-reference with ideas)
result = cursor.execute(
    "SELECT COUNT(*) FROM pragma_table_info('thoughts') WHERE name='scenario_id'"
).fetchone()[0]
if result == 0:
    cursor.execute("ALTER TABLE thoughts ADD COLUMN scenario_id TEXT REFERENCES scenarios(id)")
```

在文件顶部 import 添加 `import time`。

- [ ] **Step 2: 添加 scenario 相关方法**

在 `MemoryStore` 类中添加：

```python
def add_scenario(
    self,
    trigger_event: str,
    variable_structure: str = None,
    causal_chain: str = None,
    predicted_outcome: str = None,
    actual_outcome: str = None,
    lesson: str = None,
) -> str:
    """Add a new scenario record"""
    import time
    scenario_id = f"scenario_{int(time.time())}"
    conn = self._get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO scenarios
           (id, trigger_event, variable_structure, causal_chain,
            predicted_outcome, actual_outcome, lesson)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (scenario_id, trigger_event, variable_structure,
         causal_chain, predicted_outcome, actual_outcome, lesson),
    )
    conn.commit()
    conn.close()
    return scenario_id

def get_scenarios(self, limit: int = 50) -> list:
    """Get recent scenarios"""
    conn = self._get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM scenarios ORDER BY created_at DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "trigger_event": r[1], "variable_structure": r[2],
         "causal_chain": r[3], "predicted_outcome": r[4],
         "actual_outcome": r[5], "lesson": r[6], "created_at": r[7]}
        for r in rows
    ]

def update_scenario_result(
    self,
    scenario_id: str,
    actual_outcome: str,
    lesson: str = None,
) -> bool:
    """Update scenario with actual result after event unfolds"""
    conn = self._get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE scenarios
           SET actual_outcome = ?, lesson = ?
           WHERE id = ?""",
        (actual_outcome, lesson, scenario_id),
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def link_thought_to_scenario(self, thought_id: int, scenario_id: str) -> bool:
    """Link a thought to a scenario"""
    conn = self._get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE thoughts SET scenario_id = ? WHERE id = ?",
        (scenario_id, thought_id),
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def get_scenario_thoughts(self, scenario_id: str) -> list:
    """Get all thoughts linked to a scenario"""
    conn = self._get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM thoughts WHERE scenario_id = ? ORDER BY created_at DESC",
        (scenario_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "text": r[1], "ticker": r[2], "price": r[3],
         "indicator": r[4], "created_at": r[5], "scenario_id": r[6]}
        for r in rows
    ]
```

- [ ] **Step 3: 测试**

```python
# 临时测试脚本
from src.mcp_server.memory.store import MemoryStore
store = MemoryStore()
sid = store.add_scenario(
    trigger_event="鲍威尔转鸽",
    causal_chain="降息预期→美元走弱→科技估值抬升",
    predicted_outcome="科技股上涨",
)
scenarios = store.get_scenarios()
print(f"✅ scenarios 表正常，记录数: {len(scenarios)}")
```

Run: `python -c "from src.mcp_server.memory.store import MemoryStore; s = MemoryStore(); sid = s.add_scenario('test', 'chain', 'pred'); print('OK', sid)"`
Expected: `OK scenario_XXXXX`

- [ ] **Step 4: Commit**

```bash
git add src/mcp_server/memory/store.py
git commit -m "feat(coaching): add scenarios table and scenario_id column"
```

- [ ] **Step 3.5: 新增 coaching scene 配置到 deepseek_client.py（Bug 2 修复）**

**Files:**
- Modify: `src/mcp_server/llm/deepseek_client.py`

在 `SCENE_CONFIGS` 字典末尾添加：

```python
    "coaching_simple": LLMConfig(
        model="deepseek-chat",
        temperature=0.5,
    ),
    "coaching_synthesis": LLMConfig(
        model="deepseek-chat",
        temperature=0.4,
    ),
    "coaching_archive": LLMConfig(
        model="deepseek-chat",
        temperature=0.3,
    ),
```

然后 commit：
```bash
git add src/mcp_server/llm/deepseek_client.py
git commit -m "feat(coaching): add coaching scene configs for LLM routing"
```

---

## Task 2: Prompt 模板内置

**Files:**
- Create: `src/mcp_server/coaching/__init__.py`
- Create: `src/mcp_server/coaching/prompts.py`

- [ ] **Step 1: 创建 coaching 模块目录和 __init__.py**

```python
"""Learning Coaching Module

提供学习辅导框架的核心组件：
- prompts: 三组 Prompt 模板
- trigger: 简单/复杂触发判断
- scenario: 情景库 CRUD
- llm: 辅导 LLM 调用
"""
```

- [ ] **Step 2: 创建 prompts.py**

```python
"""三组核心 Prompt 模板"""

# ========== 第一组：基础投研 10 步（标准模板）==========

GROUP1_STEPS = [
    {
        "step": 1,
        "prompt": "请拆解【{event}】影响的关键宏观/市场变量，并按照对资产价格的影响重要性排序。",
        "description": "变量拆解",
    },
    {
        "step": 2,
        "prompt": "请把上述变量的相互作用和传导逻辑，用带箭头的因果链完整表达出来。",
        "description": "因果链",
    },
    {
        "step": 3,
        "prompt": "上述变量的变化，会分别如何影响利率、汇率、A股/美股、大宗商品四类资产的价格趋势？请分品类说明。",
        "description": "资产影响",
    },
    {
        "step": 4,
        "prompt": "历史上是否出现过和当前变量结构一致的情景？请列出对应时间和最终各类资产的表现。",
        "description": "历史情景",
    },
    {
        "step": 5,
        "prompt": "情景推演：如果上述某个核心变量出现了与预期不一致的变化，这对整体传导逻辑意味着什么？会对原有路径产生什么改变？",
        "description": "情景推演",
    },
    {
        "step": 6,
        "prompt": "当前市场（最近1-2周）价格变动，最隐含的核心交易逻辑是什么？这个逻辑和公开新闻、主流观点一致吗？如果不一致，差异在哪里？",
        "description": "市场逻辑",
    },
    {
        "step": 7,
        "prompt": "如果上述推演逻辑成立，请给出具体可落地的交易方案：明确交易标的、方向、核心支撑逻辑，以及大致的持仓时间窗口。",
        "description": "交易方案",
    },
    {
        "step": 8,
        "prompt": "反向校验：如果当前这个交易逻辑是错的，最可能的漏洞在哪里？哪一个变量的变化会证伪这个逻辑？",
        "description": "反向校验",
    },
    {
        "step": 9,
        "prompt": "请明确写出这个交易逻辑的失效条件：当出现哪些信号/变量变化时，必须离场，这个逻辑已经不成立了？",
        "description": "失效条件",
    },
    {
        "step": 10,
        "prompt": "请用3句话总结本次分析：第一句讲当前市场核心结构，第二句讲核心驱动变量，第三句讲交易方向，用于归档笔记。",
        "description": "3句归档",
    },
]


# ========== 第二组：系统搭建Prompt ==========

GROUP2_ARCHIVE = """请把这次分析的以下内容整理成结构化条目，存入我的情景案例库：
- 触发事件：【{trigger_event}】
- 核心变量结构：【{variable_structure}】
- 推演情景：【{causal_chain}】
- 实际市场结果：【{actual_outcome}】
- 失效点/正确点：【{lessons}】"""

GROUP2_COMPARE = """请帮我对比当前这个新事件的变量结构，和我情景库中【{scenario_id}】的结构有什么异同？
- 相同点是什么？
- 核心差异是什么？
- 上次事件的教训是否适用于本次？"""

GROUP2_THRESHOLD = """根据我过去1年的交易记录，帮我总结：
对于【{asset_class}】，多大的变动幅度应该触发深度分析？
请给我具体的数值阈值建议，并说明理由。"""

GROUP2_ITERATE = """这次交易判断错误：
- 错误点是：【{wrong_variable}】没发生预期变化
- 正确结果是：【{correct_result}】

请帮我更新我的投研规则：下次遇到类似结构，应该把哪个变量优先级调高，哪个调低？"""


# ========== 第三组：每日执行 Prompt ==========

GROUP3_DAILY = """今天触发我分析的事件是【{event}】，请帮我按照以下步骤完成今日投研：

1. 拆解核心变量并排序
2. 画出传导因果链
3. 对比历史情景
4. 推演两种核心情景，写出对应交易方案
5. 明确写出失效条件和止损规则

最后用3句话总结归档。"""


# ========== Socratic 多轮对话 Prompt（复杂模式）==========

SOCRATIC_INTRO = """你是一位专业的投资投研教练。你的任务不是给答案，而是通过提问引导用户自己建立投研框架。

每次只问一个问题，提供2-4个选项（A/B/C/D），等待用户选择后根据选择继续追问。

核心原则：
1. 不告诉用户答案，引导用户自己思考
2. 每个问题只聚焦一个认知点
3. 用户选完后确认理解，再推进下一步
4. 如用户认知有偏差，不直接否定，而是追问让其自己发现

当前分析主题：{topic}
"""

SOCRATIC_STEP_PROMPT = """当前步骤：{step_description}

{question}

请选择：
{options}
"""
```

- [ ] **Step 3: 测试**

Run: `python -c "from src.mcp_server.coaching.prompts import GROUP1_STEPS, GROUP2_ARCHIVE, GROUP3_DAILY; print('OK', len(GROUP1_STEPS), len(GROUP2_ARCHIVE))"`
Expected: `OK 10`（无报错即可）

- [ ] **Step 4: Commit**

```bash
git add src/mcp_server/coaching/prompts.py
git commit -m "feat(coaching): add prompt templates for all 3 groups"
```

---

## Task 3: 触发判断逻辑

**Files:**
- Create: `src/mcp_server/coaching/trigger.py`

- [ ] **Step 1: 编写触发判断函数**

```python
"""触发判断：简单问题 vs 复杂主题"""

from typing import Literal

# 复杂触发词（满足任一即复杂）
COMPLEX_TRIGGERS = [
    # 问"为什么"或"为什么不一样"
    "为什么", "为何", "怎么会", "怎么不一样",
    # 多资产联动
    "和.*走势", "和.*不同", "联动", "背离",
    # 用户表达困惑/错误认知
    "我觉得", "我认为", "是不是", "是不是因为",
    "我以为", "感觉.*不对",
    # 政策+市场交叉
    "对.*什么影响", "会导致", "会带来",
    # 宏观分析类
    "怎么看.*趋势", "最近.*为什么", ".*为什么涨", ".*为什么跌",
]

# 简单触发词（符合且不含复杂特征）
SIMPLE_TRIGGERS = [
    "该买", "该卖", "要不要", "可以买",
    "怎么看", "现在.*情况", "当前.*如何",
    "是什么", "什么是",
]

import re

def detect_complexity(user_input: str) -> Literal["simple", "complex"]:
    """
    判断用户输入是简单问题还是复杂主题

    Returns:
        "simple": 直接 10 步输出
        "complex": Socratic 多轮引导
    """
    text = user_input.lower()

    # 检查是否复杂
    for pattern in COMPLEX_TRIGGERS:
        if re.search(pattern, text):
            return "complex"

    # 检查是否简单
    for pattern in SIMPLE_TRIGGERS:
        if re.search(pattern, text):
            return "simple"

    # 默认：含宏观/投资主题词但无明显特征的，走简单
    macro_keywords = ["黄金", "茅台", "股市", "利率", "汇率", "原油", "美联储", "央行", "A股", "美股", "宏观"]
    if any(kw in text for kw in macro_keywords):
        return "simple"

    return "simple"  # 默认简单，避免过度触发
```

- [ ] **Step 2: 测试**

```python
test_cases = [
    ("茅台现在怎么看", "simple"),
    ("黄金为什么一直涨", "complex"),
    ("为什么国内油价涨得少", "complex"),
    ("美联储Q3降不降息", "simple"),
    ("鲍威尔转鸽对A股科技什么影响", "complex"),
    ("我觉得美元要见顶了", "complex"),
    ("黄金和石油为什么走势不一样", "complex"),
    ("什么是安全边际", "simple"),
]

from src.mcp_server.coaching.trigger import detect_complexity
for text, expected in test_cases:
    result = detect_complexity(text)
    status = "✅" if result == expected else "❌"
    print(f"{status} '{text}' -> {result} (expected {expected})")
```

Run: `python -c "..."`（同上测试脚本）
Expected: 全部 ✅

- [ ] **Step 3: Commit**

```bash
git add src/mcp_server/coaching/trigger.py
git commit -m "feat(coaching): add complexity detection for simple vs complex"
```

---

## Task 4: Scenario 存储和 LLM 调用

**Files:**
- Create: `src/mcp_server/coaching/scenario.py`
- Create: `src/mcp_server/coaching/llm.py`

- [ ] **Step 1: scenario.py — 情景库读写**

```python
"""情景库读写操作"""

from typing import Optional
from ..memory.store import get_memory_store


def archive_scenario(
    trigger_event: str,
    variable_structure: str = None,
    causal_chain: str = None,
    predicted_outcome: str = None,
    actual_outcome: str = None,
    lesson: str = None,
) -> str:
    """写入新情景记录，返回 scenario_id"""
    store = get_memory_store()
    return store.add_scenario(
        trigger_event=trigger_event,
        variable_structure=variable_structure,
        causal_chain=causal_chain,
        predicted_outcome=predicted_outcome,
        actual_outcome=actual_outcome,
        lesson=lesson,
    )


def get_recent_scenarios(limit: int = 20) -> list:
    """获取最近的情景记录"""
    store = get_memory_store()
    return store.get_scenarios(limit=limit)


def update_scenario_with_result(
    scenario_id: str,
    actual_outcome: str,
    lesson: str = None,
) -> bool:
    """事后更新情景的实际结果（用户反馈或系统检测）"""
    store = get_memory_store()
    return store.update_scenario_result(scenario_id, actual_outcome, lesson)


def link_thought_to_scenario(thought_id: int, scenario_id: str) -> bool:
    """把一条想法关联到情景"""
    store = get_memory_store()
    return store.link_thought_to_scenario(thought_id, scenario_id)


def get_scenario_with_thoughts(scenario_id: str) -> dict:
    """获取情景及其关联的所有想法"""
    store = get_memory_store()
    scenario = store.get_scenarios(limit=1)
    # 找到指定 scenario
    all_scenarios = store.get_scenarios(limit=1000)
    matched = [s for s in all_scenarios if s["id"] == scenario_id]
    if not matched:
        return None
    thoughts = store.get_scenario_thoughts(scenario_id)
    return {
        **matched[0],
        "thoughts": thoughts,
    }
```

- [ ] **Step 2: llm.py — 辅导 LLM 调用（含校验逻辑）**

```python
"""辅导 LLM 调用，含 A+B+D 校验逻辑"""

from typing import Optional
from ..llm import get_deepseek_client, is_llm_available
from .prompts import GROUP1_STEPS


def _build_sourceCitation(llm_output: str, sources: list) -> str:
    """为 LLM 输出附加来源标注（A 原则）"""
    if not sources:
        return llm_output
    source_text = "，来源：" + "、".join([s.get("name", "") for s in sources[:3]])
    return llm_output + source_text


def _add_disclaimer(text: str) -> str:
    """添加免责声明（B 原则）"""
    return text + "\n\n⚠️ 以上分析仅供参考，不构成投资建议。决策前请自行判断。"


def coaching_llm_call(
    prompt: str,
    scene: str = "coaching_simple",
    need_sources: bool = True,
    sources: list = None,
) -> str:
    """
    辅导场景的 LLM 调用

    A 校验：带来源输出
    B 原则：附加免责声明
    D 降级：LLM 不可用时返回降级响应
    """
    if not is_llm_available():
        return "（当前 AI 不可用，请在配置 DEEPSEEK_API_KEY 后使用辅导功能）"

    client = get_deepseek_client()
    try:
        result = client.chat_simple(prompt, scene=scene)
        if need_sources and sources:
            result = _build_sourceCitation(result, sources)
        result = _add_disclaimer(result)
        return result
    except Exception as e:
        return f"（分析生成失败：{e}，请稍后重试）"


def run_simple_10steps(event: str, sources: list = None) -> str:
    """
    简单模式：直接生成 10 步投研分析
    """
    outputs = []
    for step_info in GROUP1_STEPS:
        step_num = step_info["step"]
        prompt_template = step_info["prompt"]
        description = step_info["description"]

        # 替换占位符（第一步填 event，其他步留空）
        if step_num == 1:
            prompt = prompt_template.replace("{event}", event)
        else:
            # 后续步骤传入上一步结果作为上下文
            context = "\n\n上一步结论：\n" + "\n\n".join(outputs[-3:]) if outputs else ""
            prompt = prompt_template + context

        result = coaching_llm_call(prompt, scene="coaching_synthesis")
        outputs.append(f"**步骤{step_num}【{description}】**\n{result}")

    return "\n\n".join(outputs)


def run_archive(
    trigger_event: str,
    variable_structure: str,
    causal_chain: str,
    actual_outcome: str = None,
    lesson: str = None,
) -> str:
    """调用归档 Prompt，写入情景库"""
    from .prompts import GROUP2_ARCHIVE
    from .scenario import archive_scenario

    prompt = GROUP2_ARCHIVE.format(
        trigger_event=trigger_event,
        variable_structure=variable_structure,
        causal_chain=causal_chain,
        actual_outcome=actual_outcome or "",
        lessons=lesson or "",
    )

    result = coaching_llm_call(prompt, scene="coaching_archive", need_sources=False)
    scenario_id = archive_scenario(
        trigger_event=trigger_event,
        variable_structure=variable_structure,
        causal_chain=causal_chain,
        predicted_outcome=result,
        actual_outcome=actual_outcome,
        lesson=lesson,
    )
    return f"✅ 已存入情景库 [{scenario_id}]\n\n{result}"
```

- [ ] **Step 3: Commit**

```bash
git add src/mcp_server/coaching/scenario.py src/mcp_server/coaching/llm.py
git commit -m "feat(coaching): add scenario CRUD and LLM calling with A+B+D safeguards"
```

---

## Task 5: Coaching Handler

**Files:**
- Create: `src/skills/investment_skill/handlers/coaching_handler.py`

- [ ] **Step 1: 创建 handler**

```python
"""
Coaching Handler

学习辅导主入口。
- 检测复杂度（简单/复杂）
- 简单：直接 10 步输出
- 复杂：触发 Socratic 多轮对话（Phase 2）
- 两者结束均自动归档到情景库
"""

from typing import Dict, Any
from pathlib import Path
import sys

_project_root = Path(__file__).resolve().parents[4]
_src_path = _project_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from mcp_server.coaching.trigger import detect_complexity
from mcp_server.coaching.llm import run_simple_10steps, coaching_llm_call
from mcp_server.coaching.prompts import GROUP2_ARCHIVE
from mcp_server.coaching.scenario import archive_scenario


class CoachingHandler:
    """学习辅导 handler"""

    def __init__(self):
        self.name = "coaching"
        self.triggers = [
            "怎么看.*趋势", "为什么.*涨", "为什么.*跌",
            "为什么.*不一样", "对.*什么影响",
            ".*觉得.*", ".*为什么",
        ]

    def handle(self, user_input: str, mode: str = None) -> Dict[str, Any]:
        """
        主处理函数

        Args:
            user_input: 用户输入
            mode: 强制模式 ("simple" | "complex" | None=自动判断)

        Returns:
            处理结果
        """
        # Step 1: 判断复杂度
        complexity = mode or detect_complexity(user_input)

        if complexity == "simple":
            return self._handle_simple(user_input)
        else:
            # Phase 1：复杂主题暂用简单 10 步替代（Phase 2 实现真正 Socratic 多轮对话）
            # 当前输出前加提示，让用户知道这是简化版
            result = self._handle_simple(user_input)
            result["answer"] = (
                "💡 当前复杂主题分析（简化版，Phase 2 将支持完整多轮引导）\n\n"
                + result["answer"]
            )
            result["mode"] = "complex_simplified"
            return result

    def _handle_simple(self, user_input: str) -> Dict[str, Any]:
        """简单模式：直接 10 步输出"""
        # 提取事件名作为分析主题
        event = user_input.strip()

        result_text = run_simple_10steps(event)

        # 自动归档到情景库（异步，不阻塞返回）
        try:
            scenario_id = archive_scenario(
                trigger_event=event,
                causal_chain="（见下方10步分析）",
            )
        except Exception:
            scenario_id = None

        return {
            "status": "success",
            "mode": "simple",
            "answer": result_text,
            "scenario_id": scenario_id,
            "auto_archived": scenario_id is not None,
        }
```

- [ ] **Step 2: Commit**

```bash
git add src/skills/investment_skill/handlers/coaching_handler.py
git commit -m "feat(coaching): add coaching handler with simple mode 10-step output"
```

---

## Task 6: Orchestrator 接入

**Files:**
- Modify: `src/skills/investment_skill/handlers/orchestrator_handler.py`
- Modify: `src/skills/investment_skill/skill.yaml`

- [ ] **Step 1: 在 orchestrator_handler.py 添加 coaching**

在文件顶部 import 部分添加：
```python
from .coaching_handler import CoachingHandler
```

在 `_INTENT_MAP` 字典末尾添加：
```python
"learning-coaching": {
    "handler": CoachingHandler(),
    "triggers": [
        "怎么看.*趋势", "为什么.*涨", "为什么.*跌",
        "为什么.*不一样", "对.*什么影响",
        ".*觉得.*", ".*为什么",
        # 宏观类
        "宏观", "利率", "汇率", "黄金", "原油",
        "美联储", "央行", "A股", "美股",
    ],
},
```

在 `_route_to_handler` 函数中添加：
```python
elif intent_name == "learning-coaching":
    return h.handle(user_input)
```

在 `_summarize_result` 函数中添加：
```python
elif intent == "learning-coaching":
    return result.get("answer", "（辅导分析完成）")
```

**注意**：把 coaching intent 放在 _INTENT_MAP 的最后一个，使其优先级最低（现有工具优先）。

- [ ] **Step 2: 在 skill.yaml 添加 coaching intent**

在 `intents` 列表末尾添加：
```yaml
- type: learning-coaching
  triggers:
    - "怎么看.*趋势"
    - "为什么.*涨"
    - "为什么.*跌"
    - "为什么.*不一样"
    - "对.*什么影响"
  route_to: learning-coaching
```

- [ ] **Step 3: 测试路由**

```python
# 测试 orchestrator 是否能识别辅导意图
from src.skills.investment_skill.handlers.orchestrator_handler import _detect_intents

test_cases = [
    "黄金为什么一直涨",
    "茅台现在怎么看",
    "鲍威尔转鸽对A股影响",
    "我觉得美元要见顶了",
]
for text in test_cases:
    intents = _detect_intents(text)
    print(f"'{text}' -> intents: {intents}")
```

Run: `python -c "..."`（同上）
Expected: 应返回 `learning-coaching` intent

- [ ] **Step 4: Commit**

```bash
git add src/skills/investment_skill/handlers/orchestrator_handler.py src/skills/investment_skill/skill.yaml
git commit -m "feat(coaching): integrate coaching handler into orchestrator"
```

---

## 实施后的系统状态

Phase 1 完成后：

```
用户输入
    ↓
orchestrator 路由
    ↓
coaching_handler.handle()
    ↓
detect_complexity() → simple / complex
    ↓
simple: run_simple_10steps() → 10步输出
    ↓
自动 archive_scenario() 写情景库
    ↓
返回带免责声明的答案
```

现有工具（RAG/想法记录/提醒/大师）不受影响，coaching intent 在最后兜底。

---

## Self-Review 检查清单

- [ ] scenarios 表创建成功，无报错
- [ ] 三组 Prompt 模板全部内置
- [ ] 触发判断在测试用例上全部正确
- [ ] 简单模式 10 步可生成输出
- [ ] orchestrator 能正确路由辅导类问题
- [ ] 现有工具（thought/rag/reminder/master）不受影响

---

**Plan complete and saved to `docs/superpowers/plans/2026-06-26-learning-coaching-phase1.md`**

Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks

**2. Inline Execution** - Execute tasks in this session using executing-plans

Which approach?
