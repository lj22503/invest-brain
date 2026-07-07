"""Dialogue session management"""

import json
from typing import Optional
from ..memory.store import get_memory_store


def start_session(user_input: str) -> str:
    """Start a new dialogue session, returns session_id"""
    store = get_memory_store()
    return store.create_dialogue_session(user_input)


def get_session(session_id: str) -> Optional[dict]:
    """Load a session by id"""
    store = get_memory_store()
    return store.get_dialogue_session(session_id)


def save_current_question(session_id: str, question: str, options: list, step: int) -> bool:
    """Save the current pending question + options to the session"""
    store = get_memory_store()
    return store.update_dialogue_session(
        session_id,
        pending_question=question,
        pending_options=json.dumps(options, ensure_ascii=False),
        current_step=step,
    )


def record_user_choice(
    session_id: str,
    choice_key: str,
    choice_label: str,
    user_input: str,
    llm_response: str,
) -> bool:
    """Record user's choice in dialogue history"""
    store = get_memory_store()
    session = store.get_dialogue_session(session_id)
    if not session:
        return False

    turn = {
        "step": session["current_step"],
        "question": session["pending_question"],
        "options": json.loads(session["pending_options"]) if session["pending_options"] else [],
        "user_choice_key": choice_key,
        "user_choice_label": choice_label,
        "user_raw_input": user_input,
        "llm_response": llm_response,
    }

    # Append to history
    history = json.loads(session["dialogue_history"]) if session["dialogue_history"] else []
    history.append(turn)

    return store.update_dialogue_session(
        session_id,
        dialogue_history=json.dumps(history, ensure_ascii=False),
        pending_question=None,
        pending_options=None,
    )


def advance_step(session_id: str) -> int:
    """Move to next step, returns new current_step"""
    store = get_memory_store()
    session = store.get_dialogue_session(session_id)
    if not session:
        return 0
    new_step = session["current_step"] + 1
    store.update_dialogue_session(session_id, current_step=new_step)
    return new_step


def complete_session(session_id: str, scenario_id: str, final_status: str = "completed") -> bool:
    """Mark session complete and link to scenario"""
    store = get_memory_store()
    return store.update_dialogue_session(
        session_id,
        status=final_status,
        scenario_id=scenario_id,
    )


def find_active_session_for(user_input: str) -> Optional[dict]:
    """Find active session matching user_input (for resume)"""
    store = get_memory_store()
    return store.find_active_session_for(user_input)
