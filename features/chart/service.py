"""features.chart.service — composes the warm chart interpretation ("front room").

Builds the full chart (shared.astro.kundli.compute_chart, via the ephemeris
adapter), then COMPOSES warm, plain-English cards from the verified atoms in
meanings.py — the same atoms-then-compose approach kundli_text.py uses, so the
text stays classically correct without a 200-combination hand-write.

Every card is { title, body (no jargon), sanskrit, why }. No live AI (cost rule).
Birth-time tiers: an exact time gives the Ascendant + houses; an unknown time
falls back to the sign-only reads (still reliable) + a precision note.
"""
from __future__ import annotations

from datetime import date as _date, time as _time, datetime
from zoneinfo import ZoneInfo

from features.chart import meanings as M


def _build_chart(profile: dict):
    """profile (kundli/compute shape) → (KundliChart, time_known). Needs lat/lon."""
    from shared.astro.kundli import BirthData, compute_chart

    if profile.get("lat") in (None, "") or profile.get("lon") in (None, ""):
        raise ValueError("birthplace_required")

    raw_t = profile.get("time")
    time_known = raw_t not in (None, "") and bool(profile.get("birth_time_known", True))
    if not time_known:
        t = _time(12, 0)
    elif isinstance(raw_t, str):
        parts = raw_t.split(":")
        t = _time(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
    else:
        t = raw_t

    d = profile["date"]
    bd = BirthData(
        name=profile.get("name", "You"),
        date=_date.fromisoformat(d) if isinstance(d, str) else d,
        time=t, place=profile.get("place", ""),
        lat=float(profile["lat"]), lon=float(profile["lon"]),
        tz=profile["tz"], gender=profile.get("gender", "M"),
        exact_time=bool(profile.get("exact_time", False)),
        birth_time_known=time_known,
    )
    return compute_chart(bd), time_known


# ── small composition helpers ────────────────────────────────────────────────

def _frame(domain: str, sign: str) -> str:
    return M.DOMAIN_FRAME[domain].format(essence=M.SIGN_ESSENCE.get(sign, ""))


def _pre(sign: str) -> str:
    """The adjective part of a sign's essence (before the em-dash)."""
    return M.SIGN_ESSENCE.get(sign, "").split("—")[0].strip()


def _house_short(h: int) -> str:
    """The house's life-area without the trailing dash clause (for `why`)."""
    return M.HOUSE_LIFE.get(h, "").split("—")[0].strip()


def _card(title, body, sanskrit, why) -> dict:
    return {"title": title, "body": body, "sanskrit": sanskrit, "why": why}


# ── the curated front-room read ──────────────────────────────────────────────

def interpret(profile: dict) -> dict:
    chart, time_known = _build_chart(profile)
    P = chart.planets
    cards = []

    sun_sign = P["Sun"].sign
    moon_sign = P["Moon"].sign

    # 1. You at the core — Ascendant + Sun (exact time), else Sun-led (sign-only).
    if time_known:
        asc_sign = chart.lagna.sign
        asc_lord = chart.lagna.lord
        asc_lord_house = P[asc_lord].house if asc_lord in P else None
        body = (f"{_frame('identity', asc_sign)} Underneath that, what really fuels you "
                f"is being {_pre(sun_sign)}.")
        if asc_lord_house:
            body += f" And your path keeps pulling you toward {M.HOUSE_LIFE[asc_lord_house]}."
        sanskrit = f"लग्न {M.SIGN_SANSKRIT.get(asc_sign,'')} · सूर्य {M.SIGN_SANSKRIT.get(sun_sign,'')}"
        why = (f"Your rising sign (Ascendant) is {asc_sign}; your Sun is in {sun_sign}"
               + (f"; your Ascendant ruler {asc_lord} sits in the area of {_house_short(asc_lord_house)}."
                  if asc_lord_house else "."))
    else:
        body = (f"At your core, you're {_pre(sun_sign)}. There's also a quieter, more "
                f"feeling side to you that runs {_pre(moon_sign)}.")
        sanskrit = f"सूर्य {M.SIGN_SANSKRIT.get(sun_sign,'')} · चन्द्र {M.SIGN_SANSKRIT.get(moon_sign,'')}"
        why = (f"Your Sun is in {sun_sign} and your Moon in {moon_sign}. (Without an exact "
               "birth time, your rising sign and houses can't be pinned down — these read "
               "from your Sun and Moon, which stay reliable.)")
    cards.append(_card("You at the core", body, sanskrit, why))

    # 2. Your inner world — Moon.
    mh = P["Moon"].house
    body = _frame("emotion", moon_sign)
    if time_known:
        body += f" You feel most settled when life is centred around {M.HOUSE_LIFE[mh]}."
    cards.append(_card("Your inner world", body,
                       f"चन्द्र {M.SIGN_SANSKRIT.get(moon_sign,'')}",
                       f"Your Moon — the heart and mind — is in {moon_sign}"
                       + (f", in the area of {_house_short(mh)}." if time_known else ".")))

    # 3. How you love — Venus.
    v = P["Venus"]; vh = v.house
    body = _frame("love", v.sign)
    if time_known:
        body += f" It mostly shows up around {M.HOUSE_LIFE[vh]}."
    cards.append(_card("How you love", body,
                       f"शुक्र {M.SIGN_SANSKRIT.get(v.sign,'')}",
                       f"Venus — love and pleasure — is in {v.sign}"
                       + (f", in the area of {_house_short(vh)}." if time_known else ".")))

    # 4. How you think — Mercury.
    me = P["Mercury"]
    cards.append(_card("How you think", _frame("mind", me.sign),
                       f"बुध {M.SIGN_SANSKRIT.get(me.sign,'')}",
                       f"Mercury — the thinking mind — is in {me.sign}."))

    # 5. Your drive — Mars.
    ma = P["Mars"]; mah = ma.house
    body = _frame("drive", ma.sign)
    if time_known:
        body += f" That energy goes mostly into {M.HOUSE_LIFE[mah]}."
    cards.append(_card("Your drive", body,
                       f"मंगल {M.SIGN_SANSKRIT.get(ma.sign,'')}",
                       f"Mars — drive and courage — is in {ma.sign}"
                       + (f", in the area of {_house_short(mah)}." if time_known else ".")))

    # 6. Where you grow — Saturn (gentle growth edge; only meaningful with houses).
    if time_known:
        sa = P["Saturn"]; sah = sa.house
        body = (f"The part of life that asks the most patience from you is {M.HOUSE_LIFE[sah]}. "
                "It can bring some delay or self-doubt early on — but it's also exactly where "
                "you slowly become unshakeable.")
        cards.append(_card("Where you grow", body,
                           f"शनि {M.SIGN_SANSKRIT.get(sa.sign,'')}",
                           f"Saturn — patience and mastery — sits in the area of {_house_short(sah)}."))

    # 7. The season you're in — current Vimshottari Mahadasha theme.
    current_chapter = _current_chapter(chart)

    # Headline — an evocative one-liner (contrast outside vs inside when we can).
    if time_known:
        headline = f"You come across as {_pre(chart.lagna.sign)}, but inside you run {_pre(moon_sign)}."
    else:
        headline = f"At your core, {_pre(sun_sign)} — with a {_pre(moon_sign)} heart."

    precision_note = None
    if not time_known:
        precision_note = ("Your birth time isn't set, so this reads from your Sun and Moon (which "
                          "stay accurate). Add your exact birth time to unlock your rising sign, "
                          "houses, and the full picture.")

    return {
        "ok": True,
        "headline": headline,
        "core": cards,
        "current_chapter": current_chapter,
        "precision_note": precision_note,
    }


def _current_chapter(chart) -> dict:
    """The Vimshottari Mahadasha running now, as a warm 'season you're in' card."""
    from shared.astro.astro_calc import build_vimshottari_timeline
    from shared.astro.retrospect import _DASHA_LORD

    dt_birth = chart.datetime_local
    moon_lon = chart.planets["Moon"].longitude
    now = datetime.now(dt_birth.tzinfo)
    di = build_vimshottari_timeline(dt_birth, moon_lon, now)
    md = di["current_md"]
    info = _DASHA_LORD.get(md, {"theme": md, "sanskrit": md})
    until = di["md_end"].strftime("%b %Y") if di.get("md_end") else ""
    body = (f"Right now you're moving through a {md} season — {info['theme']}."
            + (f" It runs until around {until}." if until else ""))
    return _card("The season you're in", body, f"{info['sanskrit']} महादशा",
                 f"Your current Vimshottari Mahadasha is {md}"
                 + (f", until about {until}." if until else "."))
