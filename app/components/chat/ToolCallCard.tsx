'use client';

import { ToolCall } from '@/lib/chat-store';

const STATUS_COLOR = {
  running: 'text-blue-500',
  ok: 'text-green-500',
  error: 'text-red-500',
};

const STATUS_ICON = {
  running: '⏳',
  ok: '✓',
  error: '✗',
};

export function ToolCallCard({ calls }: { calls: ToolCall[] }) {
  if (!calls?.length) return null;

  return (
    <details className="my-2 text-xs border rounded bg-white">
      <summary className="cursor-pointer px-3 py-2 text-gray-600 hover:bg-gray-50">
        工具调用 ({calls.length})
      </summary>
      <div className="px-3 py-2 space-y-1">
        {calls.map((c, i) => (
          <div key={i} className="flex items-center gap-2 font-mono">
            <span className={STATUS_COLOR[c.status]}>{STATUS_ICON[c.status]}</span>
            <span className="text-gray-800">{c.tool}</span>
            {c.durationMs != null && (
              <span className="text-gray-400">●{c.durationMs}ms</span>
            )}
            {c.status === 'error' && c.result != null && (
              <span className="text-red-400 truncate" title={String(c.result)}>
                {String(c.result)}
              </span>
            )}
          </div>
        ))}
      </div>
    </details>
  );
}
