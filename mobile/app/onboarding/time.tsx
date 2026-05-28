import { useState } from 'react';
import { View, Pressable, TextInput, Text } from 'react-native';
import { router } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { useTheme } from '@/constants/ThemeContext';
import { useApp, Precision } from '@/constants/AppContext';
import { fonts } from '@/constants/theme';
import ConstellationBG from '@/components/ConstellationBG';
import { Kicker, H1, Body, Small, Display, Btn, Card, Icon } from '@/components/ui';

type Opt = { id: string; title: string; sub: string; unlocks: string; tier: Precision };
const OPTIONS: Opt[] = [
  { id: 'know',  title: 'I know it.', sub: 'To the minute, ideally — from your birth certificate or family.',
    unlocks: 'Everything unlocks. The deepest readings (D9 Navamsa, life chapters) need this.', tier: 'exact' },
  { id: 'later', title: "I'll add it later.", sub: "We'll send one gentle reminder. No nagging.",
    unlocks: 'Works in approximate mode until you add it. Some divisional charts will be flagged.', tier: 'approximate' },
  { id: 'none',  title: "I don't know it.", sub: "About 30% of people don't — and Vedic astrology has a beautiful answer for you.",
    unlocks: 'Switches to Moon-chart mode. Daily forecasts, patterns, relationships — all work.', tier: 'unknown' },
];

export default function TimeStep() {
  const { p } = useTheme();
  const { setPrecision } = useApp();
  const insets = useSafeAreaInsets();
  const [choice, setChoice] = useState<string | null>(null);
  const [hour, setHour] = useState('06');
  const [min, setMin] = useState('45');
  const [exact, setExact] = useState(false);

  return (
    <View style={{ flex: 1, backgroundColor: p.bg0 }}>
      <ConstellationBG />
      <View style={{ paddingTop: insets.top + 8, paddingHorizontal: 16 }}>
        <Pressable onPress={() => router.back()} hitSlop={10} style={{ width: 36, height: 36, borderRadius: 18, borderWidth: 1, borderColor: p.border, alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="back" size={18} />
        </Pressable>
      </View>

      <View style={{ flex: 1 }}>
        <View style={{ flex: 1, paddingHorizontal: 28, paddingTop: 24 }}>
          <Kicker style={{ marginBottom: 14 }}>Step 2 · 3</Kicker>
          <H1>The moment you arrived.</H1>
          <Body style={{ marginTop: 8 }}>A birth time unlocks deeper readings. No pressure — we make it work either way.</Body>

          <View style={{ marginTop: 22, gap: 10 }}>
            {OPTIONS.map(o => {
              const on = choice === o.id;
              return (
                <Pressable
                  key={o.id}
                  onPress={() => { setChoice(o.id); setPrecision(o.tier); }}
                  style={{
                    padding: 16, borderRadius: 16, borderWidth: 1,
                    borderColor: on ? p.gold : p.border,
                    backgroundColor: on ? p.goldSoft : p.surface,
                  }}
                >
                  <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Display size={19}>{o.title}</Display>
                    {on && <Icon name="check" size={16} color={p.gold} />}
                  </View>
                  <Body style={{ marginTop: 6 }}>{o.sub}</Body>
                  {on && (
                    <Text style={{ marginTop: 10, paddingTop: 10, borderTopWidth: 1, borderTopColor: p.gold, fontFamily: fonts.sans, fontSize: 12, lineHeight: 18, color: p.gold }}>
                      {o.unlocks}
                    </Text>
                  )}
                </Pressable>
              );
            })}
          </View>

          {choice === 'know' && (
            <Card style={{ marginTop: 20, padding: 20 }}>
              <Kicker style={{ marginBottom: 14 }}>Your birth time</Kicker>
              <View style={{ flexDirection: 'row', justifyContent: 'center', alignItems: 'baseline', gap: 6 }}>
                <TextInput value={hour} onChangeText={setHour} maxLength={2} keyboardType="number-pad"
                  style={{ width: 76, textAlign: 'right', fontFamily: fonts.sansMedium, fontSize: 56, color: p.ink }} />
                <Text style={{ fontFamily: fonts.sansMedium, fontSize: 56, color: p.inkMute }}>:</Text>
                <TextInput value={min} onChangeText={setMin} maxLength={2} keyboardType="number-pad"
                  style={{ width: 76, textAlign: 'left', fontFamily: fonts.sansMedium, fontSize: 56, color: p.ink }} />
              </View>
              <Small style={{ textAlign: 'center', marginTop: 4 }}>tap to edit · 24-hour</Small>

              <Pressable onPress={() => setExact(e => !e)} style={{ flexDirection: 'row', alignItems: 'center', gap: 12, marginTop: 16 }}>
                <View style={{
                  width: 22, height: 22, borderRadius: 6, borderWidth: 1,
                  borderColor: exact ? p.gold : p.borderStrong, backgroundColor: exact ? p.gold : 'transparent',
                  alignItems: 'center', justifyContent: 'center',
                }}>{exact && <Icon name="check" size={13} color="#1a1408" />}</View>
                <View style={{ flex: 1 }}>
                  <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink }}>This is the exact time</Text>
                  <Small>Unlocks the deepest divisional readings (Navamsa · D60)</Small>
                </View>
              </Pressable>
            </Card>
          )}
        </View>

        <View style={{ paddingHorizontal: 22, paddingTop: 14, paddingBottom: insets.bottom + 24 }}>
          <Btn label="Continue →" variant="primary" size="lg" block
            onPress={() => choice && router.push('/onboarding/reveal')}
            style={{ opacity: choice ? 1 : 0.4 }} />
        </View>
      </View>
    </View>
  );
}
