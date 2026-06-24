"""APScheduler-based reminder scheduler for time-triggered reminders."""

import logging
import sqlite3
from pathlib import Path
from typing import Optional

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
except ImportError:
    BackgroundScheduler = None
    CronTrigger = None

from .memory.store import get_memory_store
from .notifier import send_notification

logger = logging.getLogger(__name__)

_scheduler: Optional["BackgroundScheduler"] = None


def _init_reminder_log_table():
    """Create reminder_log table if not exists."""
    db_path = Path(__file__).resolve().parents[2] / "data" / "memory" / "memory.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminder_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reminder_id TEXT NOT NULL,
            triggered_at TEXT NOT NULL,
            trigger_reason TEXT,
            FOREIGN KEY (reminder_id) REFERENCES reminders(id)
        )
    """)
    conn.commit()
    conn.close()


def _fire_time_reminder(reminder_id: str, condition: str):
    """Fire a time-based reminder."""
    _init_reminder_log_table()
    db_path = Path(__file__).resolve().parents[2] / "data" / "memory" / "memory.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    import time
    cursor.execute(
        "INSERT INTO reminder_log (reminder_id, triggered_at, trigger_reason) VALUES (?, ?, ?)",
        (reminder_id, time.strftime("%Y-%m-%d %H:%M:%S"), f"时间条件触发: {condition}")
    )
    conn.commit()
    conn.close()
    logger.info(f"Time reminder fired: {reminder_id} ({condition})")
    send_notification(
       f"⏰ 时间提醒触发\n提醒ID：{reminder_id}\n条件：{condition}",
        channel="feishu"
    )


def _parse_cron(cron_str: str) -> dict:
    """Parse a simple cron string into APScheduler args."""
    # Supports: "0 9 * * 5" (every Friday 9am)
    parts = cron_str.split()
    if len(parts) != 5:
        return {}
    minute, hour, day, month, day_of_week = parts
    return {
        "minute": minute,
        "hour": hour,
        "day": day,
        "month": month,
        "day_of_week": day_of_week,
    }


def start_scheduler():
    """Start the APScheduler background scheduler."""
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    if BackgroundScheduler is None:
        logger.warning("APScheduler not installed. Time reminders will not fire.")
        return None

    _init_reminder_log_table()

    _scheduler = BackgroundScheduler()
    store = get_memory_store()
    reminders = store.get_reminders(status="active")

    for rem in reminders:
        if rem.get("type") == "time":
            condition = rem.get("condition", "")
            cron_match = condition.replace("cron: ", "").strip()
            cron_args = _parse_cron(cron_match)
            if cron_args and CronTrigger:
                trigger = CronTrigger(
                    minute=cron_args.get("minute", "*"),
                    hour=cron_args.get("hour", "*"),
                    day=cron_args.get("day", "*"),
                    month=cron_args.get("month", "*"),
                    day_of_week=cron_args.get("day_of_week", "*"),
                )
                _scheduler.add_job(
                    _fire_time_reminder,
                    trigger=trigger,
                    args=[rem["id"], condition],
                    id=rem["id"],
                    replace_existing=True,
                )
                logger.info(f"Scheduled time reminder: {rem['id']} with cron {cron_match}")

    _scheduler.start()
    return _scheduler


def stop_scheduler():
    """Stop the scheduler."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None


def add_time_reminder(reminder_id: str, cron_str: str):
    """Dynamically add a time reminder to the running scheduler."""
    if _scheduler is None or CronTrigger is None:
        return
    cron_args = _parse_cron(cron_str)
    trigger = CronTrigger(
        minute=cron_args.get("minute", "*"),
        hour=cron_args.get("hour", "*"),
        day=cron_args.get("day", "*"),
        month=cron_args.get("month", "*"),
        day_of_week=cron_args.get("day_of_week", "*"),
    )
    _scheduler.add_job(
        _fire_time_reminder,
        trigger=trigger,
        args=[reminder_id, f"cron: {cron_str}"],
        id=reminder_id,
        replace_existing=True,
    )