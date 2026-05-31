import { useState } from 'react';
import { View, Text, Pressable, StyleSheet, LayoutAnimation, Platform, UIManager } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';

if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

export default function WhyToggle({
  children,
  sanskrit,
}: {
  children: string;
  sanskrit?: string;
}) {
  const [open, setOpen] = useState(false);
  const { p } = useTheme();

  const onPress = () => {
    LayoutAnimation.configureNext(LayoutAnimation.create(220, 'easeInEaseOut', 'opacity'));
    setOpen(o => !o);
  };

  return (
    <View style={{ marginTop: 14 }}>
      <Pressable onPress={onPress} hitSlop={8} style={styles.toggle}>
        <View style={[styles.dash, { backgroundColor: p.gold }]} />
        <Text style={[styles.label, { color: p.gold }]}>why</Text>
        <Text style={[styles.caret, { color: p.gold, transform: [{ rotate: open ? '90deg' : '0deg' }] }]}>
          ›
        </Text>
      </Pressable>
      {open && (
        <View style={[styles.panel, { borderTopColor: p.hairline }]}>
          {!!sanskrit && (
            <Text style={[styles.deva, { color: p.inkMute }]}>{sanskrit}</Text>
          )}
          <Text style={[styles.body, { color: p.inkSoft }]}>{children}</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  toggle: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  dash: { width: 10, height: 1 },
  label: {
    fontFamily: fonts.sansMedium,
    fontSize: 10,
    letterSpacing: 2.2,
    textTransform: 'uppercase',
  },
  caret: { fontSize: 12 },
  panel: {
    marginTop: 10,
    paddingTop: 12,
    borderTopWidth: 1,
  },
  deva: {
    fontFamily: fonts.deva,
    fontSize: 12,
    marginBottom: 8,
  },
  body: {
    fontFamily: fonts.sans,
    fontSize: 13,
    lineHeight: 20,
  },
});
