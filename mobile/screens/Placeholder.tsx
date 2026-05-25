import React from 'react';
import { View } from 'react-native';
import { useTheme } from '@/theme/theme';
import { H2, Body, Kicker } from '@/ui/Type';
import { Icon } from '@/ui/Icon';
import { AppBar } from '@/ui/primitives';
import { useNav } from '@/nav/NavContext';

export const Placeholder = ({ title }: { title: string }) => {
  const { c } = useTheme();
  const { back, screen } = useNav();
  return (
    <View style={{ flex: 1 }}>
      <AppBar title={title} onBack={back} />
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', padding: 40, gap: 14 }}>
        <Icon name="sparkle" size={28} color={c.gold} />
        <Kicker>{screen}</Kicker>
        <H2 style={{ textAlign: 'center' }}>{title}</H2>
        <Body style={{ textAlign: 'center' }}>This screen is being built next. The design is in — we&apos;re porting it screen by screen.</Body>
      </View>
    </View>
  );
};
