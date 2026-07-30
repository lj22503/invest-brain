"""Tests for sidecar.server.health_check.

Plan 1 范围：纯函数测试，HTTP 层留待 Playwright e2e。
"""
import sys
from pathlib import Path

# 把 src/ 加入 sys.path，避免依赖 requirements.txt 安装
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from server import VERSION, health_check  # noqa: E402


def test_health_check_returns_ok() -> None:
    result = health_check()
    assert result["status"] == "ok"


def test_health_check_includes_version() -> None:
    result = health_check()
    assert result["version"] == VERSION
    assert isinstance(result["version"], str)


def test_health_check_includes_python_version() -> None:
    result = health_check()
    py_version = result["python_version"]
    # 形如 "3.11.x"
    parts = py_version.split(".")
    assert len(parts) == 3
    assert parts[0].isdigit()


def test_health_check_has_service_field() -> None:
    result = health_check()
    assert result["service"] == "investbrain-sidecar"