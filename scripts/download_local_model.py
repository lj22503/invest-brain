#!/usr/bin/env python
"""下载本地 ONNX 模型（Qwen2-0.5B-Instruct）

用于 C3 任务：本地轻量模型兜底。

用法：
    python scripts/download_local_model.py

模型大小：~400MB（ONNX 量化版）
存放位置：models/qwen2-0.5b-onnx/
"""

import os
import sys
from pathlib import Path

MODEL_NAME = "Qwen/Qwen2-0.5B-Instruct"
TARGET_DIR = Path(__file__).resolve().parents[1] / "models" / "qwen2-0.5b-onnx"

# 注意：onnxruntime-genai 要求 ONNX 模型以特定格式导出。
# 推荐从 HuggingFace 下载预转好的 ONNX 模型：
#   huggingface-cli download Qwen/Qwen2-0.5B-Instruct-onnx --local-dir models/qwen2-0.5b-onnx
#
# 如果没有预转好的 ONNX 版本，可以用 optimum-cli 自行导出：
#   optimum-cli export onnx --model Qwen/Qwen2-0.5B-Instruct models/qwen2-0.5b-onnx/


def download_from_huggingface():
    """通过 huggingface_hub 下载"""
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("请先安装 huggingface_hub: pip install huggingface-hub")
        return False

    print(f"正在下载 {MODEL_NAME} 到 {TARGET_DIR}...")
    print("模型大小约 400MB，请耐心等待...")

    try:
        snapshot_download(
            repo_id=MODEL_NAME,
            local_dir=str(TARGET_DIR),
            local_dir_use_symlinks=False,
            resume_download=True,
        )
        print(f"下载完成！模型已保存到 {TARGET_DIR}")
        return True
    except Exception as e:
        print(f"下载失败: {e}")
        return False


def download_from_modelscope():
    """通过 ModelScope 下载（国内更快）"""
    try:
        from modelscope import snapshot_download
    except ImportError:
        print("请先安装 modelscope: pip install modelscope")
        return False

    print(f"正在从 ModelScope 下载 {MODEL_NAME} 到 {TARGET_DIR}...")
    try:
        snapshot_download(
            model_id=MODEL_NAME,
            local_dir=str(TARGET_DIR),
            revision="master",
        )
        print(f"下载完成！模型已保存到 {TARGET_DIR}")
        return True
    except Exception as e:
        print(f"下载失败: {e}")
        return False


if __name__ == "__main__":
    os.makedirs(TARGET_DIR, exist_ok=True)

    # 优先尝试 ModelScope（国内更快），失败则用 HuggingFace
    success = download_from_modelscope()
    if not success:
        print("\n尝试 HuggingFace 下载...")
        success = download_from_huggingface()

    if success:
        print("\n模型已就绪。重启 MCP Server 后，",
              "DeepSeek API 不可用时会自动降级到本地模型。")
    else:
        print("\n自动下载失败。请手动下载模型：")
        print(f"  1. pip install huggingface-hub")
        print(f"  2. huggingface-cli download {MODEL_NAME} --local-dir {TARGET_DIR}")
        print(f"\n  或设置环境变量 LOCAL_MODEL_DIR 指向已有模型目录。")
