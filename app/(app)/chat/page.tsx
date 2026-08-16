'use client';

import { useEffect, useRef } from 'react';
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
  const handleSendRef = useRef<(text: string) => void>(() => {});

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
      // 兜底：不应出现裸 TypeError，降级为可读提示
      const errMsg: Message = {
        id: `msg-${Date.now()}-err`,
        role: 'assistant',
        content: `😥 本地服务暂时不可达（${e instanceof Error ? e.message : String(e)}）。\n\n请稍后重试；如果持续出现，可到【设置】页检查服务状态。`,
        createdAt: new Date().toISOString(),
      };
      appendMessage(conversationId, errMsg);
    }
  };
  handleSendRef.current = handleSend;

  // 来自试聊引导页的带问跳转：?ask=xxx 自动发起一次对话
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const ask = params.get('ask');
    if (ask) {
      const t = window.setTimeout(() => handleSendRef.current(ask), 300);
      return () => window.clearTimeout(t);
    }
  }, []);

  return (
    <>
      <ChatView onSend={handleSend} />
      <InputBox onSend={handleSend} />
    </>
  );
}
