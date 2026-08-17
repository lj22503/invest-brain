"""InvestBrain Sidecar - HTTP 服务

提供桌面端与本地数据/配置之间的真实连通：
- GET  /health              健康检查
- GET  /api/meta            返回数据目录、版本等元信息
- GET  /api/llm/config      读取 LLM 配置（data/config/llm.json）
- POST /api/llm/config      保存 LLM 配置（与主项目 llm_router 共享同一文件）
- GET  /api/archive         汇总本地入档数据（memory.db 各表 + 计数）
- GET  /api/context         对话上下文摘要（原则/画像/最近记录）
- POST /api/chat            带「脑」的真实对话：注入用户原则/行为画像/最近记忆，
                            对话后自动入档会话，并做想法/决策/行为模式轻量识别

数据目录解析顺序：
1. 环境变量 INVESTBRAIN_DATA_DIR（Tauri 启动 sidecar 时注入）
2. 当前工作目录下的 data/
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

VERSION = "0.3.0"


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


def _db_conn():
    """打开 memory.db（不存在返回 None，不抛错）。"""
    db = data_root() / "memory" / "memory.db"
    if not db.exists():
        return None
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    return conn


def context_get() -> dict:
    """对话上下文摘要：原则 / 行为画像 / 最近想法与决策，供前端与 system prompt 使用。"""
    conn = _db_conn()
    if conn is None:
        return {"principles": [], "patterns": [], "thoughts": [], "decisions": [], "loaded": False}
    cur = conn.cursor()

    def query(sql: str, args=()):
        try:
            return [dict(r) for r in cur.execute(sql, args).fetchall()]
        except sqlite3.Error:
            return []

    principles = query(
        "SELECT id, content FROM user_principles WHERE active=1 ORDER BY created_at DESC LIMIT 10"
    )
    patterns = query(
        "SELECT pattern_type, COUNT(*) AS cnt FROM behavior_patterns "
        "GROUP BY pattern_type ORDER BY cnt DESC LIMIT 10"
    )
    thoughts = query(
        "SELECT text, ticker, created_at FROM thoughts ORDER BY id DESC LIMIT 5"
    )
    decisions = query(
        "SELECT ticker, action, price, reason, created_at FROM decisions ORDER BY id DESC LIMIT 5"
    )
    conn.close()
    return {
        "principles": principles,
        "patterns": patterns,
        "thoughts": thoughts,
        "decisions": decisions,
        "loaded": True,
    }


def build_system_prompt(ctx: dict) -> str:
    """把用户的原则、行为画像、最近记录组装成 system prompt，让对话带着「脑」。"""
    lines = [
        "你是 InvestBrain，一位专业的个人投资决策教练。你了解这位用户的投资原则、行为习惯与历史记录，回答要贴合他的实际情况，像熟悉他的老搭档一样说话。",
        "回答要求：直接、具体、可执行；发现用户有追高、情绪化、频繁交易等风险倾向时，温和提醒并给出替代方案；不编造用户没有说过的交易事实。",
    ]
    if ctx.get("principles"):
        lines.append("\n【用户的投资原则】")
        for p in ctx["principles"]:
            lines.append(f"- {p.get('content')}")
    if ctx.get("patterns"):
        lines.append("\n【用户的行为画像（历史体检统计）】")
        for p in ctx["patterns"]:
            lines.append(f"- {p.get('pattern_type')}：出现 {p.get('cnt')} 次")
    if ctx.get("thoughts"):
        lines.append("\n【用户最近的想法】")
        for t in ctx["thoughts"]:
            extra = f"（{t.get('ticker')}）" if t.get("ticker") else ""
            lines.append(f"- {t.get('text')}{extra}")
    if ctx.get("decisions"):
        lines.append("\n【用户最近的决策】")
        for d in ctx["decisions"]:
            price = f"@{d.get('price')}" if d.get("price") else ""
            lines.append(f"- {d.get('action')} {d.get('ticker')} {price}：{d.get('reason') or '—'}")
    return "\n".join(lines)


_PATTERN_RULES = [
    ("追高", ("追高", "涨停了想买", "涨这么多", "创新高", "还在涨", "怕买不到", "踏空")),
    ("情绪化", ("割肉", "恐慌", "梭哈", "全仓", "亏麻了", "冲动", "难受死了", "崩溃")),
    ("频繁交易", ("频繁", "天天买卖", "高抛低吸", "来回折腾", "反复操作")),
    ("过度自信", ("肯定涨", "必涨", "稳赚", "不会亏", "闭眼买")),
]

_THOUGHT_RE = re.compile(
    r"(?:我|打算|考虑|想|觉得|看好|准备|计划)[^。！？\n]{0,20}?(?:买入|买|建仓|加仓|布局|补仓|关注|持有)"
)
_THOUGHT_HIT = ("值得关注", "长期看好", "想长期持有", "纳入观察")
_DECISION_RE = re.compile(
    r"(买入|卖出|建仓|清仓|加仓|减仓|补仓|止损|止盈)[^。！？\n]{0,6}?([A-Za-z]{2,6}|[\u4e00-\u9fa5]{2,4})"
)


def ingest_from_message(user_msg: str) -> dict:
    """对单条用户消息做轻量业务识别：行为模式 / 想法 / 决策。保守规则，避免误报。"""
    result = {"patterns": [], "thoughts": 0, "decisions": 0}
    if not user_msg:
        return result
    conn = _db_conn()
    if conn is None:
        return result
    cur = conn.cursor()
    now = datetime.now().isoformat(timespec="seconds")

    for ptype, kws in _PATTERN_RULES:
        hit = next((k for k in kws if k in user_msg), None)
        if not hit:
            continue
        try:
            row = cur.execute(
                "SELECT id, times_count FROM behavior_patterns "
                "WHERE pattern_type=? AND trigger_content=? ORDER BY id DESC LIMIT 1",
                (ptype, hit),
            ).fetchone()
            if row:
                cur.execute(
                    "UPDATE behavior_patterns SET times_count=times_count+1, happened_at=?, context=? WHERE id=?",
                    (now, user_msg[:300], row["id"]),
                )
            else:
                n = cur.execute(
                    "SELECT COUNT(*) AS n FROM behavior_patterns WHERE pattern_type=?",
                    (ptype,),
                ).fetchone()["n"]
                pid = f"{ptype}_{(n or 0) + 1}"
                cur.execute(
                    "INSERT INTO behavior_patterns (id, pattern_type, trigger_content, context, happened_at, severity, times_count, created_at) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (pid, ptype, hit, user_msg[:300], now, 2, 1, now),
                )
            conn.commit()
            result["patterns"].append(ptype)
        except sqlite3.Error:
            pass

    is_thought = bool(_THOUGHT_RE.search(user_msg)) or any(k in user_msg for k in _THOUGHT_HIT)
    if is_thought:
        try:
            dup = cur.execute(
                "SELECT id FROM thoughts WHERE text=? AND created_at > datetime('now','-10 minutes')",
                (user_msg[:200],),
            ).fetchone()
            if not dup:
                cur.execute(
                    "INSERT INTO thoughts (text, created_at) VALUES (?,?)",
                    (user_msg[:200], now),
                )
                conn.commit()
                result["thoughts"] = 1
        except sqlite3.Error:
            pass

    m = _DECISION_RE.search(user_msg)
    if m:
        action, ticker = m.group(1), m.group(2)
        try:
            dup = cur.execute(
                "SELECT id FROM decisions WHERE ticker=? AND action=? AND created_at > datetime('now','-10 minutes')",
                (ticker, action),
            ).fetchone()
            if not dup:
                cur.execute(
                    "INSERT INTO decisions (ticker, action, reason, created_at) VALUES (?,?,?,?)",
                    (ticker, action, user_msg[:300], now),
                )
                conn.commit()
                result["decisions"] = 1
        except sqlite3.Error:
            pass

    conn.close()
    return result


def record_dialogue(user_msg: str, mode: str, status: str = "completed") -> None:
    """记录一次对话会话入档。"""
    conn = _db_conn()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        now = datetime.now().isoformat(timespec="seconds")
        sid = f"d-{now[:10]}-{uuid.uuid4().hex[:8]}"
        cur.execute(
            "INSERT INTO dialogue_sessions (id, user_input, mode, status, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?)",
            (sid, user_msg[:500], mode, status, now, now),
        )
        conn.commit()
    except sqlite3.Error:
        pass
    finally:
        conn.close()


def chat_completion(payload: dict) -> dict:
    """经本地 llm.json 配置代理真实 LLM 对话（Key 不经过前端）。

    升级为「带脑对话」：注入用户原则/行为画像/最近记忆，回复后自动入档会话，
    并做想法/决策/行为模式的轻量识别。
    """
    cfg = _read_json(data_root() / "config" / "llm.json", {})
    api_key = cfg.get("api_key")
    if not api_key:
        # 演示模式也做入档：让「聊着聊着就记下来」在无 Key 时同样成立
        ctx = context_get()
        ingested = ingest_from_message(payload.get("user_msg") or "")
        record_dialogue(payload.get("user_msg") or "", "demo")
        return {
            "status": "no_key",
            "message": "LLM Key 未配置",
            "demo": True,
            "context": {
                "principles": len(ctx["principles"]),
                "patterns": len(ctx["patterns"]),
                "thoughts": len(ctx["thoughts"]),
                "decisions": len(ctx["decisions"]),
                "loaded": ctx["loaded"],
            },
            "ingested": ingested,
        }
    provider = cfg.get("provider") or "deepseek"
    base_url = cfg.get("base_url") or "https://api.deepseek.com/v1"
    history = payload.get("history") or []
    user_msg = payload.get("user_msg") or ""

    ctx = context_get()
    system_prompt = build_system_prompt(ctx)
    messages = [{"role": "system", "content": system_prompt}]
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

    ingested = ingest_from_message(user_msg)
    record_dialogue(user_msg, provider)

    return {
        "status": "ok",
        "content": content,
        "provider": provider,
        "context": {
            "principles": len(ctx["principles"]),
            "patterns": len(ctx["patterns"]),
            "thoughts": len(ctx["thoughts"]),
            "decisions": len(ctx["decisions"]),
            "loaded": ctx["loaded"],
        },
        "ingested": ingested,
    }


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
        elif path == "/api/context":
            self._json(context_get())
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
