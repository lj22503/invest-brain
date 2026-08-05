import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Provider = 'deepseek' | 'anthropic' | 'openai';

interface LLMKeyState {
  provider: Provider | null;
  apiKey: string | null;
  setKey: (provider: Provider, key: string) => void;
  clear: () => void;
}

export const useLLMKey = create<LLMKeyState>()(
  persist(
    set => ({
      provider: null,
      apiKey: null,
      setKey: (provider, apiKey) => set({ provider, apiKey }),
      clear: () => set({ provider: null, apiKey: null }),
    }),
    { name: 'investbrain-llm-key' }
  )
);
