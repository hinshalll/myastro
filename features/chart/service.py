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
        body = (f"{_frame('identity', asc_sign)} But that's mostly the surface. Underneath, "
                f"what actually drives you is being {_pre(sun_sign)} — and people who only meet "
                "the outer version of you tend to miss that quieter core.")
        if asc_lord_house:
            body += f" Bit by bit, your life keeps pulling you toward {M.HOUSE_LIFE[asc_lord_house]}."
        sanskrit = f"लग्न {M.SIGN_SANSKRIT.get(asc_sign,'')} · सूर्य {M.SIGN_SANSKRIT.get(sun_sign,'')}"
        why = (f"Your rising sign (Ascendant) is {asc_sign}; your Sun is in {sun_sign}"
               + (f"; your Ascendant ruler {asc_lord} sits in the area of {_house_short(asc_lord_house)}."
                  if asc_lord_house else "."))
    else:
        body = (f"At your core, you're {_pre(sun_sign)}. But there's a quieter, more "
                f"private side that runs {_pre(moon_sign)} — and not everyone gets to see it.")
        sanskrit = f"सूर्य {M.SIGN_SANSKRIT.get(sun_sign,'')} · चन्द्र {M.SIGN_SANSKRIT.get(moon_sign,'')}"
        why = (f"Your Sun is in {sun_sign} and your Moon in {moon_sign}. (Without an exact "
               "birth time, your rising sign and houses can't be pinned down — these read "
               "from your Sun and Moon, which stay reliable.)")
    cards.append(_card("You at the core", body, sanskrit, why))

    # 2. Your inner world — Moon.
    mh = P["Moon"].house
    body = _frame("emotion", moon_sign) + " More than anything, you need to feel safe and settled"
    body += (f", and that comes when life is centred on {M.HOUSE_LIFE[mh]}." if time_known
             else " — and you protect that more carefully than people realise.")
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
    body = _frame("drive", ma.sign) + " Once you're genuinely committed to something, you're hard to stop."
    if time_known:
        body += f" That energy goes mostly into {M.HOUSE_LIFE[mah]}."
    cards.append(_card("Your drive", body,
                       f"मंगल {M.SIGN_SANSKRIT.get(ma.sign,'')}",
                       f"Mars — drive and courage — is in {ma.sign}"
                       + (f", in the area of {_house_short(mah)}." if time_known else ".")))

    # 6. Where you grow — Saturn (gentle growth edge; only meaningful with houses).
    if time_known:
        sa = P["Saturn"]; sah = sa.house
        body = (f"If one part of life has asked more patience from you than feels quite fair, it's "
                f"{M.HOUSE_LIFE[sah]}. There can be some delay or self-doubt here, especially early "
                "on — but this is exactly where you slowly turn into someone genuinely unshakeable. "
                "The hard bit isn't a flaw in you; it's where you're being built.")
        cards.append(_card("Where you grow", body,
                           f"शनि {M.SIGN_SANSKRIT.get(sa.sign,'')}",
                           f"Saturn — patience and mastery — sits in the area of {_house_short(sah)}."))

    # 7. Your birth star — the Moon's nakshatra (the most personal signature).
    birth_star = _birth_star(chart)

    # 8. The season you're in — current Vimshottari Mahadasha + sub-period theme.
    current_chapter = _current_chapter(chart)

    # 9. Highlights — notable gifts (yogas) + gentle growth areas (doshas).
    highlights = _highlights(chart)

    # Headline — a natural one-liner that names the outer/inner tension, varied in
    # shape so different charts don't all read from the same template.
    headline = _headline(chart, time_known, sun_sign, moon_sign)

    precision_note = None
    if not time_known:
        precision_note = ("Your birth time isn't set, so this reads from your Sun and Moon (which "
                          "stay accurate). Add your exact birth time to unlock your rising sign, "
                          "houses, and the full picture.")

    return {
        "ok": True,
        "headline": headline,
        "core": cards,
        "birth_star": birth_star,
        "current_chapter": current_chapter,
        "highlights": highlights,
        "precision_note": precision_note,
    }


def _headline(chart, time_known, sun_sign, moon_sign) -> str:
    """A natural, non-templated one-liner. Names the outer-vs-inner tension (the
    'mask' you show vs the self that runs you — really Ascendant vs Moon), in one
    of a few shapes chosen deterministically so charts don't all read alike. When
    outer and inner match, it flips to a warm 'you're all of a piece' line."""
    outer = chart.lagna.sign if time_known else sun_sign
    o, i = _pre(outer), _pre(moon_sign)
    o1, i1 = o.split(",")[0], i.split(",")[0]      # lead adjective of each
    if outer == moon_sign:
        return (f"You're {o} — and more all-of-a-piece than most: what people see really is "
                "what's underneath.")
    variants = [
        f"On the surface you're {o1}, but the part that actually runs you is {i1} — and most "
        "people only ever meet the surface.",
        f"You read as {o1} to the world, while underneath, something {i1} is quietly in charge.",
        f"Two speeds live in you — the {o1} one everyone notices, and the {i1} one that's "
        "really driving.",
    ]
    base = chart.planets["Moon"].sign_index + (
        chart.lagna.sign_index if time_known else chart.planets["Sun"].sign_index)
    return variants[base % len(variants)]


def _highlights(chart) -> list[dict]:
    """Notable chart patterns as warm cards: gifts (yogas) first, then at most a
    couple of gentle growth areas (doshas). Only patterns we have warm, reassuring
    copy for are surfaced — the scarier-named ones are left to the deeper reading.
    Deduped by canonical key. Each: { title, body, sanskrit, why, kind }."""
    from features.chart.yogas import YOGA_WARM, DOSHA_WARM

    gifts, growth, seen = [], [], set()

    for y in getattr(chart, "yogas", []) or []:
        name = y.name
        if "Negative" in name:                    # handled as a growth area below
            continue
        for key, warm in YOGA_WARM.items():
            if key in name and key not in seen:
                seen.add(key)
                gifts.append({"title": "A gift in your chart", "body": warm["body"],
                              "sanskrit": warm["sanskrit"],
                              "why": f"Your chart carries {name}.", "kind": "gift"})
                break

    for d in getattr(chart, "doshas", []) or []:
        if not getattr(d, "present", False):
            continue
        for key, warm in DOSHA_WARM.items():
            if key in d.name and key not in seen:
                seen.add(key)
                growth.append({"title": "A growth area", "body": warm["body"],
                               "sanskrit": warm["sanskrit"],
                               "why": f"Your chart carries {d.name}.", "kind": "growth"})
                break

    # Lead with gifts; keep the front room encouraging (cap growth at 2).
    return gifts[:4] + growth[:2]


def _birth_star(chart) -> dict:
    """The Moon's nakshatra as a warm 'your birth star' card. Moon-based, so it's
    reliable at every birth-time tier (it doesn't need the Ascendant)."""
    from features.chart.nakshatras import NAKSHATRA, NAK_SHADOW

    moon = chart.planets["Moon"]
    nak = moon.nakshatra
    info = NAKSHATRA.get(nak)
    if not info:                                  # safety net — never crash on a name mismatch
        return _card("Your birth star", f"Your birth star is {nak}.",
                     nak, f"Your Moon is in the nakshatra {nak}.")
    body = info["body"]
    shadow = NAK_SHADOW.get(nak)                   # the gently-defused 'flip side'
    if shadow:
        body = f"{body} {shadow}"
    return _card(
        f"Your birth star · {nak}",
        body,
        f"{info['dev']} · {info['ruler']}",
        f"Your Moon sits in {nak} (symbol: {info['symbol']}; guided by {info['deity']}; "
        f"ruling planet {info['ruler']}).",
    )


def _dignity_note(dignity: str | None) -> str:
    if not dignity:
        return ""
    d = dignity.lower()
    for key, note in M.DIGNITY_NOTE.items():
        if key in d:
            return note
    return ""


def houses(profile: dict) -> dict:
    """The 12 houses, each as a warm, plain-English card — the deeper dive behind
    the front room. Needs the Ascendant, so it requires an exact birth time."""
    chart, time_known = _build_chart(profile)
    if not time_known:
        return {"ok": False, "error": "birth_time_required",
                "message": ("The 12 houses are built from your rising sign, so they need your "
                            "exact birth time. Add it to unlock this.")}
    out = []
    for h in range(1, 13):
        hi = chart.houses[h]
        body = (f"This is the part of your life about {M.HOUSE_LIFE[h]}. "
                f"With {hi.sign} here, it tends to play out in true {hi.sign} style — {_pre(hi.sign)}.")
        occ = [p for p in hi.occupants if p in M.PLANET_FLAVOUR]
        if len(occ) == 1:
            body += f" {occ[0]} sits here, adding {M.PLANET_FLAVOUR[occ[0]]} quality."
        elif len(occ) > 1:
            names = " and ".join(occ)
            body += f" {names} sit here, each colouring this part of life."
        out.append(_card(
            f"House {h} · {hi.sign}", body,
            f"{M.HOUSE_SANSKRIT.get(h,'')} · {M.SIGN_SANSKRIT.get(hi.sign,'')}",
            f"Your {_ord(h)} house holds {hi.sign} (ruled by {hi.sign_lord})"
            + (f"; planets here: {', '.join(hi.occupants)}." if hi.occupants else "; no planets here."),
        ))
    return {"ok": True, "houses": out}


def planets(profile: dict) -> dict:
    """Each of the 9 planets in its sign (+ house, with an exact time) as a warm
    card — what that part of you is like and where it plays out."""
    chart, time_known = _build_chart(profile)
    order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    out = []
    for p in order:
        pp = chart.planets.get(p)
        if not pp:
            continue
        dom = M.PLANET_DOMAIN[p]
        body = (f"This is {dom['of']}. In {pp.sign}, that shows up as {_pre(pp.sign)}"
                f"{_dignity_note(pp.dignity)}")
        if not body.rstrip().endswith("."):
            body = body.rstrip() + "."
        if time_known and pp.house:
            body += f" It plays out mostly through {M.HOUSE_LIFE[pp.house]}."
        if getattr(pp, "is_retrograde", False) and p not in ("Rahu", "Ketu"):
            body += " It's retrograde, so this energy runs deep and inward — you revisit it a lot."
        out.append(_card(
            f"{dom['lead']} · {p} in {pp.sign}", body,
            f"{dom['sanskrit']} {M.SIGN_SANSKRIT.get(pp.sign,'')}",
            f"{p} is in {pp.sign}"
            + (f", in the area of {_house_short(pp.house)}" if time_known and pp.house else "")
            + (f" ({pp.dignity})" if pp.dignity else "") + ".",
        ))
    return {"ok": True, "planets": out, "precision_note": (
        None if time_known else
        "Without an exact birth time, these read from each planet's sign (reliable) but not its house.")}


def _ord(n: int) -> str:
    return {1:"1st",2:"2nd",3:"3rd",4:"4th",5:"5th",6:"6th",7:"7th",
            8:"8th",9:"9th",10:"10th",11:"11th",12:"12th"}.get(n, f"{n}th")


def _current_chapter(chart) -> dict:
    """The Vimshottari Mahadasha running now, as a warm 'season you're in' card."""
    from shared.astro.astro_calc import build_vimshottari_timeline
    from shared.astro.retrospect import _DASHA_LORD

    dt_birth = chart.datetime_local
    moon_lon = chart.planets["Moon"].longitude
    now = datetime.now(dt_birth.tzinfo)
    di = build_vimshottari_timeline(dt_birth, moon_lon, now)
    md, ad = di["current_md"], di["current_ad"]
    info = _DASHA_LORD.get(md, {"theme": md, "sanskrit": md})
    ad_info = _DASHA_LORD.get(ad, {"theme": ad, "sanskrit": ad})
    until = di["md_end"].strftime("%b %Y") if di.get("md_end") else ""
    ad_until = di["ad_end"].strftime("%b %Y") if di.get("ad_end") else ""

    body = f"Right now you're moving through a {md} season — {info['theme']}."
    if ad != md:
        body += (f" Within it, you're in a {ad} phase right now"
                 + (f" (until around {ad_until})" if ad_until else "")
                 + f", which adds a flavour of {ad_info['theme'].split('—')[0].strip()}.")
    if until:
        body += f" The whole {md} season runs until around {until}."

    why = (f"Your current Vimshottari period is {md} Mahadasha"
           + (f" / {ad} Antardasha" if ad != md else "")
           + (f", the {md} chapter running until about {until}." if until else "."))
    return _card("The season you're in", body, f"{info['sanskrit']} महादशा", why)
