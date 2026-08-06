import { Message, ToolCall } from './chat-store';
import { useLLMKey } from './llm-key-store';

export interface LLMResponse {
  content: string;
  toolCalls?: ToolCall[];
}

export async function callLLM(history: Message[], userMsg: string): Promise<LLMResponse> {
  const { provider, apiKey } = useLLMKey.getState();

  // Plan 2 任务 8 阶段：未接真 LLM，仅 mock 一个三工具调用的回复
  if (!provider || !apiKey) {
    throw new Error('未配置 LLM Key，请先到设置页设置');
  }

  // 模拟工具调用延迟
  await new Promise(r => setTimeout(r, 600));

  return {
    content: `[Mock 回复 - 你说了 "${userMsg}"]\n\n这是 Plan 2 任务 8 的 mock 回复。真实 LLM 接通见后续 task。`,
    toolCalls: [
      { tool: 'master_view_invoke', status: 'ok', durationMs: 45 },
      { tool: 'price_check', status: 'ok', durationMs: 120 },
      { tool: 'behavior_check', status: 'ok', durationMs: 60 },
    ],
  };
}
