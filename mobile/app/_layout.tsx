import 'react-native-gesture-handler';
import { useEffect, useCallback } from 'react';
import { View, StyleSheet } from 'react-native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import * as SplashScreen from 'expo-splash-screen';

import {
  useFonts as useHankenFonts,
  HankenGrotesk_400Regular,
  HankenGrotesk_500Medium,
  HankenGrotesk_700Bold,
} from '@expo-google-fonts/hanken-grotesk';
import { JetBrainsMono_500Medium } from '@expo-google-fonts/jetbrains-mono';
import { NotoSansDevanagari_400Regular } from '@expo-google-fonts/noto-sans-devanagari';

import { ThemeProvider, useTheme } from '@/constants/ThemeContext';
import { AppProvider } from '@/constants/AppContext';

SplashScreen.preventAutoHideAsync().catch(() => {});

function AppFrame() {
  const { p, name } = useTheme();
  return (
    <View style={[styles.root, { backgroundColor: p.bg0 }]}>
      <StatusBar style={name === 'dark' ? 'light' : 'dark'} />
      <Stack screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: p.bg0 },
        animation: 'slide_from_right',
      }} />
    </View>
  );
}

export default function RootLayout() {
  const [loaded] = useHankenFonts({
    HankenGrotesk_400Regular,
    HankenGrotesk_500Medium,
    HankenGrotesk_700Bold,
    JetBrainsMono_500Medium,
    NotoSansDevanagari_400Regular,
  });

  const onLayoutRoot = useCallback(() => {
    if (loaded) SplashScreen.hideAsync().catch(() => {});
  }, [loaded]);

  if (!loaded) return null;

  return (
    <GestureHandlerRootView style={{ flex: 1 }} onLayout={onLayoutRoot}>
      <SafeAreaProvider>
        <ThemeProvider initial="dark">
          <AppProvider>
            <AppFrame />
          </AppProvider>
        </ThemeProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
});
