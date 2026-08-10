"""Notifier configuration tools — configure_notifier, get_notifier_config"""

import json
import logging
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

notifier_tools = FastMCP("notifier-tools")

# Resolve project root: tools/ -> mcp_server/ -> src/ -> project root
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_WEBHOOK_CONFIG_PATH = _PROJECT_ROOT / "data" / "config" / "webhook.json"

DEFAULT_CONFIG = {
    "channels": {
        "feishu": {"webhook_url": None, "enabled": False},
        "dingtalk": {"webhook_url": None, "enabled": False},
        "bark": {"webhook_url": None, "enabled": False},
        "pushplus": {"token": None, "template": "html", "enabled": False},
    }
}

VALID_CHANNELS = {"feishu", "dingtalk", "bark", "pushplus"}


def _ensure_dir():
    """Ensure the config directory exists."""
    _WEBHOOK_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_config() -> dict:
    """
    Load webhook config, auto-migrating old format if needed.

    Old format: {"feishu": "https://..."}
    New format: {"channels": {"feishu": {"webhook_url": "...", "enabled": true}, ...}}
    """
    if not _WEBHOOK_CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()

    with open(_WEBHOOK_CONFIG_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # Detect old format: top-level keys are channel names with string values
    if "channels" not in data:
        logger.info("Migrating webhook.json from old format to new channels format")
        migrated = DEFAULT_CONFIG.copy()
        for channel in VALID_CHANNELS:
            if channel in data:
                migrated["channels"][channel] = {
                    "webhook_url": data[channel],
                    "enabled": True,
                }
        _save_config(migrated)
        return migrated

    return data


def _save_config(config: dict):
    """Persist config to webhook.json."""
    _ensure_dir()
    with open(_WEBHOOK_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


@notifier_tools.tool()
def configure_notifier(
    channel: str,
    webhook_url: Optional[str] = None,
    token: Optional[str] = None,
    enabled: bool = True,
    send_test: bool = False,
) -> dict:
    """
    Configure a notification channel.

    Args:
        channel: Notification channel name. Supported: feishu, dingtalk, bark, pushplus
        webhook_url: Webhook URL for webhook-based channels (feishu / dingtalk / bark)
        token: PushPlus token (only used when channel="pushplus")
        enabled: Whether to enable this channel (default True)
        send_test: Whether to immediately send a test message (default False)

    Returns:
        dict: Current configuration status for all channels, plus test result if requested
    """
    if channel not in VALID_CHANNELS:
        return {
            "error": f"Unsupported channel: {channel}",
            "supported_channels": sorted(VALID_CHANNELS),
        }

    config = _load_config()
    if channel == "pushplus":
        if not token:
            return {
                "error": "channel='pushplus' 需要提供 token 参数（PushPlus token，官网 https://www.pushplus.plus 个人中心获取）",
                "hint": "notify_configure_notifier(channel=\"pushplus\", token=\"你的token\", enabled=true)",
            }
        config["channels"][channel] = {
            "token": token,
            "template": config["channels"].get(channel, {}).get("template", "html"),
            "enabled": enabled,
        }
    else:
        config["channels"][channel] = {
            "webhook_url": webhook_url if webhook_url else None,
            "enabled": enabled,
        }
    _save_config(config)

    logger.info(f"Configured {channel} notifier: enabled={enabled}")

    result = {
        "message": f"Channel '{channel}' configured successfully",
        "channels": config["channels"],
    }

    if send_test:
        test_result = _send_test(channel)
        result["test"] = test_result

    return result


def _send_test(channel: str) -> dict:
    """Send a test message through the given channel, returning a friendly result."""
    from ..notifier import send_notification

    res = send_notification("Invest-Brain 测试消息：推送配置成功，你已能收到提醒！", channel=channel)
    ok = res.get("results", {}).get(channel, False)
    if ok:
        return {
            "sent": True,
            "message": f"测试消息已通过 {channel} 发送，请查收微信/对应客户端",
        }
    return {
        "sent": False,
        "message": f"测试消息发送失败：{res.get('results', {})}。请检查凭证是否正确、网络是否可达",
        "hint": "可通过 notify_get_notifier_config() 查看当前配置，或运行 scripts/configure_pushplus.ps1 重新引导配置",
    }


@notifier_tools.tool()
def get_notifier_config() -> dict:
    """
    Get the current notification configuration for all channels.

    Returns:
        dict: Configuration status for all channels, e.g.:
            {"channels": {"feishu": {...}, "dingtalk": {...}, "bark": {...}, "pushplus": {...}}}
    """
    config = _load_config()
    channels = config.get("channels", {})

    enabled = [ch for ch, cfg in channels.items() if cfg.get("enabled", False)]

    result = {
        "channels": channels,
        "enabled_channels": enabled,
        "configured": bool(enabled),
    }

    if not enabled:
        from ..notifier import SETUP_GUIDE
        result["setup_guide"] = SETUP_GUIDE

    return result
