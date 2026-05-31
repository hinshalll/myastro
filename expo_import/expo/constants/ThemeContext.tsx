import { createContext, useContext, useMemo, useState, ReactNode } from 'react';
import { palettes, ThemeName, Palette } from './theme';

type Ctx = {
  name: ThemeName;
  p: Palette;          // shorthand: const { p } = useTheme()
  setTheme: (n: ThemeName) => void;
  toggle: () => void;
};

const ThemeCtx = createContext<Ctx | null>(null);

export function ThemeProvider({ children, initial = 'dark' }: { children: ReactNode; initial?: ThemeName }) {
  const [name, setName] = useState<ThemeName>(initial);
  const value = useMemo<Ctx>(() => ({
    name,
    p: palettes[name],
    setTheme: setName,
    toggle: () => setName(n => (n === 'dark' ? 'light' : 'dark')),
  }), [name]);
  return <ThemeCtx.Provider value={value}>{children}</ThemeCtx.Provider>;
}

export function useTheme(): Ctx {
  const c = useContext(ThemeCtx);
  if (!c) throw new Error('useTheme must be used inside <ThemeProvider>');
  return c;
}
