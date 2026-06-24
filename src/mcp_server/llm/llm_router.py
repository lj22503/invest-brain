"""通用LLM路由 - 支持OpenAI-compatible API"""
import os
import json
from typing import Optional
from pathlib import Path

try:
    import openai
except ImportError:
    openai = None

from .providers import ProviderConfig, PROVIDER_PRESETS, DEFAULT_SCENE_MODELS

LLM_CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "data" / "config" / "llm.json"

class LLMTask:
    """LLM任务定义"""
    def __init__(self, scene: str, system: Optional[str] = None, temperature: float = 0.5, thinking: bool = False, json_mode: bool = False):
        self.scene = scene
        self.system = system
        self.temperature = temperature
        self.thinking = thinking
        self.json_mode = json_mode

class LLMRouter:
    """通用LLM路由器"""

    def __init__(self, config_file: Path = LLM_CONFIG_FILE):
        self.config_file = config_file
        self._config: Optional[dict] = None
        self._client = None
        self._load_config()

    def _load_config(self):
        """从文件加载配置"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                self._config = json.load(f)
        else:
            self._config = {"provider": "deepseek", "scenes": {}}

    def _save_config(self):
        """保存配置到文件"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self._config, f, indent=2)

    def configure(self, provider: str, api_key: str, base_url: str = None, custom_model: str = None):
        """配置Provider"""
        self._config["provider"] = provider
        self._config["api_key"] = api_key
        if base_url:
            self._config["base_url"] = base_url
        if custom_model:
            self._config["custom_model"] = custom_model
        self._save_config()
        self._client = None  # 重置客户端

    def set_scene_model(self, scene: str, model: str):
        """设置场景模型"""
        if "scenes" not in self._config:
            self._config["scenes"] = {}
        self._config["scenes"][scene] = model
        self._save_config()

    def _get_client(self):
        """获取/创建OpenAI兼容客户端"""
        if self._client:
            return self._client

        provider = self._config.get("provider", "deepseek")
        api_key = self._config.get("api_key") or os.environ.get(f"{provider.upper()}_API_KEY")
        base_url = self._config.get("base_url") or PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["deepseek"]).base_url

        if not api_key:
            raise ValueError(f"API key not set for {provider}")

        self._client = openai.OpenAI(api_key=api_key, base_url=base_url)
        return self._client

    def chat(self, messages: list[dict], scene: str) -> str:
        """发送对话请求"""
        client = self._get_client()
        provider = self._config.get("provider", "deepseek")

        # 获取模型
        scene_models = DEFAULT_SCENE_MODELS.get(provider, DEFAULT_SCENE_MODELS["deepseek"])
        model = self._config.get("scenes", {}).get(scene) or scene_models.get(scene) or scene_models["rag_synthesis"]

        # 构建参数
        kwargs = {"model": model, "temperature": 0.5}

        if provider == "deepseek" and scene == "pattern_analysis":
            kwargs["extra_body"] = {"thinking": {"type": "enabled", "budget_tokens": 8192}}

        kwargs["messages"] = messages
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def chat_simple(self, prompt: str, scene: str) -> str:
        """简易接口"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, scene)


# 单例
_router: Optional[LLMRouter] = None

def get_router() -> LLMRouter:
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router
