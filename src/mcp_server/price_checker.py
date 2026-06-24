"""Price/PE condition checker - runs on assistant startup."""

import logging
import sqlite3
import time
from pathlib import Path
from typing import Optional

from .memory.store import get_memory_store
from .notifier import send_notification
from .datasources.akshare_datasource import get_stock_quote, get_valuation

logger = logging.getLogger(__name__)


def _init_reminder_log_table():
    """Create reminder_log table if not exists."""
    db_path = Path(__file__).resolve().parents[2] / "data" / "memory" / "memory.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
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


def _log_trigger(reminder_id: str, reason: str):
    """Log a triggered reminder."""
    _init_reminder_log_table()
    db_path = Path(__file__).resolve().parents[2] / "data" / "memory" / "memory.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reminder_log (reminder_id, triggered_at, trigger_reason) VALUES (?, ?, ?)",
        (reminder_id, time.strftime("%Y-%m-%d %H:%M:%S"), reason)
    )
    conn.commit()
    conn.close()


def check_price_conditions() -> list:
    """
    Check all active price/PE reminders on startup.
    Returns list of triggered reminders.
    """
    store = get_memory_store()
    reminders = store.get_reminders(status="active")
    triggered = []

    for rem in reminders:
        if rem.get("type") not in ("price", "pe_ratio"):
            continue

        condition = rem.get("condition", "")
        parts = condition.split()
        if len(parts) < 3:
            continue

        ticker = parts[0]
        operator = parts[1]
        target_value = float(parts[2])

        try:
            if rem["type"] == "price":
                quote = get_stock_quote(ticker)
                if "error" in quote:
                    logger.warning(f"Failed to get quote for {ticker}: {quote['error']}")
                    continue
                current_price = quote.get("price")
                if current_price is None:
                    continue

                fired = False
                if operator == "below" and current_price < target_value:
                    fired = True
                elif operator == "above" and current_price > target_value:
                    fired = True

                if fired:
                    name = quote.get("name", ticker)
                    _log_trigger(rem["id"], f"{ticker} 当前价 {current_price} {operator} {target_value}")
                    send_notification(
                        f"⏰ 价格提醒触发\n{name} 当前价格 {current_price}元，条件：{operator} {target_value}",
                        channel="feishu"
                    )
                    triggered.append({
                        "reminder_id": rem["id"],
                        "ticker": ticker,
                        "name": name,
                        "current_price": current_price,
                        "condition": condition,
                    })

            elif rem["type"] == "pe_ratio":
                val = get_valuation(ticker)
                if "error" in val:
                    continue
                pe = val.get("pe")
                if pe is None:
                    continue

                fired = False
                if operator == "below" and pe < target_value:
                    fired = True
                elif operator == "above" and pe > target_value:
                    fired = True

                if fired:
                    name = val.get("name", ticker)
                    _log_trigger(rem["id"], f"{ticker} 当前PE {pe} {operator} {target_value}")
                    send_notification(
                        f"⏰ PE分位提醒触发\n{name} 当前PE {pe}，条件：{operator} {target_value}",
                        channel="feishu"
                    )
                    triggered.append({
                        "reminder_id": rem["id"],
                        "ticker": ticker,
                        "name": name,
                        "current_pe": pe,
                        "condition": condition,
                    })

        except Exception as e:
            logger.error(f"Error checking reminder {rem['id']}: {e}")

    if triggered:
        logger.info(f"Price conditions triggered: {len(triggered)} reminders")

    return triggered


def get_triggered_reminders() -> list:
    """Get recent triggered reminder log."""
    _init_reminder_log_table()
    db_path = Path(__file__).resolve().parents[2] / "data" / "memory" / "memory.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM reminder_log ORDER BY triggered_at DESC LIMIT 20"
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "reminder_id": r[1], "triggered_at": r[2], "reason": r[3]}
        for r in rows
    ]