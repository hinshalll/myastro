# AI Costs — per-feature ledger

> **Why this file exists:** to keep AI spend visible and deliberate. Rule: **deterministic / pre-saved
> text by default; AI only where it genuinely adds value** (real conversation, understanding free-text,
> interpreting a fresh chart). Every AI call that produces *astrology* must be **RAG-grounded** against
> the ingested classical books (AI alone hallucinates astrology). Keep this updated as features land.

## Models in use
- **Text:** `deepseek-v4-flash` — ~$0.14 / 1M input, ~$0.28 / 1M output; **cached input ~$0.0028 / 1M
  (≈98% off)** → exploit the prefix cache for chat/system prompts.
- **Vision:** `gemini-3.1-flash-lite` — ~$0.25 / 1M input, ~$1.50 / 1M output (palm/face only; not used
  on the Today screen).
- Routing is per-task in `shared/ai/config.py`; never hardcode a model.

## Cost tiers (rule of thumb per call, deepseek text)
- **Free** = pure math / pre-saved lookup, no model call.
- **~$0.0001** = one short extraction/classification (a few hundred tokens in, ~100 out).
- **~$0.0003–0.001** = one chat/interpretation turn (RAG context in, a few hundred out; cache helps).

## Today screen — feature-by-feature

| Feature | AI? | When | Model / cost | RAG |
|---|---|---|---|---|
| Header, Moon phase, **Hora** line | ❌ Free | render | math | n/a |
| **Grahan** heads-up | ❌ Free | render | `/dashboard/day-alerts`, math | n/a |
| **The reading** (mood + good-for/go-easy + why) | ❌ Free | render | `/dashboard/forecast` + lookup tables | n/a |
| Personal line in the reading | ❌ Free | render | `/memory/today` (pattern/trend, no AI) | n/a |
| **Good & bad times** | ❌ Free | render | `/dashboard/timing`, math | n/a |
| **Check-in** + summary line | ❌ Free | on tap | pre-written lookup (mood×energy×day-state) | n/a |
| **Mirror** — save | ✅ | per entry saved (and **only if the entry has real signal**) | extraction, ~$0.0001 | n/a |
| Mirror — the one warm line back | ❌ Free | on save | templated by detected sentiment | n/a |
| **Today's ritual** nudge | ❌ Free | render | `/rituals/today`, math | n/a |
| **My Day** scheduler | ❌ Free | use | `/dashboard/timing` + keyword→window map | n/a |
| **My Panchang** (3-day + month) | ❌ Free | use | `/dashboard/forecast` per day + `/dashboard/muhurta` | n/a |
| **Muhurat** finder | ❌ Free | on use | `/dashboard/muhurta`, math | n/a |
| **Calendar Doctor** | ❌ Free | on use | rate each event's slot, math | n/a |
| **Ask the Moment** — quick "should I now" | ❌ Free | on cast | `/dashboard/decide-quick` (Tara math) | n/a |
| **Ask the Moment** — deeper Prashna | ✅ | on a deeper cast | interpret, ~$0.0003 | **yes (Prashna books)** |
| **Time Capsule** | ❌ Free | save + deliver | store + date math, scheduled push | n/a |
| **Sage companion** — proactive opener | ❌ Free | when it fires | `/companion/patterns` text (math) | n/a |
| **Sage companion** — a chat reply | ✅ | per user message | chat, ~$0.0003–0.001 (cache) | **yes (intent→books)** |

**Takeaway:** the Today screen is **almost entirely free**. The only AI is (1) the Mirror's Memory
extraction (skipped on low-signal entries), (2) the Sage's chat replies, and (3) Ask-the-Moment's
deeper Prashna. A heavy daily user costs well under ₹0.10/day in AI.

## Standing cost rules
1. **Pre-saved > AI** wherever AI adds no real value (all the daily reads, timing, panchang, capsule).
2. **RAG-ground every AI astrology output** (only where the books are ingested). No ungrounded claims.
3. **Selective memory:** extract a fact only when the entry carries durable, prediction- or comfort-
   relevant signal (people, goals, fears, meaningful events, preferences, patterns). **Skip extraction
   entirely on trivial entries** — saves the call *and* keeps user data clean.
4. **Exploit the DeepSeek prefix cache** for chat/system prompts (≈98% off repeat input).
