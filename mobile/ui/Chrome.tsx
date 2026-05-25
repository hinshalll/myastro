import React from 'react';
import { View, Pressable, Text } from 'react-native';
import { fonts, useTheme } from '@/theme/theme';
import { Icon, IconName } from '@/ui/Icon';

export type TabId = 'today' | 'people' | 'explore' | 'you';

const TABS: { id: TabId; label: string; icon: IconName }[] = [
  { id: 'today', label: 'Today', icon: 'today' },
  { id: 'people', label: 'People', icon: 'people' },
  { id: 'explore', label: 'Explore', icon: 'explore' },
  { id: 'you', label: 'You', icon: 'you' },
];

export const TabBar = ({ active, onNav, bottom = 38 }: { active: TabId | null; onNav: (t: TabId) => void; bottom?: number }) => {
  const { c } = useTheme();
  return (
    <View style={{
      position: 'absolute', left: 14, right: 14, bottom,
      height: 60, backgroundColor: c.tabBarBg, borderWidth: 1, borderColor: c.border,
      borderRadius: 30, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around',
      paddingHorizontal: 8,
    }}>
      {TABS.map(t => {
        const on = active === t.id;
        return (
          <Pressable key={t.id} onPress={() => onNav(t.id)} style={{ flex: 1, height: '100%', alignItems: 'center', justifyContent: 'center', gap: 4 }}>
            <Icon name={t.icon} size={20} color={on ? c.ink : c.inkMute} />
            <View style={{ width: 5, height: 5, borderRadius: 2.5, backgroundColor: on ? c.gold : 'transparent' }} />
          </Pressable>
        );
      })}
    </View>
  );
};

export const AskFab = ({ onPress, bottom = 100 }: { onPress: () => void; bottom?: number }) => {
  const { c } = useTheme();
  return (
    <Pressable onPress={onPress} style={({ pressed }) => ({
      position: 'absolute', right: 18, bottom,
      height: 48, paddingLeft: 14, paddingRight: 18, borderRadius: 24,
      backgroundColor: c.ink, flexDirection: 'row', alignItems: 'center', gap: 8,
      transform: [{ translateY: pressed ? -2 : 0 }],
      shadowColor: '#000', shadowOpacity: 0.5, shadowRadius: 12, shadowOffset: { width: 0, height: 8 }, elevation: 8,
    })}>
      <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: c.gold }} />
      <Text style={{ fontFamily: fonts.sans500, fontSize: 14, color: c.bg0, letterSpacing: 0.2 }}>Ask</Text>
    </Pressable>
  );
};
