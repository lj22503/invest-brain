'use client';

import { useChatStore } from '@/lib/chat-store';
import { MessageBubble } from './MessageBubble';
import { WelcomeHero } from './WelcomeHero';

export function ChatView({ onSend }: { onSend?: (text: string) => void }) {
  const activeId = useChatStore(s => s.activeId);
  const conversations = useChatStore(s => s.conversations);
  const conversation = conversations.find(c => c.id === activeId);

  if (!conversation) {
    return <WelcomeHero onSend={onSend ?? (() => {})} />;
  }

  return (
    <div className="flex-1 overflow-y-auto p-6">
      {conversation.messages.map(m => (
        <MessageBubble key={m.id} message={m} />
      ))}
    </div>
  );
}
