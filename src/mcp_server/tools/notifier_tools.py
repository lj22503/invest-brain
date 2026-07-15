"""Notifier configuration tools — configure_notifier, get_notifier_config"""

import json
import logging
from pathlib import Path
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
    }
}

VALID_CHANNELS = {"feishu", "dingtalk", "bark"}


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
def configure_notifier(channel: str, webhook_url: str, enabled: bool = True) -> dict:
    """
    Configure a notification channel's webhook URL and enabled status.

    Args:
        channel: Notification channel name. Supported: feishu, dingtalk, bark
        webhook_url: Webhook URL for the channel (e.g. dingtalk bot webhook, bark server address)
        enabled: Whether to enable this channel (default True)

    Returns:
        dict: Current configuration status for all channels
    """
    if channel not in VALID_CHANNELS:
        return {
            "error": f"Unsupported channel: {channel}",
            "supported_channels": sorted(VALID_CHANNELS),
        }

    config = _load_config()
    config["channels"][channel] = {
        "webhook_url": webhook_url if webhook_url else None,
        "enabled": enabled,
    }
    _save_config(config)

    logger.info(f"Configured {channel} notifier: enabled={enabled}")

    return {
        "message": f"Channel '{channel}' configured successfully",
        "channels": config["channels"],
    }


@notifier_tools.tool()
def get_notifier_config() -> dict:
    """
    Get the current notification configuration for all channels.

    Returns:
        dict: Configuration status for all channels, e.g.:
            {"channels": {"feishu": {...}, "dingtalk": {...}, "bark": {...}}}
    """
    config = _load_config()
    return {"channels": config["channels"]}
