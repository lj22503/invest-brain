// app/lib/__tests__/packs-store.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('../tauri', () => ({
  invoke: vi.fn(),
}));

import { invoke } from '../tauri';
import { usePacks, ALL_PACKS } from '../packs-store';

const mockedInvoke = vi.mocked(invoke);

describe('usePacks', () => {
  beforeEach(() => {
    mockedInvoke.mockReset();
    usePacks.setState({
      local: {},
      remote: {},
      updates: [],
      checking: false,
      updating: null,
      error: null,
    });
  });

  it('ALL_PACKS exposes expected ids', () => {
    expect(ALL_PACKS).toEqual(['master_views', 'industry_concepts']);
  });

  it('check() populates state from check_packs result', async () => {
    mockedInvoke.mockResolvedValueOnce({
      local: { master_views: '1.0.0', industry_concepts: '1.0.0' },
      remote: { master_views: '1.2.3', industry_concepts: '1.0.0' },
      updates_available: [{ pack_id: 'master_views', from: '1.0.0', to: '1.2.3' }],
    });

    await usePacks.getState().check();

    const s = usePacks.getState();
    expect(s.local.master_views).toBe('1.0.0');
    expect(s.remote.master_views).toBe('1.2.3');
    expect(s.updates).toHaveLength(1);
    expect(s.updates[0].pack_id).toBe('master_views');
    expect(s.checking).toBe(false);
  });

  it('update() invokes update_pack and re-checks', async () => {
    mockedInvoke
      .mockResolvedValueOnce(undefined) // update_pack
      .mockResolvedValueOnce({
        local: { master_views: '1.2.3', industry_concepts: '1.0.0' },
        remote: { master_views: '1.2.3', industry_concepts: '1.0.0' },
        updates_available: [],
      });

    await usePacks.getState().update('master_views');

    expect(mockedInvoke).toHaveBeenCalledWith('update_pack', { packId: 'master_views' });
    expect(usePacks.getState().updating).toBeNull();
    expect(usePacks.getState().updates).toHaveLength(0);
  });
});