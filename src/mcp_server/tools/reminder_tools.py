"""Reminder tools - set_reminder, get_reminders, delete_reminder"""

import time
import uuid
from typing import Optional
from mcp.server.fastmcp import FastMCP

from ..memory.store import get_memory_store

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

    return {
        "reminder_id": reminder_id,
        "condition": condition,
        "condition_parsed": condition_str,
        "status": "active",
        "created": True,
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

    return [
        {
            "reminder_id": r["id"],
            "type": r["type"],
            "condition": r["condition"],
            "status": r["status"],
            "created_at": r["created_at"],
        }
        for r in reminders
    ]


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