import { useEffect, useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Animated, { useSharedValue, useAnimatedStyle, withTiming, Easing } from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';

import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, CardStrong, Body, Small, Kicker, Display, Btn, PremiumTag, ListRow, Icon } from '@/components/ui';
import WhyToggle from '@/components/WhyToggle';
import type { IconName } from '@/components/Icon';

type Stage = 'frame' | 'scanning' | 'result';

const NOTICED: [string, string][] = [
  ['Career line', 'Strong, late-bloomer pattern.'],
  ['Heart line', 'Deep but private — you guard well.'],
  ['Travel marks', 'Two distant moves are in here.'],
];

export default function ScanScreen({
  title, prompt, icon, route,
}: { title: string; prompt: string; icon: IconName; route: string }) {
  const { p } = useTheme();
  const [stage, setStage] = useState<Stage>('frame');
  const scan = useSharedValue(0);

  useEffect(() => {
    if (stage === 'scanning') {
      scan.value = 0;
      scan.value = withTiming(1, { duration: 2400, easing: Easing.inOut(Easing.quad) });
      const t = setTimeout(() => setStage('result'), 2400);
      return () => clearTimeout(t);
    }
  }, [stage]);

  const lineStyle = useAnimatedStyle(() => ({ top: `${scan.value * 100}%` }));

  return (
    <SubScreen title={title}>
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        {stage !== 'result' ? (
          <>
            <View style={{ borderRadius: 20, aspectRatio: 3 / 4, overflow: 'hidden', borderWidth: 1, borderColor: p.border, backgroundColor: '#14101e', alignItems: 'center', justifyContent: 'center' }}>
              <View style={[styles.slot, { borderColor: p.borderStrong }]}>
                <Icon name={icon} size={60} color={p.gold} />
                <Text style={{ fontFamily: fonts.mono, fontSize: 10, letterSpacing: 1, textTransform: 'uppercase', color: p.inkFaint, marginTop: 14 }}>camera · {route}</Text>
              </View>
              {stage === 'scanning' && (
                <Animated.View style={[{ position: 'absolute', left: 0, right: 0, height: 2 }, lineStyle]}>
                  <LinearGradient colors={['transparent', p.gold, 'transparent']} start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }} style={{ flex: 1 }} />
                </Animated.View>
              )}
            </View>

            <Body style={{ textAlign: 'center', marginVertical: 18 }}>{prompt}</Body>
            <Btn
              label={stage === 'scanning' ? 'Reading…' : 'Take photo'}
              variant="primary" size="lg" block
              onPress={() => stage === 'frame' && setStage('scanning')}
              style={{ opacity: stage === 'scanning' ? 0.6 : 1 }}
            />
            <Small style={{ textAlign: 'center', marginTop: 10 }}>1 free this month · then ₹99 deep report</Small>
          </>
        ) : (
          <>
            <CardStrong style={{ padding: 22 }}>
              <Kicker>What we saw</Kicker>
              <Display size={26} style={{ marginTop: 8 }}>A long line of quiet endurance.</Display>
              <Body style={{ marginTop: 12 }}>
                You don't burn out the way most people do. The line says: you work in chapters, and the next one is opening now.
              </Body>
              <WhyToggle sanskrit="हस्तरेखा · आयु-रेखा गभीरा">
                The life-line crosses a deep heart-line at the mid-point — a classic marker of mid-life pivots that feel chosen, not forced.
              </WhyToggle>
            </CardStrong>

            <Head title="Three things we noticed" />
            <Card>
              {NOTICED.map(([l, v], i) => (
                <ListRow key={l} last={i === NOTICED.length - 1}>
                  <Icon name="sparkle" size={14} color={p.gold} />
                  <View style={{ flex: 1 }}>
                    <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink }}>{l}</Text>
                    <Small style={{ marginTop: 2 }}>{v}</Small>
                  </View>
                </ListRow>
              ))}
            </Card>

            <Card style={{ marginTop: 14, padding: 16, borderColor: p.gold }}>
              <PremiumTag />
              <Display size={17} style={{ marginTop: 8 }}>Full deep report · 14 lines decoded · ₹99</Display>
              <Btn label="Unlock deep report" variant="gold" size="sm" style={{ marginTop: 12, alignSelf: 'flex-start' }} />
            </Card>

            <Btn label="Scan again" variant="ghost" block style={{ marginTop: 12 }} onPress={() => setStage('frame')} />
          </>
        )}
      </View>
    </SubScreen>
  );
}

function Head({ title }: { title: string }) {
  const { p } = useTheme();
  return <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, letterSpacing: 1.8, textTransform: 'uppercase', color: p.inkMute, paddingVertical: 14, paddingTop: 28 }}>{title}</Text>;
}

const styles = StyleSheet.create({
  slot: {
    position: 'absolute', top: 32, left: 32, right: 32, bottom: 32,
    borderWidth: 1, borderStyle: 'dashed', borderRadius: 12,
    alignItems: 'center', justifyContent: 'center',
  },
});
