'use client';

import Link from 'next/link';
import { Message } from '@/lib/chat-store';
import { ToolCallCard } from './ToolCallCard';

export function MessageBubble({ message }: { message: Message }) {
  const isDemo = message.toolCalls?.some(c => c.tool === 'demo_reply');
  if (message.role === 'user') {
    return (
      <div className="flex justify-end mb-3">
        <div className="max-w-2xl bg-vermillion-light/30 rounded-lg px-4 py-2">
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    );
  }
  return (
    <div className="flex justify-start mb-3">
      <div className="max-w-2xl bg-paper-warm rounded-lg px-4 py-2">
        <p className="text-xs text-ink-light mb-1">Brain</p>
        <p className="whitespace-pre-wrap">{message.content}</p>
        {message.toolCalls && <ToolCallCard calls={message.toolCalls} />}
        {isDemo && (
          <div className="mt-3 border border-amber-200 bg-amber-50 rounded-lg p-3">
            <p className="text-sm font-medium text-amber-800">解锁真实对话</p>
            <p className="text-xs text-amber-700 mt-1">
              配置 LLM Key 后可进行真实问答，并联动本地行情、知识包与行为体检。
            </p>
            <Link
              href="/settings"
              className="inline-block mt-2 text-xs bg-amber-500 text-white rounded px-3 py-1 hover:bg-amber-600"
            >
              去设置
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
