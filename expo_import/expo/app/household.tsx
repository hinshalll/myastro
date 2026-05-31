import { View, Text } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, CardStrong, Body, Small, Kicker, Display } from '@/components/ui';

export default function Household() {
  const { p } = useTheme();
  const fam = [
    { name: 'You', vibe: 'magnetic', dot: p.gold },
    { name: 'Maya', vibe: 'tender', dot: p.rose },
    { name: 'Amma', vibe: 'steady', dot: p.teal },
    { name: 'Sam', vibe: 'restless', dot: p.violet },
  ];
  return (
    <SubScreen title="Household">
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <CardStrong style={{ padding: 22 }}>
          <Kicker>Tonight's mood</Kicker>
          <Display size={30} style={{ marginTop: 10 }}>Quiet until dinner.</Display>
          <Body style={{ marginTop: 12 }}>Everyone's in their own world this afternoon. Set the table early — it pulls them in.</Body>
        </CardStrong>

        <Head title="Each of you, today" />
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 10 }}>
          {fam.map(f => (
            <Card key={f.name} style={{ width: '47.5%', padding: 16 }}>
              <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: f.dot, marginBottom: 10 }} />
              <Display size={22} style={{ lineHeight: 24 }}>{f.vibe}</Display>
              <Small style={{ marginTop: 6 }}>{f.name}</Small>
            </Card>
          ))}
        </View>

        <Head title="This week" />
        <Card style={{ padding: 16 }}>
          <Body><Text style={{ color: p.ink, fontFamily: fonts.sansMedium }}>Wed</Text> is the easy day — plan together then. <Text style={{ color: p.rose, fontFamily: fonts.sansMedium }}>Thu evening</Text> may bring a small argument; let it pass without fixing.</Body>
        </Card>
      </View>
    </SubScreen>
  );
}

function Head({ title }: { title: string }) {
  const { p } = useTheme();
  return <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, letterSpacing: 1.8, textTransform: 'uppercase', color: p.inkMute, paddingVertical: 14, paddingTop: 28 }}>{title}</Text>;
}
