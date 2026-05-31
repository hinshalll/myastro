import { useState } from 'react';
import { View, Pressable } from 'react-native';
import { useTheme } from '@/constants/ThemeContext';
import { SubScreen, Body, Kicker, Display, Btn, Icon } from '@/components/ui';

const CARDS = [
  { name: 'The window', meaning: "A door opens where you weren't looking." },
  { name: 'The flame', meaning: 'Burn the half-thing so the whole can arrive.' },
  { name: 'The river', meaning: "You've been ready longer than you knew." },
  { name: 'The bird', meaning: 'Permission. Take it.' },
  { name: 'The seed', meaning: 'Quiet weeks now mean a loud spring.' },
];

export default function Tarot() {
  const { p } = useTheme();
  const [picked, setPicked] = useState<typeof CARDS[number] | null>(null);

  return (
    <SubScreen title="Pick a card">
      <View style={{ paddingHorizontal: 22, paddingTop: 8, alignItems: 'center' }}>
        <Body style={{ textAlign: 'center', maxWidth: 280, marginBottom: 28 }}>Hold your question in mind. Tap a card.</Body>

        {!picked ? (
          <View style={{ height: 280, width: '100%', alignItems: 'center', justifyContent: 'center' }}>
            {[-2, -1, 0, 1, 2].map(i => (
              <Pressable
                key={i}
                onPress={() => setPicked(CARDS[i + 2])}
                style={{
                  position: 'absolute', width: 110, height: 170, borderRadius: 12, padding: 10,
                  transform: [{ translateX: i * 34 }, { translateY: Math.abs(i) * 6 }, { rotate: `${i * 5}deg` }],
                  borderWidth: 1, borderColor: p.gold, backgroundColor: '#14101e',
                  shadowColor: '#000', shadowOpacity: 0.5, shadowRadius: 24, shadowOffset: { width: 0, height: 10 }, elevation: 8,
                }}
              >
                <View style={{ flex: 1, borderWidth: 1, borderColor: p.gold, borderRadius: 6, alignItems: 'center', justifyContent: 'center' }}>
                  <Icon name="logo" size={42} color={p.gold} />
                </View>
              </Pressable>
            ))}
          </View>
        ) : (
          <View style={{ alignItems: 'center' }}>
            <View style={{ width: 200, height: 290, borderRadius: 14, padding: 16, borderWidth: 1, borderColor: p.gold, backgroundColor: '#2a1542', justifyContent: 'space-between' }}>
              <Kicker color="rgba(236,230,212,0.6)">Today</Kicker>
              <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
                <Icon name="logo" size={72} color={p.gold} />
              </View>
              <Display size={20} color={p.gold}>{picked.name}</Display>
            </View>
            <Display size={24} style={{ marginTop: 22, textAlign: 'center', paddingHorizontal: 8 }}>{picked.meaning}</Display>
            <Btn label="Pick again" variant="ghost" style={{ marginTop: 22 }} onPress={() => setPicked(null)} />
          </View>
        )}
      </View>
    </SubScreen>
  );
}
