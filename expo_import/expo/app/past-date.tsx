import { useState } from 'react';
import { View, Text } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, CardStrong, Body, Small, Kicker, Display, Btn, Field, Input, PremiumTag, ListRow, Icon } from '@/components/ui';
import WhyToggle from '@/components/WhyToggle';

const ACTIVE: [string, string][] = [
  ['Saturn ingress', 'Endings and rebuilds.'],
  ['Mars on your Moon', 'A spike of emotion. The feeling came first.'],
  ['Eclipse season', 'Things hidden came to light.'],
];

export default function PastDate() {
  const { p } = useTheme();
  const [date, setDate] = useState('2023-11-04');
  const [stage, setStage] = useState(0);

  return (
    <SubScreen title="Why did that happen?">
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <Body>A date you can't shake — good or bad. We'll tell you what was happening above you.</Body>

        <Card style={{ padding: 18, marginTop: 16 }}>
          <Field label="That day"><Input value={date} onChangeText={setDate} placeholder="YYYY-MM-DD" /></Field>
          <Btn label="Look at the sky that day" variant="primary" block style={{ marginTop: 14 }} onPress={() => setStage(1)} />
          <View style={{ flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 6, marginTop: 10 }}>
            <PremiumTag label="+" />
            <Small>First one is free · then Myastro+</Small>
          </View>
        </Card>

        {stage >= 1 && (
          <View style={{ marginTop: 16 }}>
            <CardStrong style={{ padding: 22 }}>
              <Kicker>November 4, 2023</Kicker>
              <Display size={24} style={{ marginTop: 6 }}>A door opened — and one quietly closed behind you.</Display>
              <Body style={{ marginTop: 12 }}>
                Saturn had just begun crossing the most private part of your chart. The change you felt that week wasn't sudden — it was a long underground river finally surfacing. You probably ended something or were ended by something.
              </Body>
              <WhyToggle sanskrit="शनि-गोचर · चतुर्थ-भावे · दशा-सन्धि">
                Saturn ingressed your 4th house with Mars on your Moon — endings around home, family, sense of safety. Lasts ~2.5 years.
              </WhyToggle>
            </CardStrong>

            <Head title="Three things were active" />
            <Card>
              {ACTIVE.map(([l, v], i) => (
                <ListRow key={l} last={i === ACTIVE.length - 1}>
                  <Icon name="sparkle" size={14} color={p.gold} />
                  <View style={{ flex: 1 }}>
                    <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink }}>{l}</Text>
                    <Small style={{ marginTop: 2 }}>{v}</Small>
                  </View>
                </ListRow>
              ))}
            </Card>
          </View>
        )}
      </View>
    </SubScreen>
  );
}

function Head({ title }: { title: string }) {
  const { p } = useTheme();
  return <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, letterSpacing: 1.8, textTransform: 'uppercase', color: p.inkMute, paddingVertical: 14, paddingTop: 28 }}>{title}</Text>;
}
