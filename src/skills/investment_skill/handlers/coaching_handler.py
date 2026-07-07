"""
Coaching Handler

学习辅导主入口。
- 检测复杂度（简单/复杂）
- 简单：直接 10 步输出（Phase 1）
- 复杂：Socratic 多轮对话（Phase 2）
- 两者结束均自动归档到情景库
"""

from typing import Dict, Any
from pathlib import Path
import sys
import json

_project_root = Path(__file__).resolve().parents[4]
_src_path = _project_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from mcp_server.coaching.trigger import detect_complexity
from mcp_server.coaching.llm import run_simple_10steps, coaching_chat_messages
from mcp_server.coaching.prompts import GROUP1_STEPS
from mcp_server.coaching.scenario import archive_scenario
from mcp_server.coaching import session as session_mod
from mcp_server.coaching import socratic


class CoachingHandler:
    """学习辅导 handler"""

    def __init__(self):
        self.name = "coaching"
        self.triggers = [
            "怎么看.*趋势", "为什么.*涨", "为什么.*跌",
            "为什么.*不一样", "对.*什么影响",
            ".*觉得.*", ".*为什么",
        ]

    def handle(
        self,
        user_input: str = None,
        mode: str = None,
        session_id: str = None,
    ) -> Dict[str, Any]:
        """
        主处理函数

        Args:
            user_input: 用户输入（新问题）
            mode: 强制模式 ("simple" | "complex" | None=自动判断)
            session_id: 现有会话 ID（继续多轮对话时使用）

        Returns:
            处理结果
        """
        # 路径 A: 继续现有 Socratic 会话
        if session_id:
            return self._handle_session_continue(session_id, user_input)

        # 路径 B: 新问题
        if not user_input:
            return {"status": "error", "message": "需要 user_input 或 session_id"}

        # 检测复杂度
        complexity = mode or detect_complexity(user_input)

        if complexity == "simple":
            return self._handle_simple(user_input)
        else:
            return self._handle_complex_new(user_input)

    def _handle_simple(self, user_input: str) -> Dict[str, Any]:
        """简单模式：直接 10 步输出"""
        event = user_input.strip()
        result_text = run_simple_10steps(event)

        # 自动归档到情景库
        try:
            scenario_id = archive_scenario(
                trigger_event=event,
                causal_chain="（见下方10步分析）",
            )
        except Exception:
            scenario_id = None

        return {
            "status": "success",
            "mode": "simple",
            "answer": result_text,
            "scenario_id": scenario_id,
            "auto_archived": scenario_id is not None,
        }

    def _handle_complex_new(self, user_input: str) -> Dict[str, Any]:
        """复杂模式：启动新 Socratic 会话"""
        # 启动新会话
        session_id = session_mod.start_session(user_input)

        # 生成第 1 步问题
        question_data = socratic.generate_question(
            step_index=1,
            user_topic=user_input,
            history=[],
        )

        # 保存当前问题
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
            "answer": self._format_question_for_display(
                question_data, current_step=1, total_steps=len(GROUP1_STEPS), user_topic=user_input
            ),
            "next_action": "请回复选项 (A/B/C/D) 或选择切换/退出",
        }

    def _handle_session_continue(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """继续现有 Socratic 会话"""
        session = session_mod.get_session(session_id)
        if not session:
            return {"status": "error", "message": f"会话 {session_id} 不存在"}
        if session["status"] != "active":
            return {"status": "error", "message": f"会话已{session['status']}"}

        # 检测中止意图
        if socratic.detect_abandon_intent(user_input):
            return self._finalize_session(session, status="abandoned")

        # 检测切换简单模式
        if socratic.detect_simple_switch(user_input):
            # 把 mode 改 simple 触发一次性输出
            simple_result = self._handle_simple(session["user_input"])
            session_mod.complete_session(session_id, simple_result.get("scenario_id", ""), final_status="switched_to_simple")
            return {
                **simple_result,
                "session_id": session_id,
                "switched_from_socratic": True,
            }

        # 加载现有 options
        options = json.loads(session["pending_options"]) if session["pending_options"] else []
        if not options:
            return {"status": "error", "message": "会话状态异常：无 pending options"}

        # 解析用户选择
        choice_key, choice_label = socratic.parse_user_choice(user_input, options)
        current_step = session["current_step"]

        # 让 LLM 处理用户选择（确认理解 + 反馈）
        handle_result = socratic.handle_user_choice(
            choice_key=choice_key,
            choice_label=choice_label,
            question=session["pending_question"],
            options=options,
            user_raw_input=user_input,
        )

        # 记录这一轮
        session_mod.record_user_choice(
            session_id,
            choice_key=choice_key,
            choice_label=choice_label,
            user_input=user_input,
            llm_response=handle_result["acknowledgement"] + " " + handle_result["feedback"],
        )

        # 加载完整 history
        session = session_mod.get_session(session_id)
        history = json.loads(session["dialogue_history"]) if session["dialogue_history"] else []

        # 判断是否结束
        if current_step >= len(GROUP1_STEPS):
            # 跑完 10 步，最终总结 + 归档
            return self._finalize_session(session, history=history, status="completed")

        # 生成下一步问题
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
            "answer": self._format_question_for_display(
                question_data, current_step=next_step, total_steps=len(GROUP1_STEPS),
                user_topic=session["user_input"],
                acknowledgement=handle_result["acknowledgement"],
                feedback=handle_result["feedback"],
            ),
            "next_action": "请回复选项 (A/B/C/D) 或选择切换/退出",
        }

    def _finalize_session(self, session, history=None, status="completed") -> Dict[str, Any]:
        """完成会话：生成最终总结 + 归档"""
        session_id = session["id"]
        history = history if history is not None else json.loads(session["dialogue_history"] or "[]")

        # 生成最终总结
        final_summary = socratic.generate_final_summary(
            topic=session["user_input"],
            history=history,
        )

        # 归档到情景库
        scenario_id = archive_scenario(
            trigger_event=session["user_input"],
            variable_structure=f"Socratic {len(history)} 轮对话",
            causal_chain="（多轮对话过程）",
            predicted_outcome=final_summary,
            lesson=f"会话模式: Socratic, 完成度: {status}",
        )

        # 标记会话完成
        session_mod.complete_session(session_id, scenario_id, final_status=status)

        return {
            "status": "success",
            "mode": "complex_finalized",
            "session_id": session_id,
            "scenario_id": scenario_id,
            "session_status": status,
            "final_summary": final_summary,
            "answer": (
                f"🎓 学习辅导完成\n\n"
                f"📝 主题：{session['user_input']}\n"
                f"📊 完成度：{len(history)}/{len(GROUP1_STEPS)} 步\n"
                f"💡 最终总结：\n{final_summary}\n\n"
                f"✅ 已归档到情景库：{scenario_id}"
            ),
        }

    def _format_question_for_display(
        self, question_data, current_step, total_steps, user_topic,
        acknowledgement=None, feedback=None,
    ) -> str:
        """Format question for display to user"""
        lines = [
            f"💡 学习辅导模式 [步骤 {current_step}/{total_steps}]",
            f"📌 主题：{user_topic}",
            "",
        ]
        if acknowledgement:
            lines.append(f"👂 上一轮确认：{acknowledgement}")
            if feedback:
                lines.append(f"💬 反馈：{feedback}")
            lines.append("")
        if question_data.get("focus"):
            lines.append(f"🎯 当前关注：{question_data['focus']}")
            lines.append("")
        lines.append(f"❓ {question_data['question']}")
        lines.append("")
        lines.append("选项：")
        for opt in question_data.get("options", []):
            lines.append(f"  {opt['key']}. {opt['label']}")
        lines.append("")
        lines.append("💡 回复选项 (A/B/C/D)，或输入「别问了」/「直接说」切换")
        return "\n".join(lines)