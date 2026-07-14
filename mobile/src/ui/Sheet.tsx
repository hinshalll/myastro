// Sheet.tsx — the bottom-sheet (astro.tsx Sheet): dim backdrop (tap to close), a panel that
// slides up (30px top radius, grab handle, maxHeight 84%), and swipe-down-to-close.
import React, { useEffect, useState } from "react";
import { View, Pressable, Dimensions, ScrollView, StyleSheet, Keyboard, Platform } from "react-native";
import Animated, {
  useSharedValue, useAnimatedStyle, withTiming, runOnJS, Easing,
} from "react-native-reanimated";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import { PAPER, HAIR, aA, shadow } from "./palette";

const DECEL = Easing.bezier(0.2, 0.85, 0.25, 1);

export function Sheet({ open, onClose, children }: { open: boolean; onClose: () => void; children: React.ReactNode }) {
  const H = Dimensions.get("window").height;
  const [mounted, setMounted] = useState(false);
  const ty = useSharedValue(H);
  const bg = useSharedValue(0);
  const kb = useSharedValue(0); // keyboard height — lifts the panel so inputs stay visible

  useEffect(() => {
    const showEvt = Platform.OS === "ios" ? "keyboardWillShow" : "keyboardDidShow";
    const hideEvt = Platform.OS === "ios" ? "keyboardWillHide" : "keyboardDidHide";
    const s = Keyboard.addListener(showEvt as any, (e: any) => { kb.value = withTiming(e?.endCoordinates?.height || 0, { duration: 220 }); });
    const h = Keyboard.addListener(hideEvt as any, () => { kb.value = withTiming(0, { duration: 200 }); });
    return () => { s.remove(); h.remove(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (open) {
      setMounted(true);
      ty.value = H;
      bg.value = withTiming(1, { duration: 250 });
      ty.value = withTiming(0, { duration: 420, easing: DECEL });
    } else if (mounted) {
      bg.value = withTiming(0, { duration: 220 });
      ty.value = withTiming(H, { duration: 300, easing: DECEL }, (fin) => {
        if (fin) runOnJS(setMounted)(false);
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const pan = Gesture.Pan()
    .onUpdate((e) => { if (e.translationY > 0) ty.value = e.translationY; })
    .onEnd((e) => {
      if (e.translationY > 90 || e.velocityY > 800) runOnJS(onClose)();
      else ty.value = withTiming(0, { duration: 240, easing: DECEL });
    });

  const backdropA = useAnimatedStyle(() => ({ opacity: bg.value }));
  const panelA = useAnimatedStyle(() => ({ transform: [{ translateY: ty.value - kb.value }] }));

  if (!mounted) return null;
  return (
    <View style={[StyleSheet.absoluteFill, { zIndex: 80 }]} pointerEvents="box-none">
      <Animated.View style={[StyleSheet.absoluteFill, { backgroundColor: aA("#0C0B0A", 0.4) }, backdropA]}>
        <Pressable style={StyleSheet.absoluteFill} onPress={onClose} />
      </Animated.View>
      <Animated.View
        style={[
          {
            position: "absolute", left: 0, right: 0, bottom: 0, maxHeight: "84%",
            backgroundColor: PAPER, borderTopLeftRadius: 30, borderTopRightRadius: 30,
            borderWidth: 1, borderColor: HAIR, paddingTop: 14, paddingHorizontal: 22, paddingBottom: 30,
            ...shadow({ y: -10, blur: 40, opacity: 0.3, elevation: 24 }),
          } as any,
          panelA,
        ]}
      >
        <GestureDetector gesture={pan}>
          <View style={{ paddingBottom: 4 }}>
            <View style={{ width: 38, height: 4, borderRadius: 999, backgroundColor: aA("#0C0B0A", 0.14), alignSelf: "center", marginBottom: 18 }} />
          </View>
        </GestureDetector>
        <ScrollView showsVerticalScrollIndicator={false} bounces={false}>
          {children}
        </ScrollView>
      </Animated.View>
    </View>
  );
}
