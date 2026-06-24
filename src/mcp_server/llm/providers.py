"""LLM Provider 配置"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProviderConfig:
    name: str
    api_key: str
    base_url: str
    default_model: str
    supports_thinking: bool = False

PROVIDER_PRESETS = {
    "deepseek": ProviderConfig(
        name="DeepSeek",
        api_key="",
        base_url="https://api.deepseek.com",
        default_model="deepseek-v4-flash",
        supports_thinking=True,
    ),
    "openai": ProviderConfig(
        name="OpenAI",
        api_key="",
        base_url="https://api.openai.com/v1",
        default_model="gpt-4o",
        supports_thinking=False,
    ),
    "anthropic": ProviderConfig(
        name="Claude",
        api_key="",
        base_url="https://api.anthropic.com/v1",
        default_model="claude-sonnet-4-20250514",
        supports_thinking=False,
    ),
    "custom": ProviderConfig(
        name="Custom",
        api_key="",
        base_url="",
        default_model="",
        supports_thinking=False,
    ),
}

SceneModelPreset = dict[str, dict[str, str]]  # provider -> {model, thinking_model}

DEFAULT_SCENE_MODELS: SceneModelPreset = {
    "deepseek": {
        "thought_parsing": "deepseek-v4-flash",
        "rag_synthesis": "deepseek-v4-flash",
        "pattern_analysis": "deepseek-v4-pro",
        "roundtable_role": "deepseek-v4-flash",
        "roundtable_judge": "deepseek-v4-pro",
    },
    "openai": {
        "thought_parsing": "gpt-4o-mini",
        "rag_synthesis": "gpt-4o-mini",
        "pattern_analysis": "gpt-4o",
        "roundtable_role": "gpt-4o-mini",
        "roundtable_judge": "gpt-4o",
    },
    "anthropic": {
        "thought_parsing": "claude-sonnet-4-20250514",
        "rag_synthesis": "claude-sonnet-4-20250514",
        "pattern_analysis": "claude-opus-4-20250514",
        "roundtable_role": "claude-sonnet-4-20250514",
        "roundtable_judge": "claude-opus-4-20250514",
    },
}
