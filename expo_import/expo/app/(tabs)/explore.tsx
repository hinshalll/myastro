import { View, Text, Pressable } from 'react-native';
import { router } from 'expo-router';

import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { EXPLORE, MOST_ASKED } from '@/constants/data';
import { useApp } from '@/constants/AppContext';
import {
  TabScroll, FadeUp, H1, H3, Body, Small, Kicker, Icon,
} from '@/components/ui';
import type { IconName } from '@/components/Icon';

const ICONS: Record<string, IconName> = {
  tarot: 'card', numerology: 'number', palm: 'hand', face: 'eye', 'best-time': 'calendar',
};

export default function Explore() {
  const { p } = useTheme();
  const { openAsk } = useApp();

  return (
    <TabScroll>
      <View style={{ paddingHorizontal: 22, paddingTop: 18 }}>
        <Kicker style={{ marginBottom: 12 }}>Explore</Kicker>
        <H1>Try something small</H1>
        <Body style={{ marginTop: 10, maxWidth: 320 }}>No commitment. Most of these are free, daily.</Body>
      </View>

      <View style={{ paddingHorizontal: 22, paddingTop: 24, marginTop: 18, borderTopWidth: 1, borderTopColor: p.hairline }}>
        {EXPLORE.map((t, i) => (
          <FadeUp key={t.id} delay={i * 60}>
            <Pressable
              onPress={() => router.push(`/${t.id}` as never)}
              style={{
                flexDirection: 'row', alignItems: 'center', gap: 16, paddingVertical: 20,
                borderBottomWidth: i === EXPLORE.length - 1 ? 0 : 1, borderBottomColor: p.hairline,
              }}
            >
              <View style={{ width: 40, height: 40, borderRadius: 20, borderWidth: 1, borderColor: p.borderStrong, alignItems: 'center', justifyContent: 'center' }}>
                <Icon name={ICONS[t.id]} size={17} color={p.gold} />
              </View>
              <View style={{ flex: 1 }}>
                <H3>{t.title}</H3>
                <Small style={{ marginTop: 4 }}>{t.sub}</Small>
              </View>
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 10, letterSpacing: 2.2, textTransform: 'uppercase', color: t.premium ? p.gold : p.inkMute }}>{t.quota}</Text>
            </Pressable>
          </FadeUp>
        ))}
      </View>

      {/* Most asked today — tappable → Ask sheet */}
      <View style={{ paddingHorizontal: 22, paddingTop: 28, marginTop: 22, borderTopWidth: 1, borderTopColor: p.hairline }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' }}>
          <Kicker>Most asked today</Kicker>
          <Small>tap to ask</Small>
        </View>
        <View style={{ marginTop: 12 }}>
          {MOST_ASKED.map((q, i) => (
            <Pressable
              key={q}
              onPress={() => openAsk({ prefill: q })}
              style={{
                flexDirection: 'row', alignItems: 'center', gap: 14, paddingVertical: 14,
                borderBottomWidth: i === MOST_ASKED.length - 1 ? 0 : 1, borderBottomColor: p.hairline,
              }}
            >
              <Text style={{ color: p.gold, fontFamily: fonts.sansMedium, fontSize: 14 }}>“</Text>
              <Text style={{ flex: 1, fontFamily: fonts.sans, fontSize: 14, lineHeight: 20, color: p.inkSoft }}>{q}</Text>
              <Icon name="chevron" size={14} color={p.inkMute} />
            </Pressable>
          ))}
        </View>
      </View>
    </TabScroll>
  );
}
