"""InvestBrain Sidecar - 最小 HTTP 服务（占位 MCP Server）。

Plan 1 范围：仅提供 health_check。MCP 工具集成后续 Plan 引入。
"""
from __future__ import annotations

import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

VERSION = "0.1.0"


def health_check() -> dict:
    """返回服务健康状态。

    Returns:
        dict: 含 status / version / python_version
    """
    return {
        "status": "ok",
        "version": VERSION,
        "python_version": sys.version.split()[0],
        "service": "investbrain-sidecar",
    }


class _Handler(BaseHTTPRequestHandler):
    """最小 HTTP 处理器。"""

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            self._json(health_check())
        else:
            self._json({"error": "not_found"}, status=404)

    def _json(self, payload: dict, status: int = 200) -> None:
        import json
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        # 静默 Tauri 子进程日志（避免污染 Tauri 控制台）
        return


def main() -> None:
    """CLI 入口：监听 127.0.0.1 随机端口（Port 由 stdin 读入，避免硬编码）。"""
    import os

    port = int(os.environ.get("SIDECAR_PORT", "0"))
    server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    print(f"SIDECAR_READY:{server.server_address[1]}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()