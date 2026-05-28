import { Tabs, router } from 'expo-router';
import { View, Text, Pressable, StyleSheet, Platform } from 'react-native';
import { BlurView } from 'expo-blur';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { useTheme } from '@/constants/ThemeContext';
import { fonts, radii } from '@/constants/theme';
import TopBar from '@/components/TopBar';
import AskFab from '@/components/AskFab';
import ConstellationBG from '@/components/ConstellationBG';

const TABS = [
  { name: 'today',   label: 'Today'   },
  { name: 'people',  label: 'People'  },
  { name: 'explore', label: 'Explore' },
  { name: 'you',     label: 'You'     },
] as const;

export default function TabsLayout() {
  const { p, name } = useTheme();
  const insets = useSafeAreaInsets();

  return (
    <View style={{ flex: 1, backgroundColor: p.bg0 }}>
      <ConstellationBG />
      <TopBar
        onBell={() => router.push('/signal-preview')}
        onSettings={() => router.push('/settings')}
      />

      <Tabs
        screenOptions={{
          headerShown: false,
          sceneStyle: { backgroundColor: p.bg0 },
        }}
        tabBar={({ state, navigation }) => (
          <FloatingPill
            insetsBottom={insets.bottom}
            active={state.routes[state.index].name}
            onPress={(routeName) => navigation.navigate(routeName as never)}
            themeName={name}
          />
        )}
      >
        {TABS.map(t => (
          <Tabs.Screen key={t.name} name={t.name} options={{ title: t.label }} />
        ))}
      </Tabs>

      <AskFab />
    </View>
  );
}

function FloatingPill({
  active, onPress, insetsBottom, themeName,
}: {
  active: string;
  onPress: (route: string) => void;
  insetsBottom: number;
  themeName: 'dark' | 'light';
}) {
  const { p } = useTheme();
  return (
    <View pointerEvents="box-none" style={[styles.pillWrap, { bottom: insetsBottom + 18 }]}>
      <BlurView
        intensity={Platform.OS === 'ios' ? 40 : 30}
        tint={themeName === 'dark' ? 'dark' : 'light'}
        style={[styles.pill, { borderColor: p.border, backgroundColor: themeName === 'dark' ? 'rgba(11,9,7,0.6)' : 'rgba(255,255,255,0.7)' }]}
      >
        {TABS.map(t => {
          const isActive = t.name === active;
          return (
            <Pressable
              key={t.name}
              onPress={() => onPress(t.name)}
              style={[
                styles.tab,
                isActive && { backgroundColor: themeName === 'dark' ? p.ink : '#1a1612' },
              ]}
              hitSlop={6}
            >
              <Text style={[
                styles.tabText,
                { color: isActive ? (themeName === 'dark' ? p.bg0 : '#ffffff') : p.inkMute },
              ]}>
                {t.label}
              </Text>
            </Pressable>
          );
        })}
      </BlurView>
    </View>
  );
}

const styles = StyleSheet.create({
  pillWrap: {
    position: 'absolute',
    left: 0, right: 0,
    alignItems: 'center',
  },
  pill: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 5,
    borderRadius: radii.pill,
    borderWidth: 1,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.35,
    shadowRadius: 24,
    elevation: 12,
  },
  tab: {
    paddingVertical: 9,
    paddingHorizontal: 14,
    borderRadius: radii.pill,
  },
  tabText: {
    fontFamily: fonts.sansMedium,
    fontSize: 11,
    letterSpacing: 1.7,
    textTransform: 'uppercase',
  },
});
