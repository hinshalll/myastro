import { View, Text } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, H2, Body, Mono, ListRow } from '@/components/ui';

const SLOTS = [
  { time: '5:30 – 6:45 am',  label: 'sit with it',   type: 'good',  note: 'Best stretch to be alone.' },
  { time: '7:00 – 9:00 am',  label: 'neutral',       type: 'meh',   note: '' },
  { time: '9:00 – 11:30 am', label: 'do the work',   type: 'good',  note: 'Focus runs deep here.' },
  { time: '11:30 – 12:30',   label: 'pause on email', type: 'avoid', note: 'A message could land sideways.' },
  { time: '12:30 – 4:00 pm', label: 'meet people',   type: 'good',  note: 'Warmth radiates. Say yes to plans.' },
  { time: '3:15 – 4:42 pm',  label: 'low window',    type: 'avoid', note: 'Chandra Sandhi · reflective hour.' },
  { time: '4:00 – 6:00 pm',  label: 'neutral',       type: 'meh',   note: '' },
  { time: '6:00 – 6:45 pm',  label: "don't react",   type: 'avoid', note: 'Something will sting. It will pass.' },
  { time: '7:00 – 10:00 pm', label: 'soft hours',    type: 'good',  note: 'Cook. Call someone. Read.' },
];

export default function Timing() {
  const { p } = useTheme();
  const dot = (t: string) => (t === 'good' ? p.gold : t === 'avoid' ? p.rose : p.inkMute);
  return (
    <SubScreen title="Today's hours">
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <H2 style={{ marginBottom: 4 }}>Your day, hour by hour.</H2>
        <Body style={{ marginBottom: 18 }}>Plan around the windows.</Body>
        <Card style={{ padding: 4 }}>
          {SLOTS.map((s, i) => (
            <ListRow key={i} last={i === SLOTS.length - 1}>
              <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: dot(s.type) }} />
              <View style={{ flex: 1 }}>
                <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink }}>{s.label}</Text>
                <Mono style={{ marginTop: 4 }}>{s.time}</Mono>
                {!!s.note && <Body style={{ marginTop: 6, fontSize: 12 }}>{s.note}</Body>}
              </View>
            </ListRow>
          ))}
        </Card>
      </View>
    </SubScreen>
  );
}
