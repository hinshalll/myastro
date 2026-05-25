import React from 'react';
import { Text, TextProps, StyleProp, TextStyle } from 'react-native';
import { fonts, useTheme } from '@/theme/theme';

type TxtProps = TextProps & { color?: string; style?: StyleProp<TextStyle> };

// Editorial serif display
export const Display = ({ color, style, ...p }: TxtProps) => {
  const { c } = useTheme();
  return <Text {...p} style={[{ fontFamily: fonts.display, color: color ?? c.ink, letterSpacing: -0.3 }, style]} />;
};

export const H1 = ({ color, style, ...p }: TxtProps) => {
  const { c } = useTheme();
  return <Text {...p} style={[{ fontFamily: fonts.display, fontSize: 38, lineHeight: 40, letterSpacing: -0.7, color: color ?? c.ink }, style]} />;
};

export const H2 = ({ color, style, ...p }: TxtProps) => {
  const { c } = useTheme();
  return <Text {...p} style={[{ fontFamily: fonts.display, fontSize: 26, lineHeight: 30, letterSpacing: -0.4, color: color ?? c.ink }, style]} />;
};

export const H3 = ({ color, style, ...p }: TxtProps) => {
  const { c } = useTheme();
  return <Text {...p} style={[{ fontFamily: fonts.display, fontSize: 20, lineHeight: 24, letterSpacing: -0.2, color: color ?? c.ink }, style]} />;
};

export const Body = ({ color, style, ...p }: TxtProps) => {
  const { c } = useTheme();
  return <Text {...p} style={[{ fontFamily: fonts.sans, fontSize: 14, lineHeight: 22, color: color ?? c.inkSoft }, style]} />;
};

export const Small = ({ color, style, ...p }: TxtProps) => {
  const { c } = useTheme();
  return <Text {...p} style={[{ fontFamily: fonts.sans, fontSize: 12, lineHeight: 17, color: color ?? c.inkMute }, style]} />;
};

export const Kicker = ({ color, gold, style, ...p }: TxtProps & { gold?: boolean }) => {
  const { c } = useTheme();
  return <Text {...p} style={[{ fontFamily: fonts.sans500, fontSize: 10, lineHeight: 12, letterSpacing: 2, textTransform: 'uppercase', color: color ?? (gold ? c.gold : c.inkMute) }, style]} />;
};

export const Mono = ({ color, style, ...p }: TxtProps) => {
  const { c } = useTheme();
  return <Text {...p} style={[{ fontFamily: fonts.mono, fontSize: 11, lineHeight: 13, letterSpacing: 0.9, textTransform: 'uppercase', color: color ?? c.inkMute }, style]} />;
};

export const Deva = ({ color, style, ...p }: TxtProps) => {
  const { c } = useTheme();
  return <Text {...p} style={[{ fontFamily: fonts.deva, fontSize: 14, lineHeight: 20, color: color ?? c.inkMute }, style]} />;
};
