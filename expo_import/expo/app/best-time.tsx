import { useState } from 'react';
import { View, Text, Pressable } from 'react-native';
import { router } from 'expo-router';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, Body, Small, Kicker, Mono, Display, Chip, Btn, ListRow, PremiumTag, Icon } from '@/components/ui';

const EVENTS = ['Start a new job', 'Sign a contract', 'Travel', 'Have a hard talk', 'Get married', 'Move house', 'Buy a car', 'Open a business', "Child's naming", 'Surgery'];
const DATES = [
  { date: 'Mon · Jun 3', day: 'Mon', num: '3', rating: 5, note: 'Best of the month. Strong Jupiter.' },
  { date: 'Fri · Jun 14', day: 'Fri', num: '14', rating: 4, note: 'Strong. Beginnings favor you.' },
  { date: 'Tue · Jun 25', day: 'Tue', num: '25', rating: 4, note: 'Steady, momentum-building.' },
  { date: 'Sat · Jul 6', day: 'Sat', num: '6', rating: 3, note: 'OK. Avoid the morning.' },
];

export default function BestTime() {
  const { p } = useTheme();
  const [event, setEvent] = useState('Sign a contract');
  const [stage, setStage] = useState(0);

  return (
    <SubScreen title="Best time for…">
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <Card style={{ padding: 18 }}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' }}>
            <Kicker>I want to</Kicker>
            <Mono>free</Mono>
          </View>
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginTop: 12 }}>
            {EVENTS.map(e => (
              <Chip key={e} label={e} active={event === e} onPress={() => { setEvent(e); setStage(0); }} />
            ))}
          </View>
          <Btn label="Find the best days" variant="primary" block style={{ marginTop: 18 }} onPress={() => setStage(1)} />
        </Card>

        {stage === 1 && (
          <>
            <Head title={`Best days · ${event.toLowerCase()}`} />
            <Card>
              {DATES.map((d, i) => (
                <ListRow key={i} last={i === DATES.length - 1}>
                  <View style={{ width: 50, height: 50, borderRadius: 12, backgroundColor: p.surfaceStrong, alignItems: 'center', justifyContent: 'center' }}>
                    <Text style={{ fontFamily: fonts.sansMedium, fontSize: 20, lineHeight: 22, color: p.gold }}>{d.num}</Text>
                    <Mono style={{ marginTop: 2 }}>{d.day}</Mono>
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink }}>{d.date.split('·')[0].trim()}</Text>
                    <Small style={{ marginTop: 2 }}>{d.note}</Small>
                    <Text style={{ marginTop: 4 }}>
                      {Array.from({ length: 5 }).map((_, j) => (
                        <Text key={j} style={{ color: j < d.rating ? p.gold : p.inkFaint }}>✦ </Text>
                      ))}
                    </Text>
                  </View>
                </ListRow>
              ))}
            </Card>

            <Pressable onPress={() => router.push('/paywall')}>
              <Card style={{ padding: 18, marginTop: 14, borderColor: p.gold }}>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                  <PremiumTag />
                  <Icon name="chevron" size={16} color={p.gold} />
                </View>
                <Display size={18} style={{ marginTop: 10 }}>Precise muhurta · down to the hour</Display>
                <Small style={{ marginTop: 4 }}>Exact ascendant + nakshatra picks, tailored to your chart. Best for marriages, big launches, surgery.</Small>
              </Card>
            </Pressable>
          </>
        )}
      </View>
    </SubScreen>
  );
}

function Head({ title }: { title: string }) {
  const { p } = useTheme();
  return <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, letterSpacing: 1.8, textTransform: 'uppercase', color: p.inkMute, paddingVertical: 14, paddingTop: 28 }}>{title}</Text>;
}
