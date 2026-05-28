import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { ReactNode } from 'react';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';

export default function Section({
  kicker,
  right,
  children,
  divider = true,
  style,
}: {
  kicker?: string;
  right?: string | ReactNode;
  children: ReactNode;
  divider?: boolean;
  style?: ViewStyle;
}) {
  const { p } = useTheme();
  return (
    <View
      style={[
        { paddingHorizontal: 22, paddingTop: 24, marginTop: 22 },
        divider && { borderTopWidth: 1, borderTopColor: p.hairline },
        style,
      ]}
    >
      {(kicker || right) && (
        <View style={styles.head}>
          {!!kicker && <Text style={[styles.kicker, { color: p.inkMute }]}>{kicker}</Text>}
          {typeof right === 'string' ? <Text style={[styles.right, { color: p.inkMute }]}>{right}</Text> : right}
        </View>
      )}
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  head: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'baseline',
    marginBottom: 10,
  },
  kicker: {
    fontFamily: fonts.sansMedium,
    fontSize: 10,
    letterSpacing: 2.2,
    textTransform: 'uppercase',
  },
  right: { fontFamily: fonts.sans, fontSize: 12 },
});
