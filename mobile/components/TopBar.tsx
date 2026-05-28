import { View, Text, Pressable, StyleSheet } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Svg, { Defs, RadialGradient, Stop, Circle } from 'react-native-svg';

import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';

export default function TopBar({ onBell, onSettings }: { onBell?: () => void; onSettings?: () => void }) {
  const { p } = useTheme();
  const insets = useSafeAreaInsets();

  return (
    <View style={[styles.row, { paddingTop: insets.top + 8 }]}>
      <View style={styles.brand}>
        <BrandMark />
        <Text style={[styles.brandText, { color: p.ink }]}>Myastro</Text>
      </View>

      <View style={styles.right}>
        <IconBtn onPress={onBell} glyph="bell" />
        <IconBtn onPress={onSettings} glyph="settings" />
      </View>
    </View>
  );
}

function BrandMark() {
  return (
    <Svg width={10} height={10} viewBox="0 0 10 10">
      <Defs>
        <RadialGradient id="m" cx="35%" cy="32%" r="60%">
          <Stop offset="0%" stopColor="#f3d99a" />
          <Stop offset="55%" stopColor="#d4af6b" />
          <Stop offset="100%" stopColor="#4f3608" />
        </RadialGradient>
      </Defs>
      <Circle cx="5" cy="5" r="5" fill="url(#m)" />
    </Svg>
  );
}

function IconBtn({ onPress, glyph }: { onPress?: () => void; glyph: 'bell' | 'settings' }) {
  const { p } = useTheme();
  // Use a unicode glyph so we don't depend on an icon font. Replace with @expo/vector-icons later if you want.
  const ch = glyph === 'bell' ? '\u25EF' : '\u2699';
  return (
    <Pressable onPress={onPress} hitSlop={10} style={styles.iconBtn}>
      <Text style={{ color: p.inkMute, fontSize: 15 }}>{ch}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 22,
    paddingBottom: 14,
  },
  brand: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  brandText: {
    fontFamily: fonts.sansMedium,
    fontSize: 11,
    letterSpacing: 3,
    textTransform: 'uppercase',
  },
  right: { flexDirection: 'row', gap: 14 },
  iconBtn: { width: 28, height: 28, alignItems: 'center', justifyContent: 'center' },
});
