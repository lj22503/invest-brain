'use client';

import { HistoryList } from './HistoryList';
import { PacksBadge } from './PacksBadge';

export function Sidebar() {
  return (
    <aside className="w-72 border-r flex flex-col bg-gray-50">
      <div className="p-4 border-b">
        <h2 className="text-sm font-semibold text-gray-700">◇ 当前对话</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        <HistoryList />
      </div>

      <div className="border-t p-3">
        <PacksBadge />
        <div className="mt-3 space-y-1 text-sm">
          <a href="/app/masters" className="block px-2 py-1 rounded hover:bg-gray-200">
            ◆ 大师
          </a>
          <a href="/app/frameworks" className="block px-2 py-1 rounded hover:bg-gray-200">
            ◇ 框架
          </a>
          <a href="/app/settings" className="block px-2 py-1 rounded hover:bg-gray-200">
            ◇ 设置
          </a>
        </div>
      </div>
    </aside>
  );
}