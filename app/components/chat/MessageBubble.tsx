'use client';

import { Message } from '@/lib/chat-store';
import { ToolCallCard } from './ToolCallCard';

export function MessageBubble({ message }: { message: Message }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end mb-3">
        <div className="max-w-2xl bg-blue-100 rounded-lg px-4 py-2">
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    );
  }
  return (
    <div className="flex justify-start mb-3">
      <div className="max-w-2xl bg-gray-100 rounded-lg px-4 py-2">
        <p className="text-xs text-gray-500 mb-1">Brain</p>
        <p className="whitespace-pre-wrap">{message.content}</p>
        {message.toolCalls && <ToolCallCard calls={message.toolCalls} />}
      </div>
    </div>
  );
}
