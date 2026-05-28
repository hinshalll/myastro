// Myastro — shared UI primitives.
// Editorial-quiet system: hairlines over chrome, restrained gold, calm type.
// Screens compose these so the visual language stays consistent.

import { ReactNode } from 'react';
import {
  View, Text, Pressable, ScrollView, TextInput, StyleSheet,
  ViewStyle, TextStyle, StyleProp, TextInputProps,
} from 'react-native';
import { router } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Animated, { FadeInDown } from 'react-native-reanimated';

import { useTheme } from '@/constants/ThemeContext';
import { useApp } from '@/constants/AppContext';
import { fonts, radii, text as T, Palette } from '@/constants/theme';
import Icon, { IconName } from './Icon';
import ConstellationBG from './ConstellationBG';

type TxtProps = { children: ReactNode; color?: string; style?: StyleProp<TextStyle>; numberOfLines?: number };

// ─── Type ───
export function Display({ children, size = 19, color, style, numberOfLines }: TxtProps & { size?: number }) {
  const { p } = useTheme();
  return (
    <Text numberOfLines={numberOfLines} style={[{
      fontFamily: fonts.sansMedium, fontSize: size, lineHeight: size * 1.22,
      letterSpacing: -0.2, color: color ?? p.ink,
    }, style]}>{children}</Text>
  );
}
export function H1({ children, color, style }: TxtProps) {
  const { p } = useTheme();
  return <Text style={[T.h1, { color: color ?? p.ink }, style]}>{children}</Text>;
}
export function H2({ children, color, style }: TxtProps) {
  const { p } = useTheme();
  return <Text style={[T.h2, { color: color ?? p.ink }, style]}>{children}</Text>;
}
export function H3({ children, color, style }: TxtProps) {
  const { p } = useTheme();
  return <Text style={[T.h3, { color: color ?? p.ink }, style]}>{children}</Text>;
}
export function Body({ children, color, style }: TxtProps) {
  const { p } = useTheme();
  return <Text style={[T.body, { color: color ?? p.inkSoft }, style]}>{children}</Text>;
}
export function Small({ children, color, style }: TxtProps) {
  const { p } = useTheme();
  return <Text style={[T.small, { color: color ?? p.inkMute }, style]}>{children}</Text>;
}
export function Kicker({ children, color, style }: TxtProps) {
  const { p } = useTheme();
  return <Text style={[T.kicker, { color: color ?? p.inkMute }, style]}>{children}</Text>;
}
export function Mono({ children, color, style }: TxtProps) {
  const { p } = useTheme();
  return <Text style={[T.mono, { color: color ?? p.inkMute }, style]}>{children}</Text>;
}

// ─── Surfaces ───
export function Card({ children, style }: { children?: ReactNode; style?: StyleProp<ViewStyle> }) {
  const { p } = useTheme();
  return <View style={[{ backgroundColor: p.surface, borderWidth: 1, borderColor: p.border, borderRadius: radii.md }, style]}>{children}</View>;
}
export function CardStrong({ children, style }: { children?: ReactNode; style?: StyleProp<ViewStyle> }) {
  const { p } = useTheme();
  return <View style={[{ backgroundColor: p.surfaceStrong, borderWidth: 1, borderColor: p.borderStrong, borderRadius: radii.md }, style]}>{children}</View>;
}
export function Hr({ style }: { style?: StyleProp<ViewStyle> }) {
  const { p } = useTheme();
  return <View style={[{ height: 1, backgroundColor: p.hairline }, style]} />;
}

// ─── Chip ───
export function Chip({
  label, active, gold, onPress, style,
}: { label: string; active?: boolean; gold?: boolean; onPress?: () => void; style?: StyleProp<ViewStyle> }) {
  const { p } = useTheme();
  const bg = active ? p.ink : gold ? p.goldSoft : p.surface;
  const fg = active ? p.bg0 : gold ? p.gold : p.inkSoft;
  const bc = active ? p.ink : gold ? p.gold : p.border;
  return (
    <Pressable onPress={onPress} style={[styles.chip, { backgroundColor: bg, borderColor: bc }, style]}>
      <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, color: fg, letterSpacing: 0.2 }}>{label}</Text>
    </Pressable>
  );
}

// ─── Button ───
type BtnVariant = 'primary' | 'gold' | 'ghost' | 'default';
export function Btn({
  label, onPress, variant = 'default', size = 'md', block, left, style,
}: {
  label: string; onPress?: () => void; variant?: BtnVariant;
  size?: 'sm' | 'md' | 'lg'; block?: boolean; left?: ReactNode; style?: StyleProp<ViewStyle>;
}) {
  const { p, name } = useTheme();
  const pad = size === 'lg' ? { paddingVertical: 17, paddingHorizontal: 24 }
    : size === 'sm' ? { paddingVertical: 8, paddingHorizontal: 14 }
    : { paddingVertical: 13, paddingHorizontal: 22 };
  const fs = size === 'lg' ? 15 : size === 'sm' ? 12 : 14;

  let bg = 'transparent', fg = p.ink, bc = p.borderStrong;
  if (variant === 'primary') { bg = name === 'dark' ? p.ink : '#1a1612'; fg = name === 'dark' ? p.bg0 : '#fff'; bc = bg; }
  if (variant === 'gold')    { bg = p.gold; fg = '#1a1408'; bc = p.gold; }
  if (variant === 'ghost')   { bg = 'transparent'; fg = p.ink; bc = p.border; }

  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [
        styles.btn, pad,
        { backgroundColor: bg, borderColor: bc, opacity: pressed ? 0.85 : 1 },
        block && { alignSelf: 'stretch' },
        style,
      ]}
    >
      {left}
      <Text style={{ fontFamily: fonts.sansMedium, fontSize: fs, color: fg }}>{label}</Text>
    </Pressable>
  );
}

// ─── Premium tag ───
export function PremiumTag({ label = 'Myastro+' }: { label?: string }) {
  const { p } = useTheme();
  return (
    <View style={[styles.tag, { backgroundColor: p.goldSoft, borderColor: p.gold }]}>
      <Text style={{ fontFamily: fonts.sansMedium, fontSize: 9, letterSpacing: 1.2, textTransform: 'uppercase', color: p.gold }}>{label}</Text>
    </View>
  );
}

// ─── Avatar ───
export function Avatar({ initials, size = 40, style }: { initials: string; size?: number; style?: StyleProp<ViewStyle> }) {
  const { p } = useTheme();
  return (
    <View style={[{
      width: size, height: size, borderRadius: size / 2,
      backgroundColor: p.surfaceStrong, borderWidth: 1, borderColor: p.border,
      alignItems: 'center', justifyContent: 'center',
    }, style]}>
      <Text style={{ fontFamily: fonts.sansMedium, fontSize: size * 0.36, color: p.ink }}>{initials}</Text>
    </View>
  );
}

// ─── List row ───
export function ListRow({ children, last, onPress, style }: { children: ReactNode; last?: boolean; onPress?: () => void; style?: StyleProp<ViewStyle> }) {
  const { p } = useTheme();
  const inner = (
    <View style={[styles.listRow, { borderBottomColor: last ? 'transparent' : p.hairline }, style]}>
      {children}
    </View>
  );
  return onPress ? <Pressable onPress={onPress}>{inner}</Pressable> : inner;
}

// ─── App bar ───
export function AppBar({ title = '', right, onBack }: { title?: string; right?: ReactNode; onBack?: () => void }) {
  const { p } = useTheme();
  return (
    <View style={styles.appBar}>
      <Pressable onPress={onBack ?? (() => router.back())} hitSlop={10} style={[styles.appBarIcon, { borderColor: p.border }]}>
        <Icon name="back" size={18} />
      </Pressable>
      <Text style={[styles.appBarTitle, { color: p.ink }]} numberOfLines={1}>{title}</Text>
      <View style={{ width: 36, alignItems: 'flex-end' }}>{right}</View>
    </View>
  );
}

export function AppBarIconBtn({ icon, onPress }: { icon: IconName; onPress?: () => void }) {
  const { p } = useTheme();
  return (
    <Pressable onPress={onPress} hitSlop={8} style={[styles.appBarIcon, { borderColor: p.border }]}>
      <Icon name={icon} size={16} />
    </Pressable>
  );
}

// ─── Precision banner (reads onboarding tier) ───
export function PrecisionBanner() {
  const { p } = useTheme();
  const { precision } = useApp();
  if (precision === 'exact') return null;
  const cfg = precision === 'approximate'
    ? { color: p.inkMute, txt: 'Birth time approximate · some readings flagged' }
    : { color: p.rose, txt: 'Moon-chart mode · add your time to unlock more' };
  return (
    <View style={[styles.precision, { backgroundColor: p.surface, borderColor: p.border }]}>
      <View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: cfg.color }} />
      <Text style={{ flex: 1, fontFamily: fonts.sansMedium, fontSize: 11, color: p.inkSoft }}>{cfg.txt}</Text>
      <Text style={{ fontFamily: fonts.sans, fontSize: 12, color: p.gold }}>Add →</Text>
    </View>
  );
}

// ─── Fade-up entrance (editorial reveal) ───
export function FadeUp({ children, delay = 0, style }: { children: ReactNode; delay?: number; style?: StyleProp<ViewStyle> }) {
  return (
    <Animated.View entering={FadeInDown.duration(450).delay(delay)} style={style}>
      {children}
    </Animated.View>
  );
}

// ─── Editorial divider section (hairline top + kicker) ───
export function EditSection({
  kicker, right, children, first, style,
}: { kicker?: string; right?: ReactNode; children: ReactNode; first?: boolean; style?: StyleProp<ViewStyle> }) {
  const { p } = useTheme();
  return (
    <View style={[{ paddingHorizontal: 22, paddingTop: 24, marginTop: 22 }, !first && { borderTopWidth: 1, borderTopColor: p.hairline }, style]}>
      {(kicker || right) && (
        <View style={styles.sectionHead}>
          {!!kicker && <Kicker>{kicker}</Kicker>}
          {right}
        </View>
      )}
      {children}
    </View>
  );
}

// ─── Sub-screen scaffold — full screen pushed over the tabs ───
export function SubScreen({
  title, right, children, scroll = true, onBack, contentStyle,
}: {
  title?: string; right?: ReactNode; children: ReactNode;
  scroll?: boolean; onBack?: () => void; contentStyle?: StyleProp<ViewStyle>;
}) {
  const { p } = useTheme();
  const insets = useSafeAreaInsets();
  return (
    <View style={{ flex: 1, backgroundColor: p.bg0 }}>
      <ConstellationBG />
      <View style={{ paddingTop: insets.top }}>
        {title !== undefined && <AppBar title={title} right={right} onBack={onBack} />}
      </View>
      {scroll ? (
        <ScrollView
          showsVerticalScrollIndicator={false}
          contentContainerStyle={[{ paddingBottom: insets.bottom + 48 }, contentStyle]}
        >
          {children}
        </ScrollView>
      ) : (
        <View style={[{ flex: 1 }, contentStyle]}>{children}</View>
      )}
    </View>
  );
}

// ─── Tab-screen scroll — content lives under the persistent TopBar; leaves
// room for the floating pill + Ask FAB at the bottom. ───
export function TabScroll({ children, contentStyle }: { children: ReactNode; contentStyle?: StyleProp<ViewStyle> }) {
  const insets = useSafeAreaInsets();
  return (
    <ScrollView
      showsVerticalScrollIndicator={false}
      contentContainerStyle={[{ paddingBottom: insets.bottom + 150 }, contentStyle]}
    >
      {children}
    </ScrollView>
  );
}

// ─── Form field + styled input ───
export function Field({ label, children, style }: { label: string; children: ReactNode; style?: StyleProp<ViewStyle> }) {
  return (
    <View style={style}>
      <Kicker style={{ marginBottom: 8 }}>{label}</Kicker>
      {children}
    </View>
  );
}

export function Input({ style, ...props }: TextInputProps) {
  const { p } = useTheme();
  return (
    <TextInput
      placeholderTextColor={p.inkMute}
      style={[{
        fontFamily: fonts.sans, fontSize: 16, color: p.ink,
        backgroundColor: p.surface, borderWidth: 1, borderColor: p.border,
        borderRadius: 12, paddingHorizontal: 16, paddingVertical: 15,
      }, style]}
      {...props}
    />
  );
}

export { Icon };
export type { Palette };

const styles = StyleSheet.create({
  chip: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingVertical: 6, paddingHorizontal: 12, borderRadius: radii.pill, borderWidth: 1,
  },
  btn: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    borderRadius: radii.pill, borderWidth: 1,
  },
  tag: {
    flexDirection: 'row', alignItems: 'center', alignSelf: 'flex-start',
    paddingVertical: 3, paddingHorizontal: 8, borderRadius: radii.pill, borderWidth: 1,
  },
  listRow: {
    flexDirection: 'row', alignItems: 'center', gap: 14,
    paddingVertical: 14, paddingHorizontal: 18, borderBottomWidth: 1,
  },
  appBar: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 18, paddingVertical: 6,
  },
  appBarIcon: {
    width: 36, height: 36, borderRadius: 18, borderWidth: 1,
    alignItems: 'center', justifyContent: 'center',
  },
  appBarTitle: { fontFamily: fonts.sansMedium, fontSize: 14, letterSpacing: 0.4, flex: 1, textAlign: 'center' },
  precision: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    paddingVertical: 10, paddingHorizontal: 14, marginHorizontal: 14, marginTop: 10,
    borderRadius: 12, borderWidth: 1,
  },
  sectionHead: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 12,
  },
});
