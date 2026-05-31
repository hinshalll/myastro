import { useState } from 'react';
import { View, Text, Pressable } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Kicker, Display } from '@/components/ui';

export default function Mala() {
  const { p } = useTheme();
  const [count, setCount] = useState(43);

  return (
    <SubScreen title="Mala" scroll={false}>
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 22 }}>
        <Kicker style={{ marginBottom: 12 }}>108 to complete · {108 - count} left</Kicker>
        <Display size={96} style={{ lineHeight: 100 }}>{count}</Display>

        <Pressable
          onPress={() => setCount(c => Math.min(108, c + 1))}
          style={{
            marginTop: 28, width: 220, height: 220, borderRadius: 110,
            alignItems: 'center', justifyContent: 'center',
            backgroundColor: '#8b6a2b',
            shadowColor: p.gold, shadowOpacity: 0.5, shadowRadius: 50, shadowOffset: { width: 0, height: 0 }, elevation: 14,
          }}
        >
          <Text style={{ fontFamily: fonts.sansMedium, fontSize: 16, color: '#1d1408' }}>tap</Text>
        </Pressable>

        <View style={{ marginTop: 32, flexDirection: 'row', gap: 24, alignItems: 'center' }}>
          <Kicker>streak 5</Kicker>
          <Kicker>·</Kicker>
          <Pressable onPress={() => setCount(0)}><Kicker color={p.gold}>reset</Kicker></Pressable>
        </View>
      </View>
    </SubScreen>
  );
}
