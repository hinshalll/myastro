# ASTROLO — RN + Expo porting package (for Claude Code)

Everything Claude Code needs to port the ASTROLO front-end to React Native + Expo. Hand it the
whole `screens/astro/` folder (source + 6 PNGs + this `handoff/`). If Claude Code has the repo
directly it can read the real files; the dump below is for copy-paste handoff.

## The package
**Start-here prompt:** `CLAUDE-CODE-PROMPT.md` ← paste into Claude Code first (the instructions).

**Answers to Claude Code's intake questions:**
- `SOURCE-DUMP.md` — every runtime file, full path + complete untruncated contents (Q1).
- `PORT-FACTS.md` — standalone status, full asset list, facts sheet (fonts/icons/libraries,
  real-vs-faked data), and the animation catalog (Q2–Q5).

**Source code** (in `screens/astro/`, load/read in this order):
`theme.ts` → `astro.tsx` → `astro-today.tsx` → `astro-plan.tsx` → `astro-screens.tsx` → `Home.html`

**Images** (in `screens/astro/`): `chatfab.png`, `chatsage1.png`, `chatsage2.png`,
`chatsage3.png`, `sage2.png` (used) · `sage1.png` (present, unused).

**Deep docs:**
- `PORT-TO-RN.md` — the deep, per-feature spec (exact visuals, motion, RN mapping).
- `../../FEATURES.md` — content/behaviour/voice/economy source of truth (exact copy).
- `../HANDOFF.md` — data models = backend contract + prototype-shortcuts-to-undo.
- `../FRONTEND-EXPLAINER.md` — short orientation.

**Screenshots** (`shots/`, the visual ground truth): 19 PNGs, one per screen/state.

## The 19 screenshots
| # | file | screen / state |
|---|---|---|
| 01 | today-read-top | Today · Read — top (greeting, eclipse, reading) |
| 02 | today-read-reading | Reading hero — mood word, chips, "why this?" |
| 03 | today-read-lower | Life areas + Mirror + Ritual |
| 04 | checkin-done | Check-in reflection + streak + +1 diya |
| 05 | plan-myday | Plan · My Day — the living-sky slider (signature) |
| 06 | plan-lower | Ask the Moment + My Panchang |
| 07 | plan-tools | Find a good day / Check my plans / Time Capsule |
| 08 | sheet-timecapsule | Time Capsule bottom-sheet |
| 09 | chat | Chat with Sage |
| 10 | wallet | Diyas wallet — hero + earn + buy |
| 11 | wallet-lower | ASTROLO Plus + history |
| 12 | decode | Decode hub — Your Kundli + readings |
| 13 | decode-tools | Matching + Explore-yourself tools grid |
| 14 | notifications | Notifications screen |
| 15 | journal-write | The Mirror — writing view |
| 16 | month | Full-screen month calendar |
| 17 | month-day-sheet | Tapped-day detail sheet |
| 18 | sheet-eclipse | Eclipse detail sheet |
| 19 | sheet-lifearea | Love/Work/Money detail sheet |

## One-line summary of the app
Clean **white** Vedic-astrology app; one of **12 daily moods** tints only accents (never the
white bg); companion is a cute sage (**Sage**); deliberately alive (ambient motion + a draggable
living-sky day-clock). Screens: Today (Read/Plan sub-tabs), Chat, Wallet, Decode, Notifications,
Journal + bottom-sheets. Timeline/People/Rituals/You are "coming soon."
