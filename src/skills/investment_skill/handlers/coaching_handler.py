"""
Coaching Handler

学习辅导主入口。
- 检测复杂度（简单/复杂）
- 简单：直接 10 步输出
- 复杂：触发 Socratic 多轮对话（Phase 2）
- 两者结束均自动归档到情景库
"""

from typing import Dict, Any
from pathlib import Path
import sys

_project_root = Path(__file__).resolve().parents[4]
_src_path = _project_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from mcp_server.coaching.trigger import detect_complexity
from mcp_server.coaching.llm import run_simple_10steps, coaching_llm_call
from mcp_server.coaching.prompts import GROUP2_ARCHIVE
from mcp_server.coaching.scenario import archive_scenario


class CoachingHandler:
    """学习辅导 handler"""

    def __init__(self):
        self.name = "coaching"
        self.triggers = [
            "怎么看.*趋势", "为什么.*涨", "为什么.*跌",
            "为什么.*不一样", "对.*什么影响",
            ".*觉得.*", ".*为什么",
        ]

    def handle(self, user_input: str, mode: str = None) -> Dict[str, Any]:
        """
        主处理函数

        Args:
            user_input: 用户输入
            mode: 强制模式 ("simple" | "complex" | None=自动判断)

        Returns:
            处理结果
        """
        # Step 1: 判断复杂度
        complexity = mode or detect_complexity(user_input)

        if complexity == "simple":
            return self._handle_simple(user_input)
        else:
            # Phase 1：复杂主题暂用简单 10 步替代（Phase 2 实现真正 Socratic 多轮对话）
            # 当前输出前加提示，让用户知道这是简化版
            result = self._handle_simple(user_input)
            result["answer"] = (
                "💡 当前复杂主题分析（简化版，Phase 2 将支持完整多轮引导）\n\n"
                + result["answer"]
            )
            result["mode"] = "complex_simplified"
            return result

    def _handle_simple(self, user_input: str) -> Dict[str, Any]:
        """简单模式：直接 10 步输出"""
        # 提取事件名作为分析主题
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
