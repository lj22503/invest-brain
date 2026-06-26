"""情景库读写操作"""

from typing import Optional
from ..memory.store import get_memory_store


def archive_scenario(
    trigger_event: str,
    variable_structure: str = None,
    causal_chain: str = None,
    predicted_outcome: str = None,
    actual_outcome: str = None,
    lesson: str = None,
) -> str:
    """写入新情景记录，返回 scenario_id"""
    store = get_memory_store()
    return store.add_scenario(
        trigger_event=trigger_event,
        variable_structure=variable_structure,
        causal_chain=causal_chain,
        predicted_outcome=predicted_outcome,
        actual_outcome=actual_outcome,
        lesson=lesson,
    )


def get_recent_scenarios(limit: int = 20) -> list:
    """获取最近的情景记录"""
    store = get_memory_store()
    return store.get_scenarios(limit=limit)


def update_scenario_with_result(
    scenario_id: str,
    actual_outcome: str,
    lesson: str = None,
) -> bool:
    """事后更新情景的实际结果（用户反馈或系统检测）"""
    store = get_memory_store()
    return store.update_scenario_result(scenario_id, actual_outcome, lesson)


def link_thought_to_scenario(thought_id: int, scenario_id: str) -> bool:
    """把一条想法关联到情景"""
    store = get_memory_store()
    return store.link_thought_to_scenario(thought_id, scenario_id)


def get_scenario_with_thoughts(scenario_id: str) -> dict:
    """获取情景及其关联的所有想法"""
    store = get_memory_store()
    all_scenarios = store.get_scenarios(limit=1000)
    matched = [s for s in all_scenarios if s["id"] == scenario_id]
    if not matched:
        return None
    thoughts = store.get_scenario_thoughts(scenario_id)
    return {
        **matched[0],
        "thoughts": thoughts,
    }