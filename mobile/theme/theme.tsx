import React, { createContext, useContext, useMemo, useState } from 'react';

// ── Design tokens, ported from the Claude Design styles.css ──
export type Mode = 'dark' | 'light';

const DARK = {
  bg0: '#0a0a10',
  bg1: '#0e0e16',
  bg2: '#14141e',
  gradTop: '#0c0c14',
  gradBottom: '#08080e',
  glowTop: 'rgba(40, 28, 80, 0.45)',
  surface: 'rgba(255, 255, 255, 0.025)',
  surfaceStrong: 'rgba(255, 255, 255, 0.05)',
  surfaceTint: 'rgba(212, 178, 102, 0.04)',
  border: 'rgba(255, 255, 255, 0.07)',
  borderStrong: 'rgba(255, 255, 255, 0.14)',
  hairline: 'rgba(255, 255, 255, 0.05)',
  ink: '#ece6d4',
  inkSoft: 'rgba(236, 230, 212, 0.70)',
  inkMute: 'rgba(236, 230, 212, 0.45)',
  inkFaint: 'rgba(236, 230, 212, 0.26)',
  gold: '#c8a253',
  goldSoft: 'rgba(200, 162, 83, 0.12)',
  goldGlow: 'rgba(200, 162, 83, 0.22)',
  violet: '#8b6df0',
  indigo: '#5b6dd9',
  rose: '#d28798',
  teal: '#7cb6ad',
  tabBarBg: 'rgba(10, 10, 16, 0.86)',
};

const LIGHT: typeof DARK = {
  bg0: '#f6f1e3',
  bg1: '#efe9d8',
  bg2: '#e3dac3',
  gradTop: '#f7f2e4',
  gradBottom: '#ede5d0',
  glowTop: 'rgba(40, 28, 80, 0.06)',
  surface: 'rgba(255, 255, 255, 0.55)',
  surfaceStrong: 'rgba(255, 255, 255, 0.75)',
  surfaceTint: 'rgba(120, 90, 200, 0.04)',
  border: 'rgba(34, 28, 18, 0.10)',
  borderStrong: 'rgba(34, 28, 18, 0.20)',
  hairline: 'rgba(34, 28, 18, 0.07)',
  ink: '#1a1714',
  inkSoft: 'rgba(26, 23, 20, 0.70)',
  inkMute: 'rgba(26, 23, 20, 0.48)',
  inkFaint: 'rgba(26, 23, 20, 0.28)',
  gold: '#8a6618',
  goldSoft: 'rgba(138, 102, 24, 0.10)',
  goldGlow: 'rgba(138, 102, 24, 0.20)',
  violet: '#5e3fc5',
  indigo: '#3a52d0',
  rose: '#b5546a',
  teal: '#2f7873',
  tabBarBg: 'rgba(246, 241, 227, 0.86)',
};

export type Palette = typeof DARK;

export const radius = { sm: 10, md: 18, lg: 24 };

// Font family names as registered by @expo-google-fonts
export const fonts = {
  display: 'CormorantGaramond_500Medium',
  displayItalic: 'CormorantGaramond_500Medium_Italic',
  display400: 'CormorantGaramond_400Regular',
  sans300: 'Manrope_300Light',
  sans: 'Manrope_400Regular',
  sans500: 'Manrope_500Medium',
  sans600: 'Manrope_600SemiBold',
  sans700: 'Manrope_700Bold',
  mono: 'JetBrainsMono_500Medium',
  deva: 'NotoSansDevanagari_400Regular',
};

type ThemeCtx = { mode: Mode; setMode: (m: Mode) => void; c: Palette };
const Ctx = createContext<ThemeCtx | null>(null);

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const [mode, setMode] = useState<Mode>('dark');
  const value = useMemo(() => ({ mode, setMode, c: mode === 'dark' ? DARK : LIGHT }), [mode]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
};

export const useTheme = () => {
  const v = useContext(Ctx);
  if (!v) throw new Error('useTheme must be used inside ThemeProvider');
  return v;
};
