import { useState } from 'react';
import { View, Pressable } from 'react-native';
import { router } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { useTheme } from '@/constants/ThemeContext';
import ConstellationBG from '@/components/ConstellationBG';
import { Kicker, H1, Body, Small, Btn, Field, Input, Icon } from '@/components/ui';

export default function Birth() {
  const { p } = useTheme();
  const insets = useSafeAreaInsets();
  const [name, setName] = useState('Aarav');
  const [date, setDate] = useState('1995-08-14');
  const [place, setPlace] = useState('Chennai, India');

  return (
    <View style={{ flex: 1, backgroundColor: p.bg0 }}>
      <ConstellationBG />
      <View style={{ paddingTop: insets.top + 8, paddingHorizontal: 16 }}>
        <Pressable onPress={() => router.back()} hitSlop={10} style={{ width: 36, height: 36, borderRadius: 18, borderWidth: 1, borderColor: p.border, alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="back" size={18} />
        </Pressable>
      </View>

      <View style={{ flex: 1, paddingHorizontal: 28, paddingTop: 24 }}>
        <Kicker style={{ marginBottom: 14 }}>Step 1 · 3</Kicker>
        <H1>A few quiet questions.</H1>
        <Body style={{ marginTop: 8 }}>Once. Then they're yours forever, in Settings.</Body>

        <View style={{ marginTop: 32, gap: 18 }}>
          <Field label="What should we call you?">
            <Input value={name} onChangeText={setName} placeholder="First name" />
          </Field>
          <Field label="When were you born?">
            <Input value={date} onChangeText={setDate} placeholder="YYYY-MM-DD" />
          </Field>
          <Field label="Where were you born?">
            <Input value={place} onChangeText={setPlace} placeholder="City, country" />
            <Small style={{ marginTop: 6 }}>City matters more than the exact pin. Common Indian cities supported.</Small>
          </Field>
        </View>
      </View>

      <View style={{ paddingHorizontal: 22, paddingBottom: insets.bottom + 24 }}>
        <Btn label="Continue →" variant="primary" size="lg" block onPress={() => router.push('/onboarding/time')} />
      </View>
    </View>
  );
}
