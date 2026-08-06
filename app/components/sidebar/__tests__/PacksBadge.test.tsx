import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { PacksBadge } from '../PacksBadge';

vi.mock('@/lib/tauri', () => ({
  callHealthCheck: vi.fn().mockResolvedValue({ status: 'ok', version: '0.1.0' }),
}));

describe('PacksBadge', () => {
  it('shows version after health check resolves', async () => {
    render(<PacksBadge />);
    await waitFor(() => expect(screen.getByText(/v0.1.0/)).toBeInTheDocument());
  });
});