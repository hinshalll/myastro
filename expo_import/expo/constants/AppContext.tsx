// Myastro — lightweight global app state.
//   • Ask sheet: any screen can openAsk({ prefill, mode }) — e.g. Explore's
//     "most asked today" rows pre-fill the sheet.
//   • precision: the birth-time tier chosen in onboarding, read by the
//     Today / You precision banners.
//
// Rendered once at the root so the Ask overlay floats above the tabs + FAB.

import { createContext, useCallback, useContext, useMemo, useState, ReactNode } from 'react';
import { View } from 'react-native';
import AskOverlay from '@/components/AskOverlay';

export type AskMode = 'ask' | 'decide';
export type Precision = 'exact' | 'approximate' | 'unknown';

type AskState = { open: boolean; prefill: string; mode: AskMode };

type Ctx = {
  openAsk: (opts?: { prefill?: string; mode?: AskMode }) => void;
  closeAsk: () => void;
  precision: Precision;
  setPrecision: (p: Precision) => void;
};

const AppCtx = createContext<Ctx | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [ask, setAsk] = useState<AskState>({ open: false, prefill: '', mode: 'ask' });
  const [precision, setPrecision] = useState<Precision>('exact');

  const openAsk = useCallback((opts?: { prefill?: string; mode?: AskMode }) => {
    setAsk({ open: true, prefill: opts?.prefill ?? '', mode: opts?.mode ?? 'ask' });
  }, []);
  const closeAsk = useCallback(() => setAsk(s => ({ ...s, open: false })), []);

  const value = useMemo<Ctx>(
    () => ({ openAsk, closeAsk, precision, setPrecision }),
    [openAsk, closeAsk, precision],
  );

  return (
    <AppCtx.Provider value={value}>
      <View style={{ flex: 1 }}>
        {children}
        {ask.open && (
          <AskOverlay
            initialQuery={ask.prefill}
            initialMode={ask.mode}
            onClose={closeAsk}
          />
        )}
      </View>
    </AppCtx.Provider>
  );
}

export function useApp(): Ctx {
  const c = useContext(AppCtx);
  if (!c) throw new Error('useApp must be used inside <AppProvider>');
  return c;
}
