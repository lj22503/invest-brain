"""
Memory Keeper Handler

用户记忆管理Skill。维护用户画像、历史投资决策、行为模式，
支持语义检索和模式发现。

触发词：我的持仓、我之前、关于XXX的想法、我的投资原则、行为模式
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

_project_root = Path(__file__).resolve().parents[4]
_src_path = _project_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from mcp_server.tools.memory_tools import get_user_profile, record_decision, get_behavior_patterns
from mcp_server.tools.thought_tools import search_memories


class MemoryHandler:
    """处理用户记忆管理请求"""

    def __init__(self):
        self.name = "memory-keeper"
        self.triggers = [
            "我的持仓",
            "我之前",
            "关于",
            "的想法",
            "我的投资原则",
            "行为模式",
        ]

    def query_memory(
        self, query_type: str, query_content: str
    ) -> Dict[str, Any]:
        """
        查询用户记忆
        """
        if query_type == "semantic":
            results = search_memories(query_content)
            return {"results": results, "count": len(results)}
        return {"results": [], "count": 0}

    def record_decision_action(self, decision: Dict[str, Any]) -> str:
        """
        记录投资决策
        """
        result = record_decision(decision)
        return result.get("decision_id", "")

    def analyze_patterns(self) -> Dict[str, Any]:
        """
        分析用户行为模式
        """
        patterns = get_behavior_patterns()
        return {"patterns": patterns, "count": len(patterns)}

    def detect_contradiction(
        self, new_idea: Dict[str, Any], profile: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        检测用户言行矛盾
        """
        #简单规则检测
        ticker = new_idea.get("ticker", "")
        risk = profile.get("risk_preference", "moderate")
        contradictions = []

        # 如果用户偏保守但想法激进
        if risk == "conservative" and new_idea.get("price") and new_idea.get("price") < 0:
            contradictions.append("您的风险偏好偏保守，但当前想法涉及下跌趋势")

        if contradictions:
            return {"has_contradiction": True, "details": contradictions}
        return None

    def get_user_profile_action(self) -> Dict[str, Any]:
        """
        获取用户画像
        """
        return get_user_profile()

    def update_user_profile(self, profile: Dict[str, Any]) -> bool:
        """
        更新用户画像（写入本地文件）
        """
        profile_path = Path("data/memory/user_profile/profile.json")
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        import json
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
        return True

    def handle(self, user_input: str, mode: str = "query") -> Dict[str, Any]:
        """
        主处理函数
        """
        if mode == "query":
            result = self.query_memory("semantic", user_input)
        elif mode == "record":
            result = self.record_decision_action({"raw_input": user_input})
        elif mode == "pattern":
            result = self.analyze_patterns()
        else:
            result = {"status": "error", "message": f"Unknown mode: {mode}"}

        return result