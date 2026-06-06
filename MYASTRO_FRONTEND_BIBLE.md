# Myastro — Frontend Build Brief (upload this to your AI builder)

You are building the **complete mobile frontend** for Myastro in **React Native + Expo**. Read this
whole brief first — it's the single source of truth for structure, navigation, and how to build.
You build the UI + navigation + placeholder data only. A separate engineer wires the real backend
later, so **build in the "wiring-ready" way described in section 5.**

---

## 1. What Myastro is
A Vedic-astrology + AI-divination app for everyone, including complete beginners. The feel is calm,
warm, premium, and personal — like a beautiful printed journal crossed with a confident editorial
app. Plain, warm English everywhere. Never cold, cryptic, or jargon-heavy. (Reference feel: CHANI's
calm warmth + Co-Star's bold quotable headlines, minus any intimidation.)

## 2. Tech
- **React Native + Expo, SDK 54** (do not change the SDK).
- **Expo Router** (file-based routing under `app/`).
- Plain **StyleSheet** for styling — no Tailwind/NativeWind.
- Icons: `lucide-react-native`. Animation: `react-native-reanimated`/Moti. Camera: `expo-camera`.
  Haptics: `expo-haptics`. Audio: `expo-av`.

## 3. The design system (CONSISTENCY — the most important rule)
The visual design is already locked (see the existing Today screen). Build the design system ONCE
and reuse it on every screen:
- A single **theme** file holds all design tokens: colors, fonts, spacing, radius, shadows.
- A set of **primitive components**: Screen, Card, Button (primary/ghost/gold), SectionHead, Chip,
  TopBar, text components (Display/Body/Small), Divider.
- **Every screen is composed from these primitives. NEVER hardcode a color, font, or spacing value
  on an individual screen.** Change a token once → it updates everywhere. This is what keeps all
  screens looking like one app.

## 4. Navigation & screen map
Five bottom tabs + a floating "Ask" bubble (FAB) + onboarding + overlays.

**Tabs:** Today · People · Explore · Rituals · You

**Screens (routes):**
- Onboarding: welcome → birth details (name, date, place, birth-time with 3 options: know it / add
  later / don't know) → depth-mode question → first "who you are" reveal.
- **Today:** home (daily forecast hero, conditional event card, 3-tap check-in + mirror, good/avoid
  times, today's ritual, 3–4 day peek, up to 2 discovery teasers) · full timing detail.
- **People:** circle list · person detail (3 modes by tag: Romantic / Family / Social-Work) · add
  person · couple space · family grid · compatibility share card.
- **Explore:** home (tool grid) · your chart (full kundli) · kundli matching (Ashta-Koota) · deep
  readings · numerology · palmistry (camera) · face reading (camera) · tarot · horoscopes · muhurta
  (event timing) · varshaphal (year ahead) · festival calendar · compare (2–10 people).
- **Rituals:** home · ritual detail · mala/japa counter · mantras · meditation/breathwork · journeys.
- **You:** home (your story) · life chapters (dasha timeline) · the Mirror (journal) · patterns ·
  "why did that happen" (the Proof, past-date) · year in review · your purpose · settings/account.
- **Overlays / always-on:** Ask chat overlay · paywall · Diyas top-up · home-screen widget.

## 5. Build "wiring-ready" (so backend hookup later is a clean swap)
1. Put ALL data access behind a **single mock API module** (e.g. `src/api/`) with clearly named
   async functions: `getTodayForecast()`, `getTiming()`, `getPeople()`, `getPerson(id)`,
   `getChart()`, `getHoroscope(timeframe)`, `askCompanion(message)`, etc. They return fake data now.
2. Define a **TypeScript type for every data shape** (Forecast, Person, ChartSummary, Ritual, etc.).
3. Screens are **presentational**: they call the api functions / receive data via props or hooks and
   render it. No content hardcoded inside JSX that should come from data.
4. Keep the **API base URL and config in ONE file** (e.g. `src/config.ts`).
5. Stub auth and payments behind simple modules too (no real Supabase/IAP yet) so they can be
   swapped later.
This way the real backend is connected by replacing the mock functions in one place — not by editing
30 screens.

## 6. Monetization (build the UI for this — and NO ADS, ever)
Exactly two paths:
- **Subscription** (weekly / monthly / yearly + a 7-day free trial).
- **Diyas** — an in-app wallet/credit balance. One-time purchases, AI chats, and premium reports are
  spent in Diyas; users top up Diyas.
- **NO advertising of any kind** (not even rewarded video). Do not build any ad components. Premium
  positioning. Premium/paid surfaces are marked with a subtle gold accent.

## 7. Content & copy rules
- Warm, plain, human English. Beginner-friendly. No jargon on the surface (a "why?" toggle can
  reveal the technical astrology underneath where relevant).
- Never sound robotic or AI-generated. **No em dashes** in user-facing copy.

## 8. What NOT to do
- Don't build or assume a backend; use placeholder data via the mock api layer.
- Don't add ads.
- Don't hardcode styling on screens — always use the theme + primitives.
- Don't change the locked visual design or the Expo SDK.

## 9. How we'll work
Build in this order, running each part in Expo Go before moving on:
1. Project + theme + primitives + 5-tab nav shell + Ask FAB.
2. Today tab. 3. People tab. 4. Explore tab. 5. Rituals tab. 6. You tab. 7. Onboarding + overlays.
Detailed content/layout for each screen will be provided one screen at a time.
