"""
Idea Recorder Handler

投资想法记录Skill。解析用户输入，识别标的、价格、指标，
关联历史决策和大师思想，生成结构化想法卡片。

触发词：想法记录、投资想法、我觉得、想看看、关注、考虑买入、准备卖出
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project src to path for direct MCP tool calls
_project_root = Path(__file__).resolve().parents[4]
_src_path = _project_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from mcp_server.tools.thought_tools import record_thought, get_thought_cards, search_memories
from mcp_server.tools.rag_tools import get_master_view


class IdeaHandler:
    """处理想法记录请求"""

    def __init__(self):
        self.name = "idea-recorder"
        self.triggers = [
            "想法记录",
            "投资想法",
            "我觉得",
            "想看看",
            "关注",
            "考虑买入",
            "准备卖出",
        ]

    def parse_entities(self, user_input: str) -> Dict[str, Any]:
        """
        从用户输入中提取关键实体

        Args:
            user_input: 用户原始输入

        Returns:
            解析结果，包含标的、价格、指标、观点倾向等
        """
        # 调用 record_thought 来解析（复用其正则解析逻辑）
        result = record_thought(user_input)
        parsed = result.get("parsed_entities", {})
        return {
            "ticker": parsed.get("ticker"),
            "price": parsed.get("price"),
            "indicator": parsed.get("indicator"),
            "master_alignment": parsed.get("master_alignment"),
            "raw_input": user_input,
        }

    def query_history(self, ticker: str) -> Dict[str, Any]:
        """
        查询同一标的的历史记录

        Args:
            ticker: 股票代码

        Returns:
            历史记录摘要
        """
        if not ticker:
            return {"thoughts": []}
        thoughts = get_thought_cards(ticker)
        return {"thoughts": thoughts, "count": len(thoughts)}

    def master_alignment(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查想法与大师思想的对照

        Args:
            idea: 想法解析结果

        Returns:
            大师对照结果
        """
        master = idea.get("master_alignment")
        if not master:
            return {"aligned": False, "reason": "未识别到大师思想关联"}

        # 尝试获取该大师的相关观点
        try:
            view = get_master_view(master=master, topic=idea.get("ticker", "投资"))
            return {
                "aligned": True,
                "master": master,
                "view": view.get("view", ""),
                "source": view.get("source", ""),
            }
        except Exception:
            return {"aligned": True, "master": master, "view": "", "source": ""}

    def generate_card(
        self, user_input: str, entities: Dict, history: Dict, master_check: Dict
    ) -> str:
        """
        生成结构化想法卡片

        Args:
            user_input: 原始输入
            entities: 解析的实体
            history: 历史关联
            master_check: 大师对照结果

        Returns:
            卡片文件路径
        """
        import time
        ticker = entities.get("ticker", "unknown")
        card_id = f"card_{int(time.time())}"
        card_dir = Path("data/cards")
        card_dir.mkdir(parents=True, exist_ok=True)
        card_path = card_dir / f"{ticker}_{card_id}.md"

        content = f"""# 投资想法卡片

## 原始输入
{user_input}

## 解析结果
- 标的：{entities.get('ticker', '未识别')}
- 价格：{entities.get('price', '未指定')}
- 指标：{entities.get('indicator', '未指定')}

## 历史关联
- 历史想法数：{history.get('count', 0)}

## 大师对照
- 关联大师：{master_check.get('master', '未关联')}
- 大师观点：{master_check.get('view', '无')}
- 来源：{master_check.get('source', '无')}
"""
        card_path.write_text(content, encoding="utf-8")
        return str(card_path)

    def handle(self, user_input: str) -> Dict[str, Any]:
        """
        主处理函数

        Args:
            user_input: 用户输入

        Returns:
            处理结果
        """
        # Step 1: 实体解析
        entities = self.parse_entities(user_input)

        # Step 2: 历史关联
        ticker = entities.get("ticker", "")
        history = self.query_history(ticker) if ticker else {"thoughts": []}

        # Step 3: 大师对照
        master_check = self.master_alignment(entities)

        # Step 4: 生成卡片
        card_path = self.generate_card(user_input, entities, history, master_check)

        return {
            "status": "success",
            "card_path": card_path,
            "entities": entities,
            "history": history,
            "master_check": master_check,
        }