# features/memory — THE MEMORY (the app's per-user brain, a headline USP)

A per-user brain that **auto-remembers what matters** and feeds it back into the
companion and the personalized forecast. Blueprint v4 §5.

## What it stores
`memory_facts` (Supabase): the **distilled, durable facts** the AI extracts from
journal entries + chat (people, goals, fears, recurring themes, dates). Raw
signals live elsewhere (`journal_entries`, `checkins`); this is the compressed
"what the app knows about you" layer. **No vector DB** — a single user's facts are
few, so they're loaded + ranked directly (salience + recency). Qdrant stays for
the shared book RAG only.

## Flow
1. **Save** a journal entry → `POST /me/journal` schedules a background task that
   calls `memory.service.extract_and_save(...)`.
2. **After a chat** → the app calls `POST /memory/extract { text, source:"chat" }`.
3. **Extract** → one cheap structured AI call distils durable facts; deduped/merged
   against existing facts (text-similarity, never raises).
4. **Recall** → `GET /memory/context` returns a compact block (top facts +
   patterns + recent mood); pass its `text` to `/consultation/ask` as
   `memory_context`, and use it to personalize the forecast.

## Endpoints (JWT)
- `GET /memory/facts` — list the user's remembered facts
- `PUT /memory/facts/{id}` — edit (fact / category / salience / status)
- `DELETE /memory/facts/{id}` — forget a fact
- `POST /memory/extract` — distil durable facts from text (call after a chat)
- `GET /memory/context` — the compact recall block (pass to `/consultation/ask`)
- `GET /memory/today?date=` — the Memory feeding the forecast: a deterministic
  personal heads-up when today's sky triggers one of the user's own patterns,
  plus recent mood trend (no AI). Merge `personal_note` with `/dashboard/forecast`.

## Frontend wiring contract (what the app must call)
1. **Journaling** → just `POST /me/journal`. Extraction happens automatically in a
   background task. Nothing else to do.
2. **Chat** → on open, `GET /memory/context`; pass its `text` as `memory_context`
   in every `POST /consultation/ask`. On session end, `POST /memory/extract
   { text: <the user's turns>, source: "chat" }`.
3. **Today** → `GET /memory/today` and show `personal_note` under the forecast.
4. **You tab → "Memory" screen** → `GET /memory/facts` (list), `PUT` to edit,
   `DELETE` to forget. This is the user's privacy/control surface.

## Status (2026-06-18)
**Built + verified:** the table, DB CRUD, extract/dedupe/recall service, all 6
endpoints, server-side sky-stamping, background extraction, chat injection,
deterministic forecast personalization (`/memory/today`). App boots, routes mount.
**Left:** the frontend wiring above; a live test once Supabase + `GEMINI_API_KEY`
+ `DEEPSEEK_API_KEY` are set (extraction uses the `json` task ladder). Optional
later: a richer AI-written daily personalization; pgvector journal topic-search.

## Privacy
Chat is ephemeral (never stored). The user can view, edit, and delete any fact.
Writes are server-side (service client); reads/edits use the user's RLS client.
