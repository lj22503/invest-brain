"""DeepSeek LLM 客户端

统一入口，按场景自动路由模型和温度。
内部委托给 llm_router，支持多 Provider 配置。

用户可通过以下方式配置：
1. 环境变量 DEEPSEEK_API_KEY（向后兼容）
2. 前端配置写入 data/config/llm.json
"""

import os
from typing import Optional
from dataclasses import dataclass

from .llm_router import get_router


# ========== 场景定义（保留接口，向后兼容）==========

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
            kwargs["extra_body"] = {"thinking": {"type": "enabled", "budget_tokens": self._effort_to_tokens()}}
        if self.json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        return kwargs

    def _effort_to_tokens(self) -> int:
        mapping = {"low": 512, "medium": 2048, "high": 8192}
        return mapping.get(self.thinking_effort, 2048)


SCENE_CONFIGS: dict[str, LLMConfig] = {
    "thought_parsing": LLMConfig(
        model="deepseek-chat",
        temperature=0.3,
        thinking_effort=None,
        json_mode=True,
    ),
    "rag_synthesis": LLMConfig(
        model="deepseek-chat",
        temperature=0.5,
        thinking_effort=None,
    ),
    "pattern_analysis": LLMConfig(
        model="deepseek-reasoner",
        temperature=0.4,
        thinking_effort="high",
    ),
    "roundtable_role": LLMConfig(
        model="deepseek-chat",
        temperature=0.7,
        thinking_effort=None,
    ),
    "roundtable_judge": LLMConfig(
        model="deepseek-reasoner",
        temperature=0.5,
        thinking_effort="high",
    ),
    "coaching_simple": LLMConfig(
        model="deepseek-chat",
        temperature=0.5,
    ),
    "coaching_synthesis": LLMConfig(
        model="deepseek-chat",
        temperature=0.4,
    ),
    "coaching_archive": LLMConfig(
        model="deepseek-chat",
        temperature=0.3,
    ),
    "coaching_socratic": LLMConfig(
        model="deepseek-chat",
        temperature=0.4,
    ),
}


# ========== DeepSeek 客户端（委托给 llm_router）==========

class DeepSeekClient:
    """DeepSeek LLM 客户端（内部委托给 llm_router）"""

    def __init__(self, api_key: str = None):
        self._api_key = api_key
        self._router = get_router()
        # 如果传了 api_key，配置到 router
        if api_key:
            self._router.configure(provider="deepseek", api_key=api_key)

    def chat(
        self,
        messages: list[dict],
        scene: str,
        system: str = None,
        **kwargs,
    ) -> str:
        """统一 chat 接口，按 scene 路由模型和温度。"""
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)
        return self._router.chat(full_messages, scene)

    def chat_simple(
        self,
        prompt: str,
        scene: str,
        system: str = None,
    ) -> str:
        """简易接口，直接传 prompt。"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, scene, system=system)


# ========== 单例（向后兼容）==========

_client: Optional[DeepSeekClient] = None


def get_deepseek_client() -> DeepSeekClient:
    """获取全局 DeepSeek 客户端（延迟初始化）"""
    global _client
    if _client is None:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        _client = DeepSeekClient(api_key)
    return _client


def is_llm_available() -> bool:
    """检查 LLM 是否可用（API Key 是否配置）"""
    router = get_router()
    config = router._config
    api_key = config.get("api_key") or os.environ.get("DEEPSEEK_API_KEY")
    return bool(api_key)


# ========== 便捷函数 ==========

def llm_chat(prompt: str, scene: str, system: str = None) -> str:
    """便捷函数：直接用 prompt 调用"""
    client = get_deepseek_client()
    if client is None:
        raise RuntimeError("DeepSeek client not initialized")
    return client.chat_simple(prompt, scene, system=system)
