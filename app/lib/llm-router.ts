import { Message, ToolCall } from './chat-store';
import { callLLMRemote, getLLMConfig } from './api';
import { renderScenario, matchScenario } from './demo-data';

export interface LLMResponse {
  content: string;
  toolCalls?: ToolCall[];
}

// 无 Key 演示模式：按用户输入匹配预置场景，返回真实闭环文本（非占位符死文本）。
function demoResponse(userMsg: string): string {
  const key = matchScenario(userMsg);
  return renderScenario(key).join('\n\n');
}

// 前端 zustand 只是本地 UI 状态；是否真实对话以 sidecar 落盘配置为准。
let lastConfigured: boolean | null = null;
let checking = false;

async function refreshConfigured(): Promise<boolean> {
  try {
    const cfg = await getLLMConfig();
    lastConfigured = !!cfg.configured;
  } catch {
    lastConfigured = null; // sidecar 不可达：不阻断 UI，保持演示模式
  }
  return lastConfigured === true;
}

export async function isLLMConfigured(): Promise<boolean> {
  if (lastConfigured !== null) return lastConfigured;
  return refreshConfigured();
}

export async function callLLM(history: Message[], userMsg: string): Promise<LLMResponse> {
  let configured: boolean;
  try {
    configured = await refreshConfigured(); // 以 sidecar 落盘配置为准，前端 zustand 仅作 UI 状态
  } catch {
    configured = false;
  }

  // 未配置 Key：演示闭环回复（不阻断、不报错），对话页会渲染升级卡片引导去设置页。
  if (!configured) {
    await new Promise(r => setTimeout(r, 600));
    return {
      content: demoResponse(userMsg),
      toolCalls: [
        { tool: 'demo_reply', status: 'ok', durationMs: 45 },
      ],
    };
  }

  // 已配置：经 sidecar 代理真实调用（Key 在本地 llm.json，不经过 WebView）。
  if (!checking) {
    checking = true;
    try {
      const result = await callLLMRemote(
        history.map(m => ({ role: m.role === 'assistant' ? 'assistant' : 'user', content: m.content })),
        userMsg,
      );
      if (result.status === 'ok' && result.content) {
        return {
          content: result.content,
          toolCalls: [
            { tool: 'llm_router', status: 'ok', durationMs: 0 },
          ],
        };
      }
      if (result.status === 'no_key') {
        lastConfigured = false;
        return {
          content: demoResponse(userMsg),
          toolCalls: [{ tool: 'demo_reply', status: 'ok', durationMs: 45 }],
        };
      }
      return {
        content: `真实模型调用失败：${result.message ?? '未知错误'}${result.detail ? `\n> ${result.detail}` : ''}\n\n可到【设置】页检查 Key 与服务商配置。`,
        toolCalls: [{ tool: 'llm_router', status: 'error', durationMs: 0 }],
      };
    } catch (e) {
      // sidecar 离线 / 网络不可达：不抛裸 TypeError，降级为友好提示。
      return {
        content: `⚠️ 本地服务（sidecar）当前不可达，无法进行真实对话。\n\n可能原因：桌面端服务未启动或正在重启。\n\n你可以：\n• 稍后重试\n• 到【设置】页检查服务状态\n\n（当前回复来自本地演示数据）\n\n${demoResponse(userMsg)}`,
        toolCalls: [{ tool: 'llm_router', status: 'error', durationMs: 0 }],
      };
    } finally {
      checking = false;
    }
  }

  return {
    content: demoResponse(userMsg),
    toolCalls: [{ tool: 'demo_reply', status: 'ok', durationMs: 45 }],
  };
}
