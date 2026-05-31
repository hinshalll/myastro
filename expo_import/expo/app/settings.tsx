import { useState } from 'react';
import { View, Text, Pressable } from 'react-native';
import { router } from 'expo-router';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, CardStrong, Small, Display, PremiumTag, ListRow, Icon } from '@/components/ui';
import type { IconName } from '@/components/Icon';

function Toggle({ on, onPress }: { on: boolean; onPress: () => void }) {
  const { p } = useTheme();
  return (
    <Pressable onPress={onPress}>
      <View style={{ width: 38, height: 22, borderRadius: 11, borderWidth: 1, backgroundColor: on ? p.gold : p.surfaceStrong, borderColor: on ? p.gold : p.borderStrong }}>
        <View style={{ position: 'absolute', top: 1, left: on ? 17 : 1, width: 18, height: 18, borderRadius: 9, backgroundColor: '#fff' }} />
      </View>
    </Pressable>
  );
}

export default function Settings() {
  const { p, name, setTheme } = useTheme();
  const dark = name === 'dark';
  const [notifs, setNotifs] = useState({ daily: true, ritual: true, eclipse: true, weather: false });
  const toggle = (k: keyof typeof notifs) => setNotifs(n => ({ ...n, [k]: !n[k] }));

  return (
    <SubScreen title="Settings">
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <Pressable onPress={() => router.push('/paywall')}>
          <CardStrong style={{ padding: 18, borderColor: p.gold, backgroundColor: p.goldSoft }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <View>
                <PremiumTag />
                <Display size={19} style={{ marginTop: 8 }}>Unlock the full app</Display>
                <Small style={{ marginTop: 4 }}>Unlimited Ask · Patterns · Couple · ₹199/mo</Small>
              </View>
              <Icon name="chevron" size={18} color={p.gold} />
            </View>
          </CardStrong>
        </Pressable>

        <Head title="You" />
        <Card>
          <Row icon="edit" label="Birth details" sub="14 Aug 1995 · 6:45 am · Chennai" />
          <Row icon="globe" label="Language" sub="English · Tamil · हिन्दी soon" />
          <ListRow last>
            <Icon name={dark ? 'moon' : 'sun'} size={16} color={p.gold} />
            <View style={{ flex: 1 }}>
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink }}>Appearance</Text>
              <Small style={{ marginTop: 2 }}>{dark ? 'Dark' : 'Light'}</Small>
            </View>
            <Toggle on={dark} onPress={() => setTheme(dark ? 'light' : 'dark')} />
          </ListRow>
        </Card>

        <Head title="Notifications" />
        <Card>
          {([
            ['daily', 'bell', "Today's Signal", '7:00 am · once'],
            ['ritual', 'leaf', 'Ritual nudge', 'A small daily push'],
            ['eclipse', 'sparkle', 'Eclipse alerts', 'A week ahead'],
            ['weather', 'heart', 'Relationship weather', 'Morning'],
          ] as [keyof typeof notifs, IconName, string, string][]).map(([k, ic, l, s], i, arr) => (
            <ListRow key={k} last={i === arr.length - 1}>
              <Icon name={ic} size={16} color={p.gold} />
              <View style={{ flex: 1 }}>
                <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink }}>{l}</Text>
                <Small style={{ marginTop: 2 }}>{s}</Small>
              </View>
              <Toggle on={notifs[k]} onPress={() => toggle(k)} />
            </ListRow>
          ))}
        </Card>

        <Head title="Privacy & data" />
        <Card>
          <Row icon="lock" label="Cosmic privacy" sub="Who sees what when you connect" chevron />
          <Row icon="sparkle" label="Patterns stay on your phone" sub="Per-user. Never sold." chevron />
          <Row icon="info" label="Delete my data" sub="Anytime · no questions" chevron />
          <Row icon="info" label="About Myastro" sub="v1.0 · made in India" chevron last />
        </Card>
      </View>
    </SubScreen>
  );
}

function Row({ icon, label, sub, chevron, last }: { icon: IconName; label: string; sub?: string; chevron?: boolean; last?: boolean }) {
  const { p } = useTheme();
  return (
    <ListRow last={last}>
      <Icon name={icon} size={16} color={p.gold} />
      <View style={{ flex: 1 }}>
        <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink }}>{label}</Text>
        {!!sub && <Small style={{ marginTop: 2 }}>{sub}</Small>}
      </View>
      {chevron && <Icon name="chevron" size={14} color={p.inkMute} />}
    </ListRow>
  );
}

function Head({ title }: { title: string }) {
  const { p } = useTheme();
  return <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, letterSpacing: 1.8, textTransform: 'uppercase', color: p.inkMute, paddingVertical: 14, paddingTop: 28 }}>{title}</Text>;
}
