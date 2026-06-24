"""
Investment Orchestrator Handler

主调度器。根据用户输入的触发词识别意图，
路由到对应的专业 handler（可多路并行），
整合结果返回给用户。
"""

import re
from typing import Dict, Any, List, Optional

from .idea_handler import IdeaHandler
from .rag_handler import RagHandler
from .memory_handler import MemoryHandler
from .reminder_handler import ReminderHandler
from .master_handler import MasterAnalystHandler


# 意图 → handler 实例 + 触发词
_INTENT_MAP = {
    "idea-recorder": {
        "handler": IdeaHandler(),
        "triggers": [
            "想法记录", "投资想法", "我觉得", "想看看", "关注",
            "考虑买入", "准备卖出", "跌到", "涨到", "买入",
        ],
    },
    "knowledge-rag": {
        "handler": RagHandler(),
        "triggers": [
            "什么是", "如何看待", "如何分析", "投资理论",
            "护城河", "安全边际", "周期理论", "风险",
        ],
    },
    "memory-keeper": {
        "handler": MemoryHandler(),
        "triggers": [
            "我的持仓", "我之前", "关于", "的想法",
            "我的投资原则", "行为模式",
        ],
    },
    "reminder-scheduler": {
        "handler": ReminderHandler(),
        "triggers": [
            "提醒我", "跌破", "涨到", "当PE分位",
            "每周检查", "每月总结", "通知我",
        ],
    },
    "master-analyst": {
        "handler": MasterAnalystHandler(),
        "triggers": [
            "巴菲特怎么看", "芒格说", "段永平思想",
            "大师观点", "投资大师",
        ],
    },
}


def _detect_intents(user_input: str) -> List[str]:
    """根据触发词检测用户意图，返回匹配的 intent 列表"""
    matched = []
    user_lower = user_input.lower()
    for intent, config in _INTENT_MAP.items():
        for trigger in config["triggers"]:
            if trigger.lower() in user_lower:
                if intent not in matched:
                    matched.append(intent)
                break
    return matched


def _route_to_handler(intent: str, user_input: str, handler_info: Dict) -> Dict[str, Any]:
    """将请求路由到指定 handler 并返回结果"""
    h = handler_info["handler"]
    intent_name = intent

    if intent_name == "idea-recorder":
        return h.handle(user_input)
    elif intent_name == "knowledge-rag":
        return h.handle(user_input)
    elif intent_name == "memory-keeper":
        return h.handle(user_input, mode="query")
    elif intent_name == "reminder-scheduler":
        return h.handle(user_input)
    elif intent_name == "master-analyst":
        return h.handle(user_input)
    else:
        return {"status": "error", "message": f"Unknown intent: {intent}"}


def _summarize_result(intent: str, result: Dict[str, Any]) -> str:
    """将 handler 结果提炼为简洁回复"""
    if result.get("status") == "error":
        return f"❌ 出错了：{result.get('message', '')}"

    if intent == "idea-recorder":
        card_path = result.get("card_path", "")
        ticker = result.get("entities", {}).get("ticker", "未识别")
        price = result.get("entities", {}).get("price")
        msg = f"✅想法已记录 [{ticker}]"
        if price:
            msg += f"，价格 {price}"
        return msg

    elif intent == "knowledge-rag":
        answer = result.get("answer", "暂无相关信息")
        return answer

    elif intent == "memory-keeper":
        results = result.get("results", [])
        count = result.get("count", 0)
        if count == 0:
            return "📭 还没有相关记忆"
        return f"📖 找到 {count} 条相关记忆"

    elif intent == "reminder-scheduler":
        reminder_id = result.get("reminder_id", "")
        parsed = result.get("parsed", {})
        rtype = parsed.get("type", "unknown")
        return f"⏰ 提醒已设置 [{rtype}]，ID：{reminder_id}"

    elif intent == "master-analyst":
        view = result.get("view", result.get("answer", ""))
        if view:
            master = result.get("master", "")
            topic = result.get("topic", "")
            return f"**{master}** 对 **{topic}** 的观点：\n{view}"
        return result.get("answer", "暂无相关信息")

    return str(result)


class OrchestratorHandler:
    """投资助手主调度器"""

    def __init__(self):
        self.name = "investment-orchestrator"
        self.triggers = [
            "投资想法", "投资问题", "记忆", "提醒",
            "持仓检查", "大师思想", "更新", "修改",
            "再次运行", "重新执行",
        ]

    def handle(self, user_input: str) -> Dict[str, Any]:
        """
        主处理函数：意图检测 → 多路路由 → 结果整合

        Args:
            user_input: 用户输入

        Returns:
            处理结果，包含路由结果和最终回复
        """
        intents = _detect_intents(user_input)

        if not intents:
            return {
                "status": "ambiguous",
                "message": "我无法识别您的意图，请明确说：\n"
                          "•投资想法（如：茅台跌到1400可以考虑买入）\n"
                          "• 投资问题（如：什么是护城河）\n"
                          "• 记忆检索（如：我之前怎么看腾讯的）\n"
                          "• 提醒设置（如：跌破1400提醒我）\n"
                          "• 大师思想（如：巴菲特怎么看周期）",
                "suggestions": [
                    "我想记录一个投资想法",
                    "什么是安全边际？",
                    "我之前关于苹果的想法",
                    "茅台跌破1500提醒我",
                    "巴菲特怎么看护城河",
                ],
            }

        # 多路并行路由
        results = {}
        for intent in intents:
            handler_info = _INTENT_MAP[intent]
            try:
                results[intent] = _route_to_handler(intent, user_input, handler_info)
            except Exception as e:
                results[intent] = {"status": "error", "message": str(e)}

        # 整合回复
        responses = []
        for intent in intents:
            r = results.get(intent, {})
            summary = _summarize_result(intent, r)
            responses.append(summary)

        final_answer = "\n\n".join(responses)

        return {
            "status": "success",
            "intents_detected": intents,
            "results": results,
            "answer": final_answer,
        }