"""shared.astro.relationship_weather — daily "relationship weather" between
two people for the mobile People tab.

FREE + cheap by design (cost rule): pure MATH + a pre-baked meaning LOOKUP.
NO live AI call, NO new dependencies. Everything is MOON-BASED, so it works even
when EITHER person's birth time is unknown (an unknown time just uses a noon
placeholder for that person's natal Moon — same fallback as forecast.py).

Two layers, both sourced from classical Indian/Vedic practice:

  1. BASELINE — "how these two mesh" — built from the RELATIONSHIP-NEUTRAL parts of
     the classical compatibility system, so it suits ANY bond (parent, friend,
     partner): Graha Maitri (how the two minds/temperaments befriend each other, /5)
     + Gana (temperament match, /6), blended with the Moon-sign (Rashi) relationship
     that colours the bond's flavour. We deliberately DROP the marriage/procreation-
     specific kootas (Yoni = sexual compatibility, Nadi = progeny) and never use the
     full 36-guna Ashta Koota *total* here — that whole system is a MARRIAGE-matching
     tool (and its Bhakoot factor penalises the warm 5-9 pairing, which caused a
     contradiction). Full Ashta Koota lives in the dedicated Compatibility & Marriage
     feature. The Rashi-relationship lore (Bhakoot / Nava-Pancham / Shad-Ashtaka,
     Brihat Parashara / Muhurta texts):
       • same sign            → mirrored moods
       • 2-12 axis (dist 1)   → natural give-and-take
       • 3-11 axis (dist 2)   → easy, friendly companions
       • 4-10 axis (dist 3)   → respect + practical care over open emotion
       • 5-9  axis (dist 4)   → Nava-Pancham: natural warmth and fondness
       • 6-8  axis (dist 5)   → Shad-Ashtaka: friction, needs extra patience
       • 7-7  axis (dist 6)   → complementary opposites that balance out

  2. DAILY — "how today feels between you" — the Tara Bala of TODAY'S transiting
     Moon read from EACH person's natal Moon. Tara Bala (RVA / PanchangBodh /
     mpanchang / Sarvatobhadra) is the classical day-quality read: count
     nakshatras from a birth star to the day's star, mod 9 → favourable (2,4,6,8,9),
     neutral/restless (1) or challenging (3,5,7). We compute it for both people
     from the SAME transiting Moon and combine the two qualities into one day-tone.
     This is the standard daily Moon read applied to two charts at once — kept
     deliberately MODEST and clearly framed (gentle guidance, never fate); there
     is no single classical "daily formula for a pair", so we do not overclaim.

Framing rule (blueprint §2): warm, plain, beginner-friendly. No jargon in the
main lines; Sanskrit/technical terms live ONLY in `why` / `sanskrit`.
"""

from datetime import date as _date, time as _time, datetime, timedelta
from zoneinfo import ZoneInfo

from shared.astro.astro_calc import (
    nakshatra_info, sign_index_from_lon, sign_name, calculate_tara_bala,
)
# Reuse the forecast helpers (same Moon-longitude logic + unknown-time fallback).
from shared.astro.forecast import (
    _natal_moon_lon, _transit_moon_lon, _NAK_DEVANAGARI, _band,
)


# ── Rashi-relationship "flavour" of the bond, keyed by the absolute Moon-sign
#    distance between the two people (0..6 after folding 7..11 back). Plain, warm
#    English; the classical name lives only in the `why` / `sanskrit` strings.
_RASHI_FLAVOUR: dict[int, dict] = {
    0: {"key": "mirror", "base": 0.62,
        "bond": "You two tend to feel things in much the same way — when one of you lifts, the other lifts; when one's low, it can echo.",
        "lean": "moving through the day in sync",
        "watch": "feeding each other's low moods"},
    1: {"key": "give_take", "base": 0.56,
        "bond": "Between you there's a natural give-and-take — one of you tends to offer and look after, the other to lean in and receive.",
        "lean": "small acts of care that go back and forth",
        "watch": "letting it get one-sided"},
    2: {"key": "easy", "base": 0.70,
        "bond": "You're easy companions — things tend to stay friendly and uncomplicated between you.",
        "lean": "relaxed, low-effort time together",
        "watch": "taking the easiness for granted"},
    3: {"key": "respectful", "base": 0.58,
        "bond": "You two connect through respect and steady, practical care more than through open emotion — practical talk often lands better than heavy feelings.",
        "lean": "doing something useful side by side",
        "watch": "expecting lots of open emotion"},
    4: {"key": "warm", "base": 0.74,
        "bond": "There's a natural fondness here — warmth and affection come easily between you.",
        "lean": "open, warm-hearted conversation",
        "watch": "assuming it'll always be effortless"},
    5: {"key": "friction", "base": 0.42,
        "bond": "You two can rub each other the wrong way if you're not careful — this bond rewards a little extra patience.",
        "lean": "small kindnesses and a soft tone",
        "watch": "letting little irritations pile up"},
    6: {"key": "opposites", "base": 0.60,
        "bond": "You're opposites in a way that fits — different styles that tend to balance each other out.",
        "lean": "letting your differences cover each other's gaps",
        "watch": "expecting them to react the way you would"},
}

# Classical name of each Rashi axis, used ONLY inside `why`.
_RASHI_CLASSICAL = {
    0: "the same Moon-sign", 1: "the 2-and-12 axis", 2: "the 3-and-11 axis",
    3: "the 4-and-10 axis", 4: "the 5-and-9 axis (Nava-Pancham, a naturally fond pairing)",
    5: "the 6-and-8 axis (Shad-Ashtaka, the one that needs patience)",
    6: "facing signs (a balancing, opposite pairing)",
}

# Tara Bala status (from calculate_tara_bala) → plain quality.
_TARA_QUALITY = {"Go": "favourable", "Stop": "challenging", "Caution": "neutral"}

# ── Daily tone: combine the two people's Tara qualities (a sorted pair) into one
#    day-state. `dscore` is the day's own tone-score (0..1); the tone_word,
#    summary clause and good_for / avoid all hang off this.
def _day_state(qa: str, qb: str) -> str:
    pair = tuple(sorted([qa, qb]))
    table = {
        ("favourable", "favourable"): "easy",
        ("favourable", "neutral"):    "light",
        ("neutral", "neutral"):       "steady",
        ("challenging", "favourable"): "uneven",
        ("challenging", "neutral"):    "careful",
        ("challenging", "challenging"): "tender",
    }
    return table[pair]

_DAY: dict[str, dict] = {
    "easy":   {"word": "Easy",   "dscore": 0.88,
               "clause": "Today the mood between you flows easily, so it's a lovely day to connect.",
               "good": "heart-to-hearts, making plans together, or smoothing over anything left hanging",
               "avoid": "overthinking it — the day is on your side"},
    "light":  {"word": "Light",  "dscore": 0.72,
               "clause": "Today feels light and friendly — easy to enjoy each other's company.",
               "good": "a relaxed catch-up and small, kind gestures",
               "avoid": "forcing a big or heavy conversation"},
    "steady": {"word": "Steady", "dscore": 0.58,
               "clause": "Today is steady and ordinary between you — nothing to push, nothing to fix.",
               "good": "everyday, practical time together",
               "avoid": "expecting a deep emotional breakthrough"},
    "uneven": {"word": "Uneven", "dscore": 0.47,
               "clause": "Today the energy is a little uneven — one of you may be more upbeat than the other, so go gently.",
               "good": "patience and meeting them where they are",
               "avoid": "taking a flat or quiet mood personally"},
    "careful": {"word": "Careful", "dscore": 0.39,
               "clause": "Today asks for a little care — keep things light and don't force anything heavy.",
               "good": "keeping it low-pressure and easygoing",
               "avoid": "big decisions or touchy subjects"},
    "tender": {"word": "Tender", "dscore": 0.30,
               "clause": "Today feels tender between you, so kindness and patience go further than anything else.",
               "good": "gentleness, a little space, and small comforts",
               "avoid": "pushing, criticism, or difficult talks"},
}


def _moon_sign_distance(moon_a: float, moon_b: float) -> int:
    """Absolute Moon-sign distance folded into 0..6 (relationship is symmetric)."""
    d = (sign_index_from_lon(moon_b) - sign_index_from_lon(moon_a)) % 12
    return min(d, 12 - d)


def daily_relationship_weather(profile_a: dict, profile_b: dict, on_date=None) -> dict:
    """Display-ready daily relationship weather between two people.

    Pure math + lookup, no AI, no new dependencies. Both profiles use the
    /kundli/compute shape. `on_date`: None → today (in profile_a's tz); else a
    date or "YYYY-MM-DD". Deterministic for the same two profiles + date.
    Works at every birth-time tier (unknown time → noon placeholder per person).
    """
    tz = profile_a.get("tz") or profile_b.get("tz")
    if on_date is None:
        on_date = datetime.now(ZoneInfo(tz)).date()
    elif isinstance(on_date, str):
        on_date = _date.fromisoformat(on_date)

    # 1. Each person's natal Moon (unknown birth time → noon placeholder).
    moon_a = _natal_moon_lon(profile_a)
    moon_b = _natal_moon_lon(profile_b)

    # 2. BASELINE — the RELATIONSHIP-NEUTRAL compatibility, so it fits any bond.
    #    Only the general kootas: Graha Maitri (minds/temperaments getting along, /5)
    #    + Gana (temperament, /6), blended with the Moon-sign rapport flavour. We
    #    DROP the marriage/procreation kootas (Yoni=sexual, Nadi=progeny) and never
    #    use the full 36-guna total (its Bhakoot factor penalises the warm 5-9
    #    pairing — the contradiction). Full Ashta Koota lives in Compatibility/Marriage.
    from shared.astro.scoring import calculate_ashta_koota  # lazy: pulls the astro stack
    koota = calculate_ashta_koota(moon_a, moon_b)
    rapport = (koota["maitri"] + koota["gana"]) / 11.0       # mind + temperament fit (0..1)
    dist = _moon_sign_distance(moon_a, moon_b)
    flav = _RASHI_FLAVOUR[dist]
    baseline = round(0.5 * rapport + 0.5 * flav["base"], 4)  # mind-fit + Moon-sign rapport

    # 3. DAILY — today's transiting Moon, read as a Tara from EACH natal Moon.
    transit = _transit_moon_lon(on_date, tz)
    tara_a = calculate_tara_bala(moon_a, transit)
    tara_b = calculate_tara_bala(moon_b, transit)
    qa = _TARA_QUALITY.get(tara_a["status"], "neutral")
    qb = _TARA_QUALITY.get(tara_b["status"], "neutral")
    state = _day_state(qa, qb)
    day = _DAY[state]

    nak, _lord, _pada = nakshatra_info(transit)
    ns = 360.0 / 27
    nak_idx = int((transit % 360) // ns)
    t_sign = sign_name(sign_index_from_lon(transit))

    # 4. Combine into the final 0..1 score. Today dominates (0.6) but the durable
    #    baseline compatibility shapes the floor (0.4). Clamped to [0.08, 0.96].
    score = round(min(0.96, max(0.08, 0.6 * day["dscore"] + 0.4 * baseline)), 2)

    summary = f"{flav['bond']} {day['clause']}"
    good_for = f"{day['good']} — especially {flav['lean']}"
    avoid = f"{day['avoid']}; with the two of you, also watch {flav['watch']}"

    why = (
        "This blends two readings. First, the two of you: how naturally your minds "
        "and temperaments get along (the classical Graha Maitri and Gana match), "
        f"together with the Moon-sign relationship between you — here, {_RASHI_CLASSICAL[dist]}. "
        f"Second, today's sky: the Moon is travelling through {nak}, which counts as "
        f"a {qa} day-star from the first of you and a {qb} one from the second — read "
        "from each birth star, that's the daily Tara Bala. Put together, today leans "
        f"“{day['word'].lower()}” between you. Take it as gentle guidance, not fate."
    )
    sanskrit = f"ग्रह-मैत्री · गण · तारा बल · चन्द्रः {_NAK_DEVANAGARI[nak_idx]}-नक्षत्रे"

    return {
        "date": on_date.isoformat(),
        "tone_word": day["word"],
        "summary": summary,
        "good_for": good_for,
        "avoid": avoid,
        "score": score,
        "why": why,
        "sanskrit": sanskrit,
        # Identical states share this key → cacheable.
        "astro_state_key": f"d{dist}-{state}-nak{nak_idx}",
        # Transparency / debug fields (cheap, Moon-based, safe at any tier).
        "maitri": koota["maitri"], "gana": koota["gana"],
        "baseline_score": round(baseline, 2),
        "rashi_relation": flav["key"],
        "moon_sign_distance": dist,
        "moon_nakshatra": nak,
        "moon_sign": t_sign,
        "tara_a": tara_a["tara"],
        "tara_b": tara_b["tara"],
        "tara_a_quality": qa,
        "tara_b_quality": qb,
        "day_state": state,
    }


def weekly_relationship_weather(profile_a: dict, profile_b: dict,
                                start_date=None, days: int = 7) -> dict:
    """`days` consecutive daily relationship-weather readings between two people,
    for the People tab's "next 7 days together" rail. Each entry is the full
    daily_relationship_weather plus a coarse `band` (good/neutral/difficult) for
    the rail colour and an `is_today` flag.

    Pure math + lookup, no AI, no new deps — just the single-day reading run over
    a span. The durable BASELINE ("how the two of you mesh") is identical every
    day, so we also lift it to a top-level `baseline` block for the rail header
    instead of repeating it on every card. Works at every birth-time tier (an
    unknown birth time uses a noon placeholder per person, as in the single-day
    reading). `start_date`: None → today in profile_a's tz (falls back to
    profile_b's). Deterministic for the same two profiles + span.
    """
    tz = profile_a.get("tz") or profile_b.get("tz")
    today = datetime.now(ZoneInfo(tz)).date()
    if start_date is None:
        start_date = today
    elif isinstance(start_date, str):
        start_date = _date.fromisoformat(start_date)

    out = []
    for i in range(max(1, days)):
        d = start_date + timedelta(days=i)
        w = daily_relationship_weather(profile_a, profile_b, d)
        w["band"] = _band(w["score"])
        w["is_today"] = (d == today)
        out.append(w)

    # The baseline is the same across the span — surface it once for the header.
    first = out[0]
    baseline = {
        "score": first["baseline_score"],
        "rashi_relation": first["rashi_relation"],
        "bond": _RASHI_FLAVOUR[first["moon_sign_distance"]]["bond"],
    }
    return {"start_date": start_date.isoformat(), "baseline": baseline, "days": out}
