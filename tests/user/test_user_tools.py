# tests/user/test_user_tools.py
"""最小用户系统 MCP 工具层测试 — monkeypatch get_user_store 指向 tmp db"""

import pytest
from pathlib import Path

import src.mcp_server.tools.user_tools as ut
from src.mcp_server.user.store import UserStore


@pytest.fixture()
def store(tmp_path: Path) -> UserStore:
    return UserStore(db_path=str(tmp_path / "users_tools_test.db"))


@pytest.fixture()
def patch_store(monkeypatch, store: UserStore):
    monkeypatch.setattr(ut, "get_user_store", lambda: store)
    return store


def test_create_profile_tool(patch_store: UserStore):
    result = ut.create_profile(
        nickname="小李",
        risk_profile="aggressive",
        investment_style="growth",
        experience_years=3,
        goals=["快速成长"],
        settings={"notify_channel": "dingtalk"},
    )
    assert result["created"] is True
    assert result["profile"]["nickname"] == "小李"
    assert result["profile"]["investment_style"] == "growth"


def test_create_profile_duplicate(patch_store: UserStore):
    ut.create_profile(user_id="local")
    result = ut.create_profile(user_id="local")
    assert result["created"] is False
    assert "已存在" in result["error"]


def test_get_profile_missing(patch_store: UserStore):
    result = ut.get_profile(user_id="ghost")
    assert result["exists"] is False
    assert "user_create_profile" in result["hint"]


def test_update_profile_tool(patch_store: UserStore):
    ut.create_profile(user_id="local", nickname="老王")
    result = ut.update_profile(user_id="local", nickname="老李", goals=["稳健增值"])
    assert result["updated"] is True
    assert result["profile"]["nickname"] == "老李"
    assert result["profile"]["goals"] == ["稳健增值"]

    missing = ut.update_profile(user_id="ghost", nickname="x")
    assert missing["updated"] is False


def test_record_activity_tool(patch_store: UserStore):
    ut.create_profile(user_id="local")
    result = ut.record_activity(activity_type="thought", detail="记录想法", user_id="local")
    assert result["recorded"] is True
    assert result["activity_id"] is not None

    no_user = ut.record_activity(activity_type="thought", user_id="ghost")
    assert no_user["recorded"] is False


def test_get_activity_stats_tool(patch_store: UserStore):
    ut.create_profile(user_id="local")
    ut.record_activity("thought", user_id="local")
    ut.record_activity("decision", user_id="local")

    result = ut.get_activity_stats(user_id="local", days=30)
    assert result["exists"] is True
    assert result["stats"]["total"] == 2
    assert result["stats"]["by_type"]["thought"] == 1

    missing = ut.get_activity_stats(user_id="ghost")
    assert missing["exists"] is False


def test_get_retention_tool(patch_store: UserStore):
    ut.create_profile(user_id="local")
    ut.record_activity("thought", user_id="local")

    result = ut.get_retention(user_id="local")
    assert result["exists"] is True
    assert result["retention"]["total_active_days"] >= 1

    missing = ut.get_retention(user_id="ghost")
    assert missing["exists"] is False
