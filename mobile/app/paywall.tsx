import { useState } from 'react';
import { View, Text, Pressable } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, Body, Small, Kicker, Mono, Display, Btn, PremiumTag, ListRow, Icon } from '@/components/ui';
import type { IconName } from '@/components/Icon';

const PLANS = [
  { id: 'weekly', label: 'Weekly', price: 49, per: 'week', note: '' },
  { id: 'monthly', label: 'Monthly', price: 199, per: 'month', note: '' },
  { id: 'annual', label: 'Annual', price: 999, per: 'year', note: 'Save 58% · ₹83/mo', popular: true },
];

const FEATURES: [string, string, IconName][] = [
  ['Unlimited Ask', 'No more 3/day cap', 'ask'],
  ['Your Patterns', 'The patterns only you can see', 'sparkle'],
  ['This happened before', 'Proactive memory · before it hits', 'moon'],
  ['Full Life Reading', 'The flagship 3-agent deep read', 'star'],
  ['Couple & Family vibes', 'Live two-way for friends', 'heart'],
  ['Your Purpose', 'Soul + career blueprint', 'flame'],
  ['Event timing planner', 'Best dates for big choices', 'calendar'],
  ['Camera readings, full', 'Palm + face deep reports', 'hand'],
];

const ALACARTE: [string, string][] = [
  ['Full Life Reading', '₹199'],
  ['Marriage / compatibility', '₹149'],
  ['Deep palm or face report', '₹99'],
];

export default function Paywall() {
  const { p } = useTheme();
  const [plan, setPlan] = useState('annual');

  return (
    <SubScreen title="">
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <Kicker color={p.gold} style={{ marginBottom: 8 }}>Myastro+</Kicker>
        <Display size={38} style={{ letterSpacing: -0.8 }}>The whole map{'\n'}of your life.</Display>
        <Body style={{ marginTop: 12 }}>Built for people who actually look at it. Cancel anytime. ₹ in India · same plan everywhere.</Body>

        <View style={{ marginTop: 24, gap: 8 }}>
          {PLANS.map(pl => {
            const on = plan === pl.id;
            return (
              <Pressable key={pl.id} onPress={() => setPlan(pl.id)}>
                <Card style={{ padding: 16, flexDirection: 'row', alignItems: 'center', gap: 14, borderColor: on ? p.gold : p.border, backgroundColor: on ? p.goldSoft : p.surface }}>
                  <View style={{ width: 22, height: 22, borderRadius: 11, borderWidth: 1, borderColor: on ? p.gold : p.borderStrong, backgroundColor: on ? p.gold : 'transparent', alignItems: 'center', justifyContent: 'center' }}>
                    {on && <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: '#1a1408' }} />}
                  </View>
                  <View style={{ flex: 1 }}>
                    <View style={{ flexDirection: 'row', gap: 8, alignItems: 'center' }}>
                      <Text style={{ fontFamily: fonts.sansMedium, fontSize: 16, color: p.ink }}>{pl.label}</Text>
                      {pl.popular && <PremiumTag label="popular" />}
                    </View>
                    {!!pl.note && <Small color={p.gold} style={{ marginTop: 2 }}>{pl.note}</Small>}
                  </View>
                  <View style={{ flexDirection: 'row', alignItems: 'baseline', gap: 2 }}>
                    <Text style={{ fontFamily: fonts.sansMedium, fontSize: 16, color: p.inkSoft }}>₹</Text>
                    <Text style={{ fontFamily: fonts.sansMedium, fontSize: 28, color: p.ink }}>{pl.price}</Text>
                    <Text style={{ fontFamily: fonts.sans, fontSize: 11, color: p.inkMute }}>/{pl.per}</Text>
                  </View>
                </Card>
              </Pressable>
            );
          })}
        </View>

        <Btn label="Begin Myastro+ →" variant="gold" size="lg" block style={{ marginTop: 18 }} />
        <Small style={{ textAlign: 'center', marginTop: 10 }}>Cancel in Settings, anytime. 7-day full refund.</Small>

        <Asterism />

        <Kicker style={{ marginBottom: 12 }}>What unlocks</Kicker>
        <Card>
          {FEATURES.map(([t, s, ic], i) => (
            <ListRow key={t} last={i === FEATURES.length - 1}>
              <View style={{ width: 32, height: 32, borderRadius: 10, backgroundColor: p.goldSoft, alignItems: 'center', justifyContent: 'center' }}>
                <Icon name={ic} size={16} color={p.gold} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink }}>{t}</Text>
                <Small style={{ marginTop: 2 }}>{s}</Small>
              </View>
              <Icon name="check" size={14} color={p.gold} />
            </ListRow>
          ))}
        </Card>

        <Card style={{ marginTop: 14, padding: 16 }}>
          <Display size={18}>"It read me the way one specific friend can — and then went further."</Display>
          <Mono style={{ marginTop: 8 }}>— R., Bangalore</Mono>
        </Card>

        <Asterism />

        <Kicker style={{ marginBottom: 12 }}>Also available, à la carte</Kicker>
        <Card>
          {ALACARTE.map(([t, price], i) => (
            <ListRow key={t} last={i === ALACARTE.length - 1}>
              <Text style={{ flex: 1, fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink }}>{t}</Text>
              <Display size={18}>{price}</Display>
            </ListRow>
          ))}
        </Card>
      </View>
    </SubScreen>
  );
}

function Asterism() {
  const { p } = useTheme();
  return <Text style={{ textAlign: 'center', fontSize: 16, letterSpacing: 12, color: p.inkMute, paddingVertical: 22 }}>✦ · ✦</Text>;
}
