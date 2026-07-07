"""Socratic multi-turn dialogue engine"""

import json
import re
from typing import Optional
from .prompts import (
    GROUP1_STEPS, SOCRATIC_INTRO, SOCRATIC_GENERATE_QUESTION,
    SOCRATIC_HANDLE_CHOICE, SOCRATIC_FINAL_SUMMARY,
)
from .llm import coaching_chat_messages
from . import session as session_mod


# Keywords that signal user wants to stop/abandon
ABANDON_KEYWORDS = ["别问了", "不聊了", "停", "算了", "不做了", "取消"]
# Keywords that signal user wants to switch to simple mode
SIMPLE_SWITCH_KEYWORDS = ["直接说", "别引导了", "直接出答案", "不用问了", "直接给答案", "简单点"]


def detect_abandon_intent(text: str) -> bool:
    """Detect if user wants to abandon the dialogue"""
    return any(kw in text for kw in ABANDON_KEYWORDS)


def detect_simple_switch(text: str) -> bool:
    """Detect if user wants to switch to simple mode"""
    return any(kw in text for kw in SIMPLE_SWITCH_KEYWORDS)


def parse_user_choice(text: str, options: list) -> tuple[str, str]:
    """
    Parse user's choice from free text.
    Returns (choice_key, choice_label).

    Tries in order:
    1. Direct letter "A"/"B"/"C"/"D" (case-insensitive)
    2. Match option label text
    3. Default to "A" with raw text
    """
    text_clean = text.strip()
    text_upper = text_clean.upper()

    # Try direct letter
    for opt in options:
        if text_upper == opt["key"].upper() or text_upper == opt["key"]:
            return opt["key"], opt["label"]

    # Try matching label text
    for opt in options:
        if opt["label"] in text_clean or text_clean in opt["label"]:
            return opt["key"], opt["label"]

    # Fallback: use first option
    return options[0]["key"] if options else ("?", text_clean)


def _extract_json(text: str) -> Optional[dict]:
    """Extract JSON object from LLM response (handles ```json``` wrapping)"""
    # Try direct parse
    try:
        return json.loads(text.strip())
    except Exception:
        pass

    # Try extracting from code block
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # Try finding first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    return None


def _format_history(history: list) -> str:
    """Format dialogue history for inclusion in prompts"""
    if not history:
        return "（无）"
    lines = []
    for turn in history:
        lines.append(
            f"步骤{turn.get('step', '?')}：{turn.get('question', '')} → "
            f"用户选择 {turn.get('user_choice_key', '?')}. {turn.get('user_choice_label', '')}"
        )
    return "\n".join(lines)


def generate_question(
    step_index: int,
    user_topic: str,
    history: list,
) -> dict:
    """
    Generate the next Socratic question.
    Returns: {"question": str, "options": [{"key","label","hint"}], "focus": str}
    """
    step_info = GROUP1_STEPS[step_index - 1] if 1 <= step_index <= len(GROUP1_STEPS) else None
    if not step_info:
        return {"question": "已无更多步骤", "options": [], "focus": ""}

    prompt = SOCRATIC_GENERATE_QUESTION.format(
        topic=user_topic,
        step_index=step_index,
        step_description=step_info["description"],
        history=_format_history(history),
    )

    messages = [
        {"role": "system", "content": SOCRATIC_INTRO.format(topic=user_topic)},
        {"role": "user", "content": prompt},
    ]

    response = coaching_chat_messages(messages, scene="coaching_socratic")
    parsed = _extract_json(response)

    if not parsed or "question" not in parsed:
        # Fallback: use simple question
        return {
            "question": f"步骤{step_index}【{step_info['description']}】：请简单回答你的看法？",
            "options": [
                {"key": "A", "label": "看法A", "hint": ""},
                {"key": "B", "label": "看法B", "hint": ""},
            ],
            "focus": step_info["description"],
        }

    return parsed


def handle_user_choice(
    choice_key: str,
    choice_label: str,
    question: str,
    options: list,
    user_raw_input: str,
) -> dict:
    """
    Handle user's choice for current step.
    Returns: {"acknowledgement": str, "feedback": str, "advance_to_next": bool}
    """
    # Build options text
    opt_text = {o["key"]: o["label"] for o in options}

    prompt = SOCRATIC_HANDLE_CHOICE.format(
        choice_key=choice_key,
        choice_label=choice_label,
        question=question,
        option_a=opt_text.get("A", ""),
        option_b=opt_text.get("B", ""),
        option_c=opt_text.get("C", ""),
        user_input=user_raw_input,
    )

    response = coaching_chat_messages(
        [{"role": "user", "content": prompt}],
        scene="coaching_socratic",
    )

    parsed = _extract_json(response)
    if not parsed:
        return {
            "acknowledgement": f"好的，你选择了 {choice_key}。",
            "feedback": "",
            "advance_to_next": True,
        }

    return {
        "acknowledgement": parsed.get("acknowledgement", ""),
        "feedback": parsed.get("feedback", ""),
        "advance_to_next": parsed.get("advance_to_next", True),
    }


def generate_final_summary(topic: str, history: list) -> str:
    """Generate the final 3-sentence summary when session completes"""
    prompt = SOCRATIC_FINAL_SUMMARY.format(
        topic=topic,
        history=_format_history(history),
    )
    return coaching_chat_messages(
        [{"role": "user", "content": prompt}],
        scene="coaching_socratic",
    )
