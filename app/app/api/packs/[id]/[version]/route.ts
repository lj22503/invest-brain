import { NextResponse, type NextRequest } from 'next/server';

const ALLOWED_PACK_IDS = new Set(['master_views', 'industry_concepts']);

export const dynamic = 'force-dynamic';

export async function GET(
  req: NextRequest,
  ctx: { params: { id: string; version: string } }
) {
  const { id, version } = ctx.params;

  if (!ALLOWED_PACK_IDS.has(id)) {
    return NextResponse.json({ error: 'unknown pack_id' }, { status: 400 });
  }

  // 版本号允许带 .json 后缀以便 Tauri 拼接 URL
  const versionClean = version.replace(/\.json$/, '');
  if (!/^\d+\.\d+\.\d+$/.test(versionClean)) {
    return NextResponse.json({ error: 'invalid version format' }, { status: 400 });
  }

  const manifestUrl = process.env[`PACK_${id.toUpperCase()}_BLOB_URL`];
  if (!manifestUrl) {
    return NextResponse.json({ error: 'pack not configured' }, { status: 503 });
  }

  try {
    const upstream = await fetch(manifestUrl, { cache: 'no-store' });
    if (!upstream.ok) {
      return NextResponse.json(
        { error: 'upstream blob fail' },
        { status: 502 }
      );
    }
    const buf = Buffer.from(await upstream.arrayBuffer());
    return new NextResponse(buf, {
      status: 200,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Cache-Control': 'public, max-age=300',
      },
    });
  } catch (e) {
    return NextResponse.json(
      { error: String(e) },
      { status: 500 }
    );
  }
}