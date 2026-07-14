// BackBar.tsx — a plain back-button header used by the full-screen overlays.
import React from "react";
import { View, Text } from "react-native";
import { Mood } from "../theme";
import { INK, sans } from "./palette";
import { Press, Pill } from "./atoms";
import { Icon, Flame } from "./Icon";

export function BackBar({ onBack, bal, mood, onWallet, insetTop = 44 }: { onBack: () => void; bal?: number; mood: Mood; onWallet?: () => void; insetTop?: number }) {
  return (
    <View style={{ position: "absolute", top: insetTop + 4, left: 18, right: 18, zIndex: 10, flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
      <Press scale={0.9} onPress={onBack}>
        <Pill radius={999} style={{ width: 42, height: 42, alignItems: "center", justifyContent: "center" }}><Icon n="arrowL" s={19} c={INK} /></Pill>
      </Press>
      {bal != null && (
        <Press scale={0.94} onPress={onWallet}>
          <Pill radius={999} style={{ paddingVertical: 9, paddingHorizontal: 14, flexDirection: "row", alignItems: "center", gap: 6 }}>
            <Flame s={15} c={mood.glow} />
            <Text style={{ fontFamily: sans(800), fontSize: 15, color: INK }}>{bal}</Text>
          </Pill>
        </Press>
      )}
    </View>
  );
}
