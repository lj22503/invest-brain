"""Memory store client using SQLite"""

import sqlite3
from typing import Optional
from pathlib import Path


class MemoryStore:
    """SQLite-based memory storage client"""

    def __init__(self, db_path: str = "data/memory/memory.db"):
        """
        Initialize the memory store.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        if not self.db_path.is_absolute():
            self.db_path = Path(__file__).resolve().parents[3] / self.db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        conn = self._get_conn()
        cursor = conn.cursor()

        # Thoughts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS thoughts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                ticker TEXT,
                price REAL,
                indicator TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Decisions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                action TEXT NOT NULL,
                price REAL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Reminders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                condition TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

        # Behavior patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS behavior_patterns (
                id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                trigger_content TEXT,
                context TEXT,
                happened_at TIMESTAMP,
                severity TEXT DEFAULT '中',
                times_count INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User principles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_principles (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def _get_conn(self) -> sqlite3.Connection:
        """Get a database connection with proper Unicode handling."""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA encoding = 'UTF-8'")
        return conn

    def add_thought(self, text: str, ticker: Optional[str] = None,
                    price: Optional[float] = None, indicator: Optional[str] = None) -> int:
        """Add a thought record"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO thoughts (text, ticker, price, indicator) VALUES (?, ?, ?, ?)",
            (text, ticker, price, indicator)
        )
        conn.commit()
        thought_id = cursor.lastrowid
        conn.close()
        return thought_id

    def get_thoughts(self, ticker: Optional[str] = None, limit: int = 10) -> list:
        """Get thoughts, optionally filtered by ticker"""
        conn = self._get_conn()
        cursor = conn.cursor()

        if ticker:
            cursor.execute(
                "SELECT * FROM thoughts WHERE ticker = ? ORDER BY created_at DESC LIMIT ?",
                (ticker, limit)
            )
        else:
            cursor.execute("SELECT * FROM thoughts ORDER BY created_at DESC LIMIT ?", (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [
            {"id": r[0], "text": r[1], "ticker": r[2], "price": r[3],
             "indicator": r[4], "created_at": r[5]}
            for r in rows
        ]

    def add_decision(self, ticker: str, action: str, price: Optional[float] = None,
                     reason: Optional[str] = None) -> str:
        """Add a decision record"""
        conn = self._get_conn()
        cursor = conn.cursor()
        import time
        decision_id = f"dec_{int(time.time())}"
        cursor.execute(
            "INSERT INTO decisions (id, ticker, action, price, reason) VALUES (?, ?, ?, ?, ?)",
            (decision_id, ticker, action, price, reason)
        )
        conn.commit()
        conn.close()
        return decision_id

    def add_reminder(self, reminder_id: str, reminder_type: str, condition: str) -> bool:
        """Add a reminder"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO reminders (id, type, condition) VALUES (?, ?, ?)",
            (reminder_id, reminder_type, condition)
        )
        conn.commit()
        conn.close()
        return True

    def get_reminders(self, status: str = "active") -> list:
        """Get reminders by status"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reminders WHERE status = ?", (status,))
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "type": r[1], "condition": r[2], "status": r[3], "created_at": r[4]} for r in rows]

    def delete_reminder(self, reminder_id: str) -> bool:
        """Delete a reminder"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted


# Singleton instance
_memory_store: Optional[MemoryStore] = None


def get_memory_store() -> MemoryStore:
    """Get the singleton memory store instance"""
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryStore()
    return _memory_store