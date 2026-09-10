// 轻量埋点：匿名事件上报，不采集用户输入原文与任何个人身份信息。
// Web 端 / Tauri 桌面端共用 SDK；Tauri 端 fallback console.warn（等用户量起来再接桌面远端通道）。
// 公共属性（OPA 事实标准）：
//   cta            按钮/卡片标识
//   ref            归因上下文（'home' | 'nav' | 'card' | ...）
//   page_referrer  来源页面路径（同源）
//   utm_*          UTM 参数透传

const ENV_ENDPOINT = process.env.NEXT_PUBLIC_ANALYTICS_ENDPOINT; // 留空则 console 模式

export type TrackPayload = Record<string, string | number | boolean | undefined>;

const UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'] as const;

function readCommon(): Record<string, string> {
  if (typeof window === 'undefined') return {};
  const out: Record<string, string> = {};
  try {
    const ref = document.referrer;
    if (ref) {
      try {
        const u = new URL(ref);
        if (u.origin === window.location.origin) {
          out.page_referrer = u.pathname;
        }
      } catch {
        /* invalid */
      }
    }
    const params = new URL(window.location.href).searchParams;
    for (const k of UTM_KEYS) {
      const v = params.get(k);
      if (v) out[k] = v;
    }
  } catch {
    /* ignore */
  }
  return out;
}

function detectTauri(): boolean {
  if (typeof window === 'undefined') return false;
  // Tauri v1/v2 都会注入 __TAURI__ / __TAURI_INTERNALS__ 标记
  return Boolean((window as unknown as { __TAURI__?: unknown }).__TAURI__) ||
    Boolean((window as unknown as { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__);
}

export async function track(event: string, payload: TrackPayload = {}): Promise<void> {
  try {
    const common = readCommon();
    const body = JSON.stringify({
      event,
      path: typeof window !== 'undefined' ? window.location.pathname : '',
      ts: Date.now(),
      payload: { ...common, ...payload },
      runtime: detectTauri() ? 'tauri' : 'web',
    });

    if (ENV_ENDPOINT) {
      if (navigator.sendBeacon) {
        const ok = navigator.sendBeacon(ENV_ENDPOINT, new Blob([body], { type: 'application/json' }));
        if (ok) return;
      }
      await fetch(ENV_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
        keepalive: true,
      });
      return;
    }
    // 后端未配置：dev 模式 console 提示，避免静默
    // eslint-disable-next-line no-console
    console.info('[track]', event, body);
  } catch {
    // 埋点失败不影响主功能
  }
}

export const EVT = {
  pageView: 'page_view',
  navClick: 'nav_click', // payload: cta, ref='nav'
  homeCta: 'home_cta', // payload: cta, ref='home'
  chatSend: 'chat_send', // payload: qid（请求时匿名 hash）, mode='llm'|'rule'
  chatScore: 'chat_score', // payload: qid, score=1|2|3|4|5
  chatArchive: 'chat_archive', // payload: qid
  settingsChange: 'settings_change', // payload: key
  packOpen: 'pack_open', // payload: pack
} as const;
