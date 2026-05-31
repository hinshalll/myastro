import { View, Text, Pressable } from 'react-native';
import { router } from 'expo-router';

import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { PEOPLE } from '@/constants/data';
import {
  TabScroll, FadeUp, H1, H3, Body, Small, Kicker, Avatar, Icon,
} from '@/components/ui';

export default function People() {
  const { p } = useTheme();
  const vibe = (w: string) =>
    w === 'tender' ? p.rose : w === 'steady' ? p.teal : w === 'spicy' || w === 'warm' ? p.gold : w === 'cool' ? p.slate : p.inkFaint;

  return (
    <TabScroll>
      {/* Header */}
      <View style={{ paddingHorizontal: 22, paddingTop: 18 }}>
        <Kicker style={{ marginBottom: 12 }}>People</Kicker>
        <H1>Your circle</H1>
        <Body style={{ marginTop: 10, maxWidth: 320 }}>
          How everyone close to you is doing — and who you're matching with.
        </Body>
      </View>

      {/* Tonight → household */}
      <FadeUp style={{ paddingHorizontal: 22, paddingTop: 24, marginTop: 22, borderTopWidth: 1, borderTopColor: p.hairline }}>
        <Pressable onPress={() => router.push('/household')}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' }}>
            <Kicker>Tonight</Kicker>
            <Small>4 live →</Small>
          </View>
          <H3 style={{ marginTop: 10 }}>Quiet now. Lively at dinner.</H3>
          <View style={{ flexDirection: 'row', marginTop: 14 }}>
            {['M', 'S', 'A', 'P'].map((l, i) => (
              <Avatar key={i} initials={l} size={30} style={{ marginLeft: i === 0 ? 0 : -8, borderWidth: 2, borderColor: p.bg0 }} />
            ))}
          </View>
        </Pressable>
      </FadeUp>

      {/* Couple */}
      <FadeUp style={{ paddingHorizontal: 22, paddingTop: 24, marginTop: 22, borderTopWidth: 1, borderTopColor: p.hairline }}>
        <Pressable onPress={() => router.push('/couple')} style={{ flexDirection: 'row', alignItems: 'center', gap: 14 }}>
          <View style={{ width: 36, height: 36, borderRadius: 18, borderWidth: 1, borderColor: p.rose, alignItems: 'center', justifyContent: 'center' }}>
            <Icon name="heart" size={15} color={p.rose} />
          </View>
          <View style={{ flex: 1 }}>
            <Kicker>You & Maya</Kicker>
            <Text style={{ fontFamily: fonts.sansMedium, fontSize: 15, lineHeight: 20, color: p.ink, marginTop: 4 }}>Tension low · weekend bright</Text>
          </View>
          <Icon name="chevron" size={14} color={p.inkMute} />
        </Pressable>
      </FadeUp>

      {/* Saved roster */}
      <FadeUp style={{ paddingTop: 28, marginTop: 22, borderTopWidth: 1, borderTopColor: p.hairline }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline', paddingHorizontal: 22, paddingBottom: 12 }}>
          <Kicker>Saved · {PEOPLE.length}</Kicker>
          <Pressable onPress={() => router.push('/add-person')}>
            <Small color={p.gold}>+ add</Small>
          </Pressable>
        </View>
      </FadeUp>

      <View style={{ paddingHorizontal: 22 }}>
        {PEOPLE.map((person) => (
          <Pressable
            key={person.id}
            onPress={() => router.push({ pathname: '/person-detail', params: { id: person.id } })}
            style={{ flexDirection: 'row', alignItems: 'center', gap: 16, paddingVertical: 16, borderBottomWidth: 1, borderBottomColor: p.hairline }}
          >
            <Avatar initials={person.initials} size={36} />
            <View style={{ flex: 1 }}>
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 15, color: p.ink }}>{person.name}</Text>
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 10, letterSpacing: 2.2, textTransform: 'uppercase', marginTop: 4, color: person.tier === 'close' ? p.gold : p.inkMute }}>
                {person.rel}{person.tier === 'close' ? ' · close' : ''}{person.source === 'manual' ? ' · manual' : ''}
              </Text>
            </View>
            <Text style={{ fontFamily: fonts.sansMedium, fontSize: 12, letterSpacing: 0.4, color: vibe(person.weather) }}>
              {person.weather === '—' ? 'match →' : person.weather}
            </Text>
          </Pressable>
        ))}
      </View>

      {/* Try this */}
      <FadeUp style={{ paddingHorizontal: 22, paddingTop: 28, marginTop: 22, borderTopWidth: 1, borderTopColor: p.hairline }}>
        <Kicker style={{ marginBottom: 12 }}>Try this</Kicker>
        <Pressable onPress={() => router.push('/people-compare')} style={{ flexDirection: 'row', alignItems: 'center', gap: 14, paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: p.hairline }}>
          <H3 style={{ flex: 1 }}>Compare two people</H3>
          <Icon name="chevron" size={14} color={p.inkMute} />
        </Pressable>
        <Pressable onPress={() => router.push('/compat')} style={{ flexDirection: 'row', alignItems: 'center', gap: 14, paddingVertical: 12 }}>
          <H3 style={{ flex: 1 }}>Match for marriage</H3>
          <Icon name="chevron" size={14} color={p.inkMute} />
        </Pressable>
      </FadeUp>
    </TabScroll>
  );
}
