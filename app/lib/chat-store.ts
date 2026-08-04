import { create } from 'zustand';

export interface Conversation {
  id: string;
  title: string;
  lastMessageAt: string;
  messages: Message[];
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  toolCalls?: ToolCall[];
  createdAt: string;
}

export interface ToolCall {
  tool: string;
  status: 'running' | 'ok' | 'error';
  durationMs?: number;
  args?: Record<string, unknown>;
  result?: unknown;
}

interface ChatState {
  conversations: Conversation[];
  activeId: string | null;
  setActive: (id: string | null) => void;
  addConversation: (c: Conversation) => void;
  appendMessage: (conversationId: string, m: Message) => void;
}

export const useChatStore = create<ChatState>(set => ({
  conversations: [],
  activeId: null,
  setActive: id => set({ activeId: id }),
  addConversation: c => set(s => ({ conversations: [c, ...s.conversations] })),
  appendMessage: (id, m) =>
    set(s => ({
      conversations: s.conversations.map(c =>
        c.id === id
          ? { ...c, messages: [...c.messages, m], lastMessageAt: m.createdAt }
          : c
      ),
    })),
}));