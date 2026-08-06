// app/lib/download-config.ts
// Plan 4 任务 1：手动维护 GitHub Releases 下载链接。

export interface DownloadAsset {
  os: 'windows' | 'macos' | 'linux';
  label: string;
  url: string;
  filename: string;
  sizeHint: string;
}

export const DOWNLOAD_ASSETS: DownloadAsset[] = [
  {
    os: 'windows',
    label: 'Windows',
    url: 'https://github.com/lj22503/invest-brain/releases/latest/download/InvestBrain-windows.msi',
    filename: 'InvestBrain-windows.msi',
    sizeHint: '约 100MB',
  },
  {
    os: 'macos',
    label: 'macOS',
    url: 'https://github.com/lj22503/invest-brain/releases/latest/download/InvestBrain-mac.dmg',
    filename: 'InvestBrain-mac.dmg',
    sizeHint: '约 80MB',
  },
  {
    os: 'linux',
    label: 'Linux',
    url: 'https://github.com/lj22503/invest-brain/releases/latest/download/InvestBrain-linux.AppImage',
    filename: 'InvestBrain-linux.AppImage',
    sizeHint: '约 90MB',
  },
];

export function detectOS(): DownloadAsset['os'] {
  if (typeof navigator === 'undefined' || !navigator.userAgent) return 'windows';
  const ua = navigator.userAgent.toLowerCase();
  if (ua.includes('win')) return 'windows';
  if (ua.includes('mac')) return 'macos';
  if (ua.includes('linux')) return 'linux';
  return 'windows'; // 默认推 Windows
}