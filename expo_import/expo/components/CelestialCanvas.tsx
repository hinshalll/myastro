import { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Svg, { Defs, RadialGradient, Stop, Circle } from 'react-native-svg';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat, withTiming, withSequence, withDelay,
  Easing,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';

import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';

const CANVAS_HEIGHT = 220;
const ORB = 56;
const RINGS = [
  { size: 92,  duration: 14_000, direction: 1, opacity: 0.40, dashed: false, planets: [{ angle: 30 }] },
  { size: 138, duration: 26_000, direction: -1, opacity: 0.26, dashed: true,  planets: [{ angle: -45 }, { angle: 140, slate: true }] },
  { size: 190, duration: 50_000, direction: 1, opacity: 0.18, dashed: false, planets: [{ angle: 90 }, { angle: -120, slate: true }] },
];

// 12 deterministic twinkles
const STARS = [
  { x: 8,  y: 18, delay: 0    },
  { x: 90, y: 24, delay: 400  },
  { x: 18, y: 64, delay: 600  },
  { x: 82, y: 72, delay: 1200 },
  { x: 50, y: 8,  delay: 1600 },
  { x: 6,  y: 80, delay: 800  },
  { x: 94, y: 56, delay: 200  },
  { x: 36, y: 28, delay: 1400 },
  { x: 66, y: 14, delay: 700  },
  { x: 24, y: 88, delay: 1000 },
  { x: 76, y: 88, delay: 1800 },
  { x: 50, y: 92, delay: 300  },
];

export default function CelestialCanvas({
  kicker,
  sanskrit,
}: {
  kicker: string;
  sanskrit?: string;
}) {
  const { p } = useTheme();

  return (
    <View style={styles.canvas}>
      {/* sky wash */}
      <LinearGradient
        pointerEvents="none"
        colors={[p.goldSoft, 'transparent']}
        start={{ x: 0.5, y: 0.5 }}
        end={{ x: 0.5, y: 1 }}
        style={StyleSheet.absoluteFill}
      />

      {/* twinkle stars */}
      {STARS.map((s, i) => (
        <Twinkle key={i} xPct={s.x} yPct={s.y} delay={s.delay} color={p.ink} />
      ))}

      {/* orbit rings */}
      {RINGS.map((r, i) => (
        <Orbit key={i} ring={r} color={p.gold} slate={p.slate} />
      ))}

      {/* central orb */}
      <Orb />

      {/* date kicker */}
      <View style={styles.kickerRow}>
        <Text style={[styles.kicker, { color: p.inkMute }]}>{kicker}</Text>
        {!!sanskrit && (
          <Text numberOfLines={1} style={[styles.deva, { color: p.inkMute }]}>
            {sanskrit}
          </Text>
        )}
      </View>
    </View>
  );
}

// ─── Orb — SVG radial gradient + animated breathing + appear ───
function Orb() {
  const { p, name } = useTheme();
  const scale = useSharedValue(0.6);
  const opacity = useSharedValue(0);

  useEffect(() => {
    opacity.value = withTiming(1, { duration: 700, easing: Easing.bezier(0.22, 0.61, 0.36, 1) });
    // appear, then keep breathing forever
    scale.value = withSequence(
      withTiming(1, { duration: 900, easing: Easing.bezier(0.22, 0.61, 0.36, 1) }),
      withRepeat(
        withSequence(
          withTiming(1.025, { duration: 4000, easing: Easing.inOut(Easing.sin) }),
          withTiming(1,     { duration: 4000, easing: Easing.inOut(Easing.sin) }),
        ),
        -1, false,
      ),
    );
  }, []);

  const aStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  const lightOrb = name === 'light';
  return (
    <Animated.View style={[styles.orbWrap, aStyle]}>
      <View style={[styles.orbGlow, { shadowColor: p.gold }]} />
      <Svg width={ORB} height={ORB} viewBox="0 0 100 100">
        <Defs>
          <RadialGradient id="orb" cx="36%" cy="30%" r="70%">
            <Stop offset="0%"  stopColor={lightOrb ? '#f6e2b3' : 'rgba(255,240,210,1)'} />
            <Stop offset="32%" stopColor={p.gold} />
            <Stop offset="74%" stopColor={lightOrb ? '#6b4912' : '#5a3f10'} />
            <Stop offset="100%" stopColor={lightOrb ? '#6b4912' : '#1a1004'} />
          </RadialGradient>
        </Defs>
        <Circle cx="50" cy="50" r="50" fill="url(#orb)" />
      </Svg>
    </Animated.View>
  );
}

// ─── Orbit ring — rotates a wrapper; planet sits on the right edge ───
function Orbit({ ring, color, slate }: {
  ring: typeof RINGS[number];
  color: string;
  slate: string;
}) {
  const rot = useSharedValue(0);
  useEffect(() => {
    rot.value = withRepeat(
      withTiming(360 * ring.direction, { duration: ring.duration, easing: Easing.linear }),
      -1, false,
    );
  }, []);

  const a = useAnimatedStyle(() => ({
    transform: [{ rotate: `${rot.value}deg` }],
  }));

  return (
    <Animated.View
      pointerEvents="none"
      style={[
        styles.orbitWrap,
        {
          width: ring.size,
          height: ring.size,
          marginLeft: -ring.size / 2,
          marginTop:  -ring.size / 2,
        },
        a,
      ]}
    >
      <View
        style={[
          styles.ring,
          {
            borderColor: color,
            opacity: ring.opacity,
            borderStyle: ring.dashed ? 'dashed' : 'solid',
          },
        ]}
      />
      {ring.planets.map((pl, i) => {
        // place planet on the ring edge at given angle
        const rad = (pl.angle * Math.PI) / 180;
        const x = Math.cos(rad) * (ring.size / 2);
        const y = Math.sin(rad) * (ring.size / 2);
        return (
          <View
            key={i}
            style={[
              styles.planet,
              {
                backgroundColor: pl.slate ? slate : color,
                shadowColor: pl.slate ? slate : color,
                left: ring.size / 2 + x - 4,
                top:  ring.size / 2 + y - 4,
              },
            ]}
          />
        );
      })}
    </Animated.View>
  );
}

// ─── Star twinkle ───
function Twinkle({ xPct, yPct, delay, color }: { xPct: number; yPct: number; delay: number; color: string }) {
  const op = useSharedValue(0.2);
  useEffect(() => {
    op.value = withDelay(
      delay,
      withRepeat(
        withSequence(
          withTiming(0.85, { duration: 1800, easing: Easing.inOut(Easing.sin) }),
          withTiming(0.20, { duration: 1800, easing: Easing.inOut(Easing.sin) }),
        ),
        -1, false,
      ),
    );
  }, []);
  const a = useAnimatedStyle(() => ({ opacity: op.value }));
  return (
    <Animated.View
      pointerEvents="none"
      style={[
        styles.twinkle,
        {
          left: `${xPct}%`,
          top:  `${yPct}%`,
          backgroundColor: color,
        },
        a,
      ]}
    />
  );
}

const styles = StyleSheet.create({
  canvas: {
    height: CANVAS_HEIGHT,
    position: 'relative',
    overflow: 'hidden',
    justifyContent: 'center',
    alignItems: 'center',
  },
  kickerRow: {
    position: 'absolute',
    left: 22, right: 22, top: 4,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  kicker: {
    fontFamily: fonts.sansMedium,
    fontSize: 10,
    letterSpacing: 2.2,
    textTransform: 'uppercase',
  },
  deva: {
    fontFamily: fonts.deva,
    fontSize: 10,
    maxWidth: 200,
  },
  orbWrap: {
    width: ORB,
    height: ORB,
    alignItems: 'center',
    justifyContent: 'center',
  },
  orbGlow: {
    position: 'absolute',
    width: ORB,
    height: ORB,
    borderRadius: ORB / 2,
    shadowOpacity: 0.7,
    shadowOffset: { width: 0, height: 0 },
    shadowRadius: 22,
    elevation: 8,
  },
  orbitWrap: {
    position: 'absolute',
    left: '50%',
    top: '50%',
    alignItems: 'center',
    justifyContent: 'center',
  },
  ring: {
    ...StyleSheet.absoluteFillObject,
    borderWidth: 1,
    borderRadius: 1000,
  },
  planet: {
    position: 'absolute',
    width: 8, height: 8, borderRadius: 4,
    shadowOpacity: 0.6,
    shadowOffset: { width: 0, height: 0 },
    shadowRadius: 6,
    elevation: 4,
  },
  twinkle: {
    position: 'absolute',
    width: 1.6, height: 1.6, borderRadius: 1,
  },
});
