"""features.companion.service — the Companion payoffs' logic.

Three pieces, all pure math + lookup (no live AI):

  • micro_insight  — compares today's self-reported check-in against today's real
    Moon transit (from shared.astro.forecast) and says whether the felt mood runs
    WITH the sky or against it. Stateless.
  • compute_patterns — the Pattern Engine. Reads the user's check-ins + their
    'self' birth profile (data layer), recomputes each day's Moon state, and runs
    PLAIN STATISTICS (2×2 proportion contrasts — no ML) to surface the strongest
    personal correlation once there's enough data. Persists newly-unlocked kinds.
  • proof — thin pass-through to shared.astro.retrospect.explain_past_date.

The astrology all lives in shared/astro/ (forecast + retrospect, which go through
the ephemeris adapter). This layer adds only the self-report mapping + the stats.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


# ── How the app's check-in words map to a felt valence (-1 low … +1 light).
#    Used only by the Day-1 mirror to compare the report against the day's sky.
_ENERGY_VALENCE = {"low": -1.0, "steady": 0.0, "restless": 0.0, "bright": 1.0}
_MOOD_VALENCE = {"calm": 0.5, "tender": -0.5, "sharp": 0.0, "heavy": -1.0, "wired": 0.0}
_CLARITY_VALENCE = {"rested": 1.0, "okay": 0.0, "tired": -1.0, "off": -0.7}


def _self_valence(mood, energy, clarity) -> float | None:
    vals = []
    if mood in _MOOD_VALENCE:
        vals.append(_MOOD_VALENCE[mood])
    if energy in _ENERGY_VALENCE:
        vals.append(_ENERGY_VALENCE[energy])
    if clarity in _CLARITY_VALENCE:
        vals.append(_CLARITY_VALENCE[clarity])
    return sum(vals) / len(vals) if vals else None


# ─────────────────────────────────────────────────────────────────────────────
# 1. Day-1 micro-insight (the mirror) — stateless, no AI
# ─────────────────────────────────────────────────────────────────────────────

def micro_insight(profile: dict, mood=None, energy=None, clarity=None, date=None) -> dict:
    from shared.astro.forecast import daily_moon_forecast

    f = daily_moon_forecast(profile, date)
    day_valence = (f["vibe_score"] - 0.5) * 2.0          # 0..1 → -1..+1
    self_v = _self_valence(mood, energy, clarity)

    label = mood or energy or clarity or "this"
    # The day's own texture, in plain words already written by the forecast.
    day_ctx = f["mood"].rstrip(".")

    if self_v is None:
        match = "neutral"
        clause = "Check in with a word or two and I'll mirror it against today's sky."
    elif abs(self_v) < 0.25 or abs(day_valence) < 0.20:
        match = "neutral"
        clause = "That sits about where the day does — no strong pull either way, so set your own pace."
    elif (self_v > 0) == (day_valence > 0):
        match = "aligned"
        if self_v < 0:
            clause = "The sky agrees with you today, so the heaviness is real, not random — be gentle and let it be slow."
        else:
            clause = "The day is leaning the same way, so ride it — what you're feeling has the sky behind it."
    else:
        match = "crosscurrent"
        if self_v > 0:
            clause = "You're lighter than the day around you — that's your own momentum carrying you, not the sky. Enjoy it."
        else:
            clause = "The day itself is fairly open, so this weight is coming from you, not the stars — worth a gentle look at what's underneath."

    line = f"You logged '{label}' — {day_ctx}. {clause}"
    why = (f"Today the Moon is in your {f['chandra_house']}-from-Moon house "
           f"({f['moon_sign']}, {f['moon_nakshatra']}), a {f['tara_quality']} day-star "
           f"(Tara Bala). Your check-in reads as {_valence_word(self_v)}; the day reads as "
           f"{_valence_word(day_valence)}.")

    return {
        "ok": True,
        "date": f["date"],
        "line": line,
        "match": match,                      # aligned | crosscurrent | neutral
        "why": why,
        "sanskrit": f["sanskrit"],
        "day_vibe_word": f["vibe_word"],
        "day_vibe_score": f["vibe_score"],
        "astro_state_key": f["astro_state_key"],
    }


def _valence_word(v) -> str:
    if v is None:
        return "unread"
    if v <= -0.4:
        return "heavy"
    if v < 0:
        return "a little low"
    if v < 0.4:
        return "even"
    return "light"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Pattern Engine — plain statistics over the user's check-ins (JWT)
# ─────────────────────────────────────────────────────────────────────────────

MIN_CHECKINS = 30          # the "x of 30" unlock bar (matches the People-tab UI)
_MIN_BUCKET = 4            # need at least this many days in each side of a contrast
_MIN_EFFECT = 0.22         # min proportion gap to call a contrast a real pattern


def _db_profile_to_astro(p: dict) -> dict:
    """A saved DB profile (birth_date/birth_time/…) → the kundli/compute shape the
    astro stack expects. Moon-based forecast only needs date + time + tz."""
    return {
        "date": p.get("birth_date"),
        "time": p.get("birth_time") or "",
        "tz": p.get("tz") or "Asia/Kolkata",
        "lat": p.get("lat"),
        "lon": p.get("lon"),
    }


def _self_profile(profiles: list[dict]) -> dict | None:
    for p in profiles:
        if p.get("relation_tag") == "self" or p.get("source") == "self":
            return p
    return profiles[0] if profiles else None


def _contrast(rows: list[dict], flag, astro_flag) -> dict | None:
    """A 2×2 proportion contrast: among days where astro_flag is True vs False,
    how often is the self-report flag True? Returns the effect + support, or None
    if either bucket is too small."""
    pos = [r for r in rows if astro_flag(r)]
    neg = [r for r in rows if not astro_flag(r)]
    if len(pos) < _MIN_BUCKET or len(neg) < _MIN_BUCKET:
        return None
    pos_hits = sum(1 for r in pos if flag(r))
    neg_hits = sum(1 for r in neg if flag(r))
    p_pos = pos_hits / len(pos)
    p_neg = neg_hits / len(neg)
    return {
        "effect": p_pos - p_neg,
        "p_pos": p_pos, "p_neg": p_neg,
        "n_pos": len(pos), "n_neg": len(neg),
        "hits_pos": pos_hits, "hits_neg": neg_hits,
    }


def _candidate_patterns(rows: list[dict]) -> list[dict]:
    """Each candidate = a (self-report flag, astro flag, templating) triple. We
    keep the cleanest, most classically-meaningful contrasts. Tara quality and the
    Chandra-house auspiciousness are the two Moon-based axes that work at every
    birth-time tier."""
    challenging_tara = lambda r: r["_tara_quality"] == "challenging"
    favourable_tara = lambda r: r["_tara_quality"] == "favourable"
    hard_house = lambda r: r["_chandra_house"] in (2, 4, 5, 8, 9, 12)

    low_energy = lambda r: r.get("energy") == "low"
    heavy_mood = lambda r: r.get("mood") in ("heavy", "tender")
    foggy = lambda r: r.get("clarity") in ("tired", "off")

    out = []

    c = _contrast(rows, low_energy, challenging_tara)
    if c:
        out.append({"kind": "energy_tara", "metric": c,
                    "noun": "low-energy days", "axis": "challenging day-stars",
                    "sanskrit": "तारा बल"})

    c = _contrast(rows, heavy_mood, hard_house)
    if c:
        out.append({"kind": "mood_house", "metric": c,
                    "noun": "heavier-mood days", "axis": "the Moon's harder houses from your birth Moon",
                    "sanskrit": "चन्द्र गोचर"})

    c = _contrast(rows, foggy, challenging_tara)
    if c:
        out.append({"kind": "clarity_tara", "metric": c,
                    "noun": "foggy, tired days", "axis": "challenging day-stars",
                    "sanskrit": "तारा बल"})

    # Strongest absolute effect first; keep only those that clear the bar.
    out = [p for p in out if abs(p["metric"]["effect"]) >= _MIN_EFFECT]
    out.sort(key=lambda p: abs(p["metric"]["effect"]), reverse=True)
    return out


def _confidence(n: int, effect: float) -> str:
    if n >= 60 and abs(effect) >= 0.35:
        return "clear"
    if abs(effect) >= 0.30:
        return "noticeable"
    return "emerging"


def _phrase(p: dict, total: int) -> dict:
    m = p["metric"]
    pct_pos = round(m["p_pos"] * 100)
    pct_neg = round(m["p_neg"] * 100)
    direction = "lean toward" if m["effect"] > 0 else "tend to avoid"
    text = (f"Your {p['noun']} {direction} {p['axis']} — "
            f"{m['hits_pos']} of {m['n_pos']} ({pct_pos}%), "
            f"versus {pct_neg}% on the other days.")
    why = (f"Across {total} check-ins: on {p['axis']}, you logged {p['noun']} "
           f"{pct_pos}% of the time, against {pct_neg}% otherwise — a plain count, "
           "not a prediction. The more you check in, the sharper it gets.")
    return {
        "pattern_text": text,
        "kind": p["kind"],
        "confidence": _confidence(total, m["effect"]),
        "why": why,
        "sanskrit": p["sanskrit"],
        "evidence": {"kind": p["kind"], "total": total, **m},
    }


def compute_patterns(user) -> dict:
    """The Pattern Engine. Reads the user's check-ins + their 'self' profile,
    recomputes each day's Moon state, and runs plain-statistics contrasts. Below
    the bar → progress only. At/above the bar → unlocked pattern(s), persisted by
    kind. JWT-scoped via user.client (RLS)."""
    from shared.db import supabase_client as db
    from shared.astro.forecast import daily_moon_forecast

    checkins = db.list_checkins(user.client, user.user_id, limit=400)
    have = len(checkins)

    if have < MIN_CHECKINS:
        left = MIN_CHECKINS - have
        return {
            "ok": True, "unlocked": False,
            "progress": {"have": have, "need": MIN_CHECKINS},
            "message": (f"Keep checking in — {left} more "
                        f"{'day' if left == 1 else 'days'} and your first personal "
                        "pattern unlocks." if have else
                        "Check in each day and your personal patterns start to surface."),
            "patterns": [],
        }

    profiles = db.list_profiles(user.client, user.user_id)
    self_p = _self_profile(profiles)
    if not self_p or not self_p.get("birth_date"):
        return {
            "ok": True, "unlocked": False,
            "progress": {"have": have, "need": MIN_CHECKINS},
            "message": "Add your birth details and your check-ins will start forming patterns.",
            "patterns": [],
        }
    astro_profile = _db_profile_to_astro(self_p)

    # Recompute each check-in day's Moon state (deterministic, cacheable).
    rows = []
    for c in checkins:
        try:
            f = daily_moon_forecast(astro_profile, c["date"])
        except Exception:
            continue
        rows.append({
            "mood": c.get("mood"), "energy": c.get("energy"), "clarity": c.get("clarity"),
            "_tara_quality": f["tara_quality"], "_chandra_house": f["chandra_house"],
        })

    cands = _candidate_patterns(rows)
    patterns = [_phrase(p, len(rows)) for p in cands]

    # Persist newly-seen kinds (dedup by evidence.kind). Never let DB break the read.
    try:
        stored = db.list_patterns(user.client, user.user_id)
        seen = {(s.get("evidence") or {}).get("kind") for s in stored}
        for pat in patterns:
            if pat["kind"] not in seen:
                db.save_pattern(user.client, user.user_id, pat["pattern_text"], pat["evidence"])
    except Exception:
        pass

    if not patterns:
        message = ("Enough check-ins now — no single strong pattern stands out yet, "
                   "which is its own kind of steadiness. Keep going and I'll keep watching.")
    else:
        message = "Here's what your check-ins are showing so far."

    return {
        "ok": True, "unlocked": True,
        "progress": {"have": have, "need": MIN_CHECKINS},
        "message": message,
        "patterns": patterns,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. The Proof — pass-through to the shared retrospect math (stateless)
# ─────────────────────────────────────────────────────────────────────────────

def proof(profile: dict, date: str, event: str | None = None) -> dict:
    from shared.astro.retrospect import explain_past_date
    out = explain_past_date(profile, date, event)
    out["ok"] = "error" not in out
    return out
