import { View, Text, Pressable, StyleSheet } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTheme } from '@/constants/ThemeContext';
import { useApp } from '@/constants/AppContext';
import { fonts, radii } from '@/constants/theme';

export default function AskFab() {
  const { p, name } = useTheme();
  const { openAsk } = useApp();
  const insets = useSafeAreaInsets();

  // Sits above the bottom tab pill (~60px)
  const bottom = insets.bottom + 18 + 60;

  return (
    <Pressable
      onPress={() => openAsk()}
      style={[
        styles.fab,
        { bottom, backgroundColor: name === 'dark' ? p.ink : '#1a1612' },
      ]}
    >
      <View style={[styles.dot, { backgroundColor: p.gold, shadowColor: p.gold }]} />
      <Text style={[styles.label, { color: name === 'dark' ? p.bg0 : '#ffffff' }]}>Ask</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  fab: {
    position: 'absolute',
    right: 18,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 9,
    paddingHorizontal: 18,
    height: 42,
    borderRadius: radii.pill,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.5,
    shadowRadius: 24,
    elevation: 12,
  },
  dot: {
    width: 6, height: 6, borderRadius: 3,
    shadowOpacity: 0.8,
    shadowOffset: { width: 0, height: 0 },
    shadowRadius: 6,
  },
  label: {
    fontFamily: fonts.sansMedium,
    fontSize: 12,
    letterSpacing: 1.7,
    textTransform: 'uppercase',
  },
});
