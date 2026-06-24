"""
Knowledge RAG Handler

投资知识RAG Skill。基于大师思想库（巴菲特、芒格、段永平、霍华德·马克斯等）
和投资理论，回答投资问题。

触发词：什么是、如何看待、如何分析、投资理论、护城河、安全边际、周期理论
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

_project_root = Path(__file__).resolve().parents[4]
_src_path = _project_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from mcp_server.tools.rag_tools import ask_investment, search_knowledge


class RagHandler:
    """处理投资知识问答请求"""

    def __init__(self):
        self.name = "knowledge-rag"
        self.triggers = [
            "什么是",
            "如何看待",
            "如何分析",
            "投资理论",
            "护城河",
            "安全边际",
            "周期理论",
        ]

    def understand_question(self, user_input: str) -> Dict[str, Any]:
        """
        解析用户问题，识别核心概念
        """
        # 简单关键词判断问题类型
        if any(kw in user_input for kw in ["什么是", "定义", "概念"]):
            qtype = "definition"
        elif any(kw in user_input for kw in ["如何看待", "分析", "怎么"]):
            qtype = "analysis"
        elif any(kw in user_input for kw in ["比较", "区别", "vs"]):
            qtype = "comparison"
        else:
            qtype = "general"
        return {"type": qtype, "original": user_input}

    def retrieve_knowledge(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从知识图谱检索相关内容
        """
        q = query.get("original", "")
        results = search_knowledge(q)
        return results

    def generate_answer(
        self, query: Dict[str, Any], retrieved: List[Dict[str, Any]]
    ) -> str:
        """
        结合检索结果生成回答
        """
        # 调用 RAG tool 获取答案
        q = query.get("original", "")
        result = ask_investment(q)
        return result.get("answer", "暂无相关信息")

    def suggest_followups(self, answer: str) -> List[str]:
        """
        基于回答内容，提供追问建议
        """
        # 从答案中提取关键词生成简单追问
        followups = []
        if "护城河" in answer:
            followups.append("护城河如何量化？")
        if "安全边际" in answer:
            followups.append("安全边际多少算合理？")
        if not followups:
            followups = ["想了解更多大师思想吗？", "这个概念如何应用？"]
        return followups[:3]

    def handle(self, user_input: str) -> Dict[str, Any]:
        """
        主处理函数
        """
        # Step 1: 问题理解
        query = self.understand_question(user_input)

        # Step 2: 知识检索
        retrieved = self.retrieve_knowledge(query)

        # Step 3: 回答生成
        answer = self.generate_answer(query, retrieved)

        # Step 4: 追问建议
        followups = self.suggest_followups(answer)

        return {
            "status": "success",
            "question": user_input,
            "answer": answer,
            "sources": retrieved,
            "followups": followups,
        }