import { describe, it, expect, beforeEach } from 'vitest';
import { callLLM } from '../llm-router';
import { useLLMKey } from '../llm-key-store';

describe('callLLM', () => {
  beforeEach(() => {
    useLLMKey.setState({ provider: null, apiKey: null });
  });

  it('throws when no key', async () => {
    await expect(callLLM([], 'test')).rejects.toThrow(/未配置/);
  });

  it('returns mock when key set', async () => {
    useLLMKey.setState({ provider: 'deepseek', apiKey: 'sk-test' });
    const r = await callLLM([], 'hello');
    expect(r.content).toContain('hello');
    expect(r.toolCalls?.length).toBe(3);
  });
});
