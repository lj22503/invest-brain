"""Notification dispatcher - sends alerts via configured channels (feishu/dingtalk/bark)."""

import json
import logging
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# Resolve relative to this file's parent (mcp_server/), go up to project root
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_WEBHOOK_CONFIG_PATH = _PROJECT_ROOT / "data" / "config" / "webhook.json"
_cache: dict = {}

DEFAULT_CONFIG = {
    "channels": {
        "feishu": {"webhook_url": None, "enabled": False},
        "dingtalk": {"webhook_url": None, "enabled": False},
        "bark": {"webhook_url": None, "enabled": False},
    }
}
VALID_CHANNELS = {"feishu", "dingtalk", "bark"}


def _load_webhooks() -> dict:
    """
    Load webhook URLs from config, auto-migrating old format.

    Old format: {"feishu": "https://..."}
    New format: {"channels": {"feishu": {"webhook_url": "...", "enabled": true}, ...}}
    """
    if not _WEBHOOK_CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()

    with open(_WEBHOOK_CONFIG_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # Detect and migrate old format
    if "channels" not in data:
        logger.info("Migrating webhook.json from old format to new channels format")
        migrated = DEFAULT_CONFIG.copy()
        for channel in VALID_CHANNELS:
            if channel in data:
                migrated["channels"][channel] = {
                    "webhook_url": data[channel],
                    "enabled": True,
                }
        # Persist migration to disk
        _WEBHOOK_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_WEBHOOK_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(migrated, f, ensure_ascii=False, indent=2)
        return migrated

    return data


def _get_webhook(channel: str) -> Optional[str]:
    """Get webhook URL string for a channel from the channels config."""
    if channel not in _cache:
        webhooks = _load_webhooks()
        ch_cfg = webhooks.get("channels", {}).get(channel, {})
        _cache[channel] = ch_cfg.get("webhook_url")
    return _cache[channel]


def _is_enabled(channel: str) -> bool:
    """Check if a channel is enabled."""
    webhooks = _load_webhooks()
    ch_cfg = webhooks.get("channels", {}).get(channel, {})
    return ch_cfg.get("enabled", False)


def _clear_cache():
    """Clear the webhook cache to force reload on next access."""
    _cache.clear()


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
    if not _is_enabled("feishu"):
        logger.info("Feishu channel is disabled, skipping")
        return False

    try:
        payload = {
            "msg_type": "text",
            "content": {"text": message},
        }
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0 or data.get("StatusCode") == 0:
                logger.info(f"Feishu notification sent: {message[:50]}")
                return True
            else:
                logger.error(f"Feishu send failed: {resp.text}")
                return False
        else:
            logger.error(f"Feishu send failed: HTTP {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Feishu notification error: {e}")
        return False


def send_dingtalk(message: str) -> bool:
    """
    Send a message via DingTalk bot webhook.

    Args:
        message: Message content

    Returns:
        True if sent successfully
    """
    url = _get_webhook("dingtalk")
    if not url:
        logger.warning("DingTalk webhook not configured")
        return False
    if not _is_enabled("dingtalk"):
        logger.info("DingTalk channel is disabled, skipping")
        return False

    try:
        payload = {
            "msgtype": "text",
            "text": {"content": message},
        }
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("errcode") == 0:
                logger.info(f"DingTalk notification sent: {message[:50]}")
                return True
            else:
                logger.error(f"DingTalk send failed: {resp.text}")
                return False
        else:
            logger.error(f"DingTalk send failed: HTTP {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        logger.error(f"DingTalk notification error: {e}")
        return False


def send_bark(message: str) -> bool:
    """
    Send a message via Bark push.

    Bark server URL should be configured as the webhook_url, e.g.:
        https://api.day.app/your_device_key

    Args:
        message: Message content

    Returns:
        True if sent successfully
    """
    url = _get_webhook("bark")
    if not url:
        logger.warning("Bark webhook not configured")
        return False
    if not _is_enabled("bark"):
        logger.info("Bark channel is disabled, skipping")
        return False

    try:
        encoded_message = urllib.parse.quote(message, safe="")
        bark_url = f"{url.rstrip('/')}/{encoded_message}"
        resp = requests.get(bark_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 200:
                logger.info(f"Bark notification sent: {message[:50]}")
                return True
            else:
                logger.error(f"Bark send failed: {resp.text}")
                return False
        else:
            logger.error(f"Bark send failed: HTTP {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Bark notification error: {e}")
        return False


def send_notification(text: str, channel: str = "all") -> dict:
    """
    Send a notification via the specified channel(s).

    Args:
        text: Message text
        channel: "feishu", "dingtalk", "bark", "all", or "file"

    Returns:
        dict: {"results": {"feishu": true/false, "dingtalk": ..., "bark": ...}}
    """
    if channel == "file":
        ok = _write_to_file(text)
        return {"results": {"file": ok}}

    if channel == "all":
        channels_to_send = [
            ch for ch in VALID_CHANNELS if _is_enabled(ch)
        ]
        if not channels_to_send:
            logger.warning("No notification channels enabled")
            return {"results": {}}

        results = {}
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = {
                pool.submit(_SEND_FUNCTIONS[ch], text): ch
                for ch in channels_to_send
            }
            for future in as_completed(futures):
                ch = futures[future]
                try:
                    results[ch] = future.result()
                except Exception as e:
                    logger.error(f"{ch} send error: {e}")
                    results[ch] = False

        return {"results": results}

    # Single channel
    if channel not in _SEND_FUNCTIONS:
        logger.warning(f"Unknown notification channel: {channel}")
        return {"results": {channel: False}}

    send_fn = _SEND_FUNCTIONS[channel]
    ok = send_fn(text)
    return {"results": {channel: ok}}


_SEND_FUNCTIONS = {
    "feishu": send_feishu,
    "dingtalk": send_dingtalk,
    "bark": send_bark,
}


def _write_to_file(message: str) -> bool:
    """Write notification to local file as fallback."""
    notif_dir = _PROJECT_ROOT / "data" / "notifications"
    notif_dir.mkdir(parents=True, exist_ok=True)
    filename = notif_dir / f"notif_{int(time.time())}.txt"
    filename.write_text(message, encoding="utf-8")
    logger.info(f"Notification written to {filename}")
    return True


def notify_reminder_fired(reminder_id: str, ticker: str, condition: str, current_value: float) -> dict:
    """Send a reminder-fired notification to all enabled channels."""
    message = (
        f"⏰ 提醒触发\n"
        f"标的：{ticker}\n"
        f"条件：{condition}\n"
        f"当前值：{current_value}"
    )
    return send_notification(message, channel="all")
