import { View, Text } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, CardStrong, Body, Kicker, Display } from '@/components/ui';

const LIFE: [string, number][] = [['Life path', 7], ['Heart', 9], ['Name', 2], ['Birthday', 5], ['Year', 6], ['Day', 3]];

export default function Numerology() {
  const { p } = useTheme();
  return (
    <SubScreen title="Your numbers">
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <CardStrong style={{ padding: 24, alignItems: 'center' }}>
          <Kicker>Your core number</Kicker>
          <Text style={{ fontFamily: fonts.sansMedium, fontSize: 130, lineHeight: 138, color: p.gold }}>7</Text>
          <Display size={22}>The Quiet Knower</Display>
          <Body style={{ marginTop: 12, textAlign: 'center' }}>
            You learn by going deep on one thing at a time. Crowds drain you. One real friend = a hundred ok ones.
          </Body>
        </CardStrong>

        <Head title="Today vibrates at" />
        <Card style={{ padding: 18, flexDirection: 'row', alignItems: 'center', gap: 16 }}>
          <View style={{ width: 60, height: 60, borderRadius: 14, backgroundColor: p.goldSoft, alignItems: 'center', justifyContent: 'center' }}>
            <Text style={{ fontFamily: fonts.sansMedium, fontSize: 36, color: p.gold }}>3</Text>
          </View>
          <View style={{ flex: 1 }}>
            <Display size={18}>Bright, expressive</Display>
            <Body style={{ marginTop: 4 }}>Your 7 + today's 3 = a clear voice, well received. Speak up, post the thing, send the message.</Body>
          </View>
        </Card>

        <Head title="Numbers in your life" />
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 10 }}>
          {LIFE.map(([l, n]) => (
            <Card key={l} style={{ width: '31%', padding: 14, alignItems: 'center' }}>
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 36, lineHeight: 38, color: p.gold }}>{n}</Text>
              <Kicker style={{ marginTop: 6 }}>{l}</Kicker>
            </Card>
          ))}
        </View>
      </View>
    </SubScreen>
  );
}

function Head({ title }: { title: string }) {
  const { p } = useTheme();
  return <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, letterSpacing: 1.8, textTransform: 'uppercase', color: p.inkMute, paddingVertical: 14, paddingTop: 28 }}>{title}</Text>;
}
