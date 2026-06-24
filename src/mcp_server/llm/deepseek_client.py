"""DeepSeek LLM 客户端

统一入口，按场景自动路由模型和温度。
用户只需提供 DEEPSEEK_API_KEY。
"""

import os
import json
from typing import Optional, Literal
from pathlib import Path
from dataclasses import dataclass

try:
    import openai
except ImportError:
    openai = None


# ========== 场景定义 ==========

@dataclass
class LLMConfig:
    """LLM 调用配置"""
    model: str
    temperature: float
    thinking_effort: Optional[str] = None  # "low" / "medium" / "high" for reasoning models
    json_mode: bool = False  # 强制 JSON 输出

    def to_kwargs(self) -> dict:
        kwargs = {
            "model": self.model,
            "temperature": self.temperature,
        }
        if self.thinking_effort:
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": self._effort_to_tokens()}
        if self.json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        return kwargs

    def _effort_to_tokens(self) -> int:
        """将思考力度转换为 token 预算"""
        mapping = {"low": 512, "medium": 2048, "high": 8192}
        return mapping.get(self.thinking_effort, 2048)


# 场景 → 模型配置
SCENE_CONFIGS: dict[str, LLMConfig] = {
    # 想法解析：实体提取，要求准确不随机，强制 JSON 输出
    "thought_parsing": LLMConfig(
        model="deepseek-v4-flash",
        temperature=0.3,
        thinking_effort=None,
        json_mode=True,
    ),
    # RAG 合成：连贯 + 适度创造性
    "rag_synthesis": LLMConfig(
        model="deepseek-v4-flash",
        temperature=0.5,
        thinking_effort=None,
    ),
    # 行为模式分析：深度推理
    "pattern_analysis": LLMConfig(
        model="deepseek-v4-pro",
        temperature=0.4,
        thinking_effort="high",
    ),
    # 圆桌角色话术：风格鲜明
    "roundtable_role": LLMConfig(
        model="deepseek-v4-flash",
        temperature=0.7,
        thinking_effort=None,
    ),
    # 圆桌综合裁判：推理但不极端
    "roundtable_judge": LLMConfig(
        model="deepseek-v4-pro",
        temperature=0.5,
        thinking_effort="high",
    ),
}


# ========== DeepSeek 客户端 ==========

class DeepSeekClient:
    """DeepSeek LLM 客户端"""

    def __init__(self, api_key: str = None):
        if openai is None:
            raise ImportError("openai package required: pip install openai")

        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")

        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com",
        )

    def chat(
        self,
        messages: list[dict],
        scene: str,
        system: str = None,
        **kwargs,
    ) -> str:
        """
        统一 chat 接口，按 scene 路由模型和温度。

        Args:
            messages: 对话消息历史 [{"role": "user", "content": "..."}]
            scene: 场景名，对应 SCENE_CONFIGS
            system: 系统提示（可选，会拼接在 messages 前面）
            **kwargs: 透传额外参数到 API

        Returns:
            模型生成的文本
        """
        config = SCENE_CONFIGS.get(scene)
        if not config:
            raise ValueError(f"Unknown scene: {scene}")

        # 构建完整消息
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        # 构建 API 参数
        api_kwargs = config.to_kwargs()
        api_kwargs.update(kwargs)
        api_kwargs["messages"] = full_messages

        response = self.client.chat.completions.create(**api_kwargs)
        return response.choices[0].message.content

    def chat_simple(
        self,
        prompt: str,
        scene: str,
        system: str = None,
    ) -> str:
        """
        简易接口，直接传 prompt。

        Args:
            prompt: 用户 prompt
            scene: 场景名
            system: 系统提示（可选）

        Returns:
            模型生成的文本
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, scene, system=system)


# ========== 单例 ==========

_client: Optional[DeepSeekClient] = None


def get_deepseek_client() -> DeepSeekClient:
    """获取全局 DeepSeek 客户端（延迟初始化）"""
    global _client
    if _client is None:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if api_key:
            _client = DeepSeekClient(api_key)
    return _client


def is_llm_available() -> bool:
    """检查 LLM 是否可用（API Key 是否配置）"""
    return bool(os.environ.get("DEEPSEEK_API_KEY"))


# ========== 便捷函数 ==========

def llm_chat(prompt: str, scene: str, system: str = None) -> str:
    """便捷函数：直接用 prompt 调用"""
    client = get_deepseek_client()
    if client is None:
        raise RuntimeError("DEEPSEEK_API_KEY not configured")
    return client.chat_simple(prompt, scene, system=system)
