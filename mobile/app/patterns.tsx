import { useState } from 'react';
import { View, Text } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, CardStrong, Body, Small, Kicker, Display, AppBarIconBtn, Icon } from '@/components/ui';
import WhyToggle from '@/components/WhyToggle';

const PATTERNS = [
  { kicker: "You've told us", title: "You're calmest on Sundays.", body: '11 of your last 12 "calm" days were Sundays. Protect them.' },
  { kicker: "We've noticed", title: 'Mondays are loud in your body.', body: 'Your "off" check-ins cluster at the start of the week.' },
  { kicker: 'A lunar pattern', title: 'Sharpest mood three days before full moon.', body: 'Three months running. Notice it next time.' },
  { kicker: 'A streak', title: "You've shown up 18 days in a row.", body: "Quietly. Without anyone watching. That's the good kind." },
];

export default function Patterns() {
  const { p } = useTheme();
  const [unlocked, setUnlocked] = useState(true);

  return (
    <SubScreen title="Patterns" right={<AppBarIconBtn icon="settings" onPress={() => setUnlocked(u => !u)} />}>
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <Body>What we've learned about you, from the small things you tell us each day.</Body>

        {!unlocked ? (
          <CardStrong style={{ marginTop: 18, padding: 22 }}>
            <Kicker>Building your patterns</Kicker>
            <Display size={22} style={{ marginTop: 8 }}>12 of 30 check-ins.</Display>
            <View style={{ marginTop: 14, height: 4, borderRadius: 2, backgroundColor: p.border }}>
              <View style={{ width: '40%', height: '100%', borderRadius: 2, backgroundColor: p.gold }} />
            </View>
            <Body style={{ marginTop: 14 }}>We won't show patterns until they're real. A wrong long-term pattern on day 3 would destroy your trust.</Body>
            <Small style={{ marginTop: 12 }}>Today's mirror is below — that's free, every day.</Small>
          </CardStrong>
        ) : (
          <View style={{ marginTop: 18, gap: 10 }}>
            {PATTERNS.map((pt, i) => (
              <Card key={i} style={{ padding: 18 }}>
                <Kicker color={p.gold}>{pt.kicker}</Kicker>
                <Display size={19} style={{ marginTop: 6 }}>{pt.title}</Display>
                <Body style={{ marginTop: 8 }}>{pt.body}</Body>
              </Card>
            ))}

            <CardStrong style={{ padding: 22, borderColor: p.gold }}>
              <Kicker color={p.gold}>A new pattern · unlocked just now</Kicker>
              <Display size={22} style={{ marginTop: 8 }}>You're sharpest on Moon-in-Virgo days.</Display>
              <Body style={{ marginTop: 10 }}>
                Past three months — your "bright" check-ins cluster around it. The next Virgo-Moon day is in 6 days. Plan something hard.
              </Body>
              <WhyToggle sanskrit="चन्द्रः कन्या-राशौ · मेधा-वर्धन">
                Virgo's ruler (Mercury) sits well with your natal chart's intellect houses — analytical clarity peaks.
              </WhyToggle>
            </CardStrong>
          </View>
        )}

        <Card style={{ marginTop: 14, padding: 14, flexDirection: 'row', gap: 10, alignItems: 'flex-start' }}>
          <Icon name="lock" size={14} color={p.inkMute} />
          <Small style={{ flex: 1 }}>Patterns are private. Per-user only. Never sold, never shared. Delete-my-data in Settings.</Small>
        </Card>
      </View>
    </SubScreen>
  );
}
