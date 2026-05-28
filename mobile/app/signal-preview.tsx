import { View, Text } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, Body, Small, Kicker, Display, ListRow, Icon } from '@/components/ui';
import ConstellationBG from '@/components/ConstellationBG';
import type { IconName } from '@/components/Icon';

const ALERTS: [string, string, IconName][] = [
  ['Eclipse · 6 days ahead', 'Sutak begins 4:32 am', 'bell'],
  ['"This happened before"', 'Premium · proactive memory', 'sparkle'],
  ['Birth-time nudge', "If you added 'later'", 'edit'],
];

export default function SignalPreview() {
  const { p } = useTheme();
  return (
    <SubScreen title="Today's Signal · preview">
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <Body>This is the one notification you'll get each morning. No spam — that's the deal.</Body>

        <Kicker style={{ marginTop: 24, marginBottom: 10 }}>Lock screen · 7:00 am</Kicker>

        <View style={{ borderRadius: 24, padding: 24, overflow: 'hidden', borderWidth: 1, borderColor: p.border, backgroundColor: '#1a1230' }}>
          <ConstellationBG seed={5} density={40} opacity={0.4} color="#ece6d4" />
          <View style={{ alignItems: 'center' }}>
            <Text style={{ fontFamily: fonts.sansMedium, fontSize: 10, letterSpacing: 2.2, color: 'rgba(236,230,212,0.65)' }}>FRI · MAY 25</Text>
            <Text style={{ fontFamily: fonts.sansMedium, fontSize: 56, color: 'rgba(236,230,212,0.95)', lineHeight: 60, marginTop: 4 }}>7:00</Text>
          </View>

          <View style={{ marginTop: 50, borderRadius: 18, padding: 14, flexDirection: 'row', gap: 12, backgroundColor: 'rgba(10,8,28,0.7)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.10)' }}>
            <View style={{ width: 32, height: 32, borderRadius: 8, backgroundColor: p.gold, alignItems: 'center', justifyContent: 'center' }}>
              <Icon name="logo" size={20} color="#1a1408" />
            </View>
            <View style={{ flex: 1 }}>
              <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                <Text style={{ fontFamily: fonts.sansMedium, fontSize: 10, letterSpacing: 2.2, color: 'rgba(236,230,212,0.7)' }}>MYASTRO</Text>
                <Text style={{ fontFamily: fonts.sansMedium, fontSize: 10, letterSpacing: 2.2, color: 'rgba(236,230,212,0.5)' }}>now</Text>
              </View>
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, lineHeight: 19, color: 'rgba(236,230,212,0.95)', marginTop: 6 }}>
                Magnetic day. Send the half-finished idea — don't reply when annoyed.
              </Text>
            </View>
          </View>
        </View>

        <Kicker style={{ marginTop: 24, marginBottom: 10 }}>Other alerts (optional)</Kicker>
        <Card>
          {ALERTS.map(([t, s, ic], i) => (
            <ListRow key={i} last={i === ALERTS.length - 1}>
              <Icon name={ic} size={16} color={p.gold} />
              <View style={{ flex: 1 }}>
                <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink }}>{t}</Text>
                <Small style={{ marginTop: 2 }}>{s}</Small>
              </View>
            </ListRow>
          ))}
        </Card>
      </View>
    </SubScreen>
  );
}
