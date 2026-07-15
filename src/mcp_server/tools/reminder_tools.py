"""Reminder tools - set_reminder, get_reminders, delete_reminder"""

import time
import uuid
from typing import Optional
from mcp.server.fastmcp import FastMCP

from ..memory.store import get_memory_store
from ..notifier import _load_webhooks, VALID_CHANNELS

# Guide text for users who need to set up notification channels
CHANNEL_GUIDE = {
    "feishu": (
        "飞书机器人 webhook。获取方式："
        "飞书群 → 群设置 → 群机器人 → 添加机器人 → 自定义机器人 → 复制 webhook 地址"
    ),
    "dingtalk": (
        "钉钉机器人 webhook。获取方式："
        "钉钉群 → 群设置 → 智能群助手 → 添加机器人 → 自定义 → 复制 webhook 地址"
    ),
    "bark": (
        "Bark 推送（仅 iOS）。获取方式："
        "App Store 安装 Bark → 打开 App → 复制首页显示的 URL"
    ),
}


def _get_enabled_channels() -> list[str]:
    """Return list of currently enabled notification channels."""
    webhooks = _load_webhooks()
    return [
        ch for ch in VALID_CHANNELS
        if webhooks.get("channels", {}).get(ch, {}).get("enabled", False)
    ]


def _build_notification_status() -> dict:
    """
    Build notification status block for reminder responses.
    Returns guidance if no channels are configured.
    """
    enabled = _get_enabled_channels()

    if enabled:
        return {
            "configured": True,
            "enabled_channels": enabled,
        }

    return {
        "configured": False,
        "message": (
            "尚未配置任何通知渠道，提醒触发时将无法收到推送。"
            "请通过 notify_configure_notifier 工具配置至少一个渠道。"
        ),
        "channels_guide": CHANNEL_GUIDE,
        "next_action": (
            "调用 notify_configure_notifier，例如：\n"
            '  notify_configure_notifier(channel="feishu", webhook_url="https://open.feishu.cn/...", enabled=true)'
        ),
    }

reminder_tools = FastMCP("reminder-tools")


def _parse_reminder_condition(condition: dict) -> tuple:
    """
    Parse and validate reminder condition.

    Returns:
        (reminder_type, condition_str) tuple
    """
    cond_type = condition.get("type", "unknown")
    if cond_type == "price":
        ticker = condition.get("ticker", "")
        operator = condition.get("operator", "below")
        value = condition.get("value", 0)
        return (cond_type, f"{ticker} {operator} {value}")
    elif cond_type == "time":
        cron = condition.get("cron", "")
        return (cond_type, f"cron: {cron}")
    elif cond_type == "pe_ratio":
        ticker = condition.get("ticker", "")
        operator = condition.get("operator", "below")
        value = condition.get("value", 0)
        return (cond_type, f"{ticker} PE {operator} {value}")
    else:
        return (cond_type, str(condition))


@reminder_tools.tool()
def set_reminder(condition: dict) -> dict:
    """
    Set a reminder with trigger condition.

    Args:
        condition: Reminder condition, e.g.:
            - {"type": "price", "ticker": "贵州茅台", "operator": "below", "value": 1400}
            - {"type": "time", "cron": "0 9 * * 5"}  # Every Friday 9am
            - {"type": "pe_ratio", "ticker": "贵州茅台", "operator": "below", "value": 20}

    Returns:
        dict: Created reminder with ID
    """
    reminder_type, condition_str = _parse_reminder_condition(condition)
    reminder_id = f"rem_{int(time.time())}_{uuid.uuid4().hex[:6]}"

    store = get_memory_store()
    store.add_reminder(reminder_id, reminder_type, condition_str)

    notification_status = _build_notification_status()

    return {
        "reminder_id": reminder_id,
        "condition": condition,
        "condition_parsed": condition_str,
        "status": "active",
        "created": True,
        "notification_status": notification_status,
    }


@reminder_tools.tool()
def get_reminders() -> list:
    """
    Get all active reminders.

    Returns:
        list: All active reminders
    """
    store = get_memory_store()
    reminders = store.get_reminders(status="active")
    notification_status = _build_notification_status()

    return {
        "count": len(reminders),
        "reminders": [
            {
                "reminder_id": r["id"],
                "type": r["type"],
                "condition": r["condition"],
                "status": r["status"],
                "created_at": r["created_at"],
            }
            for r in reminders
        ],
        "notification_status": notification_status,
    }


@reminder_tools.tool()
def delete_reminder(id: str) -> dict:
    """
    Delete a reminder by ID.

    Args:
        id: Reminder ID to delete

    Returns:
        dict: Deletion confirmation
    """
    store = get_memory_store()
    deleted = store.delete_reminder(id)

    return {
        "reminder_id": id,
        "deleted": deleted,
    }