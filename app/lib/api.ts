// Sidecar HTTP 客户端：桌面端所有本地能力（配置 / 档案 / 对话）经此与后端真实连通。
// CSP 已放行 connect-src http://127.0.0.1:*；Web 开发环境（无 sidecar）自动降级并给出明确错误。

export interface LLMConfig {
  provider: string;
  api_key?: string | null;
  base_url?: string;
  configured?: boolean;
  [key: string]: unknown;
}

export interface ArchiveSection {
  data_dir: string;
  database: string;
  exists: boolean;
  counts: Record<string, number>;
  sections: {
    thoughts?: Array<Record<string, unknown>>;
    decisions?: Array<Record<string, unknown>>;
    behavior_patterns?: Array<Record<string, unknown>>;
    dialogue_sessions?: Array<Record<string, unknown>>;
    user_principles?: Array<Record<string, unknown>>;
    [key: string]: unknown;
  };
}

export interface ChatResult {
  status: 'ok' | 'no_key' | 'error';
  content?: string;
  message?: string;
  demo?: boolean;
  provider?: string;
  detail?: string;
  context?: {
    loaded: boolean;
    principles: number;
    patterns: number;
    thoughts: number;
    decisions: number;
  };
  ingested?: {
    patterns: string[];
    thoughts: number;
    decisions: number;
  };
}

export interface BrainContext {
  loaded: boolean;
  principles: Array<{ id: number; content: string }>;
  patterns: Array<{ pattern_type: string; cnt: number }>;
  thoughts: Array<Record<string, unknown>>;
  decisions: Array<Record<string, unknown>>;
}

const SIDECAR_BASE = 'http://127.0.0.1:8765';

async function sidecarFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${SIDECAR_BASE}${path}`, init);
  if (!resp.ok) {
    throw new Error(`sidecar ${path} -> HTTP ${resp.status}`);
  }
  return resp.json() as Promise<T>;
}

export async function getMeta(): Promise<{ version: string; service: string; data_dir: string }> {
  return sidecarFetch('/api/meta');
}

export async function getLLMConfig(): Promise<LLMConfig> {
  return sidecarFetch('/api/llm/config');
}

export async function saveLLMConfig(config: {
  provider: string;
  api_key?: string;
  base_url?: string;
}): Promise<{ status: string; configured: boolean; path: string }> {
  return sidecarFetch('/api/llm/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
}

export async function getArchive(): Promise<ArchiveSection> {
  return sidecarFetch('/api/archive');
}

export async function getContext(): Promise<BrainContext> {
  return sidecarFetch('/api/context');
}

export async function callLLMRemote(history: { role: string; content: string }[], userMsg: string): Promise<ChatResult> {
  return sidecarFetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ history, user_msg: userMsg }),
  });
}
