"""features.memory.service — THE MEMORY: distil, store, recall.

The headline moat: a per-user brain that auto-remembers what matters.

  • extract_and_save  — a cheap structured AI call distils DURABLE facts from a
    journal entry or a chat, deduped/merged against what's already known, and
    stored in `memory_facts` (server-side, SERVICE client). Never raises.
  • build_memory_context — assembles a compact "what you remember about this
    person" block (top facts + unlocked patterns + recent mood) to inject into
    the companion and to personalize the forecast. Cheap: a few reads, no AI.
  • list/edit/delete — the user owns their memory (privacy/trust), via their own
    RLS-scoped client.

NO vector DB: a single user's facts are few, so we load + rank them directly
(salience + recency). Qdrant stays for the shared book RAG only. If semantic
search over raw journal text is ever wanted, use Supabase pgvector, not a second
service.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from difflib import SequenceMatcher

from shared.db import supabase_client as db

_MAX_FACTS_IN_CONTEXT = 18
_DUP_RATIO = 0.82            # text similarity above this = the same fact (reinforce, don't duplicate)
_VALID_CATEGORIES = {
    "person", "relationship", "event", "goal", "fear",
    "preference", "health", "work", "money", "other",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


# ─────────────────────────────────────────────────────────────────────────────
# Extraction (cheap structured AI; robust — never raises)
# ─────────────────────────────────────────────────────────────────────────────

_EXTRACT_PROMPT = """You maintain the long-term memory of a warm astrology companion. \
From the TEXT below, extract only DURABLE facts about the user that are worth \
remembering for months: people in their life (with their relation), ongoing \
situations, goals, fears, recurring themes, important dates, strong preferences. \
IGNORE passing moods, weather, one-off trivia, and anything ephemeral.

Each fact: ONE short third-person line about the user, written in ENGLISH even if \
the text is in another language (translate as needed, so memory stays uniform). \
Assign a category from \
[person, relationship, event, goal, fear, preference, health, work, money, other] \
and a salience 0.0-1.0 (how important to remember long-term).

Do NOT repeat anything already in EXISTING FACTS.

Return STRICT JSON only: a list like \
[{"fact": "Has a partner named Rahul", "category": "person", "salience": 0.8}]. \
If nothing durable is present, return [].

EXISTING FACTS:
{existing}

TEXT:
{text}
"""


def _extract_facts_ai(text: str, existing: list[str]) -> list[dict]:
    """Return a list of {fact, category, salience}. Never raises — [] on failure."""
    if not text or not text.strip():
        return []
    try:
        from shared.ai.gemini_client import generate_content_with_fallback
        ex = "\n".join(f"- {e}" for e in existing[:40]) or "(none yet)"
        prompt = (_EXTRACT_PROMPT
                  .replace("{existing}", ex)
                  .replace("{text}", text.strip()[:4000]))
        raw = generate_content_with_fallback(prompt, task="json") or ""
        m = re.search(r"\[.*\]", raw, re.DOTALL)          # tolerate prose around the JSON
        data = json.loads(m.group(0)) if m else json.loads(raw)
        out = []
        for d in (data if isinstance(data, list) else []):
            fact = str(d.get("fact", "")).strip()
            if not fact:
                continue
            cat = str(d.get("category", "other")).strip().lower()
            if cat not in _VALID_CATEGORIES:
                cat = "other"
            try:
                sal = float(d.get("salience", 0.5))
            except (TypeError, ValueError):
                sal = 0.5
            out.append({"fact": fact[:300], "category": cat,
                        "salience": min(1.0, max(0.0, sal))})
        return out[:12]
    except Exception:
        return []


def extract_and_save(user_id: str, text: str, source: str = "chat") -> dict:
    """Distil durable facts from `text` and MERGE them into the user's memory.
    Server-side (SERVICE client, like the wallet). Never raises.
    Returns {ok, added, reinforced}."""
    try:
        svc = db.get_service_client()
    except Exception:
        return {"ok": False, "added": 0, "reinforced": 0}

    try:
        existing = db.list_memory_facts(svc, user_id, limit=200, only_active=True)
    except Exception:
        existing = []
    existing_pairs = [(e, _norm(e.get("fact", ""))) for e in existing]
    candidates = _extract_facts_ai(text, [e.get("fact", "") for e in existing])

    added = reinforced = 0
    for c in candidates:
        cn = _norm(c["fact"])
        match = None
        for row, rn in existing_pairs:
            if rn == cn or SequenceMatcher(None, rn, cn).ratio() >= _DUP_RATIO:
                match = row
                break
        try:
            if match:
                db.update_memory_fact(svc, match["id"], {
                    "last_seen": _now_iso(),
                    "times_seen": int(match.get("times_seen", 1)) + 1,
                    "salience": max(float(match.get("salience", 0.5)), c["salience"]),
                })
                reinforced += 1
            else:
                row = db.insert_memory_fact(
                    svc, user_id, c["fact"],
                    category=c["category"], source=source, salience=c["salience"],
                )
                existing_pairs.append((row, cn))
                added += 1
        except Exception:
            continue
    return {"ok": True, "added": added, "reinforced": reinforced}


# ─────────────────────────────────────────────────────────────────────────────
# The user's own view of their memory (RLS-scoped client — privacy/control)
# ─────────────────────────────────────────────────────────────────────────────

def list_facts(user) -> list[dict]:
    return db.list_memory_facts(user.client, user.user_id, limit=300, only_active=False)


def edit_fact(user, fact_id: str, fields: dict) -> dict | None:
    allowed = {k: v for k, v in fields.items()
               if k in {"fact", "category", "salience", "status"} and v is not None}
    if not allowed:
        return None
    return db.update_memory_fact(user.client, fact_id, allowed)


def delete_fact(user, fact_id: str) -> None:
    db.delete_memory_fact(user.client, fact_id)


# ─────────────────────────────────────────────────────────────────────────────
# Recall: the compact context the companion + forecast read (cheap, no AI)
# ─────────────────────────────────────────────────────────────────────────────

def build_memory_context(user) -> dict:
    """Assemble the user's memory into a compact prompt block.
    Returns {text, facts, patterns}."""
    facts = db.list_memory_facts(user.client, user.user_id, limit=40, only_active=True)
    top = facts[:_MAX_FACTS_IN_CONTEXT]

    try:
        patterns = db.list_patterns(user.client, user.user_id, limit=5)
    except Exception:
        patterns = []

    try:
        mood_line = _recent_mood_summary(db.list_checkins(user.client, user.user_id, 7))
    except Exception:
        mood_line = ""

    parts = []
    if top:
        parts.append("\n".join(f"- [{f.get('category') or 'note'}] {f['fact']}" for f in top))
    if patterns:
        parts.append("Patterns noticed in their data:\n"
                     + "\n".join(f"- {p['pattern_text']}" for p in patterns))
    if mood_line:
        parts.append(mood_line)

    return {"text": "\n\n".join(parts).strip(), "facts": top, "patterns": patterns}


def _recent_mood_summary(checkins: list[dict]) -> str:
    if not checkins:
        return ""
    energies = [c.get("energy") for c in checkins if c.get("energy")]
    moods = [c.get("mood") for c in checkins if c.get("mood")]
    if not energies and not moods:
        return ""

    def _common(xs):
        return max(set(xs), key=xs.count) if xs else None

    bits = []
    e, m = _common(energies), _common(moods)
    if e:
        bits.append(f"energy mostly '{e}'")
    if m:
        bits.append(f"mood often '{m}'")
    return ("Recent check-ins: " + ", ".join(bits) + ".") if bits else ""


# ─────────────────────────────────────────────────────────────────────────────
# The Memory feeding the daily forecast — DETERMINISTIC, no AI, no per-day cost.
# When today's sky triggers one of the user's OWN unlocked patterns, surface a
# gentle heads-up. Honest (a count over their own data), never fabricated.
# ─────────────────────────────────────────────────────────────────────────────

_PATTERN_TODAY_NOTE = {
    "energy_tara": "On day-stars like today, you've tended to run low. Plan a lighter day, and don't read the dip as a problem.",
    "clarity_tara": "Focus can feel slippery on days like this for you, so maybe save the hard thinking for tomorrow.",
    "mood_house": "Today's Moon sits in one of the houses that has weighed on you before. If the mood dips, it's the sky, not you.",
}


def _self_astro(client, user_id):
    try:
        profiles = db.list_profiles(client, user_id)
    except Exception:
        return None
    sp = None
    for p in profiles:
        if p.get("relation_tag") == "self" or p.get("source") == "self":
            sp = p
            break
    if sp is None and profiles:
        sp = profiles[0]
    if not sp or not sp.get("birth_date"):
        return None
    return {"date": sp.get("birth_date"), "time": sp.get("birth_time") or "",
            "tz": sp.get("tz") or "Asia/Kolkata", "lat": sp.get("lat"), "lon": sp.get("lon")}


def _pattern_fires_today(kind: str, tara_quality: str, chandra_house: int) -> bool:
    if kind in ("energy_tara", "clarity_tara"):
        return tara_quality == "challenging"
    if kind == "mood_house":
        return chandra_house in (2, 4, 5, 8, 9, 12)
    return False


def _trend_note(checkins: list[dict]) -> str:
    """A gentle, honest line from the user's OWN recent check-ins (reflective, not
    predictive). Fires from just a few days, so a new user feels seen long before
    the 30-check-in Pattern unlock."""
    recent = checkins[:5]
    if len(recent) < 3:
        return ""
    low = sum(1 for c in recent
             if c.get("energy") == "low" or c.get("mood") in ("heavy", "tender"))
    bright = sum(1 for c in recent
                if c.get("energy") == "bright" or c.get("mood") == "calm")
    if low >= 3:
        return "You've been running low these last few days, so be gentle with yourself today."
    if bright >= 3:
        return "You've had a good run lately, so lean into it while it lasts."
    return ""


def personalize_today(user, on_date=None) -> dict:
    """Which of the user's OWN patterns the sky triggers today + their recent mood
    trend. Deterministic, no AI. The app merges `personal_note` with the
    deterministic /dashboard/forecast. Returns {ok, personal_note, matched_kinds,
    mood_trend}."""
    ap = _self_astro(user.client, user.user_id)
    if not ap:
        return {"ok": True, "personal_note": "", "matched_kinds": [], "mood_trend": ""}

    try:
        from shared.astro.forecast import daily_moon_forecast
        f = daily_moon_forecast(ap, on_date)
        tq, ch = f.get("tara_quality"), f.get("chandra_house")
    except Exception:
        return {"ok": True, "personal_note": "", "matched_kinds": [], "mood_trend": ""}

    matched: list[str] = []
    try:
        for pat in db.list_patterns(user.client, user.user_id, limit=20):
            kind = (pat.get("evidence") or {}).get("kind")
            if kind and kind not in matched and _pattern_fires_today(kind, tq, ch):
                matched.append(kind)
    except Exception:
        matched = []

    try:
        recent = db.list_checkins(user.client, user.user_id, 7)
    except Exception:
        recent = []
    mood_trend = _recent_mood_summary(recent)

    notes = [_PATTERN_TODAY_NOTE[k] for k in matched if k in _PATTERN_TODAY_NOTE]
    pattern_note = " ".join(dict.fromkeys(notes))   # de-dup if energy+clarity both fire
    # An unlocked Pattern (needs ~30 check-ins) is the strongest; otherwise fall
    # back to a gentle read of the user's OWN recent trend (works from a few days)
    # so the daily line feels personal early, not generic.
    personal_note = pattern_note or _trend_note(recent)
    return {"ok": True, "personal_note": personal_note,
            "matched_kinds": matched, "mood_trend": mood_trend}
