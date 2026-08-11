"""最小用户系统 MCP 工具 — 本地 SQLite profile + 活跃度/留存追踪。

遵循项目工具组模式（FastMCP 子实例 + server.py 统一注册，前缀 user）：
- user_create_profile / user_get_profile / user_update_profile
- user_record_activity / user_get_activity_stats / user_get_retention

默认单用户模式（user_id="local"），同时保留多用户支持以支撑留存统计。
"""

import time
from mcp.server.fastmcp import FastMCP

from ..user.store import get_user_store

user_tools = FastMCP("user-tools")


@user_tools.tool()
def create_profile(
    nickname: str = "",
    risk_profile: str = "moderate",
    investment_style: str = "value",
    experience_years: int = 0,
    goals: list = None,
    settings: dict = None,
    user_id: str = "local",
) -> dict:
    """创建本地用户 profile。

    首次使用前必须创建，用于留存/活跃度追踪的锚点。

    Args:
        nickname: 用户昵称
        risk_profile: 风险偏好，可选 conservative / moderate / aggressive
        investment_style: 投资风格，可选 value / growth / trend / mixed
        experience_years: 投资经验年限
        goals: 投资目标列表，如 ["长期复利", "跑赢沪深300"]
        settings: 附加设置（JSON 对象），如 {"currency": "CNY", "notify_channel": "feishu"}
        user_id: 用户 ID（默认 local 单用户）

    Returns:
        {created: true, profile: {...}}
    """
    store = get_user_store()
    if store.get_user(user_id):
        return {"created": False, "error": f"用户 {user_id} 已存在，请使用 user_update_profile 更新"}

    profile = store.create_user(
        user_id=user_id,
        nickname=nickname,
        risk_profile=risk_profile,
        investment_style=investment_style,
        experience_years=experience_years,
        goals=goals or [],
        settings=settings or {},
    )
    return {"created": True, "profile": profile}


@user_tools.tool()
def get_profile(user_id: str = "local") -> dict:
    """读取本地用户 profile。

    Args:
        user_id: 用户 ID（默认 local）

    Returns:
        {exists: true/false, profile: {...}} — profile 含昵称/风险偏好/投资风格/
        经验年限/目标/设置/创建与最近活跃时间
    """
    store = get_user_store()
    profile = store.get_user(user_id)
    if not profile:
        return {"exists": False, "profile": None, "hint": "尚未创建用户 profile，请先调用 user_create_profile"}
    return {"exists": True, "profile": profile}


@user_tools.tool()
def update_profile(
    nickname: str = None,
    risk_profile: str = None,
    investment_style: str = None,
    experience_years: int = None,
    goals: list = None,
    settings: dict = None,
    user_id: str = "local",
) -> dict:
    """更新本地用户 profile（只更新传入字段）。

    Args:
        nickname / risk_profile / investment_style / experience_years / goals / settings: 需更新的字段
        user_id: 用户 ID（默认 local）

    Returns:
        {updated: true/false, profile: {...}}
    """
    store = get_user_store()
    profile = store.update_user(
        user_id=user_id,
        nickname=nickname,
        risk_profile=risk_profile,
        investment_style=investment_style,
        experience_years=experience_years,
        goals=goals,
        settings=settings,
    )
    if not profile:
        return {"updated": False, "error": f"用户 {user_id} 不存在，请先调用 user_create_profile"}
    return {"updated": True, "profile": profile}


@user_tools.tool()
def record_activity(
    activity_type: str,
    detail: str = "",
    user_id: str = "local",
) -> dict:
    """记录一次用户活跃事件（自动更新 last_active_at）。

    供其他工具/Agent 在关键行为后调用，用于留存与活跃度统计。

    Args:
        activity_type: 事件类型，如 thought / decision / reminder / pattern / search / coaching / report
        detail: 事件说明（可选，最多 500 字）
        user_id: 用户 ID（默认 local）

    Returns:
        {recorded: true/false, activity_id}
    """
    store = get_user_store()
    activity_id = store.record_activity(user_id=user_id, activity_type=activity_type, detail=detail)
    if activity_id is None:
        return {"recorded": False, "error": f"用户 {user_id} 不存在，请先调用 user_create_profile"}
    return {"recorded": True, "activity_id": activity_id}


@user_tools.tool()
def get_activity_stats(user_id: str = "local", days: int = 30) -> dict:
    """获取用户活跃度统计（近 N 天）。

    Args:
        user_id: 用户 ID（默认 local）
        days: 统计窗口天数，默认 30

    Returns:
        {exists, stats: {total, active_days, daily_avg, by_type, last_activity_at, active_date_list}}
    """
    store = get_user_store()
    if not store.get_user(user_id):
        return {"exists": False, "error": f"用户 {user_id} 不存在，请先调用 user_create_profile"}
    stats = store.get_activity_stats(user_id=user_id, days=days)
    return {"exists": True, "stats": stats}


@user_tools.tool()
def get_retention(user_id: str = "local") -> dict:
    """获取用户留存摘要（首次/最近活跃、活跃天数、连续活跃天数、留存跨度）。

    Args:
        user_id: 用户 ID（默认 local）

    Returns:
        {exists, retention: {...}}
    """
    store = get_user_store()
    retention = store.get_retention_summary(user_id=user_id)
    if not retention:
        return {"exists": False, "error": f"用户 {user_id} 不存在，请先调用 user_create_profile"}
    return {"exists": True, "retention": retention}
