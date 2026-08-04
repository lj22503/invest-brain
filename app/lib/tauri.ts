// Tauri IPC 客户端：统一 WebView / Web 两路径。

export function isTauri(): boolean {
  if (typeof window === 'undefined') return false;
  return '__TAURI_INTERNALS__' in window || '__TAURI__' in window;
}

export async function invoke<T = unknown>(cmd: string, args?: Record<string, unknown>): Promise<T> {
  if (isTauri()) {
    const tauri = (window as any).__TAURI__ ?? (window as any).__TAURI_INTERNALS__;
    if (tauri?.core?.invoke) {
      return tauri.core.invoke<T>(cmd, args);
    }
  }
  // Web fallback：试聊 Demo / 普通浏览器开发用
  throw new Error(
    `Command "${cmd}" unavailable in web context. Run from Tauri or implement web fallback.`
  );
}

export interface HealthResponse {
  status: string;
  version: string;
  python_version?: string;
  sidecar_url?: string;
  [key: string]: unknown;
}

export async function callHealthCheck(): Promise<HealthResponse> {
  return invoke<HealthResponse>('health_check');
}