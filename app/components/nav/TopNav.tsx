'use client';

import Link from 'next/link';
import { DownloadButton } from './DownloadButton';

export function TopNav() {
  return (
    <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur border-b">
      <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl">🧠</span>
          <span className="font-semibold">InvestBrain</span>
        </Link>

        <div className="flex items-center gap-3">
          <Link
            href="/try"
            className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded hover:bg-gray-100"
          >
            试聊
          </Link>
          <DownloadButton variant="ghost" />
        </div>
      </div>
    </nav>
  );
}