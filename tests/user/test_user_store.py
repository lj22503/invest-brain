# tests/user/test_user_store.py
"""UserStore 存储层测试 — 使用 tmp 数据库，不污染 data/memory/users.db"""

import pytest
from pathlib import Path

from src.mcp_server.user.store import UserStore


@pytest.fixture()
def store(tmp_path: Path) -> UserStore:
    return UserStore(db_path=str(tmp_path / "users_test.db"))


def test_create_and_get_user(store: UserStore):
    profile = store.create_user(
        user_id="local",
        nickname="老王",
        risk_profile="moderate",
        investment_style="value",
        experience_years=10,
        goals=["长期复利", "跑赢沪深300"],
        settings={"currency": "CNY"},
    )
    assert profile["id"] == "local"
    assert profile["nickname"] == "老王"
    assert profile["risk_profile"] == "moderate"
    assert profile["investment_style"] == "value"
    assert profile["experience_years"] == 10
    assert profile["goals"] == ["长期复利", "跑赢沪深300"]
    assert profile["settings"] == {"currency": "CNY"}

    fetched = store.get_user("local")
    assert fetched == profile


def test_get_missing_user_returns_none(store: UserStore):
    assert store.get_user("nobody") is None


def test_create_duplicate_user_raises(store: UserStore):
    store.create_user(user_id="local")
    with pytest.raises(Exception):
        store.create_user(user_id="local")


def test_create_user_rejects_bad_enum(store: UserStore):
    with pytest.raises(ValueError):
        store.create_user(user_id="local", risk_profile="super-risk")
    with pytest.raises(ValueError):
        store.create_user(user_id="local", investment_style="meme")


def test_update_user_partial(store: UserStore):
    store.create_user(user_id="local", nickname="老王", risk_profile="moderate")
    updated = store.update_user(user_id="local", nickname="老李", risk_profile="aggressive")
    assert updated["nickname"] == "老李"
    assert updated["risk_profile"] == "aggressive"
    # 未传字段保持不变
    assert updated["investment_style"] == "value"

    # 更新失败：用户不存在
    assert store.update_user(user_id="ghost", nickname="x") is None


def test_record_activity_requires_user(store: UserStore):
    assert store.record_activity("local", "thought") is None


def test_activity_stats_and_touch(store: UserStore):
    store.create_user(user_id="local", nickname="测试用户")
    assert store.record_activity("local", "thought", "记录想法") is not None
    assert store.record_activity("local", "decision", "买入茅台") is not None
    assert store.record_activity("local", "thought", "第二笔想法") is not None

    stats = store.get_activity_stats("local", days=30)
    assert stats["total"] == 3
    assert stats["active_days"] >= 1
    assert stats["daily_avg"] > 0
    assert stats["by_type"]["thought"] == 2
    assert stats["by_type"]["decision"] == 1
    assert len(stats["active_date_list"]) == stats["active_days"]


def test_retention_summary(store: UserStore):
    store.create_user(user_id="local", nickname="测试用户")
    store.record_activity("local", "thought")
    store.record_activity("local", "thought")

    summary = store.get_retention_summary("local")
    assert summary["user_id"] == "local"
    assert summary["total_active_days"] >= 1
    assert summary["consecutive_active_days"] >= 1
    assert summary["retention_days"] >= 1
    assert summary["first_active_at"] is not None
    assert summary["last_active_at"] is not None

    assert store.get_retention_summary("ghost") is None


def test_delete_user(store: UserStore):
    store.create_user(user_id="local")
    store.record_activity("local", "thought")
    assert store.delete_user("local") is True
    assert store.get_user("local") is None
    assert store.get_activity_stats("local", days=30)["total"] == 0
