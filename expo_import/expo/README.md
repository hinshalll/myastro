# Myastro — Expo

React Native + Expo port of the Myastro design.

## Stack

- Expo SDK 51+ (TypeScript)
- expo-router (file-based routing)
- react-native-reanimated v3 (orbit + breathing motion)
- react-native-svg (gradient orb + planet dots)
- expo-linear-gradient (sky wash)
- @expo-google-fonts/hanken-grotesk + jetbrains-mono + noto-sans-devanagari
- expo-blur (bottom-tabs pill)
- react-native-safe-area-context

## Setup

```bash
npx create-expo-app@latest myastro -t expo-template-blank-typescript
cd myastro

# overwrite the generated files with the contents of this folder
# then:

npx expo install \
  expo-router expo-linear-gradient expo-blur expo-font \
  react-native-svg react-native-reanimated react-native-safe-area-context \
  react-native-screens react-native-gesture-handler \
  @expo-google-fonts/hanken-grotesk \
  @expo-google-fonts/jetbrains-mono \
  @expo-google-fonts/noto-sans-devanagari

npx expo start
```

## Structure

```
app/
  _layout.tsx           # Root Stack — fonts, safe area, ThemeProvider + AppProvider
  index.tsx             # Entry redirect → /onboarding/welcome
  onboarding/
    welcome.tsx · birth.tsx · time.tsx · reveal.tsx
  (tabs)/
    _layout.tsx         # Custom centered-pill bottom tabs + TopBar + AskFab + backdrop
    today.tsx · people.tsx · explore.tsx · you.tsx
  # pushed sub-screens (full-screen, slide-from-right over the tabs):
  timing.tsx · rituals.tsx · ritual-detail.tsx · mala.tsx · signal-preview.tsx
  person-detail.tsx · add-person.tsx · household.tsx · couple.tsx · compat.tsx · people-compare.tsx
  tarot.tsx · numerology.tsx · best-time.tsx · palm.tsx · face.tsx
  chart.tsx · chapters.tsx · past-date.tsx · patterns.tsx · year.tsx · purpose.tsx · reading.tsx
  settings.tsx · widget.tsx · paywall.tsx

components/
  ui.tsx                # Primitives: Display/H1-3/Body/Small/Kicker/Mono, Card, Btn, Chip,
                        #   PremiumTag, Avatar, ListRow, AppBar, Field/Input, FadeUp,
                        #   PrecisionBanner, SubScreen, TabScroll
  Icon.tsx              # 35 line icons (react-native-svg) + logo
  ConstellationBG.tsx   # Deterministic faint star backdrop
  TopBar.tsx            # Brand mark + bell / settings (no tabs here)
  CelestialCanvas.tsx   # SVG orb + animated orbits + twinkles (the Today hero)
  DayRail.tsx           # 7-day strip, color-coded vibes
  WhyToggle.tsx         # Expandable "why" with Sanskrit subtitle
  HeroMeta.tsx          # Opportunity / Caution / Why rows
  AskFab.tsx            # Floating Ask pill → opens the global Ask sheet
  AskOverlay.tsx        # Bottom sheet — Ask + Decide modes, scripted replies, quota paywall
  ScanScreen.tsx        # Shared palm/face camera-scan flow
  Section.tsx           # (legacy helper, retained)

constants/
  theme.ts              # Color tokens + spacing + radius + type scale + easing
  data.ts               # SEVEN_DAYS, PEOPLE, EXPLORE, MOST_ASKED
  ThemeContext.tsx      # Dark/light provider — useTheme() → { p, name, setTheme, toggle }
  AppContext.tsx        # Global Ask sheet state + birth-time precision; hosts <AskOverlay>
```

## Notes for integration

- **Entry flow:** `/` redirects to onboarding; `reveal.tsx` does `router.replace('/today')`.
  In a real app, gate this on whether setup is complete.
- **typedRoutes is OFF** (`app.json`) so navigation uses plain string paths. Re-enable once
  routes are stable to get type-checked hrefs.
- **Birth-time precision** chosen in onboarding lives in `AppContext` and drives the
  `PrecisionBanner` on Today / You.
- **Ask sheet** is global: `useApp().openAsk({ prefill, mode })` from any screen
  (Explore's "most asked" rows use this).

## Design tokens

Dark by default (warm near-black + parchment ink + restrained gold). Toggle to true white via the theme context — see `constants/theme.ts`.
