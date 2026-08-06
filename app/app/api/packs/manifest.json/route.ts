import { NextResponse } from 'next/server';

const PACK_IDS = ['master_views', 'industry_concepts'] as const;
type PackId = typeof PACK_IDS[number];

interface PackManifest {
  pack_id: PackId;
  version: string;
  updated_at: string;
}

async function fetchManifest(packId: PackId): Promise<PackManifest | null> {
  const url = process.env[`PACK_${packId.toUpperCase()}_BLOB_URL`];
  if (!url) return null;
  try {
    const resp = await fetch(url, { cache: 'no-store' });
    if (!resp.ok) return null;
    return (await resp.json()) as PackManifest;
  } catch {
    return null;
  }
}

export const dynamic = 'force-dynamic';

export async function GET() {
  const entries = await Promise.all(
    PACK_IDS.map(async (id) => {
      const m = await fetchManifest(id);
      return [id, m?.version ?? '0.0.0'];
    })
  );

  return NextResponse.json(Object.fromEntries(entries), {
    headers: {
      'Cache-Control': 'public, max-age=60',
    },
  });
}