import { View, Text, Pressable } from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { PEOPLE } from '@/constants/data';
import {
  SubScreen, Card, CardStrong, H2, Body, Small, Kicker, Display, Avatar, Chip, AppBarIconBtn, Icon,
} from '@/components/ui';
import WhyToggle from '@/components/WhyToggle';
import type { IconName } from '@/components/Icon';

const ROMANTIC = ['partner', 'spouse', 'love', 'matchmaking', 'fiancé', 'fiance', 'fiancee', 'prospective match'];
const isRomantic = (rel?: string) => !!rel && ROMANTIC.some(k => rel.toLowerCase().includes(k));

const HOW_TO: [string, string][] = [
  ['Money & home', 'Different instincts. Talk it out before you act.'],
  ['Under stress', 'She softens, you go quiet. Name yours out loud.'],
  ['Rituals', 'A weekly tea + walk — keep the small rhythm.'],
];

export default function PersonDetail() {
  const { p } = useTheme();
  const { id } = useLocalSearchParams<{ id?: string }>();
  const person = PEOPLE.find(x => x.id === id) ?? PEOPLE.find(x => x.id === 'maya')!;
  const romantic = isRomantic(person.rel);

  const together: { title: string; sub: string; icon: IconName }[] = romantic
    ? [
        { title: 'Tension forecast', sub: '7-day outlook', icon: 'flame' },
        { title: 'Shared pulse', sub: 'Both feel it', icon: 'sparkle' },
        { title: 'Best date night', sub: 'Sat 7 – 9 pm', icon: 'star' },
        { title: 'A hard week', sub: 'Plan softly', icon: 'moon' },
      ]
    : [
        { title: 'Best time to talk', sub: 'Tue · 11 am', icon: 'sparkle' },
        { title: 'Their week', sub: 'Steady · low key', icon: 'today' },
        { title: 'Gift ideas', sub: 'When in doubt', icon: 'heart' },
        { title: 'Calling rhythm', sub: 'Once a month is enough', icon: 'bell' },
      ];

  return (
    <SubScreen title="" right={<AppBarIconBtn icon="settings" />}>
      <View style={{ paddingHorizontal: 22 }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 14, paddingTop: 8, paddingBottom: 22 }}>
          <Avatar initials={person.initials} size={56} />
          <View style={{ flex: 1 }}>
            <H2 style={{ marginBottom: 2 }}>{person.name}</H2>
            <Small>{person.rel} · {person.tier !== '—' ? `${person.tier} · ` : ''}{person.source}</Small>
          </View>
          {person.source === 'friend' && <Chip label="live" gold />}
        </View>

        <CardStrong style={{ padding: 20 }}>
          <Kicker>Today with {person.name}</Kicker>
          <Display size={28} style={{ marginTop: 8 }}>Tender.{'\n'}Quiet care lands hard.</Display>
          <Body style={{ marginTop: 12 }}>
            She'll feel softer than usual. A small specific thing — tea ready, a chore done — will mean more than a grand gesture.
          </Body>
          <View style={{ marginTop: 16, flexDirection: 'row', gap: 8 }}>
            {([['Best', '3 – 6 pm', p.gold], ['Avoid', '9 pm', p.rose]] as const).map(([k, v, c]) => (
              <Card key={k} style={{ flex: 1, padding: 12 }}>
                <Kicker color={c}>{k}</Kicker>
                <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.ink, marginTop: 6 }}>{v}</Text>
              </Card>
            ))}
          </View>
          <WhyToggle sanskrit="चन्द्रः कर्क-राशौ · शुक्रः मीने">
            Her Moon is in a tender water sign, and your charts share a quiet anchor today — the planet of care is active for both of you.
          </WhyToggle>
        </CardStrong>

        {romantic && (
          <>
            <SectionHead title="Marriage compatibility" right="27/32 →" rightGold />
            <Pressable onPress={() => router.push('/compat')}>
              <CardStrong style={{ padding: 18, borderColor: p.gold }}>
                <View style={{ flexDirection: 'row', gap: 14, alignItems: 'flex-start' }}>
                  <View style={{ width: 56, height: 56, borderRadius: 14, backgroundColor: p.goldSoft, borderWidth: 1, borderColor: p.gold, alignItems: 'center', justifyContent: 'center' }}>
                    <Display size={22} color={p.gold} style={{ lineHeight: 24 }}>27</Display>
                    <Text style={{ fontFamily: fonts.mono, fontSize: 8, color: p.gold }}>/32</Text>
                  </View>
                  <View style={{ flex: 1 }}>
                    <Display size={18}>Built to last.{'\n'}Same direction, different speeds.</Display>
                    <Small style={{ marginTop: 8 }}>Ashta Koota across 8 dimensions — strong on mind, family, long-term path.</Small>
                  </View>
                </View>
                <Kicker style={{ marginTop: 16 }}>How to make it work</Kicker>
                <View style={{ marginTop: 8, gap: 6 }}>
                  {HOW_TO.map(([l, v]) => (
                    <View key={l} style={{ flexDirection: 'row', gap: 10, alignItems: 'flex-start' }}>
                      <View style={{ width: 4, height: 4, borderRadius: 2, backgroundColor: p.gold, marginTop: 7 }} />
                      <View style={{ flex: 1 }}>
                        <Text style={{ fontFamily: fonts.sansMedium, fontSize: 13, color: p.ink }}>{l}</Text>
                        <Small style={{ marginTop: 2 }}>{v}</Small>
                      </View>
                    </View>
                  ))}
                </View>
              </CardStrong>
            </Pressable>
          </>
        )}

        <SectionHead title="Together" />
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 10 }}>
          {together.map(c => (
            <Card key={c.title} style={{ width: '47.5%', padding: 14 }}>
              <Icon name={c.icon} size={16} color={p.gold} />
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 13, color: p.ink, marginTop: 10 }}>{c.title}</Text>
              <Small style={{ marginTop: 2 }}>{c.sub}</Small>
            </Card>
          ))}
        </View>

        <SectionHead title="Notes · private" />
        <Card style={{ padding: 16 }}>
          <Body><Text style={{ fontFamily: fonts.mono, fontSize: 10, color: p.inkMute }}>MAY 12 · </Text>Apologized in person. She cried then laughed. I'll remember the laughing.</Body>
        </Card>
        <View style={{ marginTop: 8, flexDirection: 'row', gap: 6, alignItems: 'center' }}>
          <Icon name="lock" size={12} color={p.inkMute} />
          <Small>Notes stay on your phone. Never shared.</Small>
        </View>
      </View>
    </SubScreen>
  );
}

function SectionHead({ title, right, rightGold }: { title: string; right?: string; rightGold?: boolean }) {
  const { p } = useTheme();
  return (
    <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline', paddingVertical: 14, paddingTop: 28 }}>
      <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, letterSpacing: 1.8, textTransform: 'uppercase', color: p.inkMute }}>{title}</Text>
      {!!right && <Text style={{ fontFamily: fonts.sans, fontSize: 11, color: rightGold ? p.gold : p.inkMute }}>{right}</Text>}
    </View>
  );
}
