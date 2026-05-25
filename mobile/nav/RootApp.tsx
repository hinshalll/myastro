import React from 'react';
import { View, ScrollView, Pressable, Text } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { fonts, useTheme } from '@/theme/theme';
import { AppBackground } from '@/ui/Background';
import { TabBar, AskFab, TabId } from '@/ui/Chrome';
import { Icon } from '@/ui/Icon';
import { H3, Body, Kicker } from '@/ui/Type';
import { NavProvider, useNav, ScreenId } from '@/nav/NavContext';
import { Placeholder } from '@/screens/Placeholder';
import {
  TodayScreen, TimingScreen, RitualsHub, RitualDetail, MalaScreen, SignalPreviewScreen,
} from '@/screens/today';
import { ChartScreen, YouScreen } from '@/screens/chart';

// Which tab each screen belongs to (for the active highlight)
const TAB_GROUPS: Record<TabId, ScreenId[]> = {
  today: ['today', 'rituals-hub', 'ritual-detail', 'mala', 'timing', 'signal-preview'],
  people: ['people', 'person-detail', 'household', 'couple', 'compat', 'add-person'],
  explore: ['explore', 'tarot', 'numerology', 'best-time', 'palm', 'face'],
  you: ['you', 'chart', 'chapters', 'past-date', 'patterns', 'year', 'purpose', 'reading', 'settings', 'widget'],
};

const HIDE_CHROME = ['onboarding-welcome', 'onboarding-birth', 'onboarding-time', 'onboarding-reveal', 'widget', 'paywall', 'signal-preview'];

const TITLES: Record<string, string> = {
  people: 'People', explore: 'Explore', you: 'You', paywall: 'Myastro+',
};

function renderScreen(screen: ScreenId) {
  switch (screen) {
    case 'today': return <TodayScreen />;
    case 'timing': return <TimingScreen />;
    case 'rituals-hub': return <RitualsHub />;
    case 'ritual-detail': return <RitualDetail />;
    case 'mala': return <MalaScreen />;
    case 'signal-preview': return <SignalPreviewScreen />;
    case 'you': return <YouScreen />;
    case 'chart': return <ChartScreen />;
    default: return <Placeholder title={TITLES[screen] ?? screen} />;
  }
}

// Temporary Ask overlay until the full conversational screen is ported
const AskOverlay = ({ onClose }: { onClose: () => void }) => {
  const { c } = useTheme();
  const insets = useSafeAreaInsets();
  return (
    <View style={{ position: 'absolute', inset: 0, zIndex: 70 }}>
      <Pressable onPress={onClose} style={{ position: 'absolute', inset: 0, backgroundColor: 'rgba(2,1,8,0.7)' }} />
      <View style={{ position: 'absolute', left: 0, right: 0, bottom: 0, backgroundColor: c.bg0, borderTopLeftRadius: 28, borderTopRightRadius: 28, borderTopWidth: 1, borderColor: c.border, paddingTop: 14, paddingBottom: insets.bottom + 24, paddingHorizontal: 22 }}>
        <View style={{ width: 36, height: 4, borderRadius: 2, backgroundColor: c.inkMute, alignSelf: 'center', marginBottom: 14, opacity: 0.6 }} />
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <Icon name="ask" size={22} color={c.gold} />
          <H3>Ask the stars</H3>
        </View>
        <Body>Type anything — &ldquo;should I text my ex?&rdquo;, &ldquo;is this a good week to switch jobs?&rdquo; The full conversational astrologer is being built next.</Body>
        <Kicker style={{ marginTop: 16 }}>Coming soon</Kicker>
      </View>
    </View>
  );
};

const Shell = () => {
  const { c } = useTheme();
  const insets = useSafeAreaInsets();
  const { screen, nav, askOpen, setAskOpen } = useNav();
  const activeTab = (Object.keys(TAB_GROUPS) as TabId[]).find(k => TAB_GROUPS[k].includes(screen)) ?? null;
  const showChrome = !HIDE_CHROME.includes(screen);

  return (
    <View style={{ flex: 1, backgroundColor: c.bg0 }}>
      <AppBackground />
      <ScrollView
        key={screen}
        style={{ flex: 1 }}
        contentContainerStyle={{ paddingTop: insets.top + 6, paddingBottom: showChrome ? 130 : insets.bottom + 24, flexGrow: 1 }}
        showsVerticalScrollIndicator={false}
      >
        {renderScreen(screen)}
      </ScrollView>

      {showChrome ? <TabBar active={activeTab} onNav={(t) => nav(t)} bottom={insets.bottom + 14} /> : null}
      {showChrome ? <AskFab onPress={() => setAskOpen(true)} bottom={insets.bottom + 78} /> : null}
      {askOpen ? <AskOverlay onClose={() => setAskOpen(false)} /> : null}
    </View>
  );
};

export const RootApp = () => (
  <NavProvider start="today">
    <Shell />
  </NavProvider>
);
