# Myastro — Screen-by-Screen Prompts (Stitch design + Antigravity build)

**How to use this file**
1. Read `FRONTEND_HANDOFF.md` first (the big picture + rules).
2. Work top to bottom. Each screen has TWO prompts:
   - **🎨 STITCH** — paste into Google Stitch to generate the look. **Always prepend the STYLE
     BLOCK below.** Export to AI Studio, save under `design_import/<screen>/` (folder + screenshot).
   - **🛠️ ANTIGRAVITY** — paste into Antigravity to build the REAL React Native + Expo screen
     from that design.
3. The AI Studio export is a WEB mockup — Antigravity uses it for the LOOK only and rebuilds it
   native. (See handoff §4b.)
4. **Build the Foundation first.** Every screen reuses it.
5. Wiring to the live backend is NOT in these prompts — that is the final step the user does with
   Claude. Antigravity should use realistic placeholder/dummy data for now.

---

## ⭐ THE STYLE BLOCK (prepend to EVERY Stitch prompt, word-for-word)

> Calm, airy, premium. Soft off-white / warm paper background (not pure white, not dark).
> Generous spacing and breathing room. Light, barely-there paper texture. Accent palette: soft
> blush and lavender pastels, with a single warm gold reserved only for premium/special moments.
> Headlines use a confident, expressive serif/editorial display font that feels personal and
> quotable; body and UI text use a clean geometric sans-serif. Bold, plain-spoken typography over
> decoration. Rounded, soft-edged cards. Gentle, quiet, ritual feel — pretty and approachable,
> like a beautiful printed journal crossed with a confident editorial app. Beginner-friendly:
> warm plain English, never cold or cryptic, no jargon.

---

# 0. FOUNDATION  *(Antigravity only — no Stitch. Build this BEFORE any screen.)*

🛠️ **ANTIGRAVITY**
> Set up the Myastro mobile app as **React Native + Expo (SDK 54)** with **Expo Router** (file-based
> routing under `mobile/app/`). Then build the design system that every screen will reuse:
>
> 1. **`mobile/theme/theme.ts`** — design tokens in one place:
>    - Colors: warm off-white background (`#FAF7F2`-ish), soft surface/card, ink (near-black text),
>      muted ink, blush accent, lavender accent, ONE warm gold (premium only), soft green (good) +
>      soft red (avoid), hairline border.
>    - Fonts: an expressive serif display (e.g. Libre Caslon Text / Fraunces) for headings; a clean
>      geometric sans (e.g. Inter) for body/UI; a mono for tiny timestamps. Load via `expo-font`.
>    - Spacing scale, border-radius scale, shadow/elevation tokens.
> 2. **Primitive components** in `mobile/components/`: `Screen` (safe-area + bg), `Card`,
>    `Button` (primary/ghost/gold variants), `SectionHead`, `Chip`, `TopBar`, `Display`/`Body`/
>    `Small` text components, `Divider`. All read from `theme.ts`.
> 3. **5-tab navigation shell** (`mobile/app/(tabs)/`): Today / People / Explore / Rituals / You,
>    quiet minimal line icons (`lucide-react-native`), active tab in the accent color, soft bg.
> 4. A **floating "Ask" bubble** (FAB) visible above the tabs on the main screens.
> 5. Safe-area handling so headers/tab bar never collide with the notch.
>
> **Rule:** screens NEVER hardcode a color/font/spacing — always import from `theme.ts` and compose
> primitives. Use plain `StyleSheet` (no NativeWind/Tailwind). Get it building and runnable in Expo
> Go (`npx expo start`) before moving on.

---

# 1. ONBOARDING  *(first-run; the wow + conversion moment)*

## 1.1 Welcome / intro
🎨 **STITCH**
> A warm welcome screen for an astrology app. A single beautiful serif headline ("Let's read your
> sky"), a one-line warm subtitle, a soft celestial illustration or simple star motif, and one
> gold "Begin" button at the bottom. Lots of empty space. Optional tiny "I already have an account"
> text link below.

🛠️ **ANTIGRAVITY**
> Build the onboarding welcome screen (`app/onboarding/index.tsx`) from `design_import/welcome/`,
> using the foundation primitives. "Begin" routes to the birth-details step. Keep it a thin
> presentational screen.

## 1.2 Birth details (conversational, NOT a dry form)
🎨 **STITCH**
> A gentle, conversational birth-details screen — feels like a friendly chat, not a government form.
> One question visible at a time, each in a soft card: first name, then birth date (nice date
> picker), then birth place (search field with suggestions). Then a **birth-time** step shown as
> THREE soft choice cards: "I know my time" / "I'll add it later" / "I don't know it" — making clear
> the app works either way. A calm progress indicator (dots) at top. Warm, reassuring microcopy.

🛠️ **ANTIGRAVITY**
> Build the multi-step birth-details flow from `design_import/birth-details/`. Steps: name → date →
> place (autocomplete UI, dummy suggestions for now) → birth-time with the 3 options (exact /
> later / unknown). Store answers in local state / a simple onboarding context. The place search and
> chart calc wire to the backend later — use placeholders now. Reassuring, one-question-at-a-time.

## 1.3 Depth-mode question
🎨 **STITCH**
> A single gentle question screen: "How do you like your astrology?" with 3 soft selectable cards —
> e.g. "Keep it simple" / "Balanced" / "Give me the full depth" — each with a one-line description.
> Calm, no pressure.

🛠️ **ANTIGRAVITY**
> Build the depth-mode picker from `design_import/depth-mode/`. Save the choice to onboarding state
> (drives how much detail screens show later). Routes to the Proof reveal.

## 1.4 The Proof reveal / "who you are" wow
🎨 **STITCH**
> A delightful reveal screen — the first "wow." A warm, personal "Here's who you are" summary in
> beautiful serif, 2–3 short plain-English insight cards about the person, and a subtle animation
> feel. One gentle "Continue" button. This comes BEFORE any paywall. Premium, emotional, screenshot-
> worthy.

🛠️ **ANTIGRAVITY**
> Build the reveal screen from `design_import/proof-reveal/` with placeholder insight text for now
> (it wires to the chart/AI later). End of onboarding → routes into the Today tab.

---

# 2. TODAY TAB

## 2.1 Today home  *(design already generated — "Celestial Journal")*
🎨 **STITCH** — *(already done; this is the locked Today prompt for reference)*
> A single mobile home screen called "Today." Calm scrollable vertical stack of soft cards:
> (1) top bar with greeting + date + avatar; (2) a large **Daily Forecast hero** card — one bold
> mood word in big serif (e.g. "Slow"), a one-line warm vibe sentence, then four labeled rows
> (Mood, Opportunity, Caution, Action) each one short sentence, plus a share icon; (3) a **3-tap
> Check-in** card ("How's your energy today?") with three soft pill choices + a streak indicator;
> (4) a **Good times / Avoid times** split card (green good window, soft-red avoid window) with a
> "see full timing →" link; (5) a **Today's Ritual** card (one tiny action + "Begin →"); (6) a
> small horizontal **3-day peek** rail; (7) one dismissible discovery teaser. Floating "Ask" bubble
> bottom-right. Minimal 5-tab bottom nav (Today active).

🛠️ **ANTIGRAVITY**
> Build the Today home (`app/(tabs)/index.tsx`) from `design_import/today/` using foundation
> primitives. Each card is its own component. Tapping the forecast hero opens a share sheet; check-in
> pills update a local streak; "see full timing" → timing screen; ritual "Begin" → Rituals tab. Use
> dummy data shaped like the real forecast (mood word, vibe line, the 4 rows, good/avoid windows,
> 3-day peek). I will wire the live data later.

## 2.2 Timing detail (Good / Avoid times)
🎨 **STITCH**
> A "Today's timing" detail screen. A clean vertical timeline of the day's windows — each window a
> soft row with a time range, a one-word label (Good / Neutral / Avoid) color-coded (soft green /
> grey / soft red), and a short plain-English note ("good for important talks"). A small legend.
> Calm, scannable, no astrology jargon on the surface (a tiny "why?" toggle reveals Choghadiya /
> Rahu-Kaal terms).

🛠️ **ANTIGRAVITY**
> Build `app/timing.tsx` from `design_import/timing/`. Timeline list of windows from dummy data;
> "why?" toggle reveals the classical names. Wires to the timing endpoint later.

---

# 3. PEOPLE TAB

## 3.1 Your circle (people list)
🎨 **STITCH**
> A "People" screen: your saved circle. A warm list of person cards — each with avatar/initial,
> name, a relationship tag chip (💕 / 👨‍👩‍👧 / 🤝), and today's one-line relationship weather ("Warm
> day with Mom"). A prominent "＋ Add someone" button. Calm, personal, uncluttered. Maybe a small
> "Couple" highlight at top if a partner is linked.

🛠️ **ANTIGRAVITY**
> Build `app/(tabs)/people.tsx` from `design_import/people/`. List of person cards (dummy data),
> tag chips, today's nudge line; tap a card → person-detail; "Add someone" → add-person. Filter/
> sort optional.

## 3.2 Person detail (the 3-mode profile — LOCKED spec)
🎨 **STITCH**
> A per-person profile screen. **Header:** name + relationship tag chip + their key signs in plain
> words. **Hero:** "Today between you" — ONE actionable nudge in confident serif ("Warm window —
> good day to call Mom"), not just a vibe. **Body changes by tag mode:**
> - 💕 Romantic: an overall harmony read + gentle score ring, "what flows / what to watch" two-column,
>   a 5–7 day harmony-vs-tension mini-graph, talk/avoid nudges; if spouse/serious, a small Kundli-
>   Milan guna summary card with "See full matching →".
> - 👨‍👩‍👧 Family: bond dynamics + daily nudge + short peek. No marriage content.
> - 🤝 Social/Work: how you two click (communication/energy) + nudge.
> **Always:** a "why?" depth toggle, a privacy reminder line, and a "Share" card button. Warm, never
> clinical.

🛠️ **ANTIGRAVITY**
> Build `app/person-detail.tsx` from `design_import/person-detail/`. Render the body conditionally on
> a `mode` prop derived from the person's tag (romantic / family / social). Build the three mode
> bodies as separate components. "See full matching" → Explore kundli-matching tool; "Share" → a
> share-card screen. Dummy data per mode for now.

## 3.3 Add a person
🎨 **STITCH**
> An "Add someone" screen with two soft choices at top: "By birth details" (works solo) and "Invite
> a friend" (they join). The birth-details path reuses the gentle conversational fields (name, date,
> place, birth-time 3-options) plus a relationship tag picker (the 💕/👨‍👩‍👧/🤝 set). Warm, simple.

🛠️ **ANTIGRAVITY**
> Build `app/add-person.tsx` from `design_import/add-person/`. Two modes; reuse the birth-details
> field components from onboarding; relationship-tag picker. Saves to local list for now.

## 3.4 Couple space
🎨 **STITCH**
> A "Couple" screen for two linked partners: a shared "How are we today" hero card (one warm line +
> a soft pulse/score), then a multi-day tension-vs-harmony forecast strip, and a couple of gentle
> "talk about / lean into" nudges. Romantic, calm, premium. Subtle gold accents (premium feature).

🛠️ **ANTIGRAVITY**
> Build `app/couple.tsx` from `design_import/couple/`. Shared hero + forecast strip + nudges, dummy
> data. Marked as a premium ([SUB]/[Diyas]) surface visually.

## 3.5 Family grid (across timezones)
🎨 **STITCH**
> A "Family" grid screen — the whole household's day at a glance. A soft grid/list of family members,
> each tile showing name, local time (different timezones), and a one-word daily vibe + tiny color
> dot. Designed for diaspora families. Calm, glanceable. Premium accents.

🛠️ **ANTIGRAVITY**
> Build `app/household.tsx` from `design_import/family-grid/`. Grid of member tiles with per-person
> local time + vibe, dummy data across timezones.

## 3.6 Compatibility share card
🎨 **STITCH**
> A beautiful **shareable compatibility card** (portrait, screenshot/Instagram-story friendly): two
> names, a warm headline result, a soft score or harmony visual, a short poetic line, and small
> Myastro branding + "invite them to see their side" call. Gorgeous, gift-like, very shareable.

🛠️ **ANTIGRAVITY**
> Build `app/compat-share.tsx` (and a reusable `ShareCard` component) from `design_import/compat-
> share/`. Render to an image for sharing (`react-native-view-shot` + `expo-sharing`). Dummy result.

---

# 4. EXPLORE TAB

## 4.1 Explore home (the tool grid / "back room")
🎨 **STITCH**
> An "Explore" home screen — a calm, organized grid of astrology tools grouped under soft section
> headers: "Your charts" (Full Kundli, Life Chapters), "Readings" (Full Life Reading, Marriage,
> Purpose), "Compatibility" (Kundli Matching), "Timing" (Muhurta, Varshaphal), "Divination" (Tarot,
> Palmistry, Face reading, Numerology), "Calendar" (Panchanga/Festivals). Each tool a soft tile with
> a small line icon + name + tiny tag (FREE / Diyas / SUB where relevant). Premium tiles get a subtle
> gold accent. Searchable. Tidy, not overwhelming.

🛠️ **ANTIGRAVITY**
> Build `app/(tabs)/explore.tsx` from `design_import/explore/`. Sectioned grid of tool tiles routing
> to each tool screen below. Tag chips driven by data. Optional search filter.

## 4.2 Your Chart (full Kundli)
🎨 **STITCH**
> A "Your Chart" screen showing a Vedic birth chart. A clean North/South-Indian style chart diagram
> at top (soft lines, not garish), then collapsible plain-English sections below: planets & signs,
> houses, current dasha, key yogas/doshas — each in soft cards, depth shown per the user's depth-mode.
> A "Download PDF" gold button (premium). Beautiful, readable, beginner-friendly summaries with a
> "why?/show technical" toggle for depth.

🛠️ **ANTIGRAVITY**
> Build `app/chart.tsx` from `design_import/chart/`. Chart diagram component + collapsible info
> sections, dummy chart data. Respect depth-mode (show/hide technical). PDF button stubbed.

## 4.3 Kundli Matching (Ashta Koota — the 36-guna tool)
🎨 **STITCH**
> A "Kundli Matching" tool screen. Two person inputs at top (you + partner, or pick two saved
> people). A big warm result: the total guna score (e.g. "27 / 36") in a soft ring, a one-line verdict,
> then the 8 kootas as soft rows each with its score and a tiny plain-English note. A "full report"
> gold button. Classical but approachable, not intimidating.

🛠️ **ANTIGRAVITY**
> Build `app/compat.tsx` (Ashta Koota) from `design_import/kundli-matching/`. Two-person selectors,
> score ring, 8-koota breakdown list, dummy data. Deep-linkable from person-detail.

## 4.4 Premium readings (Full Life Reading / Marriage / Purpose)
🎨 **STITCH**
> A "Deep readings" screen presenting the flagship AI reports as elegant offer cards: "Full Life
> Reading" (the 3-agent flagship), "Marriage & Destiny", "Your Purpose" — each card with a serif
> title, a one-line promise, a price in Diyas, and a soft gold "Get reading" button. Premium, calm,
> trustworthy. A tasteful testimonial line.

🛠️ **ANTIGRAVITY**
> Build `app/reading.tsx` from `design_import/readings/` — offer cards + a results/reading view
> template (long-form scrollable reading with sections). Dummy content; AI wires later.

## 4.5 Numerology
🎨 **STITCH**
> A "Numerology" screen: the person's core numbers (life path, etc.) shown as big soft number tiles,
> each with a one-line plain-English meaning, then cycle/forecast sections below. Warm, clean.

🛠️ **ANTIGRAVITY**
> Build `app/numerology.tsx` from `design_import/numerology/`. Number tiles + meaning cards, dummy data.

## 4.6 Palmistry (camera)
🎨 **STITCH**
> A "Palmistry" camera screen: a friendly capture screen with a hand-outline guide overlay and a
> warm instruction ("Place your right palm in the frame"), a capture button, then a results view —
> the photo with soft highlighted lines and plain-English reading cards below. Approachable, a little
> magical, 1 free taste then Diyas.

🛠️ **ANTIGRAVITY**
> Build `app/palm.tsx` from `design_import/palmistry/` using `expo-camera`. Capture + a results
> screen with reading cards (dummy). The vision call wires to backend later — just capture + POST
> placeholder.

## 4.7 Face reading (camera)
🎨 **STITCH**
> A "Face reading" camera screen mirroring palmistry: a gentle selfie-capture with a face-outline
> guide, warm instructions, then a results view with plain-English insight cards. Calm, respectful,
> not gimmicky. 1 free taste then Diyas.

🛠️ **ANTIGRAVITY**
> Build `app/face.tsx` from `design_import/face-reading/` using `expo-camera` (front). Capture +
> results cards (dummy). Vision wires later.

## 4.8 Tarot (78-card picker)
🎨 **STITCH**
> A "Tarot" screen: a beautiful interactive card spread — a fan/row of face-down cards with soft
> backs the user taps to pick. After picking, the chosen cards flip with a gentle animation and a
> reading appears in warm serif below (card name + plain-English meaning + how it applies). Calm,
> elegant, a touch of magic. 1 free/day then Diyas.

🛠️ **ANTIGRAVITY**
> Build `app/tarot.tsx` from `design_import/tarot/`. Tap-to-pick card interaction + flip animation
> (`react-native-reanimated`), reading view with dummy meanings. Daily-limit gating UI.

## 4.9 Horoscopes
🎨 **STITCH**
> A "Horoscopes" screen: a segmented toggle (Daily / Monthly / Yearly), then warm plain-English
> horoscope content in soft cards by life area (love, work, health). Optional sign selector. Clean,
> readable, screenshot-worthy.

🛠️ **ANTIGRAVITY**
> Build `app/horoscopes.tsx` from `design_import/horoscopes/`. Timeframe toggle + content cards,
> dummy data.

## 4.10 Event Timing Planner (Muhurta)
🎨 **STITCH**
> A "Best dates for…" (Muhurta) screen: pick an activity (marriage, travel, business, etc.), then a
> calm list of recommended dates/windows, each a soft row with date, a quality indicator, and a one-
> line reason. A premium "deep search" gold option. Practical and clear.

🛠️ **ANTIGRAVITY**
> Build `app/timing-planner.tsx` (Muhurta) from `design_import/muhurta/`. Activity picker + ranked
> date list, dummy data. (Note: distinct from the daily `timing.tsx`.)

## 4.11 Varshaphal (year-ahead)
🎨 **STITCH**
> A "Your Year Ahead" (Varshaphal) screen: a warm annual overview hero, then month-by-month or
> theme-by-theme soft cards (career, love, health, finances) with plain-English outlooks. Premium
> gold accents. Optimistic, useful.

🛠️ **ANTIGRAVITY**
> Build `app/year-ahead.tsx` from `design_import/varshaphal/`. Annual hero + themed cards, dummy data.

## 4.12 Festival / Panchanga calendar
🎨 **STITCH**
> A "Calendar" screen: a soft monthly calendar with festival/auspicious days marked by gentle dots,
> a list of upcoming festivals below (name, date, one-line significance), and a reminder toggle.
> Clean, useful for diaspora users.

🛠️ **ANTIGRAVITY**
> Build `app/calendar.tsx` from `design_import/calendar/`. Month grid + festival list + reminder
> toggle, dummy data.

## 4.13 Compare (2–10 people, tucked away)
🎨 **STITCH**
> A power-user "Compare" screen: add 2–10 people, then a ranked table/list showing how each scores
> on a chosen dimension, with soft bars. Tucked-away, advanced, still on-brand calm. Premium (Diyas).

🛠️ **ANTIGRAVITY**
> Build `app/people-compare.tsx` from `design_import/compare/`. Multi-person add + ranked list, dummy.

---

# 5. RITUALS TAB  *(the calm soul; mostly FREE)*

## 5.1 Rituals home
🎨 **STITCH**
> A "Rituals" home screen — the calm heart of the app. Today's ritual featured at top (one doable
> action, soft illustration, "Begin"), then soft entry cards: Mala counter, Mantras, Meditation /
> Breathwork, and Ritual Journeys (21/40-day). Serene, spacious, candle-soft palette. Never
> superstitious — framed as gentle energy-tuning / wellbeing.

🛠️ **ANTIGRAVITY**
> Build `app/(tabs)/rituals.tsx` from `design_import/rituals/`. Featured today's-ritual + entry
> cards routing to each sub-screen. Dummy data.

## 5.2 Ritual detail
🎨 **STITCH**
> A single-ritual detail screen: a calm full-bleed soft header, the ritual name in serif, simple
> step-by-step instructions in soft numbered cards, a gentle timer/breath option, and a "Mark done"
> button that feels rewarding (subtle celebration). Peaceful.

🛠️ **ANTIGRAVITY**
> Build `app/ritual-detail.tsx` from `design_import/ritual-detail/`. Steps + optional timer + mark-
> done with a small completion animation. Dummy content.

## 5.3 Mala / japa counter
🎨 **STITCH**
> A "Mala" japa counter screen: a large central tap target (a soft mala-bead ring or circle) showing
> the count, a mantra label at top, and a progress ring toward 108. Tapping increments with a sense
> of haptic feedback. Minimal, meditative, beautiful. A reset and a session log.

🛠️ **ANTIGRAVITY**
> Build `app/mala.tsx` from `design_import/mala/`. Tap-to-count with `expo-haptics`, progress to 108,
> reset, session count. Local state.

## 5.4 Mantras
🎨 **STITCH**
> A "Mantras" screen: a list of personalized mantra cards, each with the mantra in Devanagari +
> transliteration + one-line purpose, and a soft play button (audio). A featured mantra at top. Calm,
> reverent, clean.

🛠️ **ANTIGRAVITY**
> Build `app/mantras.tsx` from `design_import/mantras/`. Mantra cards + audio play (`expo-av`), dummy
> list + placeholder audio.

## 5.5 Meditation / breathwork
🎨 **STITCH**
> A "Meditation" screen: a list of calm guided audio sessions (title, duration, soft thumbnail), and
> a player view with a gentle animated breathing circle. Serene, spacious, candle-soft.

🛠️ **ANTIGRAVITY**
> Build `app/meditation.tsx` from `design_import/meditation/`. Session list + player with an animated
> breathing circle (`react-native-reanimated`), placeholder audio.

## 5.6 Ritual journeys (21 / 40-day)
🎨 **STITCH**
> A "Journeys" screen: gamified multi-day remedy journeys shown as soft progress cards (e.g. "40-Day
> Calm", "21-Day Confidence") each with a progress ring (day 7/40) and a streak feel. A detail view
> shows the day-by-day path as a gentle vertical trail with completed/locked states. Motivating but
> calm; framed as energy-tuning, never superstition.

🛠️ **ANTIGRAVITY**
> Build `app/journeys.tsx` + `app/journey-detail.tsx` from `design_import/journeys/`. Journey cards
> with progress + a day-trail detail (done/today/locked). Local progress state.

---

# 6. YOU TAB  *(the data moat / companion home)*

## 6.1 You home (Your story)
🎨 **STITCH**
> A "You" home screen: a warm "Your story" hero — a plain-English "who you are" summary in serif —
> then soft entry cards to: Life Chapters, The Mirror (journal), Patterns, Why did that happen (the
> Proof), Year in Review, Your Purpose, and Settings/Account. A small streak + Diyas balance chip at
> top. Personal, calm, the app's "home base."

🛠️ **ANTIGRAVITY**
> Build `app/(tabs)/you.tsx` from `design_import/you/`. Story hero + entry cards routing to each
> sub-screen; streak + Diyas balance chip (dummy). 

## 6.2 Life Chapters (Dasha timeline)
🎨 **STITCH**
> A "Life Chapters" screen: a beautiful vertical life timeline of dasha periods — each chapter a soft
> segment with its years, a plain-English theme name ("A time for building"), and current-chapter
> highlighted. Tap a chapter for detail. Elegant, story-like, not technical on the surface.

🛠️ **ANTIGRAVITY**
> Build `app/chapters.tsx` from `design_import/chapters/`. Vertical timeline of chapters with current
> highlighted + detail expand, dummy data.

## 6.3 The Mirror (private journal)
🎨 **STITCH**
> A "Mirror" journal screen: a calm, private writing space — a soft "How are you, really?" prompt, a
> clean text area, and below it past entries each stamped with the day's sky (a tiny moon/planet
> note) and date. A gentle "the app reflects this back over time" feel. Private, safe, beautiful. A
> small lock icon (biometric privacy).

🛠️ **ANTIGRAVITY**
> Build `app/mirror.tsx` from `design_import/mirror/`. Write area + entries list with sky-stamp +
> date, local storage for now; optional biometric lock (`expo-local-authentication`). AI reflections
> stubbed (premium).

## 6.4 Patterns (the Pattern Engine payoff)
🎨 **STITCH**
> A "Patterns" screen: warm plain-English personal correlations as insight cards ("You tend to feel
> low energy on Moon-in-Scorpio days"), with simple soft charts. If not enough data yet, a friendly
> progress state ("12 of 30 check-ins — your patterns unlock soon"). Encouraging, never clinical.

🛠️ **ANTIGRAVITY**
> Build `app/patterns.tsx` from `design_import/patterns/`. Insight cards + simple charts (e.g.
> `react-native-svg`) + a cold-start progress state. Dummy data + a toggle to preview both states.

## 6.5 "Why did that happen?" (the Proof)
🎨 **STITCH**
> A "Why did that happen?" screen: a warm prompt to enter a past date, a date picker, then a result —
> a plain-English explanation of what the sky was doing then + "how this repeats for you." Soft,
> insightful, a little awe-inspiring. Premium (Diyas/SUB).

🛠️ **ANTIGRAVITY**
> Build `app/past-date.tsx` from `design_import/proof/`. Date input + explanation result view, dummy.
> Premium gating UI.

## 6.6 Year in Review (Cosmic Wrapped)
🎨 **STITCH**
> A "Year in Review" screen: a Spotify-Wrapped-style shareable recap — a few gorgeous full-screen
> story cards summarizing the user's year (moods, themes, growth) in bold serif over soft pastel
> backgrounds, swipeable, very shareable. Branded, delightful.

🛠️ **ANTIGRAVITY**
> Build `app/year.tsx` from `design_import/year-review/`. Swipeable story cards + share-to-image,
> dummy recap.

## 6.7 Your Purpose
🎨 **STITCH**
> A "Your Purpose" screen: a soul/career blueprint — a warm headline purpose statement in serif,
> then sections (strengths, calling, ideal paths) in soft cards. Inspiring, premium, cached-forever
> feel. Diyas/SUB.

🛠️ **ANTIGRAVITY**
> Build `app/purpose.tsx` from `design_import/purpose/`. Purpose hero + section cards, dummy content.

## 6.8 History + account / Settings
🎨 **STITCH**
> A "Settings & Account" screen: tidy soft sections — profile + birth details (editable, incl. "add
> birth time" if skipped), Diyas wallet (balance + top-up + history), Subscription (plan + manage),
> depth-mode, language, notifications, privacy (delete my data, biometric lock), and an About/Credits
> link (this is where the geocoder attribution lives). Clean, trustworthy, calm.

🛠️ **ANTIGRAVITY**
> Build `app/settings.tsx` from `design_import/settings/`. Sectioned list with the above rows; Diyas
> wallet + subscription rows route to paywall/top-up. Include an About/Credits screen stub. Dummy
> state; account actions wire later.

---

# 7. ALWAYS-ON / OVERLAYS

## 7.1 Ask bubble overlay (the Companion)
🎨 **STITCH**
> An "Ask" chat overlay that slides up from the floating bubble: a warm chat interface — the
> companion's messages in soft cards, the user's on the right, a calm input bar at the bottom with a
> mic option, and quick-action chips at top ("Ask", "Decide", "Talk"). Feels personal and "knows
> you", not a generic chatbot. A small "3 free today" indicator. Premium calm.

🛠️ **ANTIGRAVITY**
> Build `components/AskOverlay.tsx` (slide-up sheet) + `app/ask.tsx` from `design_import/ask/`. Chat
> UI with the 3 quick-action chips, input bar (+ mic stub), daily-limit indicator. Messages from
> dummy data; the AI wires to the backend later.

## 7.2 Paywall  *(NO ADS — Subscription + Diyas ONLY)*
🎨 **STITCH**
> A "Paywall" screen — premium, warm, trustworthy, NO ads anywhere. A serif value headline, a short
> list of premium perks (each a soft row with a small icon), the subscription plans as soft
> selectable cards (weekly / monthly / yearly with a "best value" gold tag + 7-day trial note), a
> single gold "Start free trial" button, and a smaller "or top up Diyas" secondary option. A
> tasteful testimonial line. Calm, never pushy or spammy.

🛠️ **ANTIGRAVITY**
> Rebuild `app/paywall.tsx` from `design_import/paywall/`. Plan cards (weekly/monthly/yearly + trial),
> perks list, primary trial CTA, secondary "top up Diyas" path. NO ad components of any kind.
> Purchases wire to IAP later — buttons stubbed.

## 7.3 Diyas top-up
🎨 **STITCH**
> A "Top up Diyas" screen: warm Diya/coin balance at top, then soft purchase tiles (small/medium/
> large bundles with a bonus on bigger ones), a gentle "what Diyas unlock" note, and a transaction
> history link. Premium, friendly, clear value. Gold accents.

🛠️ **ANTIGRAVITY**
> Build `app/diyas.tsx` from `design_import/diyas/`. Balance + bundle tiles + history link, stubbed
> purchase. IAP wires later.

## 7.4 Home/lock-screen widget
🎨 **STITCH**
> A minimal home-screen **widget** design (small + medium sizes): the daily vibe word + a tiny
> indicator (mood/good-time), on the soft off-white card with one serif word. Glanceable, beautiful,
> no clutter.

🛠️ **ANTIGRAVITY**
> Build the widget from `design_import/widget/` (note: native widgets need `expo-apple-targets` /
> Android widget config — flag if it needs a config plugin; an in-app preview screen `app/widget.tsx`
> is fine as a first pass). Dummy daily word.

---

# ✅ When the whole frontend is built
1. Make sure each session updated `FRONTEND_PROGRESS.md` (what's done / broken / left).
2. Run the full app in Expo Go and click through every tab + screen.
3. **Then come back to Claude** to wire every screen to the live backend (real charts, forecasts,
   AI chat, people weather, etc.) and make the app fully functional. That wiring step is mine.
