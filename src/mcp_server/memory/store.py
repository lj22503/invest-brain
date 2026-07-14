"""Memory store client using SQLite"""

import sqlite3
import time
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

        # Scenarios table for learning coaching
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scenarios (
                id TEXT PRIMARY KEY,
                trigger_event TEXT NOT NULL,
                variable_structure TEXT,
                causal_chain TEXT,
                predicted_outcome TEXT,
                actual_outcome TEXT,
                lesson TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Add scenario_id to thoughts table (for cross-reference with ideas)
        result = cursor.execute(
            "SELECT COUNT(*) FROM pragma_table_info('thoughts') WHERE name='scenario_id'"
        ).fetchone()[0]
        if result == 0:
            cursor.execute("ALTER TABLE thoughts ADD COLUMN scenario_id TEXT REFERENCES scenarios(id)")

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

        # Dialogue sessions for Socratic multi-turn coaching
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dialogue_sessions (
                id TEXT PRIMARY KEY,
                scenario_id TEXT,
                user_input TEXT NOT NULL,
                current_step INTEGER DEFAULT 1,
                mode TEXT DEFAULT 'complex',
                status TEXT DEFAULT 'active',
                dialogue_history TEXT,
                pending_question TEXT,
                pending_options TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
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
        decision_id = f"dec_{int(time.time())}"
        cursor.execute(
            "INSERT INTO decisions (id, ticker, action, price, reason) VALUES (?, ?, ?, ?, ?)",
            (decision_id, ticker, action, price, reason)
        )
        conn.commit()
        conn.close()
        return decision_id

    def get_pattern_counts(self) -> dict:
        """Get current pattern counts keyed by pattern_type."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT pattern_type, COUNT(*) as cnt FROM behavior_patterns GROUP BY pattern_type"
        )
        rows = cursor.fetchall()
        conn.close()
        return {r[0]: r[1] for r in rows}

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

    def add_scenario(
        self,
        trigger_event: str,
        variable_structure: str = None,
        causal_chain: str = None,
        predicted_outcome: str = None,
        actual_outcome: str = None,
        lesson: str = None,
    ) -> str:
        """Add a new scenario record"""
        scenario_id = f"scenario_{int(time.time())}"
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO scenarios
               (id, trigger_event, variable_structure, causal_chain,
                predicted_outcome, actual_outcome, lesson)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (scenario_id, trigger_event, variable_structure,
             causal_chain, predicted_outcome, actual_outcome, lesson),
        )
        conn.commit()
        conn.close()
        return scenario_id

    def get_scenarios(self, limit: int = 50) -> list:
        """Get recent scenarios"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM scenarios ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {"id": r[0], "trigger_event": r[1], "variable_structure": r[2],
             "causal_chain": r[3], "predicted_outcome": r[4],
             "actual_outcome": r[5], "lesson": r[6], "created_at": r[7]}
            for r in rows
        ]

    def update_scenario_result(
        self,
        scenario_id: str,
        actual_outcome: str,
        lesson: str = None,
    ) -> bool:
        """Update scenario with actual result after event unfolds"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE scenarios
               SET actual_outcome = ?, lesson = ?
               WHERE id = ?""",
            (actual_outcome, lesson, scenario_id),
        )
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated

    def link_thought_to_scenario(self, thought_id: int, scenario_id: str) -> bool:
        """Link a thought to a scenario"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE thoughts SET scenario_id = ? WHERE id = ?",
            (scenario_id, thought_id),
        )
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated

    def get_scenario_thoughts(self, scenario_id: str) -> list:
        """Get all thoughts linked to a scenario"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM thoughts WHERE scenario_id = ? ORDER BY created_at DESC",
            (scenario_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {"id": r[0], "text": r[1], "ticker": r[2], "price": r[3],
             "indicator": r[4], "created_at": r[5], "scenario_id": r[6]}
            for r in rows
        ]

    def create_dialogue_session(self, user_input: str) -> str:
        """Create a new dialogue session"""
        import time
        session_id = f"session_{int(time.time() * 1000)}"
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO dialogue_sessions (id, user_input) VALUES (?, ?)""",
            (session_id, user_input),
        )
        conn.commit()
        conn.close()
        return session_id

    def get_dialogue_session(self, session_id: str) -> dict | None:
        """Get dialogue session by id"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM dialogue_sessions WHERE id = ?",
            (session_id,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row[0], "scenario_id": row[1], "user_input": row[2],
            "current_step": row[3], "mode": row[4], "status": row[5],
            "dialogue_history": row[6], "pending_question": row[7],
            "pending_options": row[8], "created_at": row[9], "updated_at": row[10],
        }

    def update_dialogue_session(self, session_id: str, **fields) -> bool:
        """Update dialogue session fields"""
        allowed = {"scenario_id", "current_step", "mode", "status",
                   "dialogue_history", "pending_question", "pending_options", "updated_at"}
        set_parts = []
        values = []
        for k, v in fields.items():
            if k in allowed:
                set_parts.append(f"{k} = ?")
                values.append(v)
        if not set_parts:
            return False
        set_parts.append("updated_at = CURRENT_TIMESTAMP")
        values.append(session_id)
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE dialogue_sessions SET {', '.join(set_parts)} WHERE id = ?",
            values,
        )
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated

    def append_dialogue_turn(self, session_id: str, turn: dict) -> bool:
        """Append a turn to dialogue_history (JSON array)"""
        import json
        session = self.get_dialogue_session(session_id)
        if not session:
            return False
        history = json.loads(session["dialogue_history"]) if session["dialogue_history"] else []
        history.append(turn)
        return self.update_dialogue_session(session_id, dialogue_history=json.dumps(history, ensure_ascii=False))

    def find_active_session_for(self, user_input: str) -> dict | None:
        """Find an active session matching the user_input (for resume after restart)"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM dialogue_sessions WHERE user_input = ? AND status = 'active' ORDER BY updated_at DESC LIMIT 1",
            (user_input,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row[0], "scenario_id": row[1], "user_input": row[2],
            "current_step": row[3], "mode": row[4], "status": row[5],
            "dialogue_history": row[6], "pending_question": row[7],
            "pending_options": row[8], "created_at": row[9], "updated_at": row[10],
        }


# Singleton instance
_memory_store: Optional[MemoryStore] = None


def get_memory_store() -> MemoryStore:
    """Get the singleton memory store instance"""
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryStore()
    return _memory_store