import { useState } from 'react';
import { View, Text, Pressable } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, Display, Kicker, AppBarIconBtn, Icon } from '@/components/ui';
import WhyToggle from '@/components/WhyToggle';

const TASKS = [
  'Sit by a window for three minutes.',
  'Three slow breaths, eyes closed.',
  "Write one sentence you don't want to say.",
];

export default function RitualDetail() {
  const { p } = useTheme();
  const [checked, setChecked] = useState([true, true, false]);

  return (
    <SubScreen title="Settle the mind" right={<AppBarIconBtn icon="share" />}>
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <Card style={{ padding: 20 }}>
          <Kicker>Day 8 of 21</Kicker>
          <Display size={24} style={{ marginTop: 8 }}>The body remembers before the mind catches up.</Display>
          <View style={{ marginTop: 20, flexDirection: 'row', gap: 3 }}>
            {Array.from({ length: 21 }).map((_, i) => (
              <View key={i} style={{ flex: 1, height: 4, borderRadius: 2, backgroundColor: i < 8 ? p.gold : p.border }} />
            ))}
          </View>
          <WhyToggle sanskrit="चन्द्र-शान्ति · Moon-pacification practice">
            This 21-day cycle works on Moon energy — emotional regulation through small, rhythmic acts. Repetition + breath = recalibration.
          </WhyToggle>
        </Card>

        <Kicker style={{ marginTop: 20, marginBottom: 10 }}>Today · three things</Kicker>
        {TASKS.map((t, i) => (
          <Pressable key={i} onPress={() => setChecked(c => c.map((v, j) => (j === i ? !v : v)))}>
            <Card style={{ padding: 14, marginBottom: 8, flexDirection: 'row', gap: 12, alignItems: 'center', borderColor: checked[i] ? p.gold : p.border }}>
              <View style={{
                width: 22, height: 22, borderRadius: 6, borderWidth: 1,
                borderColor: checked[i] ? p.gold : p.borderStrong,
                backgroundColor: checked[i] ? p.gold : 'transparent',
                alignItems: 'center', justifyContent: 'center',
              }}>{checked[i] && <Icon name="check" size={14} color="#1a1408" />}</View>
              <Text style={{
                fontFamily: fonts.sans, fontSize: 14,
                textDecorationLine: checked[i] ? 'line-through' : 'none',
                color: checked[i] ? p.inkMute : p.ink,
              }}>{t}</Text>
            </Card>
          </Pressable>
        ))}
      </View>
    </SubScreen>
  );
}
