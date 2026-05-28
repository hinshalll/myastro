import { View, Text } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, CardStrong, Body, Kicker, Display } from '@/components/ui';
import WhyToggle from '@/components/WhyToggle';

const DOORS = [
  { title: 'Build something quiet that compounds.', body: 'Newsletter. Practice. Book. Slow, steady, real.' },
  { title: 'Teach what you already know.', body: "You're further along than you think." },
  { title: 'Choose depth over breadth.', body: 'One subject for ten years. Not ten for one.' },
];

export default function Purpose() {
  const { p } = useTheme();
  return (
    <SubScreen title="Your Purpose">
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <CardStrong style={{ padding: 22 }}>
          <Kicker>The work you came here to do</Kicker>
          <Display size={30} style={{ marginTop: 10 }}>To make hidden things useful.</Display>
          <Body style={{ marginTop: 14 }}>
            You notice what others walk past. You're built to take the buried, the technical, the misunderstood — and bring it into the light. Writer. Teacher. Researcher. Therapist. Anyone whose job it is to translate.
          </Body>
          <WhyToggle sanskrit="आत्मकारकः बुधः · दशम-स्वामी पञ्चमे">
            Your 10th house ruler (career karma) sits in a deep-knowledge sign, conjunct Mercury. The atmakaraka points to communication of complex truths.
          </WhyToggle>
        </CardStrong>

        <Head title="Three doors" />
        {DOORS.map((d, i) => (
          <Card key={i} style={{ padding: 18, marginBottom: 8, flexDirection: 'row', gap: 16 }}>
            <Text style={{ fontFamily: fonts.sansMedium, fontSize: 22, color: p.gold, width: 28 }}>{i + 1}</Text>
            <View style={{ flex: 1 }}>
              <Display size={17}>{d.title}</Display>
              <Body style={{ marginTop: 6 }}>{d.body}</Body>
            </View>
          </Card>
        ))}
      </View>
    </SubScreen>
  );
}

function Head({ title }: { title: string }) {
  const { p } = useTheme();
  return <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, letterSpacing: 1.8, textTransform: 'uppercase', color: p.inkMute, paddingVertical: 14, paddingTop: 28 }}>{title}</Text>;
}
