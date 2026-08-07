'use client';

import { useEffect, useState } from 'react';
import { detectOS, fetchAssets, FALLBACK_ASSETS, DownloadAsset } from '@/lib/download-config';

export function DownloadButton({ variant = 'primary' }: { variant?: 'primary' | 'ghost' }) {
  const [asset, setAsset] = useState<DownloadAsset | null>(null);

  useEffect(() => {
    fetchAssets().then(list => {
      const os = detectOS();
      setAsset(list.find(a => a.os === os) ?? FALLBACK_ASSETS[0]);
    });
  }, []);

  if (!asset) return null;

  const isPrimary = variant === 'primary';
  return (
    <a
      href={asset.url}
      className={
        isPrimary
          ? 'bg-vermillion text-white px-8 py-4 rounded text-base font-medium hover:bg-[#A8322A] transition-all hover:-translate-y-px hover:shadow-md inline-flex items-center gap-2'
          : 'border border-vermillion text-vermillion px-6 py-2 rounded text-sm hover:bg-vermillion/[0.04] transition-colors inline-flex items-center gap-2'
      }
      download
    >
      <span>⬇ 下载 {asset.label}</span>
    </a>
  );
}