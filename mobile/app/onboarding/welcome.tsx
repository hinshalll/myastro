import { View } from 'react-native';
import { router } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import ConstellationBG from '@/components/ConstellationBG';
import { Display, Body, Small, Btn, Icon } from '@/components/ui';
import { Text } from 'react-native';

const BULLETS = [
  'A daily vibe, in plain English',
  'A "why?" for the curious',
  'Patterns only you can see',
  'Private — your data never sold',
];

export default function Welcome() {
  const { p } = useTheme();
  const insets = useSafeAreaInsets();

  return (
    <View style={{ flex: 1, backgroundColor: p.bg0 }}>
      <ConstellationBG />
      <View style={{ flex: 1, paddingHorizontal: 28, paddingTop: insets.top + 64 }}>
        <Icon name="logo" size={36} color={p.gold} />

        <Display size={52} style={{ marginTop: 50, lineHeight: 53, letterSpacing: -1 }}>
          Astrology{'\n'}that learns you.
        </Display>

        <Body style={{ marginTop: 22, fontSize: 16, lineHeight: 25, maxWidth: 300 }}>
          A quiet, daily companion. No charts to decode. No words you'd have to Google.
        </Body>

        <Text style={{ fontFamily: fonts.deva, fontSize: 15, color: p.inkMute, marginTop: 28 }}>
          अन्तर्ज्ञानम् · the inner knowing
        </Text>

        <View style={{ marginTop: 28, gap: 12 }}>
          {BULLETS.map(t => (
            <View key={t} style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
              <View style={{ width: 4, height: 4, borderRadius: 2, backgroundColor: p.gold }} />
              <Text style={{ fontFamily: fonts.sans, fontSize: 14, color: p.inkSoft }}>{t}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={{ paddingHorizontal: 22, paddingBottom: insets.bottom + 24 }}>
        <Btn label="Begin →" variant="primary" size="lg" block onPress={() => router.push('/onboarding/birth')} />
        <Small style={{ textAlign: 'center', marginTop: 14 }}>About 90 seconds.</Small>
      </View>
    </View>
  );
}
