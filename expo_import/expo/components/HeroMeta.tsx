import { View, Text, StyleSheet } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SEVEN_DAYS } from '@/constants/data';
import WhyToggle from './WhyToggle';

export default function HeroMeta({ day }: { day: number }) {
  const { p } = useTheme();
  const d = SEVEN_DAYS[day];
  return (
    <View style={{ paddingHorizontal: 22, paddingTop: 20 }}>
      <Row label="Opportunity" body={d.op} labelColor={p.gold} />
      <Row label="Caution"     body={d.caution} labelColor={p.rose} bottomBorder />
      <WhyToggle sanskrit={d.sanskrit}>{d.why}</WhyToggle>
    </View>
  );
}

function Row({
  label, body, labelColor, bottomBorder,
}: {
  label: string;
  body: string;
  labelColor: string;
  bottomBorder?: boolean;
}) {
  const { p } = useTheme();
  return (
    <View style={[
      styles.row,
      { borderTopColor: p.hairline, borderBottomColor: bottomBorder ? p.hairline : 'transparent' },
    ]}>
      <Text style={[styles.label, { color: labelColor }]}>{label}</Text>
      <Text style={[styles.body, { color: p.ink }]}>{body}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingVertical: 12,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    gap: 14,
  },
  label: {
    fontFamily: fonts.sansMedium,
    fontSize: 10,
    letterSpacing: 2.2,
    textTransform: 'uppercase',
    width: 96,
    marginTop: 2,
  },
  body: {
    flex: 1,
    fontFamily: fonts.sans,
    fontSize: 13,
    lineHeight: 19,
  },
});
