'use client';

import Link from 'next/link';
import { DownloadButton } from './DownloadButton';

export function TopNav() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 px-16 py-6 flex justify-between items-center bg-paper/95 backdrop-blur-sm border-b border-border">
      <Link href="/" className="font-serif text-xl font-bold tracking-tight">
        Brain<span className="text-vermillion">.</span>
      </Link>

      <div className="flex items-center gap-10 text-sm text-ink-light">
        <Link href="/#features" className="hover:text-ink transition-colors">
          功能
        </Link>
        <Link href="/#coaching" className="hover:text-ink transition-colors">
          学习辅导
        </Link>
        <Link href="/try" className="hover:text-ink transition-colors">
          试聊
        </Link>
        <DownloadButton variant="ghost" />
      </div>
    </nav>
  );
}