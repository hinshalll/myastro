// palette.ts — ASTROLO-clean white visual constants (ported from astro.tsx).
// The app is bright white; only small accents carry the day's mood colour.
import { Platform } from "react-native";

export const PAPER = "#FFFFFF";
export const WASH = "#F4F4F6";
export const INK = "#0C0B0A";
export const INK2 = "#3A3733";
export const GRAY = "#9A958C";
export const HAIR = "rgba(12,11,10,0.07)";
export const ORANGE = "#DF6B35";

// hex/rgb → rgba(). Mirrors astro.tsx `aA`.
export function aA(hex: string, al: number): string {
  const h = (hex || "#000").replace("#", "");
  const n = parseInt(h.length === 3 ? h.split("").map((c) => c + c).join("") : h, 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${al})`;
}

// ---- Fonts ----
// @expo-google-fonts registers each weight as its own family; reference by exact name
// (RN can't pick a weight from one family the way CSS fontWeight does). Loaded in App.tsx.
type SansW = 400 | 500 | 600 | 700 | 800;
type SerifW = 400 | 500 | 600;
type MonoW = 500 | 600;

export function sans(w: SansW = 400): string {
  return ({
    400: "HankenGrotesk_400Regular",
    500: "HankenGrotesk_500Medium",
    600: "HankenGrotesk_600SemiBold",
    700: "HankenGrotesk_700Bold",
    800: "HankenGrotesk_800ExtraBold",
  } as const)[w];
}
export function serif(w: SerifW = 400, italic = false): string {
  if (italic) {
    return ({
      400: "Newsreader_400Regular_Italic",
      500: "Newsreader_500Medium_Italic",
      600: "Newsreader_500Medium_Italic",
    } as const)[w];
  }
  return ({
    400: "Newsreader_400Regular",
    500: "Newsreader_500Medium",
    600: "Newsreader_600SemiBold",
  } as const)[w];
}
export function mono(w: MonoW = 500): string {
  return ({
    500: "SplineSansMono_500Medium",
    600: "SplineSansMono_600SemiBold",
  } as const)[w];
}

// ---- Shadows ----
// Cross-platform soft shadow, correct on web AND native. On native we must NOT use RN
// `boxShadow` strings: they render as hard, opaque SQUARES and get clipped to squares under
// overflow:'hidden'. Instead we emit real shadow* props (+ Android elevation), which are
// soft, rounded and transparent. On web we emit a normal CSS box-shadow (which always
// renders correctly). For a rounded tile that needs overflow:'hidden', put this shadow on a
// NON-clipping wrapper view (the inner view does the clipping).
export function shadow(opts: { y?: number; blur?: number; opacity?: number; color?: string; elevation?: number } = {}) {
  const { y = 8, blur = 20, opacity = 0.16, color = "#1A1408", elevation } = opts;
  if (Platform.OS === "web") {
    return { boxShadow: `0px ${y}px ${blur}px ${aA(color, opacity)}` } as any;
  }
  return {
    shadowColor: color,
    shadowOffset: { width: 0, height: y },
    shadowOpacity: opacity,
    shadowRadius: blur / 2,
    elevation: elevation ?? Math.max(1, Math.round(blur / 3)),
  } as any;
}

// soft white card surface (solid #FFF; the only surface with a gradient is <Pill>).
export function cardStyle(extra: object = {}) {
  return {
    backgroundColor: PAPER,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: HAIR,
    ...shadow({ y: 10, blur: 30, opacity: 0.13, elevation: 3 }),
    ...extra,
  } as any;
}

// nav-bar / bottom inset height used to pad scroll bodies above the tab bar.
export const NAV_H = 86;
