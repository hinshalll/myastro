import { View, Text, Pressable } from 'react-native';
import { router } from 'expo-router';

import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import {
  TabScroll, FadeUp, H1, H3, Body, Small, Kicker, PremiumTag, PrecisionBanner, Icon,
} from '@/components/ui';

type Sec = { title: string; sub: string; route: string; premium?: boolean };
const SECTIONS: Sec[] = [
  { title: 'Your chart',           sub: 'In plain English',               route: '/chart' },
  { title: 'Life Chapters',        sub: 'The seasons of your life',       route: '/chapters' },
  { title: 'Patterns',             sub: 'Insights only you can see',      route: '/patterns', premium: true },
  { title: 'Why did that happen?', sub: 'Enter a past date',              route: '/past-date', premium: true },
  { title: 'Year in Review',       sub: 'A shareable recap of 2026',      route: '/year' },
  { title: 'Your Purpose',         sub: 'Soul · career · what to build',  route: '/purpose', premium: true },
  { title: 'Full Life Reading',    sub: '38 pages · ₹199 one-time',       route: '/reading', premium: true },
];

export default function You() {
  const { p } = useTheme();

  return (
    <TabScroll>
      {/* Birth header */}
      <View style={{ paddingHorizontal: 22, paddingTop: 14 }}>
        <Kicker style={{ marginBottom: 12 }}>Born</Kicker>
        <H1 style={{ fontSize: 32, lineHeight: 35 }}>14 Aug 1995</H1>
        <Text style={{ fontFamily: fonts.sans, fontSize: 17, lineHeight: 22, marginTop: 6, color: p.inkSoft }}>6:45 am · Chennai</Text>

        <View style={{ marginTop: 22, flexDirection: 'row', gap: 18, paddingVertical: 14, borderTopWidth: 1, borderBottomWidth: 1, borderColor: p.hairline }}>
          {[['Element', 'Fire'], ['Energy', 'Slow build'], ['Path', 'Builder, late']].map(([l, v]) => (
            <View key={l} style={{ flex: 1 }}>
              <Kicker style={{ marginBottom: 6 }}>{l}</Kicker>
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: p.gold }}>{v}</Text>
            </View>
          ))}
        </View>

        <PrecisionBanner />
      </View>

      {/* Your story */}
      <View style={{ paddingHorizontal: 22, paddingTop: 28, marginTop: 22, borderTopWidth: 1, borderTopColor: p.hairline }}>
        <Kicker style={{ marginBottom: 8 }}>Your story</Kicker>
        {SECTIONS.map((s, i) => (
          <FadeUp key={s.route} delay={i * 50}>
            <Pressable
              onPress={() => router.push(s.route as never)}
              style={{
                flexDirection: 'row', alignItems: 'center', gap: 14, paddingVertical: 18,
                borderBottomWidth: i === SECTIONS.length - 1 ? 0 : 1, borderBottomColor: p.hairline,
              }}
            >
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 12, color: p.inkMute, width: 22 }}>
                {String(i + 1).padStart(2, '0')}
              </Text>
              <View style={{ flex: 1 }}>
                <H3>{s.title}</H3>
                <Small style={{ marginTop: 4 }}>{s.sub}</Small>
              </View>
              {s.premium && <PremiumTag label="+" />}
              <Icon name="chevron" size={14} color={p.inkMute} />
            </Pressable>
          </FadeUp>
        ))}
      </View>

      {/* Widget */}
      <FadeUp style={{ paddingHorizontal: 22, paddingTop: 28, marginTop: 22, borderTopWidth: 1, borderTopColor: p.hairline }}>
        <Pressable onPress={() => router.push('/widget')} style={{ flexDirection: 'row', alignItems: 'center', gap: 14 }}>
          <View style={{ width: 36, height: 36, borderRadius: 18, borderWidth: 1, borderColor: p.borderStrong, alignItems: 'center', justifyContent: 'center' }}>
            <Icon name="home" size={15} color={p.gold} />
          </View>
          <View style={{ flex: 1 }}>
            <Kicker>On your home screen</Kicker>
            <H3 style={{ marginTop: 4 }}>Daily vibe widget</H3>
          </View>
          <Icon name="chevron" size={14} color={p.inkMute} />
        </Pressable>
      </FadeUp>
    </TabScroll>
  );
}
