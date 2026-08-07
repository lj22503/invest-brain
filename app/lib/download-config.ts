// app/lib/download-config.ts
// Plan 4 任务 1：手动维护 GitHub Releases 下载链接。
// Plan 5 任务 5：加 fetchAssets() 优先读 /.well-known/releases.json，回退到 FALLBACK_ASSETS。

export interface DownloadAsset {
  os: 'windows' | 'macos' | 'linux';
  label: string;
  url: string;
  filename: string;
  sizeHint: string;
}

export const FALLBACK_ASSETS: DownloadAsset[] = [
  {
    os: 'windows',
    label: 'Windows',
    url: 'https://github.com/lj22503/invest-brain/releases/download/v0.1.0/InvestBrain_0.1.0_x64_en-US.msi',
    filename: 'InvestBrain_0.1.0_x64_en-US.msi',
    sizeHint: '约 4.5MB',
  },
  {
    os: 'macos',
    label: 'macOS',
    url: 'https://github.com/lj22503/invest-brain/releases/tag/v0.1.0',
    filename: 'macos-pending',
    sizeHint: '待 v1.2',
  },
  {
    os: 'linux',
    label: 'Linux',
    url: 'https://github.com/lj22503/invest-brain/releases/tag/v0.1.0',
    filename: 'linux-pending',
    sizeHint: '待 v1.2',
  },
];

// 向后兼容别名（旧引用）
export const DOWNLOAD_ASSETS = FALLBACK_ASSETS;

interface RemoteAsset {
  os: 'windows' | 'macos' | 'linux';
  url: string;
  size_hint: string;
}

interface ReleasesJson {
  version: string;
  generated_at: string;
  assets: RemoteAsset[];
}

const LABEL_MAP: Record<RemoteAsset['os'], string> = {
  windows: 'Windows',
  macos: 'macOS',
  linux: 'Linux',
};

export async function fetchAssets(): Promise<DownloadAsset[]> {
  if (typeof window === 'undefined') return FALLBACK_ASSETS;
  try {
    const r = await fetch('/.well-known/releases.json', { cache: 'no-store' });
    if (!r.ok) return FALLBACK_ASSETS;
    const data: ReleasesJson = await r.json();
    return data.assets.map(a => ({
      os: a.os,
      label: LABEL_MAP[a.os] ?? a.os,
      url: a.url,
      filename: a.url.split('/').pop() ?? '',
      sizeHint: a.size_hint,
    }));
  } catch {
    return FALLBACK_ASSETS;
  }
}

export function detectOS(): DownloadAsset['os'] {
  if (typeof navigator === 'undefined' || !navigator.userAgent) return 'windows';
  const ua = navigator.userAgent.toLowerCase();
  if (ua.includes('win')) return 'windows';
  if (ua.includes('mac')) return 'macos';
  if (ua.includes('linux')) return 'linux';
  return 'windows'; // 默认推 Windows
}