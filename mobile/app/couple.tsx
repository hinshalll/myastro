import { View, Text } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, CardStrong, Body, Small, Kicker, Mono, Display, ListRow, AppBarIconBtn, Icon } from '@/components/ui';
import type { IconName } from '@/components/Icon';

const PRIVATE: [string, string, IconName][] = [
  ['Shared journal', '12 entries', 'edit'],
  ['Anniversary timing', 'Oct 14 · Best in 3 years', 'heart'],
  ['First-meeting chart', 'Aug 8, 2019', 'sparkle'],
];

export default function Couple() {
  const { p } = useTheme();
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const tension = [0.2, 0.4, 0.15, 0.7, 0.55, 0.1, 0.05];

  return (
    <SubScreen title="You & Maya" right={<AppBarIconBtn icon="settings" />}>
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <CardStrong style={{ padding: 22 }}>
          <Kicker>Shared pulse today</Kicker>
          <Display size={30} style={{ marginTop: 8 }}>You're both softening.</Display>
          <Body style={{ marginTop: 12 }}>Same wavelength all evening. Skip the screens.</Body>
        </CardStrong>

        <Head title="Tension forecast · 7 days" />
        <Card style={{ padding: 20 }}>
          <View style={{ flexDirection: 'row', alignItems: 'flex-end', gap: 8, height: 100 }}>
            {tension.map((t, i) => (
              <View key={i} style={{ flex: 1, alignItems: 'center', gap: 6 }}>
                <View style={{ width: '100%', height: `${t * 80}%`, minHeight: 4, borderRadius: 3, backgroundColor: t > 0.6 ? p.rose : t > 0.3 ? p.gold : p.teal }} />
                <Mono>{days[i]}</Mono>
              </View>
            ))}
          </View>
          <Body style={{ marginTop: 14 }}><Text style={{ color: p.rose, fontFamily: fonts.sansMedium }}>Thu evening</Text> needs softness — postpone the hard talk. Weekend's clear.</Body>
        </Card>

        <Head title="Private to you two" />
        <Card>
          {PRIVATE.map(([l, s, ic], i) => (
            <ListRow key={l} last={i === PRIVATE.length - 1}>
              <Icon name={ic} size={16} color={p.gold} />
              <View style={{ flex: 1 }}>
                <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink }}>{l}</Text>
                <Small style={{ marginTop: 2 }}>{s}</Small>
              </View>
              <Icon name="chevron" size={16} color={p.inkMute} />
            </ListRow>
          ))}
        </Card>
      </View>
    </SubScreen>
  );
}

function Head({ title }: { title: string }) {
  const { p } = useTheme();
  return <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, letterSpacing: 1.8, textTransform: 'uppercase', color: p.inkMute, paddingVertical: 14, paddingTop: 28 }}>{title}</Text>;
}
