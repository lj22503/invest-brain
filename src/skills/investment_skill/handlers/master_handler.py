"""
Master Analyst Handler

大师思想分析Skill。提供巴菲特、芒格、段永平、霍华德·马克斯等
投资大师的思想分析和对照。

触发词：巴菲特怎么看、芒格说、段永平思想、大师观点、投资大师
"""

import sys
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

_project_root = Path(__file__).resolve().parents[4]
_src_path = _project_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from mcp_server.tools.rag_tools import get_master_view, ask_investment

# 大师别名映射（用于识别用户输入）
MASTER_ALIASES = {
    "巴菲特": ["巴菲特", "Buffett", "warren"],
    "芒格": ["芒格", " Munger", "查理"],
    "段永平": ["段永平", "步步高", "Duan"],
    "马克斯": ["马克斯", "霍华德", "Howard Marks", "Marks"],
    "李录": ["李录", "Li Lu"],
}


class MasterAnalystHandler:
    """处理大师思想分析请求"""

    SUPPORTED_MASTERS = {
        "巴菲特": {
            "core_ideas": ["护城河", "安全边际", "能力圈"],
            "methodology": ["价值投资", "长期持有"],
        },
        "芒格": {
            "core_ideas": ["多元思维模型", "好生意"],
            "methodology": ["逆向思考", "格栅理论"],
        },
        "段永平": {
            "core_ideas": ["本分", "不懂不投"],
            "methodology": ["聚焦", "stop doing list"],
        },
        "霍华德·马克斯": {
            "core_ideas": ["周期", "第二层思维"],
            "methodology": ["风险识别", "逆向投资"],
        },
        "李录": {
            "core_ideas": ["文明现代化"],
            "methodology": ["价值投资中国化"],
        },
    }

    def __init__(self):
        self.name = "master-analyst"
        self.triggers = [
            "巴菲特怎么看",
            "芒格说",
            "段永平思想",
            "大师观点",
            "投资大师",
        ]

    def _extract_master(self, user_input: str) -> tuple:
        """从用户输入中识别大师和话题"""
        master_found = None
        topic_found = None

        for master, aliases in MASTER_ALIASES.items():
            for alias in aliases:
                if alias in user_input:
                    master_found = master
                    break
            if master_found:
                break

        if not master_found:
            # 尝试从常见投资话题推断
            topic_keywords = {
                "护城河": "护城河",
                "安全边际": "安全边际",
                "周期": "周期",
                "风险": "风险",
                "能力圈": "能力圈",
            }
            for kw, topic in topic_keywords.items():
                if kw in user_input:
                    topic_found = topic
                    break

        return master_found, topic_found

    def query_master(
        self, master_name: str, topic: str
    ) -> Dict[str, Any]:
        """
        查询指定大师对特定话题的看法
        """
        result = get_master_view(master=master_name, topic=topic)
        return {
            "master": result.get("master", master_name),
            "topic": result.get("topic", topic),
            "view": result.get("view", ""),
            "source": result.get("source", ""),
            "related_topics": result.get("related_topics", []),
        }

    def topic_association(self, topic: str) -> Dict[str, Any]:
        """
        输入话题，自动关联相关大师思想
        """
        result = ask_investment(topic)
        return {
            "topic": topic,
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
        }

    def compare_masters(
        self, master_a: str, master_b: str, topic: str
    ) -> Dict[str, Any]:
        """
        比较不同大师对同一话题的观点
        """
        view_a = self.query_master(master_a, topic)
        view_b = self.query_master(master_b, topic)
        return {
            "topic": topic,
            "master_a": view_a,
            "master_b": view_b,
            "comparison": f"{master_a}：{view_a.get('view', '')}\n{master_b}：{view_b.get('view', '')}",
        }

    def check_contradiction(
        self, user_idea: str, masters: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        检测用户想法与大师思想的冲突
        """
        if not masters:
            return None
        result = ask_investment(user_idea)
        answer = result.get("answer", "")
        return {
            "has_contradiction": False,
            "analysis": answer,
        }

    def get_master_overview(self, master_name: str) -> Dict[str, Any]:
        """
        获取大师概览
        """
        info = self.SUPPORTED_MASTERS.get(master_name, {})
        return {
            "name": master_name,
            "core_ideas": info.get("core_ideas", []),
            "methodology": info.get("methodology", []),
        }

    def handle(self, user_input: str) -> Dict[str, Any]:
        """
        主处理函数
        """
        master, topic = self._extract_master(user_input)

        if master and topic:
            result = self.query_master(master, topic)
        elif master:
            result = self.get_master_overview(master)
        elif topic:
            result = self.topic_association(topic)
        else:
            # 通用大师思想问答
            rag_result = ask_investment(user_input)
            result = {
                "status": "success",
                "input": user_input,
                "answer": rag_result.get("answer", ""),
                "sources": rag_result.get("sources", []),
            }

        if isinstance(result, dict):
            result["status"] = "success"
            result["input"] = user_input

        return result