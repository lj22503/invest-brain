import { Message, ToolCall } from './chat-store';
import { useLLMKey } from './llm-key-store';

export interface LLMResponse {
  content: string;
  toolCalls?: ToolCall[];
}

export async function callLLM(history: Message[], userMsg: string): Promise<LLMResponse> {
  const { provider, apiKey } = useLLMKey.getState();

  // 未配置 Key：仍给演示回复，让用户先体验完整闭环（不阻断、不报错）。
  // 首页欢迎引导会提示可到设置页配置真实 Key。
  const demoTag = provider && apiKey ? '' : '\n\n> 演示模式：尚未配置 LLM Key，以上为预置演示回复。到【设置】页配置后即可接入真实模型。';

  // 模拟工具调用延迟
  await new Promise(r => setTimeout(r, 600));

  return {
    content: `[Mock 回复 - 你说了 "${userMsg}"]\n\n这是 Plan 2 任务 8 的 mock 回复。真实 LLM 接通见后续 task。${demoTag}`,
    toolCalls: [
      { tool: 'master_view_invoke', status: 'ok', durationMs: 45 },
      { tool: 'price_check', status: 'ok', durationMs: 120 },
      { tool: 'behavior_check', status: 'ok', durationMs: 60 },
    ],
  };
}
