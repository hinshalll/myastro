import { View, Text, Pressable } from 'react-native';
import { router } from 'expo-router';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, CardStrong, H2, Body, Small, Kicker, Mono, Display, Icon } from '@/components/ui';
import type { IconName } from '@/components/Icon';

const JOURNEYS: { title: string; sub: string; days: number; icon: IconName }[] = [
  { title: 'Open the heart', sub: 'Venus · soften',   days: 40, icon: 'heart' },
  { title: 'Money flow',     sub: 'Jupiter · expansion', days: 21, icon: 'sparkle' },
  { title: 'Old grief',      sub: 'Moon · release',    days: 40, icon: 'moon' },
  { title: 'Health & body',  sub: 'Sun · vitality',    days: 21, icon: 'sun' },
  { title: 'Speak the truth', sub: 'Mars · courage',   days: 21, icon: 'flame' },
];

export default function Rituals() {
  const { p } = useTheme();
  return (
    <SubScreen title="Rituals">
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <H2 style={{ marginBottom: 4 }}>Small daily things.</H2>
        <Body style={{ marginBottom: 20 }}>Choose one. Show up for it.</Body>

        <Kicker style={{ marginBottom: 10 }}>In progress</Kicker>
        <Pressable onPress={() => router.push('/ritual-detail')}>
          <CardStrong style={{ padding: 18, marginBottom: 16 }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 14 }}>
              <View style={{ width: 44, height: 44, borderRadius: 12, backgroundColor: p.goldSoft, borderWidth: 1, borderColor: p.gold, alignItems: 'center', justifyContent: 'center' }}>
                <Icon name="leaf" size={22} color={p.gold} />
              </View>
              <View style={{ flex: 1 }}>
                <Display size={19}>Settle the mind</Display>
                <Mono color={p.gold} style={{ marginTop: 4 }}>Day 8 of 21</Mono>
              </View>
            </View>
            <View style={{ marginTop: 14, height: 3, borderRadius: 2, backgroundColor: p.border }}>
              <View style={{ width: `${(8 / 21) * 100}%`, height: '100%', backgroundColor: p.gold, borderRadius: 2 }} />
            </View>
          </CardStrong>
        </Pressable>

        <Kicker style={{ marginBottom: 10 }}>Begin a journey</Kicker>
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 10 }}>
          {JOURNEYS.map(j => (
            <Card key={j.title} style={{ width: '47.5%', padding: 14 }}>
              <View style={{ width: 32, height: 32, borderRadius: 10, backgroundColor: p.surfaceStrong, alignItems: 'center', justifyContent: 'center' }}>
                <Icon name={j.icon} size={16} color={p.gold} />
              </View>
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink, marginTop: 10 }}>{j.title}</Text>
              <Small style={{ marginTop: 2 }}>{j.sub}</Small>
              <Mono style={{ marginTop: 8 }}>{j.days} days</Mono>
            </Card>
          ))}
        </View>

        <Pressable onPress={() => router.push('/mala')}>
          <Card style={{ padding: 16, marginTop: 16, flexDirection: 'row', gap: 12, alignItems: 'center' }}>
            <View style={{ width: 36, height: 36, borderRadius: 10, backgroundColor: p.surfaceStrong, alignItems: 'center', justifyContent: 'center' }}>
              <Icon name="sparkle" size={18} color={p.gold} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink }}>Mala · bead counter</Text>
              <Small>108 taps · with haptics</Small>
            </View>
            <Icon name="chevron" size={18} color={p.inkMute} />
          </Card>
        </Pressable>
      </View>
    </SubScreen>
  );
}
