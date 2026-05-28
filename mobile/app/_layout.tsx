// Root layout — full chain (providers + fonts + AskOverlay), MINUS the
// expo-splash-screen manual calls that crashed on SDK 54 Android. The
// expo-splash-screen plugin in app.json handles the splash automatically.
import 'react-native-gesture-handler';
import { View, StyleSheet } from 'react-native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

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
  // Load fonts in the background; don't gate the UI on it.
  useHankenFonts({
    HankenGrotesk_400Regular,
    HankenGrotesk_500Medium,
    HankenGrotesk_700Bold,
    JetBrainsMono_500Medium,
    NotoSansDevanagari_400Regular,
  });

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
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
