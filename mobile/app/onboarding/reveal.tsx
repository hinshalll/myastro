import { useEffect, useState } from 'react';
import { View, Text } from 'react-native';
import { router } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Svg, { Defs, RadialGradient, Stop, Circle } from 'react-native-svg';
import Animated, {
  useSharedValue, useAnimatedStyle, withTiming, withRepeat, FadeInDown, Easing,
} from 'react-native-reanimated';

import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import ConstellationBG from '@/components/ConstellationBG';
import { Kicker, Display, Body, Btn } from '@/components/ui';

export default function Reveal() {
  const { p } = useTheme();
  const insets = useSafeAreaInsets();
  const [stage, setStage] = useState(0);

  const scale = useSharedValue(0.6);
  const spin = useSharedValue(0);

  useEffect(() => {
    scale.value = withTiming(1, { duration: 1200, easing: Easing.bezier(0.2, 0.7, 0.2, 1) });
    spin.value = withRepeat(withTiming(360, { duration: 30000, easing: Easing.linear }), -1, false);
    const timers = [
      setTimeout(() => setStage(1), 700),
      setTimeout(() => setStage(2), 1800),
      setTimeout(() => setStage(3), 3000),
      setTimeout(() => setStage(4), 4200),
    ];
    return () => timers.forEach(clearTimeout);
  }, []);

  const orbStyle = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));
  const ringStyle = useAnimatedStyle(() => ({ transform: [{ rotate: `${spin.value}deg` }] }));

  return (
    <View style={{ flex: 1, backgroundColor: p.bg0 }}>
      <ConstellationBG />
      <View style={{ flex: 1, paddingHorizontal: 28, paddingTop: insets.top + 48 }}>
        <View style={{ width: 100, height: 100, alignSelf: 'center', marginTop: 20, alignItems: 'center', justifyContent: 'center' }}>
          <Animated.View style={[{ position: 'absolute', width: 100, height: 100 }, orbStyle]}>
            <Svg width={100} height={100} viewBox="0 0 100 100">
              <Defs>
                <RadialGradient id="rev" cx="38%" cy="32%" r="70%">
                  <Stop offset="0%" stopColor="#e6c373" />
                  <Stop offset="45%" stopColor="#a07c2c" />
                  <Stop offset="90%" stopColor="#4a3208" />
                </RadialGradient>
              </Defs>
              <Circle cx="50" cy="50" r="50" fill="url(#rev)" />
            </Svg>
          </Animated.View>
          {stage >= 1 && (
            <Animated.View style={[{
              position: 'absolute', width: 144, height: 144, borderRadius: 72,
              borderWidth: 1, borderColor: p.gold, opacity: 0.3,
            }, ringStyle]} />
          )}
        </View>

        <View style={{ marginTop: 38, minHeight: 260 }}>
          {stage >= 1 && (
            <Animated.View entering={FadeInDown.duration(450)}>
              <Kicker style={{ marginBottom: 14 }}>Here's who you are</Kicker>
            </Animated.View>
          )}
          {stage >= 2 && (
            <Animated.View entering={FadeInDown.duration(450)}>
              <Display size={42} style={{ lineHeight: 44, letterSpacing: -0.8 }}>
                A quiet flame{'\n'}with a long memory.
              </Display>
            </Animated.View>
          )}
          {stage >= 3 && (
            <Animated.View entering={FadeInDown.duration(450)}>
              <Body style={{ marginTop: 16, fontSize: 15, lineHeight: 23 }}>
                You move slowly on purpose. People who know you, trust you completely. Today you'll feel the pull of an old idea — let it visit, don't move in yet.
              </Body>
            </Animated.View>
          )}
          {stage >= 4 && (
            <Animated.View entering={FadeInDown.duration(450)} style={{
              marginTop: 22, paddingVertical: 14, flexDirection: 'row', gap: 24,
              borderTopWidth: 1, borderBottomWidth: 1, borderColor: p.hairline,
            }}>
              {[['Element', 'Fire'], ['Energy', 'Slow build'], ['Path', 'Builder, late']].map(([l, v]) => (
                <View key={l}>
                  <Kicker style={{ marginBottom: 4 }}>{l}</Kicker>
                  <Text style={{ fontFamily: fonts.sansMedium, fontSize: 17, color: p.gold }}>{v}</Text>
                </View>
              ))}
            </Animated.View>
          )}
        </View>
      </View>

      <View style={{ paddingHorizontal: 22, paddingBottom: insets.bottom + 24, opacity: stage >= 4 ? 1 : 0 }}>
        <Btn label="See today →" variant="primary" size="lg" block onPress={() => router.replace('/today')} />
      </View>
    </View>
  );
}
