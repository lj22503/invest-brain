// 埋点后端占位（Web 端）。B 方案：当前 dev 模式 console 输出；接 Upstash/PostHog 后续可填
// 接口形态与 iAsk /api/events 兼容，便于将来统一

import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

interface EventBody {
  event?: unknown;
  path?: unknown;
  ts?: unknown;
  payload?: unknown;
  runtime?: unknown;
}

const SAFE_PAYLOAD_KEYS = new Set([
  'cta',
  'ref',
  'qid',
  'score',
  'mode',
  'pack',
  'key',
  'page_referrer',
  'utm_source',
  'utm_medium',
  'utm_campaign',
  'utm_term',
  'utm_content',
]);

export async function POST(req: NextRequest) {
  let body: EventBody;
  try {
    body = (await req.json()) as EventBody;
  } catch {
    return NextResponse.json({ error: 'bad_request' }, { status: 400 });
  }

  if (typeof body.event !== 'string' || !body.event) {
    return NextResponse.json({ error: 'bad_request' }, { status: 400 });
  }

  const payload: Record<string, string> = {};
  if (body.payload && typeof body.payload === 'object') {
    for (const [k, v] of Object.entries(body.payload as Record<string, unknown>)) {
      if (!SAFE_PAYLOAD_KEYS.has(k)) continue;
      if (typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean') {
        payload[k] = String(v);
      }
    }
  }

  const entry = {
    e: String(body.event).slice(0, 64),
    p: typeof body.path === 'string' ? body.path.slice(0, 128) : '',
    t: typeof body.ts === 'number' ? body.ts : Date.now(),
    r: typeof body.runtime === 'string' ? body.runtime.slice(0, 16) : 'web',
    ...(Object.keys(payload).length ? { d: payload } : {}),
  };

  // 当前 dev 模式：console 占位。接 Redis/PostHog 时在这里替换
  // eslint-disable-next-line no-console
  console.info('[brain-events]', entry);

  return NextResponse.json({ ok: true });
}
