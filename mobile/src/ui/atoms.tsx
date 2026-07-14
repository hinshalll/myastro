// atoms.tsx — shared surfaces + primitives (ported from astro.tsx).
import React, { useRef } from "react";
import { View, Text, Pressable, StyleSheet, ViewStyle } from "react-native";
import Animated, { useSharedValue, useAnimatedStyle, withTiming } from "react-native-reanimated";
import { LinearGradient } from "expo-linear-gradient";
import Svg, { Defs, RadialGradient as SvgRadial, Stop, Rect } from "react-native-svg";
import { GRAY, HAIR, aA, sans, shadow } from "./palette";

// ---- Press: tap wrapper with a subtle scale (astro.tsx Press) ----
// The animated element is the Pressable itself, so layout styles like flex:1 on `style`
// affect the row correctly and the whole surface (bg + padding) scales together.
const AnimatedPressable = Animated.createAnimatedComponent(Pressable);
export function Press({
  children, onPress, scale = 0.97, style, disabled, hitSlop,
}: { children: React.ReactNode; onPress?: () => void; scale?: number; style?: ViewStyle | ViewStyle[]; disabled?: boolean; hitSlop?: number }) {
  const s = useSharedValue(1);
  const a = useAnimatedStyle(() => ({ transform: [{ scale: s.value }] }));
  return (
    <AnimatedPressable
      onPress={onPress}
      disabled={disabled}
      hitSlop={hitSlop}
      onPressIn={() => { s.value = withTiming(scale, { duration: 120 }); }}
      onPressOut={() => { s.value = withTiming(1, { duration: 120 }); }}
      style={[style as any, a]}
    >
      {children}
    </AnimatedPressable>
  );
}

// ---- Pill: the soft glossy white gradient surface (astro.tsx pill()) ----
export function Pill({
  children, radius = 999, style,
}: { children?: React.ReactNode; radius?: number; style?: ViewStyle | ViewStyle[] }) {
  return (
    <LinearGradient
      colors={["#FFFFFF", "#F1F1F3"]}
      start={{ x: 0, y: 0 }}
      end={{ x: 0, y: 1 }}
      style={[{ borderRadius: radius, borderWidth: 1, borderColor: "rgba(0,0,0,0.05)", ...shadow({ y: 4, blur: 14, opacity: 0.1, elevation: 2 }) } as any, style]}
    >
      {children}
    </LinearGradient>
  );
}

// ---- Label: tiny uppercase section label (astro.tsx Label) ----
export function Label({ children, c = GRAY }: { children: React.ReactNode; c?: string }) {
  return (
    <Text style={{ fontFamily: sans(700), fontSize: 11.5, letterSpacing: 1.6, textTransform: "uppercase", color: c }}>
      {children}
    </Text>
  );
}

// ---- GlossIcon: colourful glossy rounded-square icon tile (astro.tsx GlossIcon) ----
export function GlossIcon({
  c1, c2, size = 36, radius = 11, children,
}: { c1: string; c2: string; size?: number; radius?: number; children?: React.ReactNode }) {
  // Outer wrapper carries the (rounded, soft) shadow; it must NOT clip, or the shadow
  // squares off. Its solid backgroundColor gives iOS a rounded shape to cast from. The
  // inner view does the overflow clipping for the gradient + gloss layers.
  return (
    <View style={{ width: size, height: size, borderRadius: radius, backgroundColor: c2, ...shadow({ y: 3, blur: 9, opacity: 0.32, color: c2, elevation: 3 }) } as any}>
      <View style={{ width: size, height: size, borderRadius: radius, overflow: "hidden", alignItems: "center", justifyContent: "center" }}>
        <LinearGradient colors={[c1, c2]} start={{ x: 0.15, y: 0 }} end={{ x: 0.85, y: 1 }} style={StyleSheet.absoluteFill as any} />
        <View style={{ position: "absolute", top: 0, left: 0, right: 0, height: "45%" }}>
          <LinearGradient colors={[aA("#FFF", 0.4), aA("#FFF", 0)]} start={{ x: 0, y: 0 }} end={{ x: 0, y: 1 }} style={{ flex: 1 }} />
        </View>
        {/* child must be absolutely positioned so it paints ABOVE the gradient layers on web
            (CSS paints positioned siblings over static ones regardless of DOM order) */}
        <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, alignItems: "center", justifyContent: "center" }}>
          {children}
        </View>
      </View>
    </View>
  );
}

// ---- RadialGlow: a soft radial halo (replaces CSS radial-gradient glows) ----
export function RadialGlow({
  color, size, opacity = 0.4, style,
}: { color: string; size: number; opacity?: number; style?: ViewStyle | ViewStyle[] }) {
  const id = useRef("rg" + Math.random().toString(36).slice(2, 9)).current;
  return (
    <Svg width={size} height={size} style={[{ pointerEvents: "none" }, style] as any}>
      <Defs>
        <SvgRadial id={id} cx="50%" cy="50%" r="50%">
          <Stop offset="0" stopColor={color} stopOpacity={opacity} />
          <Stop offset="0.7" stopColor={color} stopOpacity={0} />
        </SvgRadial>
      </Defs>
      <Rect x="0" y="0" width={size} height={size} fill={`url(#${id})`} />
    </Svg>
  );
}
