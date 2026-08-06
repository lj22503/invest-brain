'use client';

import { useChatStore } from '@/lib/chat-store';
import { MessageBubble } from './MessageBubble';

export function ChatView() {
  const activeId = useChatStore(s => s.activeId);
  const conversations = useChatStore(s => s.conversations);
  const conversation = conversations.find(c => c.id === activeId);

  if (!conversation) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400">
        <div className="text-center">
          <p className="text-lg mb-2">💡 试试：</p>
          <ul className="text-sm space-y-1">
            <li>• 我刚买了 X，帮我审视一下</li>
            <li>• 茅台现在估值贵不贵</li>
            <li>• 我最近又追涨了吗</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6">
      {conversation.messages.map(m => (
        <MessageBubble key={m.id} message={m} />
      ))}
    </div>
  );
}
