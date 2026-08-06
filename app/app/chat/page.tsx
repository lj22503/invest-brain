'use client';

import { ChatView } from '@/components/chat/ChatView';
import { InputBox } from '@/components/chat/InputBox';
import { useChatStore, Message } from '@/lib/chat-store';
import { callLLM } from '@/lib/llm-router';

export default function HomePage() {
  const activeId = useChatStore(s => s.activeId);
  const conversations = useChatStore(s => s.conversations);
  const setActive = useChatStore(s => s.setActive);
  const addConversation = useChatStore(s => s.addConversation);
  const appendMessage = useChatStore(s => s.appendMessage);

  const handleSend = async (text: string) => {
    const conversationId = activeId ?? `conv-${Date.now()}`;
    if (!activeId) {
      addConversation({
        id: conversationId,
        title: text.slice(0, 30),
        lastMessageAt: new Date().toISOString(),
        messages: [],
      });
      setActive(conversationId);
    }
    const userMsg: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: text,
      createdAt: new Date().toISOString(),
    };
    appendMessage(conversationId, userMsg);

    try {
      const resp = await callLLM(conversations.find(c => c.id === conversationId)?.messages ?? [], text);
      const aiMsg: Message = {
        id: `msg-${Date.now()}-ai`,
        role: 'assistant',
        content: resp.content,
        toolCalls: resp.toolCalls,
        createdAt: new Date().toISOString(),
      };
      appendMessage(conversationId, aiMsg);
    } catch (e) {
      const errMsg: Message = {
        id: `msg-${Date.now()}-err`,
        role: 'assistant',
        content: `✗ ${String(e)}`,
        createdAt: new Date().toISOString(),
      };
      appendMessage(conversationId, errMsg);
    }
  };

  return (
    <>
      <ChatView />
      <InputBox onSend={handleSend} />
    </>
  );
}
