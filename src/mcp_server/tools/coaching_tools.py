"""Coaching tools — learning coaching MCP tools

学习辅导模式：自动判断简单/复杂问题
- 简单：直接输出 10 步投研分析
- 复杂：Socratic 多轮引导对话
- 两者结束均自动归档到情景库
"""

from mcp.server.fastmcp import FastMCP

from ..coaching.trigger import detect_complexity
from ..coaching.llm import run_simple_10steps
from ..coaching.prompts import GROUP1_STEPS
from ..coaching.scenario import archive_scenario, get_recent_scenarios
from ..coaching import session as session_mod
from ..coaching import socratic

coaching_tools = FastMCP("coaching-tools")


def _handle_simple(user_input: str) -> dict:
    """Simple mode: direct 10-step analysis"""
    result_text = run_simple_10steps(user_input.strip())

    scenario_id = None
    try:
        scenario_id = archive_scenario(
            trigger_event=user_input.strip(),
            causal_chain="（见下方10步分析）",
        )
    except Exception:
        pass

    return {
        "status": "success",
        "mode": "simple",
        "answer": result_text,
        "scenario_id": scenario_id,
    }


def _handle_complex_new(user_input: str) -> dict:
    """Complex mode: start new Socratic session"""
    session_id = session_mod.start_session(user_input)

    question_data = socratic.generate_question(
        step_index=1,
        user_topic=user_input,
        history=[],
    )

    session_mod.save_current_question(
        session_id,
        question=question_data["question"],
        options=question_data["options"],
        step=1,
    )

    return {
        "status": "success",
        "mode": "complex",
        "session_id": session_id,
        "current_step": 1,
        "total_steps": len(GROUP1_STEPS),
        "question": question_data["question"],
        "options": question_data["options"],
        "focus": question_data.get("focus", ""),
    }


def _handle_session_continue(session_id: str, user_input: str) -> dict:
    """Continue existing Socratic session"""
    import json

    session = session_mod.get_session(session_id)
    if not session:
        return {"status": "error", "message": f"会话 {session_id} 不存在"}
    if session["status"] != "active":
        return {"status": "error", "message": f"会话已{session['status']}"}

    # Check abandon intent
    if socratic.detect_abandon_intent(user_input):
        return _finalize_session(session, status="abandoned")

    # Check simple switch
    if socratic.detect_simple_switch(user_input):
        simple_result = _handle_simple(session["user_input"])
        session_mod.complete_session(
            session_id, simple_result.get("scenario_id", ""),
            final_status="switched_to_simple",
        )
        return {**simple_result, "session_id": session_id, "switched_from_socratic": True}

    # Parse user choice
    options = json.loads(session["pending_options"]) if session.get("pending_options") else []
    if not options:
        return {"status": "error", "message": "会话状态异常：无 pending options"}

    choice_key, choice_label = socratic.parse_user_choice(user_input, options)
    current_step = session["current_step"]

    handle_result = socratic.handle_user_choice(
        choice_key=choice_key,
        choice_label=choice_label,
        question=session["pending_question"],
        options=options,
        user_raw_input=user_input,
    )

    session_mod.record_user_choice(
        session_id,
        choice_key=choice_key,
        choice_label=choice_label,
        user_input=user_input,
        llm_response=handle_result["acknowledgement"] + " " + handle_result["feedback"],
    )

    # Reload session for updated history
    session = session_mod.get_session(session_id)
    history = json.loads(session["dialogue_history"]) if session.get("dialogue_history") else []

    # Check if done
    if current_step >= len(GROUP1_STEPS):
        return _finalize_session(session, history=history, status="completed")

    # Generate next question
    next_step = current_step + 1
    question_data = socratic.generate_question(
        step_index=next_step,
        user_topic=session["user_input"],
        history=history,
    )

    session_mod.save_current_question(
        session_id,
        question=question_data["question"],
        options=question_data["options"],
        step=next_step,
    )

    return {
        "status": "success",
        "mode": "complex",
        "session_id": session_id,
        "current_step": next_step,
        "total_steps": len(GROUP1_STEPS),
        "question": question_data["question"],
        "options": question_data["options"],
        "focus": question_data.get("focus", ""),
        "acknowledgement": handle_result["acknowledgement"],
        "feedback": handle_result["feedback"],
    }


def _finalize_session(session, history=None, status="completed"):
    """Complete a coaching session with summary and archive"""
    import json

    session_id = session["id"]
    history = history if history is not None else json.loads(session.get("dialogue_history") or "[]")

    final_summary = socratic.generate_final_summary(
        topic=session["user_input"],
        history=history,
    )

    scenario_id = archive_scenario(
        trigger_event=session["user_input"],
        variable_structure=f"Socratic {len(history)} 轮对话",
        causal_chain="（多轮对话过程）",
        predicted_outcome=final_summary,
        lesson=f"会话模式: Socratic, 完成度: {status}",
    )

    session_mod.complete_session(session_id, scenario_id, final_status=status)

    return {
        "status": "success",
        "mode": "complex_finalized",
        "session_id": session_id,
        "scenario_id": scenario_id,
        "session_status": status,
        "final_summary": final_summary,
    }


@coaching_tools.tool()
def start_coaching(user_input: str, mode: str = None) -> dict:
    """
    启动学习辅导，分析投资问题。

    自动判断问题是简单还是复杂：
    - 简单问题（如"该不该买XX"）→ 直接输出 10 步标准投研分析
    - 复杂问题（如"为什么XX和YY走势背离"）→ 启动 Socratic 多轮引导对话

    Args:
        user_input: 用户提出的投资问题（如"茅台2000块值得买吗"）
        mode: 强制模式，"simple" 或 "complex"，留空则自动判断

    Returns:
        simple 模式: {"status":"success", "mode":"simple", "answer": "...", "scenario_id":"..."}
        complex 模式: {"status":"success", "mode":"complex", "session_id":"...", "question":"...", "options":[...]}
    """
    complexity = mode or detect_complexity(user_input)
    if complexity == "simple":
        return _handle_simple(user_input)
    else:
        return _handle_complex_new(user_input)


@coaching_tools.tool()
def continue_coaching(session_id: str, user_input: str) -> dict:
    """
    继续一个进行中的 Socratic 多轮辅导会话。

    回复选项字母 (A/B/C/D) 来推进对话，或输入
    「直接说」切换到简单模式、「别问了」放弃本轮。

    Args:
        session_id: 由 start_coaching 返回的会话 ID
        user_input: 用户对当前问题的回答（选项字母或指令文本）

    Returns:
        dict: 下一轮问题或最终结果
    """
    return _handle_session_continue(session_id, user_input)


@coaching_tools.tool()
def abandon_coaching(session_id: str) -> dict:
    """
    放弃当前进行中的 Socratic 辅导会话并归档。

    Args:
        session_id: 要放弃的会话 ID

    Returns:
        dict: 包含 final_summary 的归档结果
    """
    import json

    session = session_mod.get_session(session_id)
    if not session:
        return {"status": "error", "message": f"会话 {session_id} 不存在"}
    history = json.loads(session.get("dialogue_history") or "[]")
    return _finalize_session(session, history=history, status="abandoned")


@coaching_tools.tool()
def list_coaching_scenarios(limit: int = 20) -> dict:
    """
    列出最近的学习辅导情景记录。

    每次辅导结束（无论是简单模式还是复杂模式）都会自动归档到情景库，
    包括触发事件、变量结构、因果链和最终结论。

    Args:
        limit: 返回的记录数量，默认 20

    Returns:
        dict: {"count": N, "scenarios": [...]}
    """
    scenarios = get_recent_scenarios(limit=limit)
    return {"count": len(scenarios), "scenarios": scenarios}
