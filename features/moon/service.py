"""features.moon.service — the PROACTIVE companion (the Sage).

The user-facing character is the **Sage**; this backend module keeps the legacy
name `moon` (module / table `moon_messages` / `/moon/*`). "Moon" below means the Sage.

When the app opens, the Sage may "reach out first": it surfaces ONE warm opener
and the floating button glows with a dot until the user reads it. Three kinds,
in priority order:

  • lookback — a journal entry from ~a year ago (an anniversary; rare, special).
  • pattern  — one of the user's OWN unlocked patterns that today's sky triggers
               (reuses memory.personalize_today, so the Sage and the Memory agree).
  • nudge    — a gentle relational nudge: a warm/relational day + a person the
               user has told us about.

DETERMINISTIC, no AI (the AI is the chat REPLY when the user taps in). The picker
`pick_opener` is pure (takes the data) so it is unit-testable without a DB.
"""

from __future__ import annotations

from datetime import date as _date, timedelta

from shared.db import supabase_client as db
from shared.companion import COMPANION_NAME   # single source of the companion's name


def build_welcome(name: str | None) -> dict:
    """The companion's ONE-TIME intro, sent on the user's first app open. Curated
    (no AI): who it is + what it can do, in its warm, plain voice. `name` = the
    user's first name (optional). Returns a moon-message dict (kind 'welcome')."""
    first = name.split()[0] if name else ""
    hi = f"Hi {first}, " if first else "Hi, "
    body = (
        f"{hi}I'm {COMPANION_NAME}, and I'll be your guide here. I read your real "
        "birth chart, so what I tell you is about you, not a generic horoscope. As "
        "you write to me and check in, I quietly remember: your good days and your "
        "hard ones, the people you mention, what's been on your mind. So over time I "
        "come to understand you, and I'll reach out now and then when I notice "
        "something worth telling you, a pattern in your days or a gentle nudge. You "
        "can ask me anything, any time, even a quick yes or no. Whatever you share "
        "stays private, always. I'm glad you're here."
    )
    return {"kind": "welcome", "body": body, "meta": {"companion": COMPANION_NAME}}


# ─────────────────────────────────────────────────────────────────────────────
# Pure picker (no DB) — given the data, choose the single best opener or None.
# ─────────────────────────────────────────────────────────────────────────────

def _lookback(journals: list[dict], today: _date) -> dict | None:
    """A journal entry from ~a year ago (±2 days). We never quote it back (gentle,
    private) — just mark the anniversary."""
    target = today - timedelta(days=365)
    for j in journals:
        raw = j.get("date")
        if not raw:
            continue
        try:
            jd = _date.fromisoformat(raw)
        except ValueError:
            continue
        if abs((jd - target).days) <= 2:
            return {
                "body": "A year ago around today, you wrote to me. Look how far you've "
                        "come since then.",
                "meta": {"journal_date": raw},
            }
    return None


def _nudge(forecast: dict, facts: list[dict]) -> dict | None:
    """A warm/relational day + someone the user has mentioned → a gentle nudge."""
    relational = forecast.get("chandra_house") == 7 or forecast.get("vibe_word") in ("Warm", "Tender")
    if not relational:
        return None
    person = next((f for f in facts
                   if (f.get("category") in ("person", "relationship")) and f.get("fact")), None)
    if not person:
        return None
    fact = person["fact"].strip().rstrip(".")
    return {
        "body": f"It's a warm day for the people you love. You once told me: {fact}. "
                f"Today might be a good day to reach out.",
        "meta": {"fact_id": person.get("id")},
    }


def pick_opener(forecast: dict, matched_kinds: list[str], personal_note: str,
                journals: list[dict], facts: list[dict], today: _date) -> dict | None:
    """Choose the best opener: lookback > pattern > nudge. Pure (no DB)."""
    lb = _lookback(journals, today)
    if lb:
        return {"kind": "lookback", **lb}

    if matched_kinds and personal_note:
        return {"kind": "pattern", "body": personal_note,
                "meta": {"matched": matched_kinds}}

    nd = _nudge(forecast, facts)
    if nd:
        return {"kind": "nudge", **nd}

    return None


# ─────────────────────────────────────────────────────────────────────────────
# Gather the data + pick (reads DB via the user's RLS client)
# ─────────────────────────────────────────────────────────────────────────────

def build_opener(user, today: _date) -> dict | None:
    """Fetch the inputs and run the pure picker. None = nothing to say today."""
    from features.memory.service import personalize_today, _self_astro
    from shared.astro.forecast import daily_moon_forecast

    ap = _self_astro(user.client, user.user_id)
    if not ap:
        return None
    try:
        forecast = daily_moon_forecast(ap, today.isoformat())
    except Exception:
        return None

    pt = personalize_today(user, today.isoformat())
    try:
        journals = db.list_journal(user.client, user.user_id, 400)
    except Exception:
        journals = []
    try:
        facts = db.list_memory_facts(user.client, user.user_id, limit=40, only_active=True)
    except Exception:
        facts = []

    return pick_opener(forecast, pt.get("matched_kinds", []),
                       pt.get("personal_note", ""), journals, facts, today)
