import { View, Text } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, CardStrong, Body, Kicker, Mono, Display } from '@/components/ui';

const CHAPTERS = [
  { years: '0 – 6', title: 'The home years', lord: 'Moon', note: 'Inward, watching, learning to trust.' },
  { years: '7 – 22', title: 'The seeker', lord: 'Mars', note: 'Restless, hungry. Found and lost a lot.' },
  { years: '23 – 35', title: 'The builder', lord: 'Rahu', note: 'Roots, work, choosing your people.', current: true },
  { years: '36 – 51', title: 'The teacher', lord: 'Jupiter', note: 'You become a quiet authority. Mentors arrive too.' },
  { years: '52 – 68', title: 'The harvest', lord: 'Saturn', note: 'Reaping what you built. Travel, depth.' },
  { years: '69 +', title: 'The elder', lord: 'Mercury', note: 'A long, gentle close.' },
];

export default function Chapters() {
  const { p } = useTheme();
  return (
    <SubScreen title="Life Chapters">
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <Body>Your life moves in chapters — long planetary seasons. Here are yours.</Body>

        <View style={{ marginTop: 20, position: 'relative' }}>
          <View style={{ position: 'absolute', left: 18, top: 14, bottom: 14, width: 1, backgroundColor: p.hairline }} />
          {CHAPTERS.map((c, i) => (
            <View key={i} style={{ paddingLeft: 50, marginBottom: 12, position: 'relative' }}>
              <View style={{
                position: 'absolute', left: 12, top: 18, width: 12, height: 12, borderRadius: 6,
                backgroundColor: c.current ? p.gold : p.surfaceStrong,
                borderWidth: 2, borderColor: p.bg0,
              }} />
              {c.current ? (
                <CardStrong style={{ padding: 16, borderColor: p.gold }}>
                  <ChapterBody c={c} />
                </CardStrong>
              ) : (
                <Card style={{ padding: 16 }}>
                  <ChapterBody c={c} />
                </Card>
              )}
            </View>
          ))}
        </View>
      </View>
    </SubScreen>
  );
}

function ChapterBody({ c }: { c: typeof CHAPTERS[number] }) {
  const { p } = useTheme();
  return (
    <>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <Mono color={c.current ? p.gold : p.inkMute}>{c.years}{c.current ? ' · now' : ''}</Mono>
        <Kicker>{c.lord} dasha</Kicker>
      </View>
      <Display size={19} style={{ marginTop: 6 }}>{c.title}</Display>
      <Body style={{ marginTop: 8 }}>{c.note}</Body>
    </>
  );
}
