import React from "react";
import { View, Text, ScrollView, Platform } from "react-native";
import { StatusBar } from "expo-status-bar";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { useAppFonts } from "./src/ui/useAppFonts";
import { PAPER } from "./src/ui/palette";
import { AstroApp } from "./src/AstroApp";

// Web only: react-native-web draws a focus outline on inputs via a stylesheet rule that
// inline styles can't override. It showed as a square "golden border" poking past the
// rounded Mirror page. Kill it once, globally. (No-op on native.)
if (Platform.OS === "web" && typeof document !== "undefined" && !document.getElementById("rnw-focus-reset")) {
  const st = document.createElement("style");
  st.id = "rnw-focus-reset";
  st.textContent = "input:focus,input:focus-visible,textarea:focus,textarea:focus-visible,[contenteditable]:focus{outline:none !important;}";
  document.head.appendChild(st);
}

// Dev error boundary — surfaces the real crash message instead of a black screen.
class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { err: any }> {
  constructor(props: any) { super(props); this.state = { err: null }; }
  static getDerivedStateFromError(err: any) { return { err }; }
  componentDidCatch(err: any) { console.log("App error:", err?.message); }
  render() {
    if (this.state.err) {
      return (
        <ScrollView style={{ flex: 1, backgroundColor: "#fff" }} contentContainerStyle={{ padding: 40 }}>
          <Text style={{ color: "#c00", fontSize: 16, fontWeight: "700", marginBottom: 12 }}>App crashed</Text>
          <Text selectable style={{ color: "#111", fontSize: 13 }}>{String(this.state.err?.message || this.state.err)}</Text>
          <Text selectable style={{ color: "#666", fontSize: 11, marginTop: 12 }}>{String(this.state.err?.stack || "").slice(0, 1500)}</Text>
        </ScrollView>
      );
    }
    return this.props.children as any;
  }
}

export default function App() {
  const fontsLoaded = useAppFonts();
  if (!fontsLoaded) return <View style={{ flex: 1, backgroundColor: PAPER }} />;
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <StatusBar style="dark" />
        <ErrorBoundary>
          <AstroApp />
        </ErrorBoundary>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}
