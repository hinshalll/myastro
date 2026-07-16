// Welcome.tsx — the first impression. Faint constellations + twinkling stars sit behind a
// hero collage that floats under a soft violet halo; a serif headline writes in, then
// "Begin" + "I already have an account". Ported from screens/onboarding/onboarding.tsx
// (Welcome + HeroArt + Ambient/Constellations), with the ambient kept subtle.
import React from "react";
import { View, Text, Image } from "react-native";
import Animated from "react-native-reanimated";
import Svg, { Polyline, Circle } from "react-native-svg";
import { serif, sans, aA } from "../ui/palette";
import { RadialGlow } from "../ui/atoms";
import { useFloatY, useHalo, useTwinkle } from "../ui/motion";
import { P, OScreen, PrimaryButton, TextLink, Rise, useTopPad } from "./kit";

const HERO = require("../../assets/onboarding-hero.png");

// a single twinkling star dot (gold or violet), positioned by percent
function Star({ x, y, size, color, lo, hi, period }: any) {
  const tw = useTwinkle(lo, hi, period);
  return <Animated.View pointerEvents="none" style={[{ position: "absolute", left: x, top: y, width: size, height: size, borderRadius: size, backgroundColor: color }, tw]} />;
}

const STARS = [
  { x: "12%", y: "13%", size: 2.4, color: P.gold, lo: 0.15, hi: 0.7, period: 3.4 },
  { x: "83%", y: "9%", size: 2.0, color: P.violet, lo: 0.12, hi: 0.55, period: 4.6 },
  { x: "89%", y: "27%", size: 2.6, color: P.gold, lo: 0.15, hi: 0.65, period: 3.0 },
  { x: "7%", y: "31%", size: 2.2, color: P.violet, lo: 0.12, hi: 0.5, period: 4.0 },
  { x: "22%", y: "41%", size: 1.8, color: P.gold, lo: 0.12, hi: 0.55, period: 3.6 },
  { x: "78%", y: "42%", size: 2.2, color: P.violet, lo: 0.12, hi: 0.5, period: 4.2 },
  { x: "50%", y: "4%", size: 2.0, color: P.violet, lo: 0.12, hi: 0.5, period: 3.8 },
  { x: "35%", y: "45%", size: 1.8, color: P.gold, lo: 0.12, hi: 0.55, period: 3.2 },
];

// two faint constellations that sit behind the hero (static, very subtle)
function ConstellationSky() {
  return (
    <Svg style={{ position: "absolute", top: 0, left: 0, right: 0, height: "56%", width: "100%" }} viewBox="0 0 390 460" preserveAspectRatio="xMidYMid slice" pointerEvents="none">
      {[
        [[30, 120], [78, 92], [122, 132], [158, 96]],
        [[300, 96], [336, 146], [292, 188]],
      ].map((pts, i) => (
        <React.Fragment key={i}>
          <Polyline points={pts.map((p) => p.join(",")).join(" ")} fill="none" stroke={aA(P.violetDeep, 0.14)} strokeWidth={0.9} strokeLinecap="round" strokeLinejoin="round" />
          {pts.map((p, j) => <Circle key={j} cx={p[0]} cy={p[1]} r={j === 0 || j === pts.length - 1 ? 1.8 : 1.3} fill={aA(j % 2 ? P.gold : P.violet, 0.5)} />)}
        </React.Fragment>
      ))}
    </Svg>
  );
}

function HeroArt({ size = 300 }: { size?: number }) {
  const float = useFloatY(7, 6);
  const halo = useHalo(6);
  return (
    <View style={{ width: size, height: size, alignItems: "center", justifyContent: "center" }}>
      <Animated.View pointerEvents="none" style={[{ position: "absolute", width: size * 1.05, height: size * 1.05, alignItems: "center", justifyContent: "center" }, halo]}>
        <RadialGlow color={P.violetGlow} size={size * 1.05} opacity={0.5} />
      </Animated.View>
      <Animated.View style={float}>
        <Image source={HERO} resizeMode="contain" style={{ width: size, height: size }} />
      </Animated.View>
    </View>
  );
}

export function Welcome({ onBegin, onLogin }: { onBegin: () => void; onLogin: () => void }) {
  const top = useTopPad(70);
  return (
    <OScreen crown={0.18}>
      {/* ambient night sky behind everything */}
      <View pointerEvents="none" style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 }}>
        <ConstellationSky />
        {STARS.map((s, i) => <Star key={i} {...s} />)}
      </View>

      <View style={{ flex: 1, alignItems: "center", paddingTop: top, paddingBottom: 44, paddingHorizontal: 32 }}>
        <Rise delay={220} dist={18}><HeroArt size={300} /></Rise>

        <View style={{ marginTop: 26, alignItems: "center" }}>
          <Rise delay={620} dist={16}>
            <Text style={{ fontFamily: serif(500), fontSize: 40, lineHeight: 44, color: P.ink, letterSpacing: -0.7 }}>Astrology that</Text>
          </Rise>
          <Rise delay={760} dist={16}>
            <Text style={{ fontFamily: serif(500, true), fontSize: 40, lineHeight: 46, color: P.ink, letterSpacing: -0.5 }}>learns you.</Text>
          </Rise>
        </View>

        {/* This line carries FOUR jobs the hero cannot: that it is a DAILY habit (the app is
            built to be opened every morning, not consulted once), that it is one whole app
            rather than a horoscope widget, that the astrology is real, and that it is readable.
            "Your day, your chart, your people" names the actual product (Today / Readings /
            People) so breadth is shown rather than claimed — no hollow "all in one". "every
            day" is the load-bearing bit: it sets the expectation that this is somewhere you
            come back to. */}
        <Rise delay={960} dist={14} style={{ marginTop: 16 }}>
          <Text style={{ fontFamily: sans(400), fontSize: 16, lineHeight: 24, color: P.inkSoft, letterSpacing: 0.1, textAlign: "center", maxWidth: 300 }}>
            Your day, your chart, your people. Real Vedic astrology every day, in plain words.
          </Text>
        </Rise>

        <View style={{ flex: 1, minHeight: 22 }} />

        <Rise delay={1180} dist={16} style={{ width: "100%", maxWidth: 304 }}>
          <PrimaryButton label="Begin" onPress={onBegin} />
        </Rise>
        <Rise delay={1340} dist={12} style={{ marginTop: 16 }}>
          <TextLink label="I already have an account" onPress={onLogin} color={P.inkMid} />
        </Rise>
      </View>
    </OScreen>
  );
}
