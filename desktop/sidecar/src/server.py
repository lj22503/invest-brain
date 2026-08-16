"""InvestBrain Sidecar - HTTP 服务

提供桌面端与本地数据/配置之间的真实连通：
- GET  /health              健康检查
- GET  /api/meta            返回数据目录、版本等元信息
- GET  /api/llm/config      读取 LLM 配置（data/config/llm.json）
- POST /api/llm/config      保存 LLM 配置（与主项目 llm_router 共享同一文件）
- GET  /api/archive         汇总本地入档数据（memory.db 各表 + 计数）

数据目录解析顺序：
1. 环境变量 INVESTBRAIN_DATA_DIR（Tauri 启动 sidecar 时注入）
2. 当前工作目录下的 data/
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

VERSION = "0.2.0"


def data_root() -> Path:
    """数据根目录：优先环境变量，否则 cwd/data。"""
    env = os.environ.get("INVESTBRAIN_DATA_DIR")
    if env:
        return Path(env)
    return Path.cwd() / "data"


def _read_json(path: Path, default):
    try:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return default


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def health_check() -> dict:
    return {
        "status": "ok",
        "version": VERSION,
        "python_version": sys.version.split()[0],
        "service": "investbrain-sidecar",
        "data_dir": str(data_root()),
    }


def llm_config_get() -> dict:
    cfg = _read_json(
        data_root() / "config" / "llm.json",
        {"provider": "deepseek", "scenes": {}},
    )
    cfg["configured"] = bool(cfg.get("api_key"))
    return cfg


def llm_config_save(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {"status": "error", "message": "invalid payload"}
    path = data_root() / "config" / "llm.json"
    cfg = _read_json(path, {"provider": "deepseek", "scenes": {}})
    if "provider" in payload:
        cfg["provider"] = payload["provider"]
    if "api_key" in payload:
        cfg["api_key"] = payload["api_key"]
    if "base_url" in payload and payload["base_url"]:
        cfg["base_url"] = payload["base_url"]
    _write_json(path, cfg)
    return {"status": "ok", "configured": bool(cfg.get("api_key")), "path": str(path)}


def archive_get() -> dict:
    """汇总本地入档数据，供桌面端「我的档案」页展示。"""
    root = data_root()
    db = root / "memory" / "memory.db"
    result = {
        "data_dir": str(root),
        "database": str(db),
        "exists": db.exists(),
        "counts": {},
        "sections": {},
    }
    if not db.exists():
        return result

    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    def query(sql: str, args=()):
        try:
            return [dict(r) for r in cur.execute(sql, args).fetchall()]
        except sqlite3.Error:
            return []

    tables = (
        "thoughts", "decisions", "reminders", "scenarios",
        "behavior_patterns", "user_principles", "dialogue_sessions",
    )
    for t in tables:
        try:
            result["counts"][t] = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        except sqlite3.Error:
            result["counts"][t] = 0

    result["sections"]["thoughts"] = query(
        "SELECT id, text, ticker, price, indicator, created_at "
        "FROM thoughts ORDER BY id DESC LIMIT 50"
    )
    result["sections"]["decisions"] = query(
        "SELECT id, ticker, action, price, reason, created_at "
        "FROM decisions ORDER BY id DESC LIMIT 50"
    )
    result["sections"]["behavior_patterns"] = query(
        "SELECT id, pattern_type, trigger_content, context, happened_at, "
        "severity, times_count FROM behavior_patterns "
        "ORDER BY COALESCE(happened_at, created_at) DESC LIMIT 50"
    )
    result["sections"]["dialogue_sessions"] = query(
        "SELECT id, user_input, mode, status, created_at "
        "FROM dialogue_sessions ORDER BY created_at DESC LIMIT 20"
    )
    result["sections"]["user_principles"] = query(
        "SELECT id, content, active, created_at FROM user_principles "
        "WHERE active = 1 ORDER BY created_at DESC LIMIT 20"
    )
    conn.close()
    return result


def chat_completion(payload: dict) -> dict:
    """经本地 llm.json 配置代理真实 LLM 对话（Key 不经过前端）。"""
    cfg = _read_json(data_root() / "config" / "llm.json", {})
    api_key = cfg.get("api_key")
    if not api_key:
        return {"status": "no_key", "message": "LLM Key 未配置", "demo": True}
    provider = cfg.get("provider") or "deepseek"
    base_url = cfg.get("base_url") or "https://api.deepseek.com/v1"
    history = payload.get("history") or []
    user_msg = payload.get("user_msg") or ""

    messages = []
    for m in history[-10:]:
        role = m.get("role")
        content = m.get("content")
        if role in ("user", "assistant") and isinstance(content, str):
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_msg})

    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": messages,
        "stream": False,
        "temperature": 0.7,
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"status": "error", "message": f"LLM HTTP {e.code}", "detail": e.read().decode("utf-8", "ignore")[:500]}
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"LLM 请求失败: {e}"}

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return {"status": "error", "message": "LLM 响应格式异常", "detail": json.dumps(data, ensure_ascii=False)[:500]}
    return {"status": "ok", "content": content, "provider": provider}


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            self._json(health_check())
        elif path == "/api/meta":
            self._json({
                "version": VERSION,
                "service": "investbrain-sidecar",
                "data_dir": str(data_root()),
            })
        elif path == "/api/llm/config":
            self._json(llm_config_get())
        elif path == "/api/archive":
            self._json(archive_get())
        else:
            self._json({"error": "not_found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"
            payload = json.loads(raw.decode("utf-8")) if raw.strip() else {}
        except (ValueError, json.JSONDecodeError):
            self._json({"status": "error", "message": "invalid JSON body"}, status=400)
            return

        if path == "/api/llm/config":
            self._json(llm_config_save(payload))
        elif path == "/api/chat":
            self._json(chat_completion(payload))
        else:
            self._json({"error": "not_found"}, status=404)

    def _json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _cors(self) -> None:
        # Tauri WebView 以 tauri://localhost / http://tauri.localhost 为 origin，
        # 需显式放行跨域；sidecar 仅监听 127.0.0.1，通配 Accept 安全。
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        return


def main() -> None:
    port = int(os.environ.get("SIDECAR_PORT", "0"))
    server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    print(f"SIDECAR_READY:{server.server_address[1]}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
