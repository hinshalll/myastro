import { View, Text, Pressable, StyleSheet } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts, vibeColor } from '@/constants/theme';
import { SEVEN_DAYS } from '@/constants/data';

export default function DayRail({
  active,
  onPick,
}: {
  active: number;
  onPick: (i: number) => void;
}) {
  const { p } = useTheme();
  return (
    <View style={styles.rail}>
      {SEVEN_DAYS.map((d, i) => {
        const isActive = i === active;
        const isToday = i === 0;
        const vc = vibeColor(p, d.vibe);
        return (
          <Pressable key={i} onPress={() => onPick(i)} style={styles.cell} hitSlop={4}>
            <Text style={[styles.wkd, { color: p.inkMute, opacity: isActive ? 1 : 0.7 }]}>
              {isToday ? 'Today' : d.wkd}
            </Text>
            <Text style={[
              styles.dt,
              { color: isActive ? p.ink : vc, opacity: isActive ? 1 : 0.95 },
            ]}>
              {d.dt}
            </Text>
            <View style={[styles.bar, { backgroundColor: vc, opacity: isActive ? 1 : 0.55 }]} />
            {isActive && (
              <View style={[styles.activeBar, { backgroundColor: p.ink }]} />
            )}
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  rail: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 22,
  },
  cell: {
    minWidth: 36,
    paddingVertical: 6,
    paddingHorizontal: 4,
    alignItems: 'center',
    gap: 5,
    position: 'relative',
  },
  wkd: {
    fontFamily: fonts.sansMedium,
    fontSize: 9,
    letterSpacing: 1.6,
    textTransform: 'uppercase',
  },
  dt: {
    fontFamily: fonts.sansMedium,
    fontSize: 15,
    lineHeight: 15,
  },
  bar: {
    width: 14,
    height: 2,
    borderRadius: 1,
  },
  activeBar: {
    position: 'absolute',
    bottom: -2,
    width: 22,
    height: 2,
    borderRadius: 1,
  },
});
