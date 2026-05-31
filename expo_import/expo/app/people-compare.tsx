import { useState } from 'react';
import { View, Text } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { PEOPLE, Person } from '@/constants/data';
import { SubScreen, Card, CardStrong, Body, Small, Kicker, Display, Avatar, Chip, Hr, ListRow, Icon } from '@/components/ui';

const SELF: Person = { id: 'you', name: 'You', rel: 'self', weather: '—', source: 'friend', tier: '—', initials: 'Y' };
const ALL = [SELF, ...PEOPLE];

const TRAITS: Record<string, { strengths: string[]; stress: string }> = {
  you: { strengths: ['Patient', 'Deeply loyal', 'Reads the room'], stress: 'You go quiet and over-think.' },
  maya: { strengths: ['Soft, attuned', 'Holds people well', 'Forgiving'], stress: 'She softens further; vanishes.' },
  amma: { strengths: ['Anchored', 'Decisive', 'Practical'], stress: 'She becomes brisk.' },
  sam: { strengths: ['Funny', 'Honest fast', 'Spirited'], stress: 'She sharpens her tongue.' },
  priya: { strengths: ['Warm', 'Steady', 'Brilliant listener'], stress: 'She over-helps; forgets herself.' },
  arjun: { strengths: ['Sharp', 'Reliable', 'Detail-driven'], stress: 'He turns down the lights.' },
  rohit: { strengths: ['Open', 'Curious', 'Family-oriented'], stress: 'He defers too much.' },
  ishaan: { strengths: ['Curious', 'Energetic', 'Wide-eyed'], stress: 'He spirals into questions.' },
};
const COMPLEMENTS: Record<string, string> = {
  'you+maya': 'You bring patient steadiness; she brings emotional warmth. You hold the room, she softens it. Together: a quiet shelter.',
  'you+amma': 'You think long; she acts now. She gets things off the page; you make them stick.',
  'you+sam': 'She talks; you listen. You ground her; she gets you out of your head.',
  'you+priya': "You're both fixers — pace yourselves. Best together over long unhurried evenings.",
  'you+arjun': 'Detail meets depth. Work projects sing here. Outside work, watch the silence.',
  default: 'Different rhythms — let it be that. You move slowly to be sure; they move quickly to find out.',
};

export default function PeopleCompare() {
  const { p } = useTheme();
  const [a, setA] = useState('you');
  const [b, setB] = useState('maya');
  const A = ALL.find(x => x.id === a)!;
  const B = ALL.find(x => x.id === b)!;
  const ta = TRAITS[A.id] ?? TRAITS.you;
  const tb = TRAITS[B.id] ?? TRAITS.maya;
  const complement = COMPLEMENTS[`${A.id}+${B.id}`] ?? COMPLEMENTS[`${B.id}+${A.id}`] ?? COMPLEMENTS.default;

  const Picker = ({ value, onChange, exclude, label }: { value: string; onChange: (id: string) => void; exclude: string; label: string }) => (
    <View style={{ flex: 1 }}>
      <Kicker style={{ marginBottom: 8 }}>{label}</Kicker>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6 }}>
        {ALL.filter(x => x.id !== exclude).map(x => (
          <Chip key={x.id} label={x.name} active={value === x.id} onPress={() => onChange(x.id)} />
        ))}
      </View>
    </View>
  );

  return (
    <SubScreen title="Compare two people">
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <Card style={{ padding: 18 }}>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 14 }}>
            <Face person={A} />
            <View style={{ flex: 1, alignItems: 'center' }}><Icon name="sparkle" size={18} color={p.gold} /></View>
            <Face person={B} />
          </View>
          <Hr style={{ marginVertical: 18 }} />
          <View style={{ flexDirection: 'row', gap: 14 }}>
            <Picker value={a} onChange={setA} exclude={b} label="Person A" />
            <Picker value={b} onChange={setB} exclude={a} label="Person B" />
          </View>
        </Card>

        <Head title="Where each is strong" />
        <View style={{ flexDirection: 'row', gap: 10 }}>
          {[{ person: A, t: ta }, { person: B, t: tb }].map(({ person, t }) => (
            <Card key={person.id} style={{ flex: 1, padding: 16 }}>
              <Display size={17}>{person.name}</Display>
              <Small style={{ marginTop: 2 }}>{person.rel}</Small>
              <View style={{ marginTop: 12, gap: 8 }}>
                {t.strengths.map(s => (
                  <View key={s} style={{ flexDirection: 'row', gap: 8, alignItems: 'center' }}>
                    <View style={{ width: 4, height: 4, borderRadius: 2, backgroundColor: p.gold }} />
                    <Text style={{ fontFamily: fonts.sans, fontSize: 13, color: p.ink }}>{s}</Text>
                  </View>
                ))}
              </View>
            </Card>
          ))}
        </View>

        <Head title="How you complement" />
        <CardStrong style={{ padding: 18, borderColor: p.gold }}>
          <Display size={19}>{complement}</Display>
        </CardStrong>

        <Head title="Under stress" />
        <Card>
          {[{ person: A, t: ta }, { person: B, t: tb }].map(({ person, t }, i) => (
            <ListRow key={person.id} last={i === 1}>
              <Avatar initials={person.initials} size={32} />
              <View style={{ flex: 1 }}>
                <Text style={{ fontFamily: fonts.sansMedium, fontSize: 13, color: p.ink }}>{person.name}</Text>
                <Small style={{ marginTop: 2 }}>{t.stress}</Small>
              </View>
            </ListRow>
          ))}
        </Card>
      </View>
    </SubScreen>
  );
}

function Face({ person }: { person: Person }) {
  const { p } = useTheme();
  return (
    <View style={{ alignItems: 'center', gap: 8 }}>
      <Avatar initials={person.initials} size={56} />
      <Text style={{ fontFamily: fonts.sansMedium, fontSize: 13, color: p.ink }}>{person.name}</Text>
      <Small style={{ marginTop: -4 }}>{person.rel}</Small>
    </View>
  );
}

function Head({ title }: { title: string }) {
  const { p } = useTheme();
  return <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, letterSpacing: 1.8, textTransform: 'uppercase', color: p.inkMute, paddingVertical: 14, paddingTop: 28 }}>{title}</Text>;
}
