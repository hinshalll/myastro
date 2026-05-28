// Myastro — design tokens
// Warm near-black + parchment ink + single restrained gold.
// Dark by default; toggle via the ThemeProvider in app/_layout.tsx.

import { Easing } from 'react-native';

export type ThemeName = 'dark' | 'light';

const dark = {
  bg0:        '#0b0907',
  bg1:        '#100c08',
  bg2:        '#16110b',

  surface:        'rgba(255, 247, 230, 0.025)',
  surfaceStrong:  'rgba(255, 247, 230, 0.05)',
  surfaceTint:    'rgba(212, 175, 107, 0.04)',
  border:         'rgba(255, 247, 230, 0.07)',
  borderStrong:   'rgba(255, 247, 230, 0.14)',
  hairline:       'rgba(255, 247, 230, 0.06)',

  ink:        '#f3ecd9',
  inkSoft:    'rgba(243, 236, 217, 0.68)',
  inkMute:    'rgba(243, 236, 217, 0.44)',
  inkFaint:   'rgba(243, 236, 217, 0.24)',

  gold:       '#d4af6b',
  goldSoft:   'rgba(212, 175, 107, 0.10)',
  goldGlow:   'rgba(212, 175, 107, 0.20)',

  slate:      '#6f7a90',
  rose:       '#c98a8a',
  teal:       '#87a99e',
  violet:     '#8b6df0',
};

const light = {
  bg0:        '#ffffff',
  bg1:        '#ffffff',
  bg2:        '#fbfaf6',

  surface:        'rgba(26, 22, 18, 0.02)',
  surfaceStrong:  'rgba(26, 22, 18, 0.04)',
  surfaceTint:    'rgba(148, 106, 24, 0.03)',
  border:         'rgba(26, 22, 18, 0.08)',
  borderStrong:   'rgba(26, 22, 18, 0.16)',
  hairline:       'rgba(26, 22, 18, 0.06)',

  ink:        '#1a1612',
  inkSoft:    'rgba(26, 22, 18, 0.66)',
  inkMute:    'rgba(26, 22, 18, 0.44)',
  inkFaint:   'rgba(26, 22, 18, 0.22)',

  gold:       '#946a18',
  goldSoft:   'rgba(148, 106, 24, 0.08)',
  goldGlow:   'rgba(148, 106, 24, 0.16)',

  slate:      '#4a5266',
  rose:       '#b35454',
  teal:       '#38766e',
  violet:     '#5e3fc5',
};

export const palettes = { dark, light };
export type Palette = typeof dark;

export const radii = {
  sm: 10,
  md: 16,
  lg: 22,
  pill: 999,
};

export const spacing = {
  xxs: 2,
  xs:  4,
  sm:  8,
  md:  14,
  lg:  22,
  xl:  28,
  xxl: 40,
};

export const fonts = {
  sans:        'HankenGrotesk_400Regular',
  sansMedium:  'HankenGrotesk_500Medium',
  sansBold:    'HankenGrotesk_700Bold',
  mono:        'JetBrainsMono_500Medium',
  deva:        'NotoSansDevanagari_400Regular',
};

export const text = {
  h1:     { fontFamily: fonts.sansMedium, fontSize: 28, lineHeight: 32, letterSpacing: -0.34 },
  h2:     { fontFamily: fonts.sansMedium, fontSize: 22, lineHeight: 26, letterSpacing: -0.18 },
  h3:     { fontFamily: fonts.sansMedium, fontSize: 17, lineHeight: 22 },
  body:   { fontFamily: fonts.sans,       fontSize: 13, lineHeight: 20 },
  small:  { fontFamily: fonts.sans,       fontSize: 12, lineHeight: 18 },
  kicker: { fontFamily: fonts.sansMedium, fontSize: 10, lineHeight: 12, letterSpacing: 2.2, textTransform: 'uppercase' as const },
  mono:   { fontFamily: fonts.mono,       fontSize: 10, lineHeight: 12, letterSpacing: 1.0,  textTransform: 'uppercase' as const },
};

// Reanimated easings
export const easings = {
  out:    Easing.bezier(0.22, 0.61, 0.36, 1),
  spring: Easing.bezier(0.34, 1.32, 0.42, 1),
};

// Vibe color helper (good / neutral / tough)
export type Vibe = 'good' | 'neutral' | 'tough';
export const vibeColor = (p: Palette, v: Vibe) =>
  v === 'good' ? p.gold : v === 'tough' ? p.rose : p.inkMute;
