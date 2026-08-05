'use client';

import { useState } from 'react';
import { ChatView } from '@/components/chat/ChatView';
import { InputBox } from '@/components/chat/InputBox';
import { useChatStore } from '@/lib/chat-store';

export default function HomePage() {
  const [dummyText, setDummyText] = useState('');
  const setActive = useChatStore(s => s.setActive);
  const addConversation = useChatStore(s => s.addConversation);
  const appendMessage = useChatStore(s => s.appendMessage);

  const handleSend = (text: string) => {
    setDummyText(text);
    // Plan 2 任务 4 仅更新 UI，不调 LLM
    // 真正调用在任务 7+ 引入
    const newId = `conv-${Date.now()}`;
    addConversation({
      id: newId,
      title: text.slice(0, 30),
      lastMessageAt: new Date().toISOString(),
      messages: [
        {
          id: `msg-${Date.now()}`,
          role: 'user',
          content: text,
          createdAt: new Date().toISOString(),
        },
      ],
    });
    setActive(newId);
  };

  return (
    <>
      <ChatView />
      <InputBox onSend={handleSend} />
    </>
  );
}
