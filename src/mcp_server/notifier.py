"""Notification dispatcher - sends alerts via configured channels (feishu/dingtalk/serverchan)."""

import json
import logging
import time
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# Resolve relative to this file's parent (mcp_server/), go up to project root
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_WEBHOOK_CONFIG_PATH = _PROJECT_ROOT / "data" / "config" / "webhook.json"
_cache: dict = {}


def _load_webhooks() -> dict:
    """Load webhook URLs from config."""
    if _WEBHOOK_CONFIG_PATH.exists():
        with open(_WEBHOOK_CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _get_webhook(channel: str) -> Optional[str]:
    """Get webhook URL for a channel."""
    if channel not in _cache:
        webhooks = _load_webhooks()
        _cache[channel] = webhooks.get(channel)
    return _cache[channel]


def send_feishu(message: str, msg_type: str = "text") -> bool:
    """
    Send a message via Feishu bot.

    Args:
        message: Message content
        msg_type: "text" or "markdown"

    Returns:
        True if sent successfully
    """
    url = _get_webhook("feishu")
    if not url:
        logger.warning("Feishu webhook not configured")
        return False

    try:
        payload = {
            "msg_type": msg_type,
            "content": {
                "text": message if msg_type == "text" else message
            }
        }
        if msg_type == "markdown":
            payload["msg_type"] = "interactive"
            payload["card"] = {
                "header": {"title": {"tag": "plain_text", "content": "投资助手提醒"}},
                "elements": [{"tag": "markdown", "content": message}]
            }
            # Fallback to text if markdown card fails, use simple text
            payload = {"msg_type": "text", "content": {"text": message}}

        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200 and resp.json().get("code") == 0:
            logger.info(f"Feishu notification sent: {message[:50]}")
            return True
        else:
            logger.error(f"Feishu send failed: {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Feishu notification error: {e}")
        return False


def send_notification(text: str, channel: str = "feishu") -> bool:
    """
    Send a notification via the specified channel.

    Args:
        text: Message text
        channel: "feishu", "dingtalk", "serverchan", or "file"

    Returns:
        True if sent successfully
    """
    if channel == "feishu":
        return send_feishu(text)
    elif channel == "file":
        return _write_to_file(text)
    else:
        logger.warning(f"Unknown notification channel: {channel}")
        return False


def _write_to_file(message: str) -> bool:
    """Write notification to local file as fallback."""
    notif_dir = _PROJECT_ROOT / "data" / "notifications"
    notif_dir.mkdir(parents=True, exist_ok=True)
    filename = notif_dir / f"notif_{int(time.time())}.txt"
    filename.write_text(message, encoding="utf-8")
    logger.info(f"Notification written to {filename}")
    return True


def notify_reminder_fired(reminder_id: str, ticker: str, condition: str, current_value: float) -> bool:
    """Send a reminder-fired notification."""
    message = (
        f"⏰ 提醒触发\n"
        f"标的：{ticker}\n"
        f"条件：{condition}\n"
        f"当前值：{current_value}"
    )
    return send_notification(message)