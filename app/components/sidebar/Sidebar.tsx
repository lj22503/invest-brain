'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { HistoryList } from './HistoryList';
import { PacksBadge } from './PacksBadge';

const NAV_ITEMS = [
  { href: '/chat', label: '◇ 对话' },
  { href: '/archive', label: '◇ 我的档案' },
  { href: '/packs', label: '◇ 知识包' },
  { href: '/settings', label: '◇ 设置' },
  { href: '/try', label: '◇ 试聊引导' },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="w-72 border-r border-border flex flex-col bg-paper-warm">
      <div className="p-4 border-b">
        <h2 className="text-sm font-semibold text-ink-light">◇ 当前对话</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        <HistoryList />
      </div>

      <div className="border-t border-border p-3">
        <PacksBadge />
        <nav className="mt-3 space-y-1 text-sm">
          {NAV_ITEMS.map(item => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block px-2 py-1 rounded transition-colors ${active ? 'bg-vermillion-light/40 text-vermillion' : 'hover:bg-paper-warm text-ink-light'}`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}