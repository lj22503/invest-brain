"""辅导 LLM 调用，含 A+B+D 校验逻辑"""

from typing import Optional
from ..llm import get_deepseek_client, is_llm_available
from .prompts import GROUP1_STEPS


def _build_sourceCitation(llm_output: str, sources: list) -> str:
    """为 LLM 输出附加来源标注（A 原则）"""
    if not sources:
        return llm_output
    source_text = "，来源：" + "、".join([s.get("name", "") for s in sources[:3]])
    return llm_output + source_text


def _add_disclaimer(text: str) -> str:
    """添加免责声明（B 原则）"""
    return text + "\n\n⚠️ 以上分析仅供参考，不构成投资建议。决策前请自行判断。"


def coaching_llm_call(
    prompt: str,
    scene: str = "coaching_simple",
    need_sources: bool = True,
    sources: list = None,
) -> str:
    """
    辅导场景的 LLM 调用

    A 校验：带来源输出
    B 原则：附加免责声明
    D 降级：LLM 不可用时返回降级响应
    """
    if not is_llm_available():
        return "（当前 AI 不可用，请在配置 DEEPSEEK_API_KEY 后使用辅导功能）"

    client = get_deepseek_client()
    try:
        result = client.chat_simple(prompt, scene=scene)
        if need_sources and sources:
            result = _build_sourceCitation(result, sources)
        result = _add_disclaimer(result)
        return result
    except Exception as e:
        return f"（分析生成失败：{e}，请稍后重试）"


def run_simple_10steps(event: str, sources: list = None) -> str:
    """
    简单模式：直接生成 10 步投研分析
    """
    outputs = []
    for step_info in GROUP1_STEPS:
        step_num = step_info["step"]
        prompt_template = step_info["prompt"]
        description = step_info["description"]

        # 替换占位符（第一步填 event，其他步留空）
        if step_num == 1:
            prompt = prompt_template.replace("{event}", event)
        else:
            # 后续步骤传入上一步结果作为上下文
            context = "\n\n上一步结论：\n" + "\n\n".join(outputs[-3:]) if outputs else ""
            prompt = prompt_template + context

        result = coaching_llm_call(prompt, scene="coaching_synthesis", need_sources=False)
        outputs.append(f"**步骤{step_num}【{description}】**\n{result}")

    return "\n\n".join(outputs)


def run_archive(
    trigger_event: str,
    variable_structure: str,
    causal_chain: str,
    actual_outcome: str = None,
    lesson: str = None,
) -> str:
    """调用归档 Prompt，写入情景库"""
    from .prompts import GROUP2_ARCHIVE
    from .scenario import archive_scenario

    prompt = GROUP2_ARCHIVE.format(
        trigger_event=trigger_event,
        variable_structure=variable_structure,
        causal_chain=causal_chain,
        actual_outcome=actual_outcome or "",
        lessons=lesson or "",
    )

    result = coaching_llm_call(prompt, scene="coaching_archive", need_sources=False)
    scenario_id = archive_scenario(
        trigger_event=trigger_event,
        variable_structure=variable_structure,
        causal_chain=causal_chain,
        predicted_outcome=result,
        actual_outcome=actual_outcome,
        lesson=lesson,
    )
    return f"✅ 已存入情景库 [{scenario_id}]\n\n{result}"


def coaching_chat_messages(
    messages: list,
    scene: str = "coaching_socratic",
    need_sources: bool = False,
    sources: list = None,
) -> str:
    """
    Multi-turn dialogue LLM call.

    Args:
        messages: list of {"role": "system/user/assistant", "content": "..."}
        scene: LLM scene config to use
        need_sources: whether to append source citations
        sources: list of source dicts for citation
    """
    from ..llm import get_deepseek_client, is_llm_available

    if not is_llm_available():
        return "（当前 AI 不可用，请在配置 DEEPSEEK_API_KEY 后使用辅导功能）"

    client = get_deepseek_client()
    try:
        result = client.chat(messages, scene=scene)
        if need_sources and sources:
            result = _build_sourceCitation(result, sources)
        result = _add_disclaimer(result)
        return result
    except Exception as e:
        return f"（分析生成失败：{e}，请稍后重试）"