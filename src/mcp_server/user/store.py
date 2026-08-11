"""User profile store using SQLite — 本地用户 profile 与活跃度/留存追踪。

遵循 memory/store.py 的既有 SQLite 模式：
- 默认 db 为 data/memory/users.db（已被 .gitignore 保护，数据不出本地）
- 相对路径基于仓库根解析
- 每次操作独立连接，避免多线程/多进程共享连接问题
"""

import json
import sqlite3
import time
from typing import Optional
from pathlib import Path

# profile 字段白名单（update 时只允许更新这些字段）
_PROFILE_FIELDS = {
    "nickname",
    "risk_profile",
    "investment_style",
    "experience_years",
    "goals",
    "settings",
}

_RISK_PROFILES = {"conservative", "moderate", "aggressive"}
_STYLES = {"value", "growth", "trend", "mixed"}


class UserStore:
    """SQLite-based local user profile storage client"""

    def __init__(self, db_path: str = "data/memory/users.db"):
        """
        Initialize the user store.

        Args:
            db_path: Path to SQLite database (relative paths resolve from repo root)
        """
        self.db_path = Path(db_path)
        if not self.db_path.is_absolute():
            self.db_path = Path(__file__).resolve().parents[3] / self.db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Get a database connection with proper Unicode handling."""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA encoding = 'UTF-8'")
        return conn

    def _init_db(self):
        """Initialize database schema"""
        conn = self._get_conn()
        cursor = conn.cursor()

        # Users table — 本地用户 profile
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                nickname TEXT,
                risk_profile TEXT DEFAULT 'moderate',
                investment_style TEXT DEFAULT 'value',
                experience_years INTEGER DEFAULT 0,
                goals TEXT,
                settings TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User activity table — 留存与活跃度追踪
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                detail TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_user_activity_user_time "
            "ON user_activity (user_id, created_at)"
        )

        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Profile CRUD
    # ------------------------------------------------------------------

    def create_user(
        self,
        user_id: str = "local",
        nickname: str = "",
        risk_profile: str = "moderate",
        investment_style: str = "value",
        experience_years: int = 0,
        goals: Optional[list] = None,
        settings: Optional[dict] = None,
    ) -> dict:
        """Create a user profile. Raises ValueError if user already exists."""
        if risk_profile not in _RISK_PROFILES:
            raise ValueError(f"risk_profile 必须是 {'/'.join(sorted(_RISK_PROFILES))} 之一")
        if investment_style not in _STYLES:
            raise ValueError(f"investment_style 必须是 {'/'.join(sorted(_STYLES))} 之一")

        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO users
               (id, nickname, risk_profile, investment_style, experience_years, goals, settings)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                nickname,
                risk_profile,
                investment_style,
                int(experience_years),
                json.dumps(goals, ensure_ascii=False) if goals is not None else None,
                json.dumps(settings, ensure_ascii=False) if settings is not None else None,
            ),
        )
        conn.commit()
        conn.close()

        return self.get_user(user_id)

    def get_user(self, user_id: str = "local") -> Optional[dict]:
        """Get user profile by id, or None if not found."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None

        return {
            "id": row[0],
            "nickname": row[1],
            "risk_profile": row[2],
            "investment_style": row[3],
            "experience_years": row[4],
            "goals": json.loads(row[5]) if row[5] else [],
            "settings": json.loads(row[6]) if row[6] else {},
            "created_at": row[7],
            "updated_at": row[8],
            "last_active_at": row[9],
        }

    def update_user(self, user_id: str = "local", **fields) -> Optional[dict]:
        """Update user profile fields (whitelist). Returns updated profile or None if user missing."""
        if not fields:
            return self.get_user(user_id)

        set_parts = []
        values = []
        for k, v in fields.items():
            if k not in _PROFILE_FIELDS:
                continue
            if v is None:
                continue  # None 表示不更新该字段
            if k == "risk_profile" and v not in _RISK_PROFILES:
                raise ValueError(f"risk_profile 必须是 {'/'.join(sorted(_RISK_PROFILES))} 之一")
            if k == "investment_style" and v not in _STYLES:
                raise ValueError(f"investment_style 必须是 {'/'.join(sorted(_STYLES))} 之一")
            if k in ("goals", "settings"):
                v = json.dumps(v, ensure_ascii=False) if v is not None else None
            set_parts.append(f"{k} = ?")
            values.append(v)

        if not set_parts:
            return self.get_user(user_id)

        set_parts.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)

        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE users SET {', '.join(set_parts)} WHERE id = ?",
            values,
        )
        conn.commit()
        conn.close()
        if cursor.rowcount == 0:
            return None
        return self.get_user(user_id)

    def delete_user(self, user_id: str = "local") -> bool:
        """Delete a user profile and its activity history."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_activity WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted

    # ------------------------------------------------------------------
    # 活跃度 / 留存追踪
    # ------------------------------------------------------------------

    def touch(self, user_id: str = "local") -> bool:
        """Update last_active_at for a user. Returns False if user does not exist."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET last_active_at = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,),
        )
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated

    def record_activity(
        self,
        user_id: str = "local",
        activity_type: str = "interaction",
        detail: str = "",
    ) -> Optional[int]:
        """Record a user activity event (auto-touches last_active_at).

        Returns:
            activity record id, or None if the user profile does not exist.
        """
        if not self.get_user(user_id):
            return None
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO user_activity (user_id, activity_type, detail)
               VALUES (?, ?, ?)""",
            (user_id, activity_type, detail[:500]),
        )
        conn.commit()
        activity_id = cursor.lastrowid
        conn.close()
        self.touch(user_id)
        return activity_id

    def get_activity_stats(self, user_id: str = "local", days: int = 30) -> dict:
        """Return activity statistics for the last N days.

        Returns:
            {total, days, active_days, daily_avg, by_type: {type: count},
             last_activity_at, active_date_list: [...]}
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT COUNT(*), COUNT(DISTINCT date(created_at)),
                      MAX(created_at)
               FROM user_activity
               WHERE user_id = ? AND created_at >= datetime('now', ?)""",
            (user_id, f"-{int(days)} days"),
        )
        total, active_days, last_activity = cursor.fetchone()

        cursor.execute(
            """SELECT activity_type, COUNT(*)
               FROM user_activity
               WHERE user_id = ? AND created_at >= datetime('now', ?)
               GROUP BY activity_type ORDER BY COUNT(*) DESC""",
            (user_id, f"-{int(days)} days"),
        )
        by_type = {r[0]: r[1] for r in cursor.fetchall()}

        cursor.execute(
            """SELECT DISTINCT date(created_at)
               FROM user_activity
               WHERE user_id = ? AND created_at >= datetime('now', ?)
               ORDER BY date(created_at) DESC""",
            (user_id, f"-{int(days)} days"),
        )
        active_date_list = [r[0] for r in cursor.fetchall()]
        conn.close()

        return {
            "total": total,
            "days": int(days),
            "active_days": active_days,
            "daily_avg": round(total / active_days, 2) if active_days else 0.0,
            "by_type": by_type,
            "last_activity_at": last_activity,
            "active_date_list": active_date_list,
        }

    def get_retention_summary(self, user_id: str = "local") -> Optional[dict]:
        """Return a retention-oriented summary for the user.

        Returns:
            None if user missing, else {first_active_at, last_active_at, total_active_days,
            consecutive_active_days, registration_date, retention_days}
        """
        user = self.get_user(user_id)
        if not user:
            return None

        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MIN(date(created_at)), MAX(date(created_at)), COUNT(DISTINCT date(created_at)) "
            "FROM user_activity WHERE user_id = ?",
            (user_id,),
        )
        first_day, last_day, total_active_days = cursor.fetchone()

        # Consecutive active days ending at the most recent activity day
        if last_day:
            cursor.execute(
                """WITH RECURSIVE days(d) AS (
                       SELECT date(?)
                       UNION ALL
                       SELECT date(d, '-1 day') FROM days
                       WHERE date(d, '-1 day') >= date(?, '-90 day')
                   )
                   SELECT COUNT(*) FROM days d
                   WHERE d.d IN (SELECT DISTINCT date(created_at) FROM user_activity WHERE user_id = ?)""",
                (last_day, last_day, user_id),
            )
            consecutive = cursor.fetchone()[0]
        else:
            consecutive = 0
        conn.close()

        # 留存天数：自首次活跃到最近活跃的天数跨度（含首尾）
        retention_days = 0
        if first_day and last_day:
            retention_days = (time.mktime(time.strptime(last_day, "%Y-%m-%d"))
                              - time.mktime(time.strptime(first_day, "%Y-%m-%d"))) // 86400 + 1

        return {
            "user_id": user_id,
            "registered_at": user["created_at"],
            "first_active_at": first_day,
            "last_active_at": last_day,
            "total_active_days": total_active_days,
            "consecutive_active_days": int(consecutive),
            "retention_days": int(retention_days),
        }


# Singleton instance
_user_store: Optional[UserStore] = None


def get_user_store() -> UserStore:
    """Get the singleton user store instance"""
    global _user_store
    if _user_store is None:
        _user_store = UserStore()
    return _user_store
