// Myastro — faint constellation backdrop (deterministic stars + a few links).
// Ported from the prototype's ConstellationBG. Sits behind screen content.

import { useMemo } from 'react';
import { StyleSheet, ViewStyle } from 'react-native';
import Svg, { Circle, Line } from 'react-native-svg';
import { useTheme } from '@/constants/ThemeContext';

export default function ConstellationBG({
  seed = 3,
  density = 70,
  opacity,
  color,
  style,
}: {
  seed?: number;
  density?: number;
  opacity?: number;
  color?: string;
  style?: ViewStyle;
}) {
  const { p, name } = useTheme();

  const stars = useMemo(() => {
    let s = seed * 9301 + 49297;
    const rand = () => {
      s = (s * 9301 + 49297) % 233280;
      return s / 233280;
    };
    return Array.from({ length: density }, () => ({
      x: rand() * 100,
      y: rand() * 100,
      r: 0.4 + rand() * 1.4,
      o: 0.25 + rand() * 0.7,
    }));
  }, [seed, density]);

  const lines = useMemo(() => {
    const picks: [typeof stars[number], typeof stars[number]][] = [];
    for (let i = 0; i < 8; i++) {
      const a = stars[(i * 7) % stars.length];
      const b = stars[(i * 7 + 3) % stars.length];
      if (a && b) picks.push([a, b]);
    }
    return picks;
  }, [stars]);

  const c = color ?? p.ink;
  const baseOpacity = opacity ?? (name === 'light' ? 0.18 : 0.32);

  return (
    <Svg
      pointerEvents="none"
      style={[StyleSheet.absoluteFill, { opacity: baseOpacity }, style]}
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
    >
      {lines.map(([a, b], i) => (
        <Line key={`l${i}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={c} strokeWidth={0.08} opacity={0.2} />
      ))}
      {stars.map((st, i) => (
        <Circle key={`s${i}`} cx={st.x} cy={st.y} r={st.r * 0.15} fill={c} opacity={st.o} />
      ))}
    </Svg>
  );
}
