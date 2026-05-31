import { useState } from 'react';
import { View, Text, Pressable, LayoutAnimation, Platform, UIManager } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, Body, Kicker, Mono, Display, Btn, AppBarIconBtn, Icon } from '@/components/ui';
import ConstellationBG from '@/components/ConstellationBG';

if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

const PERIODS = [
  { m: 'Jan', title: 'Started something quietly.', body: 'January was a private re-set. Jupiter sat low in your chart — a season for choosing the next decade quietly, on paper. The two notebooks you started in Jan are still load-bearing.' },
  { m: 'Feb', title: 'A quiet middle distance.', body: 'Steady, undramatic. You showed up most days. Saturn was building the floor — the work you did here you cannot see yet.' },
  { m: 'Mar', title: 'A heavy week. You stayed.', body: "Saturn squared your Moon — the heaviest stretch of the year. Two things you almost walked away from, you didn't. That's the whole story of the year, right there." },
  { m: 'Apr', title: 'The fog began to lift.', body: 'A small clearing. You said no to one big thing and yes to two small ones — exactly the right ratio for the season.' },
  { m: 'May', title: 'Tender and a little raw.', body: 'Venus through your private house — old feelings surfaced, and not without reason. You let them through without organizing them.' },
  { m: 'Jun', title: 'A real conversation, finally.', body: "Mercury direct + Venus in your relationship house. You said the thing you'd been editing for two years. It went better than you feared." },
  { m: 'Jul', title: 'Slow summer; deep rest.', body: "Sun in a soft water sign and you let it be. You read more, talked less. The body remembered things the mind didn't catch." },
  { m: 'Aug', title: 'A second chance you took.', body: 'Mars retrograde gifted you an old opportunity in a new shape. You moved faster than you usually do, and it suited you.' },
  { m: 'Sep', title: 'Quiet completion.', body: "Three projects ended cleanly. You'd resisted endings before — this year you got better at them." },
  { m: 'Oct', title: 'You felt like yourself again.', body: 'Jupiter trined your Ascendant — the lightest month of the year. The version of you October met is the one to keep.' },
  { m: 'Nov', title: 'A small grief, met well.', body: 'Saturn touched your chart of memory. You let yourself be sad without making a project out of it.' },
  { m: 'Dec', title: 'Settling, gently.', body: "Old loops closed. You stopped explaining yourself to a few specific people. That's a real shift; carry it into next year." },
];

const STATS: [string, string][] = [['Days shown up', '198'], ['Mood most often', 'calm'], ['Heaviest month', 'March'], ['Lightest month', 'October']];

export default function Year() {
  const { p } = useTheme();
  const [open, setOpen] = useState<number | null>(null);

  return (
    <SubScreen title="Year in review" right={<AppBarIconBtn icon="share" />}>
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <View style={{ borderRadius: 22, padding: 24, overflow: 'hidden', borderWidth: 1, borderColor: p.gold, backgroundColor: '#14101e' }}>
          <ConstellationBG seed={42} density={50} opacity={0.4} color="#ece6d4" />
          <Kicker color="rgba(236,230,212,0.6)">Your 2026</Kicker>
          <Text style={{ fontFamily: fonts.sansMedium, fontSize: 42, lineHeight: 44, letterSpacing: -0.8, color: 'rgba(236,230,212,0.98)', marginTop: 10 }}>
            The year you{'\n'}stopped explaining{'\n'}yourself.
          </Text>
          <View style={{ marginTop: 22, flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
            {STATS.map(([l, v]) => (
              <View key={l} style={{ width: '47%', borderRadius: 12, padding: 12, backgroundColor: 'rgba(255,255,255,0.04)' }}>
                <Kicker color="rgba(236,230,212,0.55)">{l}</Kicker>
                <Text style={{ fontFamily: fonts.sansMedium, fontSize: 22, color: p.gold, marginTop: 4 }}>{v}</Text>
              </View>
            ))}
          </View>
        </View>

        <Btn label="Share your year" variant="primary" size="lg" block style={{ marginTop: 16 }} left={<Icon name="share" size={14} color={p.bg0} />} />

        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline', paddingTop: 28, paddingBottom: 14 }}>
          <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, letterSpacing: 1.8, textTransform: 'uppercase', color: p.inkMute }}>The full story</Text>
          <Body style={{ fontSize: 11 }}>tap a month</Body>
        </View>

        <Card style={{ overflow: 'hidden' }}>
          {PERIODS.map((period, i) => {
            const isOpen = open === i;
            return (
              <View key={period.m} style={{ borderBottomWidth: i === PERIODS.length - 1 ? 0 : 1, borderBottomColor: p.hairline }}>
                <Pressable
                  onPress={() => { LayoutAnimation.configureNext(LayoutAnimation.create(200, 'easeInEaseOut', 'opacity')); setOpen(isOpen ? null : i); }}
                  style={{ flexDirection: 'row', alignItems: 'center', gap: 14, paddingVertical: 14, paddingHorizontal: 18 }}
                >
                  <Mono color={isOpen ? p.gold : p.inkMute} style={{ width: 32 }}>{period.m}</Mono>
                  <Text style={{ flex: 1, fontFamily: fonts.sansMedium, fontSize: 14, color: isOpen ? p.ink : p.inkSoft }}>{period.title}</Text>
                  <Text style={{ color: p.inkMute, transform: [{ rotate: isOpen ? '90deg' : '0deg' }] }}>
                    <Icon name="chevron" size={14} color={p.inkMute} />
                  </Text>
                </Pressable>
                {isOpen && (
                  <Body style={{ paddingHorizontal: 18, paddingLeft: 64, paddingBottom: 18, paddingTop: 4, lineHeight: 21 }}>{period.body}</Body>
                )}
              </View>
            );
          })}
        </Card>
      </View>
    </SubScreen>
  );
}
