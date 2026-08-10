"""Coaching tools — learning coaching MCP tools

学习辅导模式：自动判断简单/复杂问题
- 简单：直接输出 10 步投研分析
- 复杂：Socratic 多轮引导对话
- 两者结束均自动归档到情景库
- 补充工具：切换模式 / 对比历史 / 阈值建议 / 判断迭代
"""

from mcp.server.fastmcp import FastMCP

from ..coaching.trigger import detect_complexity
from ..coaching.llm import run_simple_10steps, coaching_llm_call
from ..coaching.prompts import GROUP1_STEPS, GROUP2_COMPARE, GROUP2_THRESHOLD, GROUP2_ITERATE
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


# ========== 补充工具 #5-#8 ==========


def _find_scenario_by_id(scenario_id: str) -> dict:
    """从情景库按 ID 查找单条记录"""
    all_scenarios = get_recent_scenarios(limit=1000)
    for s in all_scenarios:
        if s.get("id") == scenario_id:
            return s
    return None


@coaching_tools.tool()
def coaching_switch_to_simple(session_id: str) -> dict:
    """
    将进行中的 Socratic 多轮辅导会话切换到简单模式。

    放弃剩余的问答题，直接用已有的分析上下文走一遍
    10 步标准投研模板输出，并正常归档到情景库。

    Args:
        session_id: 由 start_coaching 返回的会话 ID

    Returns:
        dict: simple 模式结果，含 answer 和 scenario_id
    """
    import json

    session = session_mod.get_session(session_id)
    if not session:
        return {"status": "error", "message": f"会话 {session_id} 不存在"}
    if session["status"] != "active":
        return {"status": "error", "message": f"会话已{session['status']}，无法切换"}

    simple_result = _handle_simple(session["user_input"])
    session_mod.complete_session(
        session_id,
        simple_result.get("scenario_id", ""),
        final_status="switched_to_simple",
    )
    return {**simple_result, "session_id": session_id, "switched_from_socratic": True}


@coaching_tools.tool()
def coaching_compare_history(event: str, scenario_id: str) -> dict:
    """
    对比当前新事件与历史情景的变量结构异同。

    从情景库中取出指定历史事件，用 LLM 对比分析：
    - 相同点是什么
    - 核心差异是什么
    - 上次的教训是否适用于本次

    Args:
        event: 当前新事件的描述（如"美联储降息50bp"）
        scenario_id: 要对比的历史情景 ID（从 list_coaching_scenarios 获取）

    Returns:
        dict: {"status":"success", "comparison": "..."}
    """
    scenario = _find_scenario_by_id(scenario_id)
    if not scenario:
        return {"status": "error", "message": f"情景 {scenario_id} 不存在"}

    # 构建历史情景摘要
    scenario_summary = (
        f"触发事件：{scenario.get('trigger_event', '')}\n"
        f"变量结构：{scenario.get('variable_structure', '')}\n"
        f"因果链：{scenario.get('causal_chain', '')}\n"
        f"教训：{scenario.get('lesson', '')}"
    )

    prompt = GROUP2_COMPARE.replace("{scenario_id}", scenario_id) + "\n\n【历史情景详情】\n" + scenario_summary + "\n\n【当前新事件】\n" + event

    comparison = coaching_llm_call(prompt, scene="coaching_synthesis")
    return {"status": "success", "comparison": comparison, "scenario_id": scenario_id}


@coaching_tools.tool()
def coaching_suggest_thresholds(asset_class: str) -> dict:
    """
    根据用户过去的交易记录，建议触发深度分析的数值阈值。

    对于指定的资产类别（如"利率"、"汇率"、"商品"），
    LLM 会分析多大的变动幅度应该触发深度分析，
    给出具体数值阈值建议并说明理由。

    Args:
        asset_class: 资产类别，如"利率"、"汇率"、"商品"、"A股"、"美股"

    Returns:
        dict: {"status":"success", "suggestion": "..."}
    """
    prompt = GROUP2_THRESHOLD.format(asset_class=asset_class)
    suggestion = coaching_llm_call(prompt, scene="coaching_synthesis")
    return {"status": "success", "suggestion": suggestion, "asset_class": asset_class}


@coaching_tools.tool()
def coaching_iterate_judgment(wrong_variable: str, correct_result: str) -> dict:
    """
    当用户判断错误后，更新投研规则中的变量优先级。

    输入上次判断错误的变量和实际正确结果，
    LLM 会分析并给出变量优先级调整建议——下次遇到类似结构，
    哪个变量该调高、哪个该调低。

    Args:
        wrong_variable: 未按预期变化的变量（如"黄金与美元同涨"）
        correct_result: 实际发生的正确结果（如"黄金独立上涨，美元回落"）

    Returns:
        dict: {"status":"success", "iteration": "..."}
    """
    prompt = GROUP2_ITERATE.format(
        wrong_variable=wrong_variable,
        correct_result=correct_result,
    )
    iteration = coaching_llm_call(prompt, scene="coaching_synthesis")
    return {"status": "success", "iteration": iteration}
