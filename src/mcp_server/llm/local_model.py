"""本地轻量模型兜底 — ONNX Runtime GenAI 推理

当 DeepSeek API 不可用时，降级到本地 ONNX 格式小模型。

降级链：DeepSeek API → 本地 ONNX 模型 → 简单拼接

支持模型：
- Qwen2-0.5B-Instruct（推荐，~400MB ONNX 量化版）
- 任何 onnxruntime-genai 兼容模型

模型下载：
  推荐从 HuggingFace 下载 ONNX 量化版：
  huggingface-cli download Qwen/Qwen2-0.5B-Instruct-onnx --local-dir models/qwen2-0.5b-onnx
  
  或使用 ModelScope 国内镜像：
  modelscope download --model Qwen/Qwen2-0.5B-Instruct-GGUF qwen2-0.5b-instruct-q4_k_m.gguf --local_dir models/

环境变量：
  LOCAL_MODEL_DIR: ONNX 模型目录路径
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# 模型目录：项目根/models/qwen2-0.5b-onnx/
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_DIR = _PROJECT_ROOT / "models" / "qwen2-0.5b-onnx"


class LocalModelFallback:
    """本地 ONNX 模型兜底推理器

    惰性加载：首次调用 chat_simple() 时自动加载模型。
    加载失败不抛异常，返回 None 让上游走下一级降级。

    Usage:
        model = LocalModelFallback()
        result = model.chat_simple(prompt, scene="fallback")
        if result is None:
            # 走简单拼接降级
            ...
    """

    def __init__(self, model_dir: str = None):
        self._model_dir = Path(model_dir) if model_dir else Path(
            os.environ.get("LOCAL_MODEL_DIR", str(DEFAULT_MODEL_DIR))
        )
        self._model = None
        self._tokenizer = None
        self._loaded = False
        self._load_attempted = False

    def _ensure_loaded(self) -> bool:
        """惰性加载模型，仅尝试一次"""
        if self._loaded:
            return True
        if self._load_attempted:
            return False

        self._load_attempted = True

        if not self._model_dir.exists():
            logger.info(
                "ONNX model not found at %s. "
                "Download via: huggingface-cli download Qwen/Qwen2-0.5B-Instruct-onnx "
                "--local-dir models/qwen2-0.5b-onnx",
                self._model_dir,
            )
            return False

        try:
            import onnxruntime_genai as og

            self._model = og.Model(str(self._model_dir))
            self._tokenizer = og.Tokenizer(self._model)
            self._loaded = True
            logger.info("Local ONNX model loaded from %s", self._model_dir)
            return True
        except ImportError:
            logger.info("onnxruntime_genai not installed. Run: pip install onnxruntime-genai")
        except Exception as e:
            logger.warning("Failed to load ONNX model from %s: %s", self._model_dir, e)

        return False

    def chat_simple(self, prompt: str, scene: str = "fallback") -> Optional[str]:
        """与 DeepSeekClient.chat_simple 接口对齐

        Returns:
            模型生成的回复字符串，加载失败或推理失败返回 None
        """
        if not self._ensure_loaded():
            return None

        try:
            return self._generate_with_onnx_genai(prompt)
        except Exception as e:
            logger.warning("ONNX generation failed: %s", e)
            return None

    def _generate_with_onnx_genai(self, prompt: str) -> str:
        """使用 ONNX Runtime GenAI 生成回复"""
        import onnxruntime_genai as og

        # 构建生成参数
        params = og.GeneratorParams(self._model)
        params.set_search_options(
            max_length=512,  # 限制最大 token 数（回答为核心，不需要太长）
            do_sample=True,
            top_p=0.9,
            temperature=0.3,  # 低温度保证回答稳定
        )

        # 编码输入
        input_ids = self._tokenizer.encode(prompt)
        params.input_ids = input_ids

        # 生成
        generator = og.Generator(self._model, params)
        output_tokens = []

        while not generator.is_done():
            generator.compute_logits()
            generator.generate_next_token()
            new_token = generator.get_output(0)
            output_tokens.append(new_token)

        # 解码输出
        result = self._tokenizer.decode(output_tokens)
        return result

    @property
    def is_available(self) -> bool:
        """检查模型是否可用（不触发加载）"""
        if self._loaded:
            return True
        if self._load_attempted:
            return False
        # 仅检查文件存在，不加载
        return self._model_dir.exists()


# ========== 单例（惰性） ==========

_local_fallback: Optional[LocalModelFallback] = None


def get_local_model() -> LocalModelFallback:
    """获取全局本地模型实例（延迟初始化）"""
    global _local_fallback
    if _local_fallback is None:
        _local_fallback = LocalModelFallback()
    return _local_fallback


def is_local_model_available() -> bool:
    """检查本地模型是否可用（不触发加载）"""
    return get_local_model().is_available
