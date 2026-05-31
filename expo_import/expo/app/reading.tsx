import { View, Text } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, CardStrong, Body, Small, Mono, Display, Btn, PremiumTag, Icon } from '@/components/ui';

const INCLUDES = [
  'Your full chart, decoded',
  'Next 7 years month-by-month',
  'Marriage, money, work in depth',
  'Hand-written by senior astrologer',
  'Yours to keep',
];

export default function Reading() {
  const { p } = useTheme();
  return (
    <SubScreen title="Full Life Reading">
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <CardStrong style={{ padding: 22, borderColor: p.gold }}>
          <PremiumTag label="Premium · one-time" />
          <Display size={32} style={{ marginTop: 14 }}>The whole map{'\n'}of your life.</Display>
          <Body style={{ marginTop: 12 }}>
            A 38-page read of who you are, the chapters ahead, your relationships, money, soul work, and the next 7 turning years.
          </Body>

          <View style={{ marginTop: 20, gap: 10 }}>
            {INCLUDES.map(t => (
              <View key={t} style={{ flexDirection: 'row', gap: 10, alignItems: 'center' }}>
                <Icon name="check" size={14} color={p.gold} />
                <Text style={{ fontFamily: fonts.sans, fontSize: 13, color: p.inkSoft }}>{t}</Text>
              </View>
            ))}
          </View>

          <View style={{ marginTop: 20, paddingVertical: 14, borderTopWidth: 1, borderTopColor: p.hairline, flexDirection: 'row', alignItems: 'baseline', justifyContent: 'space-between' }}>
            <View style={{ flexDirection: 'row', alignItems: 'baseline', gap: 4 }}>
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 16, color: p.inkSoft }}>₹</Text>
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 42, lineHeight: 44, color: p.ink, letterSpacing: -0.8 }}>199</Text>
              <Text style={{ fontFamily: fonts.sans, fontSize: 11, color: p.inkMute, marginLeft: 4 }}>one-time</Text>
            </View>
            <Small>Delivered in 48h</Small>
          </View>

          <Btn label="Begin reading" variant="gold" size="lg" block style={{ marginTop: 12 }} />
          <Small style={{ textAlign: 'center', marginTop: 10 }}>Full refund if it doesn't land.</Small>
        </CardStrong>

        <Head title="What people have said" />
        <Card style={{ padding: 18 }}>
          <Display size={18}>"It read me the way one specific friend can — and then went further. I keep coming back to a sentence on page 14."</Display>
          <Mono style={{ marginTop: 12 }}>— R., Bangalore</Mono>
        </Card>
      </View>
    </SubScreen>
  );
}

function Head({ title }: { title: string }) {
  const { p } = useTheme();
  return <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, letterSpacing: 1.8, textTransform: 'uppercase', color: p.inkMute, paddingVertical: 14, paddingTop: 28 }}>{title}</Text>;
}
