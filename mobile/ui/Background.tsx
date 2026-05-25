import React, { useMemo } from 'react';
import { View } from 'react-native';
import Svg, { Circle, Line, Defs, RadialGradient, Stop, Rect } from 'react-native-svg';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '@/theme/theme';

// Deterministic starfield + faint connecting lines
export const ConstellationBG = ({ seed = 1, density = 60, opacity }: { seed?: number; density?: number; opacity?: number }) => {
  const { c, mode } = useTheme();
  const stars = useMemo(() => {
    let s = seed * 9301 + 49297;
    const rand = () => { s = (s * 9301 + 49297) % 233280; return s / 233280; };
    return Array.from({ length: density }, () => ({
      x: rand() * 100, y: rand() * 100,
      r: 0.4 + rand() * 1.4,
      o: 0.25 + rand() * 0.7,
    }));
  }, [seed, density]);

  const lines = useMemo(() => {
    const picks: [typeof stars[0], typeof stars[0]][] = [];
    for (let i = 0; i < 8; i++) {
      const a = stars[(i * 7) % stars.length];
      const b = stars[(i * 7 + 3) % stars.length];
      if (a && b) picks.push([a, b]);
    }
    return picks;
  }, [stars]);

  return (
    <View style={{ position: 'absolute', inset: 0, opacity: opacity ?? (mode === 'light' ? 0.18 : 0.32) }} pointerEvents="none">
      <Svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
        {lines.map(([a, b], i) => (
          <Line key={`l${i}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={c.ink} strokeWidth={0.08} opacity={0.2} />
        ))}
        {stars.map((st, i) => (
          <Circle key={`s${i}`} cx={st.x} cy={st.y} r={st.r * 0.15} fill={c.ink} opacity={st.o} />
        ))}
      </Svg>
    </View>
  );
};

// Full-screen app backdrop: vertical gradient + soft top glow + stars
export const AppBackground = () => {
  const { c } = useTheme();
  return (
    <View style={{ position: 'absolute', inset: 0, backgroundColor: c.bg0 }} pointerEvents="none">
      <LinearGradient colors={[c.gradTop, c.gradBottom]} style={{ position: 'absolute', inset: 0 }} />
      <Svg width="100%" height="100%" style={{ position: 'absolute', top: 0, left: 0 }}>
        <Defs>
          <RadialGradient id="glow" cx="50%" cy="0%" rx="70%" ry="45%">
            <Stop offset="0%" stopColor={c.glowTop} stopOpacity={1} />
            <Stop offset="60%" stopColor={c.glowTop} stopOpacity={0} />
          </RadialGradient>
        </Defs>
        <Rect x="0" y="0" width="100%" height="100%" fill="url(#glow)" />
      </Svg>
      <ConstellationBG seed={3} density={70} />
    </View>
  );
};
