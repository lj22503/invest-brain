// app/components/providers/TauriProvider.tsx
'use client';

import { createContext, useContext } from 'react';
import { isTauri } from '@/lib/tauri';

const TauriContext = createContext({ isTauri: false });

export function TauriProvider({ children }: { children: React.ReactNode }) {
  return (
    <TauriContext.Provider value={{ isTauri: isTauri() }}>
      {children}
    </TauriContext.Provider>
  );
}

export const useTauri = () => useContext(TauriContext);