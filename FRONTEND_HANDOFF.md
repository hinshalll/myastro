# Myastro — Frontend Handoff Brief

**Purpose:** hand the frontend build to any AI coding agent (Antigravity, Cursor, Claude, etc.)
without re-explaining the project. Read this, then the source-of-truth docs.

---

## 0. Read these first (source of truth — do NOT contradict them)
1. `MOBILE_APP_BLUEPRINT.md` — the full app plan (tabs, screens, features). **Authoritative.**
2. `FEATURE_SPEC.md` — per-feature detail.
3. `SYSTEM_REFERENCE.md` — backend/API + AI routing reference.
4. `features/<feature>/README.md` — individual feature notes.

If anything here conflicts with those docs, the docs win.

---

## 1. What we're building
**Myastro** = Vedic-astrology + AI-divination mobile app. Beginner-friendly, premium feel.
Polish like CHANI / Co-Star, with deeper Vedic substance.

- **Backend:** already built + LIVE (FastAPI on Render). Do NOT rebuild it. Wire the app to it.
- **Frontend:** the existing `mobile/` folder is a REJECTED dummy mockup. We are rebuilding the
  UI fresh in a clean CHANI-style design. Reuse `mobile/` only if helpful; the design is new.

## 2. App structure (locked)
5 tabs + floating Ask bubble + home widget:
- **Today** — daily habit + discovery (daily forecast, good/avoid times, 3-tap check-in, ritual).
- **People** — relationships; 3 tag-driven modes: Romantic / Family / Social-Work.
- **Explore** — read my charts + classical tools (incl. the Kundli Milan 36-guna calculator).
- **Rituals** — daily practice / rituals (the daily doable actions live here).
- **You** — profile, the Mirror journal, Patterns/Proof, settings.

## 3. Monetization (locked — DO NOT add ads, ever)
Exactly two ways:
- **Subscription** (premium tier).
- **Diyas** = in-app wallet/credits. All one-time purchases, AI chats, reports spend Diyas.
- **NO ADS at all** (not even rewarded). Deliberate premium positioning.

## 4. Design direction (locked)
**Warm-minimal canvas + bold confident headlines + beginner-friendly plain language.**
- Take from **CHANI:** calm, warm, airy off-white base; soft, unintimidating, ritual feel.
- Take from **Co-Star:** typographic confidence — big, bold, plain-spoken quotable one-liners.
- **Reject** Co-Star's cold, cryptic, dense complexity. Stay warm; depth is opt-in.

**The frozen "style block"** — paste this verbatim at the top of EVERY design (Stitch) prompt:

> Calm, airy, premium. Soft off-white / warm paper background (not pure white, not dark).
> Generous spacing and breathing room. Light, barely-there paper texture. Accent palette:
> soft blush and lavender pastels, with a single warm gold reserved only for premium/special
> moments. Headlines use a confident, expressive serif/editorial display font that feels
> personal and quotable; body and UI text use a clean geometric sans-serif. Bold, plain-spoken
> typography over decoration. Rounded, soft-edged cards. Gentle, quiet, ritual feel — pretty
> and approachable, like a beautiful printed journal crossed with a confident editorial app.

## 4b. Design source files (IMPORTANT — read before building a screen)
Screen designs are produced in **Google Stitch**, then exported via **Google AI Studio**, and
saved under `design_import/<screen>/` (folder + screenshot).

**The AI Studio export is a WEB mockup, not a runnable Expo app.** It imports web-only libs
(`lucide-react`, `motion/react`, `vite.config.ts`, `index.css`). DO NOT try to run it or copy it
verbatim. Use it ONLY as the **visual source of truth**: colors, fonts, spacing, layout, copy.
Rebuild each screen as REAL React Native + Expo (`react-native` primitives, `StyleSheet`,
`lucide-react-native`, `react-native-reanimated`/Moti for motion). Match the look, not the code.

## 5. How to keep design consistent across screens (CRITICAL)
Consistency comes from two anchors, not from eyeballing:

**Anchor A — frozen style block.** Reuse the paragraph in §4 WORD-FOR-WORD on every screen prompt.

**Anchor B — a shared design system in code. Build this BEFORE any screen:**
- `theme.ts` — design tokens: colors, fonts, spacing, radius. One place.
- Primitive components: `Card`, `Button`, `SectionHead`, `Chip`, `Section`, `TopBar`, etc.
- **Rule:** every screen is assembled from these primitives. NEVER hardcode a color or font
  on an individual screen. Change a token once → it updates everywhere.

## 6. Tech stack (frontend)
- **React Native + Expo** (pinned to **Expo SDK 54** — matches the user's Expo Go client; do
  not upgrade blindly). Expo Router (file-based routing under `mobile/app/`).
- Auth/data: **Supabase**. AI/RAG handled by the backend, not the app.
- Talk to the backend via its REST API (see `SYSTEM_REFERENCE.md` for routes). The app holds
  the Supabase **anon** key only — NEVER the service_role key.

## 7. Build order (solo dev)
1. Theme + fonts + primitives + nav shell (the design system + 5-tab navigation).
2. Today tab + its sub-screens.
3. People tab (3-mode per-person profile).
4. Explore tab.
5. Rituals tab.
6. You tab.
7. Onboarding + overlays (Ask bubble, paywall).
8. Wire each screen to the live backend as it's built.

## 8. Hard rules
- Beginner-friendly plain English in all user-facing copy. Warm, personal, never AI-sounding.
  No jargon. **No em dashes.**
- No ads, anywhere.
- Don't rebuild the backend. Don't touch `shared/*` or `features/*` logic — frontend only.
- Confirm with the user before any step that costs money.

---

*Companion design prompts (per tab) are generated separately. Always prepend the §4 style block.*
