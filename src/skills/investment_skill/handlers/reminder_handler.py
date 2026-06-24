"""
Reminder Scheduler Handler

提醒调度Skill。管理价格提醒、时间提醒、条件提醒，
支持条件触发和通知。

触发词：提醒我、跌破、涨到、当PE分位、每周检查、每月总结、通知我
"""

import sys
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum

_project_root = Path(__file__).resolve().parents[4]
_src_path = _project_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from mcp_server.tools.reminder_tools import set_reminder, get_reminders, delete_reminder

#常用股票名称 → Sina代码映射
_TICKER_MAP = {
    "茅台": "sh600519",
    "贵州茅台": "sh600519",
    "苹果": "usAAPL",
    "腾讯": "us00700",
    "阿里": "usBABA",
    "谷歌": "usGOOGL",
    "微软": "usMSFT",
    "亚马逊": "usAMZN",
    "特斯拉": "usTSLA",
    "英伟达": "usNVDA",
    "谷歌": "usGOOG",
    "苹果": "usAAPL",
}


class ReminderType(Enum):
    """提醒类型"""
    PRICE = "price"
    TIME = "time"
    CONDITION = "condition"


class ReminderHandler:
    """处理提醒调度请求"""

    def __init__(self):
        self.name = "reminder-scheduler"
        self.triggers = [
            "提醒我",
            "跌破",
            "涨到",
            "当PE分位",
            "每周检查",
            "每月总结",
            "通知我",
        ]

    def parse_reminder(self, user_input: str) -> Dict[str, Any]:
        """
        解析用户输入，提取提醒条件
        """
        # 价格类：茅台跌破1400
        # 策略：匹配"股票名 + (跌|涨) +任意字符 + 数字"
        price_match = re.search(r'(茅台|苹果|腾讯|阿里|谷歌|微软|亚马逊|特斯拉|英伟达).*?(跌|涨).*?(\d+(?:\.\d+)?)', user_input)
        if price_match:
            ticker_name = price_match.group(1)
            operator = "below" if price_match.group(2) == "跌" else "above"
            value = float(price_match.group(3))
            ticker_code = _TICKER_MAP.get(ticker_name, ticker_name)
            return {"type": "price", "ticker": ticker_code, "ticker_name": ticker_name, "operator": operator, "value": value}

        # PE类：当PE分位低于30
        pe_match = re.search(r'当PE分位\s*(低于|高于)\s*(\d+)', user_input)
        if pe_match:
            operator = "below" if pe_match.group(1) == "低于" else "above"
            value = float(pe_match.group(2))
            return {"type": "pe_ratio", "ticker": "", "operator": operator, "value": value}

        # 时间类：每周五9点
        time_match = re.search(r'每周|每月|每天', user_input)
        if time_match:
            return {"type": "time", "cron": "0 9 * * 5" if "每周" in user_input else "0 9 1 * *" if "每月" in user_input else "0 9 * * *"}

        # 默认：通用提醒
        return {"type": "price", "ticker": user_input, "operator": "below", "value": 0}

    def create_reminder(self, parsed: Dict[str, Any]) -> str:
        """
        创建结构化提醒
        """
        result = set_reminder(parsed)
        return result.get("reminder_id", "")

    def list_active_reminders(self) -> List[Dict[str, Any]]:
        """
        列出所有激活状态的提醒
        """
        return get_reminders()

    def check_reminders(self) -> List[Dict[str, Any]]:
        """
        检查激活状态的提醒，触发满足条件的提醒
        """
        # 价格/PE类提醒的检查由 price_checker 在启动时做
        # 时间类提醒由 APScheduler 驱动
        return []

    def trigger_reminder(self, reminder_id: str) -> bool:
        """
        触发提醒，通知用户
        """
        # TODO: 对接外部通知（钉钉/飞书 webhook）
        return True

    def delete_reminder_action(self, reminder_id: str) -> bool:
        """
        删除提醒
        """
        result = delete_reminder(reminder_id)
        return result.get("deleted", False)

    def handle(self, user_input: str) -> Dict[str, Any]:
        """
        主处理函数
        """
        # Step 1: 提醒解析
        parsed = self.parse_reminder(user_input)

        # Step 2: 提醒创建
        reminder_id = self.create_reminder(parsed)

        return {
            "status": "success",
            "reminder_id": reminder_id,
            "parsed": parsed,
        }