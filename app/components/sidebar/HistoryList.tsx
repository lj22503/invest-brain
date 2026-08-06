'use client';

import { useChatStore } from '@/lib/chat-store';

export function HistoryList() {
  const conversations = useChatStore(s => s.conversations);
  if (conversations.length === 0) {
    return <p className="text-xs text-gray-400 px-2">暂无历史</p>;
  }
  return (
    <ul className="space-y-1">
      {conversations.map(c => (
        <li key={c.id}>
          <button className="w-full text-left px-2 py-1 rounded hover:bg-gray-200">
            <span className="block text-sm truncate">{c.title}</span>
            <span className="text-xs text-gray-400">{c.lastMessageAt}</span>
          </button>
        </li>
      ))}
    </ul>
  );
}