// useAppFonts — loads the three bundled families (offline; no runtime network).
import { useFonts } from "expo-font";
import {
  HankenGrotesk_400Regular, HankenGrotesk_500Medium, HankenGrotesk_600SemiBold,
  HankenGrotesk_700Bold, HankenGrotesk_800ExtraBold,
} from "@expo-google-fonts/hanken-grotesk";
import {
  Newsreader_400Regular, Newsreader_500Medium, Newsreader_600SemiBold,
  Newsreader_400Regular_Italic, Newsreader_500Medium_Italic,
} from "@expo-google-fonts/newsreader";
import { SplineSansMono_500Medium, SplineSansMono_600SemiBold } from "@expo-google-fonts/spline-sans-mono";

export function useAppFonts(): boolean {
  const [loaded] = useFonts({
    HankenGrotesk_400Regular, HankenGrotesk_500Medium, HankenGrotesk_600SemiBold,
    HankenGrotesk_700Bold, HankenGrotesk_800ExtraBold,
    Newsreader_400Regular, Newsreader_500Medium, Newsreader_600SemiBold,
    Newsreader_400Regular_Italic, Newsreader_500Medium_Italic,
    SplineSansMono_500Medium, SplineSansMono_600SemiBold,
  });
  return loaded;
}
