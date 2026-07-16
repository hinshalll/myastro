// DemoBadge.tsx — the on-screen giveaway that a screen is showing FAKE data.
//
// WHY THIS EXISTS: theme.demo.ts throws in production, so fakes can never ship. But in dev
// (Expo Go, which is where the app is actually being tested) the fallback stays silent —
// console.warn goes to the Metro log, which nobody reads while holding a phone. So the app
// still looks finished while quietly lying. This makes it impossible to miss.
//
// Renders NOTHING in production, so it costs the shipped app nothing.
// Tap to expand the list. Tap a second time to collapse. It never blocks a control:
// it sits under the header and is dismissible.
import React, { useEffect, useState } from "react";
import { View, Text, Pressable } from "react-native";
import { demoLedger, subscribeDemo } from "../theme";

const RED = "#B4231F";

export function DemoBadge() {
  const [seen, setSeen] = useState<string[]>(__DEV__ ? demoLedger() : []);
  const [open, setOpen] = useState(false);
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    if (!__DEV__) return;
    setSeen(demoLedger());          // catch anything recorded before this mounted
    return subscribeDemo(setSeen);
  }, []);

  if (!__DEV__ || hidden || seen.length === 0) return null;

  return (
    <View style={{ position: "absolute", top: 0, left: 0, right: 0, zIndex: 999, alignItems: "center", paddingTop: 2 }} pointerEvents="box-none">
      <Pressable onPress={() => setOpen((v) => !v)} onLongPress={() => setHidden(true)}>
        <View style={{ backgroundColor: RED, borderRadius: 999, paddingVertical: 5, paddingHorizontal: 12, flexDirection: "row", alignItems: "center", gap: 7, maxWidth: 340 }}>
          <View style={{ width: 6, height: 6, borderRadius: 999, backgroundColor: "#FFF" }} />
          <Text style={{ color: "#FFF", fontSize: 11, fontWeight: "800", letterSpacing: 0.3 }}>
            {seen.length} FAKE {seen.length === 1 ? "SOURCE" : "SOURCES"} ON SCREEN
          </Text>
          <Text style={{ color: "#FFD9D8", fontSize: 10, fontWeight: "700" }}>{open ? "tap to close" : "tap"}</Text>
        </View>
      </Pressable>
      {open ? (
        <View style={{ marginTop: 6, backgroundColor: "rgba(24,16,15,0.94)", borderRadius: 12, padding: 12, maxWidth: 340, gap: 5 }}>
          {seen.map((s) => (
            <Text key={s} style={{ color: "#FFD9D8", fontSize: 11, fontWeight: "600" }}>· {s}</Text>
          ))}
          <Text style={{ color: "#9C8F8E", fontSize: 10, marginTop: 4 }}>
            Dev only. This build would refuse to start in production. Long-press the badge to hide it.
          </Text>
        </View>
      ) : null}
    </View>
  );
}
