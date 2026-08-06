// app/lib/packs-store.ts
// Plan 3 任务 5：知识包管理 store（zustand）。

import { create } from 'zustand';
import { invoke } from './tauri';

export interface UpdateAvailable {
  pack_id: string;
  from: string;
  to: string;
}

interface PacksState {
  local: Record<string, string>;
  remote: Record<string, string>;
  updates: UpdateAvailable[];
  checking: boolean;
  updating: string | null;
  error: string | null;
  check: () => Promise<void>;
  update: (packId: string) => Promise<void>;
}

export const ALL_PACKS = ['master_views', 'industry_concepts'] as const;
export type PackId = typeof ALL_PACKS[number];

interface CheckPacksResult {
  local: Record<string, string>;
  remote: Record<string, string>;
  updates_available?: UpdateAvailable[];
}

export const usePacks = create<PacksState>((set, get) => ({
  local: {},
  remote: {},
  updates: [],
  checking: false,
  updating: null,
  error: null,

  check: async () => {
    set({ checking: true, error: null });
    try {
      const result = await invoke<CheckPacksResult>('check_packs');
      set({
        local: result.local ?? {},
        remote: result.remote ?? {},
        updates: result.updates_available ?? [],
        checking: false,
      });
    } catch (e) {
      set({ checking: false, error: String(e) });
      throw e;
    }
  },

  update: async (packId: string) => {
    set({ updating: packId, error: null });
    try {
      await invoke('update_pack', { packId });
      await get().check();
      set({ updating: null });
    } catch (e) {
      set({ updating: null, error: String(e) });
      throw e;
    }
  },
}));