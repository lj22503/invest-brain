// Tauri IPC 客户端：统一 WebView / Web 两路径。

export function isTauri(): boolean {
  if (typeof window === 'undefined') return false;
  return '__TAURI_INTERNALS__' in window || '__TAURI__' in window;
}

interface TauriCore {
  invoke: <T>(cmd: string, args?: Record<string, unknown>) => Promise<T>;
}

interface TauriGlobal {
  core?: TauriCore;
}

export async function invoke<T = unknown>(cmd: string, args?: Record<string, unknown>): Promise<T> {
  if (isTauri()) {
    // Tauri v2 始终注入 __TAURI_INTERNALS__（{ invoke, transformCallback, ... }），
    // 无需 withGlobalTauri 也无需 @tauri-apps/api 的全局命名空间。
    const internals = (window as any).__TAURI_INTERNALS__;
    if (internals?.invoke) {
      const rawInvoke = internals.invoke as <T>(cmd: string, args?: Record<string, unknown>) => Promise<T>;
      return rawInvoke<T>(cmd, args);
    }
    // 兼容 withGlobalTauri: true 的全局 __TAURI__.core.invoke 形态。
    const tauri = (window as any).__TAURI__ as TauriGlobal | undefined;
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