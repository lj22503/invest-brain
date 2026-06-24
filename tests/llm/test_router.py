# tests/llm/test_router.py
import pytest
from pathlib import Path
import tempfile
import os

from src.mcp_server.llm.llm_router import LLMRouter
from src.mcp_server.llm.providers import PROVIDER_PRESETS, DEFAULT_SCENE_MODELS

def test_provider_presets():
    assert "deepseek" in PROVIDER_PRESETS
    assert "openai" in PROVIDER_PRESETS
    assert "anthropic" in PROVIDER_PRESETS
    assert "custom" in PROVIDER_PRESETS

def test_default_scene_models():
    assert "deepseek" in DEFAULT_SCENE_MODELS
    assert "openai" in DEFAULT_SCENE_MODELS
    assert "anthropic" in DEFAULT_SCENE_MODELS

def test_router_init_with_temp_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "llm.json"
        router = LLMRouter(config_file=config_file)
        assert router._config["provider"] == "deepseek"
        assert router._config["scenes"] == {}

def test_router_configure():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "llm.json"
        router = LLMRouter(config_file=config_file)
        router.configure(provider="openai", api_key="sk-test")
        assert router._config["provider"] == "openai"
        assert router._config["api_key"] == "sk-test"
        assert config_file.exists()

def test_set_scene_model():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "llm.json"
        router = LLMRouter(config_file=config_file)
        router.set_scene_model("thought_parsing", "gpt-4o")
        assert router._config["scenes"]["thought_parsing"] == "gpt-4o"
