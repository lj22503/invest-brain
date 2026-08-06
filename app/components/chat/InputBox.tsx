'use client';

import { useState } from 'react';

export function InputBox({ onSend }: { onSend: (text: string) => void }) {
  const [text, setText] = useState('');

  const submit = () => {
    const t = text.trim();
    if (!t) return;
    onSend(t);
    setText('');
  };

  return (
    <div className="border-t p-4 flex gap-2">
      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        onKeyDown={e => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            submit();
          }
        }}
        placeholder="问点什么..."
        className="flex-1 resize-none border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-300"
        rows={2}
      />
      <button
        onClick={submit}
        className="bg-blue-500 text-white rounded px-4 py-2 hover:bg-blue-600"
      >
        ⏎ 发送
      </button>
    </div>
  );
}
