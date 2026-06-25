# Myastro — Frontend prompts (the latest, tool-agnostic) + continuity

> **Read this to resume the frontend work.** It holds the finalized, backend-accurate design
> prompts so nothing is lost across a compaction. These are **tool-agnostic** (work in Claude Design
> OR Google Stitch): they give structure, content, exact copy, and functioning, and leave the look to
> the tool. Voice for all copy: warm, plain, cozy, no jargon, **no em dashes**, no AI-slop words.

## Status (2026-06-25)
- **Frontend is being RESTARTED.** The earlier Claude Design Today build was rejected.
- **Tooling:** design in **Claude Design OR Google Stitch** (these prompts work in both) → port to
  **React Native + Expo (SDK 54)** with **Google Antigravity 2 (use Gemini 3.1 Pro)**, then I wire
  the backend + we test in Expo Go. (AI Studio errored out; z.ai rejected as low quality.)
- **Backend is ready** for all of this (engine frozen + validated; daily loop, memory, talk, wallet,
  geo, chart, proof all live on Render). Onboarding + Today endpoints all exist (mapped below).
- **App name NOT chosen** → show NO name/logo in any screen; a splash with the name comes last.
- **Nav (v4):** bottom tabs **Today · Timeline · People · Rituals · You**; top cluster on every
  screen = **avatar + Diya chip + Readings & Tools icon**; floating **Moon companion** (chat).

## Recovering anything lost to compaction (IMPORTANT meta-tool)
The full conversation transcripts live at
`C:\Users\hinsh\.claude\projects\C--Users-hinsh-Desktop-myastro\*.jsonl` (the big one:
`4b279895-12ab-45e5-b8ad-ad0f4cdc6403.jsonl`). To recover an exact past prompt/decision, run a small
python scan over those files (json.loads each line, pull `message.content[].text`, grep for a
keyword like "LocationIQ" / "Diya" / "onboarding"), then print the matching message text. This is how
the prompts below were recovered after an earlier compaction. Use it whenever detail is missing.

---

# 1. THE TODAY SCREEN PROMPT (tool-agnostic, full depth)

> Build a **premium, interactive, multi-screen mobile app prototype** (phone-sized). I am giving you
> **structure, content, exact copy, and functioning, not visual design.** For every visual and
> interaction choice, think of your own best approach first, weigh it against anything I describe, and
> use whichever is better. Bring top-tier product-design taste, make it genuinely interactive with
> realistic placeholder content. It is a warm, cozy Vedic-astrology app with a gentle, personal feel,
> like a caring friend, never clinical. **Show no app name and no logo anywhere** (a splash with the
> name comes later).
>
> **Voice for all copy:** warm, plain English, a little tender, no astrology jargon, no em dashes, no
> mystical or AI filler words (no "cosmic", "mystic", "aura", "manifest"). The companion is the Moon.
>
> Build **four connected, navigable screens/states:** the **Today** home (main), the **Chat** with the
> Moon (opens when the Moon is tapped), the **Diyas wallet** (opens when the Diya coin chip is tapped),
> and a stub **Readings & Tools** sheet (opens from the top-bar icon). Make navigation real.
>
> ## Persistent elements (on every screen)
> **Top cluster, top-right:** the user's **avatar**, a **Diya coin chip** showing a balance (e.g.
> "240 🪔"), and a small **Readings & Tools icon** (a compass or grid). The chip briefly animates "+1"
> when a coin is earned. Tap chip → Diyas wallet; tap avatar → placeholder profile; tap Readings icon →
> Readings & Tools sheet. On Today the cluster sits beside the greeting; elsewhere the greeting is gone
> but the cluster stays.
> **The Moon companion, floating bottom-right:** a small **Moon** that feels alive, softly breathing
> and drifting, showing the current lunar phase, with a gentle glow. Poking it makes it react; when
> there's a new insight it glows brighter with a small rising sparkle. **Tap → Chat.** It is the user's
> astrologer-guide, a calm celestial presence, never a pet, never a face.
>
> ## TODAY SCREEN, top to bottom
> A calm vertical scroll of clearly titled cards. Only the first reading card expands; the rest show
> their content directly, and the prompt-style cards (journal, "should I") stay slim until used.
>
> **Greeting bar.** A time-aware greeting with the user's name and date ("Good morning, Aanya" /
> "Tuesday, 24 June"), the top cluster on the right, and a small notification bell with a dot when
> there's a new alert. Below, one warm line summarising the day: "A soft, homeward kind of day."
>
> **Eclipse heads-up card (conditional, appears first when present).** On the rare days a solar or
> lunar eclipse falls within the next month, a gentle card sits at the very top. It names the eclipse
> and counts down ("A lunar eclipse in 4 days") with one calming line ("A week for rest and gentle
> routines, since feelings can run high"). Tapping it opens a small detail view with the date, fuller
> guidance, and the traditional caution-period timing ("the Sutak window begins about nine hours
> before, around the evening of the 27th"). Normally it does not exist. Build it but make it toggleable
> so the state is visible.
>
> **Card titled "Today" (the day's reading, the only card that expands).** Collapsed: a single **mood
> word** for the day, one of twelve fixed words (Settled, Guarded, Bold, Tender, Restless, Capable,
> Warm, Deep, Wandering, Driven, Upbeat, Quiet), paired with a soft image. Beneath it, one warm
> sentence ("Your heart pulls toward home today, and you may feel softer than usual."). Then, set apart
> and gentler, a **personal line that clearly speaks to this user** from their own recent history
> ("You've been running low these last few days, so be extra kind to yourself."), designed to collapse
> when there isn't one. A small **share** control. "Read more" reveals four one-sentence pieces: **what's
> good today**, **what to go easy on**, **one small thing to do**, and a plain **"why"** ("Right now the
> Moon is passing through the part of your sky that rules home and feeling, which traditionally turns
> the day soft and inward."). Changes daily. Mock realistic content.
>
> **Card titled "Check in".** "How are you today?" with two rows of selectable chips: **mood** (calm,
> tender, sharp, heavy, wired) and **energy** (low, steady, bright, restless), one per row, editable.
> The moment both are chosen, an instant **one-line reflection** appears tying how they feel to the
> day ("Heavy, and a tender kind of day, so the weight is real, not random. Let it be slow."), with a
> **streak** indicator ("12 days in a row"), and selecting earns +1 Diya (the chip animates up top). If
> already checked in, show their picks + reflection, still editable.
>
> **Card titled "Should I, right now?".** A slim card for in-the-moment decisions. The user can type a
> quick dilemma ("Should I send this text?") or just tap. Returns an instant gentle verdict (**Yes**,
> **Wait**, or **Proceed gently**), a warm reason ("It's a mixed moment, you can move ahead, just
> gently and without forcing it"), and a short plain "why" about the timing of the moment. A "Talk it
> through" control opens the Chat carrying that question. Copy should make clear it reads the timing of
> this moment, not the choice itself.
>
> **Card titled "Good times today".** The day's **best** window and the window to **ease off**, with
> times and short notes ("Best hours: 11:40am to 12:30pm, good for important talks" / "Ease off: 9:00
> to 10:30am, hold big decisions"), a one-line summary at top ("Strong window near midday, soft dip
> mid-morning."), and a live indicator if the current time is inside a window. "See full timing" opens
> a fuller breakdown of the day's good/neutral/avoid windows.
>
> **Card titled "Today's ritual".** One small doable practice ("Light a lamp at dusk and breathe
> slowly for one minute") with a one-line reason ("a good day for your Saturn practice"). "Begin" opens
> simple how-to steps; completing earns a couple of Diyas and advances a gentle practice streak. Warm,
> never preachy.
>
> **Card titled "Your journal" (the Mirror, make it distinct and inviting).** A soft prompt "What's on
> your mind?" with a slim text preview and a **mic icon** for voice. Tapping opens a calm writing view
> (type or speak, no pressure, no formatting). On save, the Moon returns **one** warm line tuned to the
> entry's feeling (comfort if heavy, a quiet celebration if happy), never advice, and the card marks
> "you wrote today." Never shows past entries here, this is for setting things down, not scrolling back.
>
> **"Looking ahead" peek.** A compact horizontal row of the next three or four days (date, one-word
> vibe, small status dot: good/neutral/difficult). Tapping a day expands a tiny inline preview (mood
> word, vibe, good/avoid), and a quiet "see your full week on the Timeline" line leads to the Timeline.
>
> **Bottom nav.** Five tabs: **Today** (active), **Timeline**, **People**, **Rituals**, **You**. Only
> Today is built; the rest are placeholders.
>
> ## CHAT SCREEN (opens from the Moon)
> A warm conversational view with the astrologer-guide. The Moon sits at the top, alive and glowing.
> Show a short example conversation that knows the user: the Moon opening with "Hey Aanya. The day's
> running tender, how are you holding up?", the user replying, and the Moon answering warmly and
> grounded in their chart/history ("That tracks. With your Moon where it is, these in-between days
> always ask more of you. Want to talk about the work thing you mentioned?"). An input field with a
> **mic** option. Warm, plain, unhurried, like texting someone who genuinely knows you.
>
> ## DIYAS WALLET SCREEN (opens from the Diya chip)
> **Balance hero:** a glowing diya/oil-lamp with the count ("240 🪔 lit"), brighter at higher balance.
> **Earn ("light a diya by doing good"):** a checklist with progress, Daily check-in +1 (done),
> Today's ritual +2, A journal note +1, 7-day streak +10, Invite a friend +25, plus a **daily-cap**
> indicator ("3 of 5 earned today").
> **Buy Diyas:** three tiles with the bonus, Glow ₹99 → 110, Blaze ₹299 → 380 (best value),
> Festival ₹799 → 1,150.
> **Go Plus card:** "Unlimited chat, couple, family and deep Patterns, cross-reference free, and 25%
> off everything. ₹199 a month, 7-day free trial."
> **History:** a ledger of earned/spent rows (date, what, ± amount), "Today's ritual +2", "Full Life
> Reading −60", "7-day streak +10".
>
> ## READINGS & TOOLS sheet (opens from the top-bar icon)
> A simple stub list: your kundli, premium readings (Full Life, Marriage, Purpose), kundli matching,
> an auspicious-days planner, and tools (numerology, palmistry, face reading, tarot). A tappable list
> is enough for now.
>
> **Overall:** four genuinely navigable screens, calm/warm/premium, your own design judgment leads.

## Today → backend wiring (for me, when it's built)
forecast (mood word + rows + why) → `POST /dashboard/forecast`; personal line → `GET /memory/today`;
check-in → `POST /me/checkins` + `POST /companion/micro-insight` + `/me/streaks`; Should I →
`POST /dashboard/decide-quick` (deeper → `/consultation/ask`); good times → `POST /dashboard/timing`;
ritual → `POST /rituals/today`; eclipse → `POST /dashboard/day-alerts`; week peek →
`POST /dashboard/week`; journal → `POST /me/journal`; chat → `POST /consultation/ask` (+memory_context);
wallet → `GET /wallet/balance|history`, earn/spend via `/wallet/*`.

---

# 2. THE ONBOARDING FLOW PROMPTS (tool-agnostic, v4, backend-accurate)

Flow: **Welcome → Name+gender → Birth date+place → Birth time → Reveal → Sign-up**, with **Login**
branching off the Welcome link. No app name/logo. Depth-mode is NOT asked here (it moved to Settings,
default 'simple'). Keep the LocationIQ attribution on the place screen (required).

**1 — Welcome**
> First screen, same calm visual system. No app name/logo. Headline "Meet yourself, exactly as you
> are." Supporting line "Astrology without the noise." A simple celestial/Moon visual. One main button
> "Begin". Below it a small text link "I already have an account" (opens Login, not onboarding). No
> input.

**2 — Name + gender**
> Step titled "Tell us about you," small step/progress indicator at top. A first-name field ("What
> should we call you?"), and an optional gender selector as three soft chips, Female / Male / Other,
> with a small note "used for certain Vedic readings." "Continue" enabled once a name is entered.
> Capture `name` (required), `gender` ('Female'|'Male'|'Other'|null). Maps to backend `name`, `gender`.

**3 — Birth date + place**
> Step titled "When and where were you born?", step indicator, generous spacing. A clear date-of-birth
> picker (day/month/year); and a place search showing live city suggestions as they type ("Mumbai,
> India", "Pune, India"), selecting one fills it in. A small note "your town is enough," and directly
> beneath it a subtle attribution line "Search by LocationIQ." "Continue" enabled once both set.
> Capture `birthDate` ("YYYY-MM-DD"), `birthPlace` as `{label,lat,lon,tz}`. Wiring: place field calls
> `POST /geo/search { query, limit:5 }` → `{ results:[{label,lat,lon,tz}] }`; the "Search by LocationIQ"
> credit MUST stay visible. Maps to `birth_date`, `birth_place`(=label), `lat`, `lon`, `tz`.

**4 — Birth time (3 levels, with consequences)**
> Step about birth time, step indicator, designed so the user always understands their choice. "Do you
> know your birth time?" with three soft option cards, each with a one-line consequence note:
> - "I know my exact time" — "Most precise: unlocks your rising sign, houses, and exact timing." →
>   reveal a time picker.
> - "I know it roughly" — "Still accurate: only the finest timing details may shift." → reveal a
>   part-of-day selector (early morning, morning, afternoon, evening, night).
> - "I don't know it" — "No problem: we'll build a Moon-based chart full of insight, and you can add
>   your time anytime to unlock your rising sign and houses."
> Below, a subtle expandable "Why does this matter?" (birth time sets your rising sign and houses,
> which fine-tune timing; your date and place alone already reveal a lot). "Continue" always enabled.
> Capture `birthTimePrecision` ('exact'|'approximate'|'unknown'), `birthTime` (exact's time; rough →
> representative time, early morning 06:00 / morning 09:00 / afternoon 14:00 / evening 18:00 / night
> 22:00; else null). Rule: rising sign + houses unlock ONLY when precision is 'exact'. Maps to
> `birth_time`, `birth_time_known` (true unless 'unknown'), `exact_time` (true only for 'exact').

**5 — Reveal (the first wow, with the Proof)**
> A warm, personal "Here's who you are," before any sign-up. A soft image keyed to gender. On load it
> shows: a serif headline naming who they are; two or three short insight cards (small label + warm
> one-line plain-English insight, with the deeper Sanskrit/technical layer behind a quiet "why?" tap);
> and its own section "Where you are right now" describing the life chapter they're in. If birth time
> is rough/unknown, a soft note explains what's already readable and what unlocks later, collapsing
> gracefully. Then "Want to see how real this is? Pick a day that mattered to you," and on a past date
> it reveals what the sky was doing then and how it fits (optional, with "Maybe later"). A primary
> "Continue" to Sign-up. Gentle loading ("Reading your sky...") + soft fallback. No sign-up/paywall here.
> Wiring: post `{ name, date:birthDate, time:birthTime or "", tz, lat, lon, gender }` to
> `/chart/interpret` → `{ headline, core:[{title,body,sanskrit,why}], current_chapter, precision_note }`.
> The Proof posts `{ profile, date }` to `/companion/proof` → `{ headline, story }`. Mock for now.

**6 — Sign-up (last onboarding screen)**
> The only place we ask, after they've felt the value. Headline "Let's keep your story safe." Line "So
> your readings, your journal, and your memory are always here." Buttons: "Continue with Apple",
> "Continue with Google", "Continue with email" (stubbed). Privacy line "Your birth details and journal
> stay private to you. Always." After this → Today. Wiring: creates the Supabase account, then saves
> the self-profile via `POST /me/profiles` (`name, gender, birth_date, birth_place, lat, lon, tz,
> birth_time, birth_time_known, exact_time, relation_tag:'self', source:'self'`).

**Login (where "I already have an account" leads)**
> Same calm system. Headline "Welcome back." Line "Pick up right where you left off." Buttons "Continue
> with Apple / Google / email" (email+password for the email option). A small link "New here? Start
> fresh" → Welcome. Wiring: Supabase Auth sign-in, then `GET /me/profiles`, then land on Today,
> skipping onboarding. (Login backend already exists: Supabase Auth client-side + `features/me/auth.py`
> JWT verification + the `handle_new_user` trigger.)

Onboarding state object: `{ name, gender, birthDate, birthPlace{label,lat,lon,tz}, birthTimePrecision,
birthTime }`. Every field maps to an existing endpoint.
