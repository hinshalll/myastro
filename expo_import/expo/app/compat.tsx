import { View, Text } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, CardStrong, Body, Small, Kicker, Mono, Display, Avatar, Btn, ListRow, Icon } from '@/components/ui';
import WhyToggle from '@/components/WhyToggle';

const DIMS: [string, number, string][] = [
  ['Mind & talk', 0.9, "You finish each other's sentences before they start."],
  ['Care & comfort', 0.85, 'You both default to acts of service. Quiet, but powerful.'],
  ['Spark & touch', 0.7, 'Hot when you make space for it — get out of the routine.'],
  ['Money & home', 0.6, 'Different instincts. Talk it out before you act.'],
  ['Long-term path', 0.95, 'Aligned on the big questions. Rare.'],
];

export default function Compat() {
  const { p } = useTheme();
  return (
    <SubScreen title="Match two people">
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
          <Card style={{ flex: 1, padding: 14, alignItems: 'center' }}>
            <Avatar initials="Y" style={{ marginBottom: 8 }} />
            <Text style={{ fontFamily: fonts.sansMedium, fontSize: 13, color: p.ink }}>You</Text>
          </Card>
          <Icon name="sparkle" size={18} color={p.gold} />
          <Card style={{ flex: 1, padding: 14, alignItems: 'center' }}>
            <Avatar initials="M" style={{ marginBottom: 8 }} />
            <Text style={{ fontFamily: fonts.sansMedium, fontSize: 13, color: p.ink }}>Maya</Text>
          </Card>
        </View>

        <CardStrong style={{ padding: 22, marginTop: 16, alignItems: 'center' }}>
          <Kicker>Ashta Koota · 32-point match</Kicker>
          <Text style={{ fontFamily: fonts.sansMedium, fontSize: 64, lineHeight: 66, color: p.gold, letterSpacing: -2, marginTop: 8 }}>
            27<Text style={{ fontSize: 28, color: p.inkMute }}>/32</Text>
          </Text>
          <Display size={20} style={{ marginTop: 12, textAlign: 'center' }}>Built to last. Same direction, different speeds.</Display>
          <View style={{ alignSelf: 'stretch' }}>
            <WhyToggle sanskrit="अष्ट-कूट · ३२-गुण">
              27 / 32 points across 8 dimensions of compatibility — mind, body, family alignment, fertility, temperament, energy, longevity and friendship.
            </WhyToggle>
          </View>
        </CardStrong>

        <Head title="Where you click" />
        <Card>
          {DIMS.map(([label, v, note], i) => (
            <ListRow key={label} last={i === DIMS.length - 1}>
              <View style={{ flex: 1 }}>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                  <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink }}>{label}</Text>
                  <Mono color={p.gold}>{Math.round(v * 100)}</Mono>
                </View>
                <View style={{ marginTop: 6, height: 3, borderRadius: 2, backgroundColor: p.border, overflow: 'hidden' }}>
                  <View style={{ width: `${v * 100}%`, height: '100%', backgroundColor: p.gold }} />
                </View>
                <Small style={{ marginTop: 6 }}>{note}</Small>
              </View>
            </ListRow>
          ))}
        </Card>

        <Head title="If you got married" />
        <Card style={{ padding: 16 }}>
          <Body>27 / 32 is rare. Two areas need attention: how you handle money differently, and how you each show up under stress. Both are workable.</Body>
          <Btn label="Full marriage report · ₹149" variant="gold" size="sm" style={{ marginTop: 14, alignSelf: 'flex-start' }} />
        </Card>
      </View>
    </SubScreen>
  );
}

function Head({ title }: { title: string }) {
  const { p } = useTheme();
  return <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, letterSpacing: 1.8, textTransform: 'uppercase', color: p.inkMute, paddingVertical: 14, paddingTop: 28 }}>{title}</Text>;
}
