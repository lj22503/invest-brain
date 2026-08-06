// Plan 2 Task 5 stub — Task 6 will replace with real LLM config persistence.
// Functions here match what settings/page.tsx (pre-existing) already imports.

export interface LLMConfig {
  provider: string;
  api_key: string;
  base_url?: string;
}

export async function saveLLMConfig(config: LLMConfig): Promise<void> {
  // TODO Task 6: persist via Tauri IPC or localStorage.
  console.warn('[stub] saveLLMConfig called — Task 6 will implement', config);
}