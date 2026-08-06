'use client';

import { useEffect, useState } from 'react';
import { detectOS, DOWNLOAD_ASSETS, DownloadAsset } from '@/lib/download-config';

export function DownloadButton({ variant = 'primary' }: { variant?: 'primary' | 'ghost' }) {
  const [asset, setAsset] = useState<DownloadAsset | null>(null);

  useEffect(() => {
    const os = detectOS();
    setAsset(DOWNLOAD_ASSETS.find(a => a.os === os) ?? DOWNLOAD_ASSETS[0]);
  }, []);

  if (!asset) return null;

  const isPrimary = variant === 'primary';
  return (
    <a
      href={asset.url}
      className={
        isPrimary
          ? 'bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 inline-flex items-center gap-2'
          : 'border border-blue-500 text-blue-500 px-4 py-2 rounded hover:bg-blue-50 inline-flex items-center gap-2'
      }
      download
    >
      <span>⬇ 下载 {asset.label}</span>
      <span className="text-xs opacity-75">{asset.sizeHint}</span>
    </a>
  );
}