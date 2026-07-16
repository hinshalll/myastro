"""shared.astro.life_areas — the Today reading's Love / Work / Money rows.

Derived from the SAME `daily_moon_forecast` the reading uses (the transiting
Moon's house from the natal Moon = `chandra_house`, plus the day's band), so the
three domain reads can NEVER contradict the reading or the Panchang colour. Moon-
based → works at every birth-time tier. Pure math + lookup, NO AI, and NO scores
(honest, planet-named, never a fake %).

Significators (confirmed against multiple standard sources):
  • Love  — 7th (marriage) + 5th (romance), karaka Venus
  • Work  — 10th (career/karma) + 6th (work/effort), karaka Saturn (+ Sun for authority)
  • Money — 2nd (savings) + 11th (gains/income), karaka Jupiter (Dhana karaka)
A domain's karaka being retrograde adds a gentle "revisit, don't begin" note.

Also `reconcile_chips`: drops any reading activity-chip whose domain contradicts
its life-area tone (e.g. no "good for big purchases" chip on a hold-your-money
day), so the reading's chips and these rows always tell the same story.
"""
from datetime import date as _date

from shared.astro import ephemeris
from shared.astro.constants import PLANETS
from shared.astro.astro_calc import get_planet_longitude_and_speed
from shared.astro.forecast import daily_moon_forecast

# Which Moon-house (counted from the natal Moon) "lights up" each domain, + its karaka.
_DOMAINS = {
    "love":  {"karaka": "Venus",   "focus": {5, 7}},
    "work":  {"karaka": "Saturn",  "focus": {6, 10}},
    "money": {"karaka": "Jupiter", "focus": {2, 11}},
}

# When the Moon is IN a domain's focus house → a strong, specific read (tone, line).
_FOCUS_LINE = {
    ("love", 7):  ("good",  "Warm and open, Venus is with you, lovely for the people you love."),
    ("love", 5):  ("mixed", "Romance and play tug at you, keep it light, no big declarations."),
    ("work", 10): ("good",  "Visible and driven, Saturn steadies your effort, push what matters."),
    ("work", 6):  ("good",  "Sharp for clearing tasks and getting on top of a nagging problem."),
    ("money", 11): ("good", "Gains and income are favoured, Jupiter supports the flow."),
    ("money", 2):  ("mixed", "Money's on your mind, hold the big spends and tend what you have."),
}

# Otherwise the domain rides the day's overall band (keeps it consistent with the
# reading, and never three flat "steady" rows on a strong or hard day).
_STEADY_LINE = {
    ("love", "good"):  ("good",   "An easy warmth around your people today."),
    ("love", "mixed"): ("steady", "Steady on the heart front, nothing pushing either way."),
    ("love", "low"):   ("low",    "A tender day for the heart, be gentle with yourself and others."),
    ("work", "good"):  ("good",   "A smooth, capable current for work today."),
    ("work", "mixed"): ("steady", "Work ticks along, no strong pull either way."),
    ("work", "low"):   ("low",    "A lower-energy day for work, save the big push."),
    ("money", "good"):  ("good",   "Money feels calm and steady, a fine day to tend it."),
    ("money", "mixed"): ("steady", "Money sits steady, nothing urgent either way."),
    ("money", "low"):   ("low",    "A quiet money day, best to hold off on big moves."),
}

_RETRO_NOTE = {
    "love":  " Venus is retrograde, so reconnect and revisit rather than start something new.",
    "work":  " Saturn is retrograde, so finish and tidy rather than launch.",
    "money": " Jupiter is retrograde, so review and plan rather than commit big.",
}

# ── Sheet content: a fuller read + the plain "why" + where to go for more ──────
# `line` = the one-liner on the card; `detail` + `why` = what the row's own
# bottom-sheet adds (so tapping shows something NEW, not a repeat).
_DOMAIN_WORD = {"love": "relationships", "work": "work", "money": "money"}
_KARAKA_DESC = {
    "Venus":   "Venus, the planet of love",
    "Saturn":  "Saturn, the planet of work and discipline",
    "Jupiter": "Jupiter, the planet of wealth and fortune",
}
_HOUSE_THEME = {
    ("love", 7): "partnership area", ("love", 5): "romance and play area",
    ("work", 10): "work and standing area", ("work", 6): "daily-work and problem-solving area",
    ("money", 11): "gains and income area", ("money", 2): "savings and belongings area",
}
# The domain's significator houses, as a label for the sheet. Counted from the natal
# Moon (gochara is judged from Chandra lagna), which is why these hold at every
# birth-time tier — no ascendant needed. The app must NOT keep its own copy of this
# table: one source of truth, or the two drift and the sheet starts naming a house
# the reading never used.
_HOUSE_LABEL = {"love": "7th & 5th", "work": "10th & 6th", "money": "2nd & 11th"}
# Where "more about this" lives. Tab-level for now (features get linked once the
# rest of the frontend exists). Only shown if a destination is set.
_LINK = {
    "love":  {"tab": "People",   "label": "See today between you and your people"},
    "work":  {"tab": "Timeline", "label": "See your work across the bigger picture"},
    "money": {"tab": "Timeline", "label": "See your money across the bigger picture"},
}
_DETAIL = {
    ("love", "good"):   "A good day to reach out, enjoy the people you love, or gently mend a small rift, warmth comes easily.",
    ("love", "mixed"):  "Feelings run a little high, keep things light and playful, and save any big declarations for a steadier day.",
    ("love", "steady"): "Nothing dramatic on the love front, just an ordinary, easy day for your close ones.",
    ("love", "low"):    "Hearts feel tender today, so be soft with yourself and others, and don't force difficult conversations.",
    ("work", "good"):   "A strong stretch to push what matters, take on the hard task, or put yourself forward, effort lands well.",
    ("work", "mixed"):  "Work is doable but uneven, clear the straightforward tasks and don't stake everything on one big move.",
    ("work", "steady"): "Work simply ticks along today, steady progress, nothing forcing your hand either way.",
    ("work", "low"):    "Energy for work runs lower today, so clear the light stuff and save the big push for a stronger day.",
    ("money", "good"):  "A favourable day to tend your money, follow up on income, or make a considered move, the flow supports you.",
    ("money", "mixed"): "Money wants care today, hold the big spends and tend what you already have rather than chasing more.",
    ("money", "steady"): "Money sits quiet today, no pressure either way, a fine day for the routine, sensible bits.",
    ("money", "low"):   "Not a day for big money moves, hold steady, skip impulse spends, and let the bigger decisions wait.",
}


def _is_retrograde(planet: str, on_date_iso: str) -> bool:
    d = _date.fromisoformat(on_date_iso)
    jd = ephemeris.julday(d.year, d.month, d.day, 12.0)     # noon; speed sign is stable over a day
    _, speed = get_planet_longitude_and_speed(jd, PLANETS[planet])
    return speed < 0


def life_areas(profile: dict, on_date=None) -> dict:
    """Love / Work / Money for a day. Each domain returns the card one-liner
    (`line`) PLUS what its own bottom-sheet shows (`detail` = a fuller read,
    `why` = the plain astrology) and a `link` to where more lives (or None).
    Returns { date, in_focus, love|work|money: {tone, line, detail, why, planet, link} }."""
    f = daily_moon_forecast(profile, on_date)
    house = f["chandra_house"]
    band = f["band"]
    date_iso = f["date"]

    out: dict = {"date": date_iso, "in_focus": None}
    for dom, spec in _DOMAINS.items():
        karaka = spec["karaka"]
        word = _DOMAIN_WORD[dom]
        if house in spec["focus"]:
            tone, line = _FOCUS_LINE[(dom, house)]
            out["in_focus"] = dom
            why = (f"{_KARAKA_DESC[karaka]}, is your marker for {word}, and today the Moon is moving "
                   f"through your {_HOUSE_THEME[(dom, house)]}, the part of your chart tied to {word}.")
        else:
            tone, line = _STEADY_LINE[(dom, band)]
            why = (f"The Moon isn't especially stirring your {word} today, so it takes the day's overall "
                   f"mood. {_KARAKA_DESC[karaka]}, is what quietly governs it here.")

        try:
            if _is_retrograde(karaka, date_iso):
                line += _RETRO_NOTE[dom]
                why += _RETRO_NOTE[dom]
                if tone == "good":
                    tone = "mixed"          # a retrograde karaka softens a green light
        except Exception:
            pass

        out[dom] = {
            "tone": tone,
            "line": line,                       # the card one-liner
            "detail": _DETAIL[(dom, tone)],     # the sheet's fuller "what it means"
            "why": why.strip(),                 # the sheet's plain astrology reason
            "planet": karaka,
            "houses": _HOUSE_LABEL[dom],        # the sheet's "7th & 5th house" label
            "in_focus": house in spec["focus"], # is the Moon actually lighting this up today?
            "link": _LINK.get(dom),             # where "more" lives (tab-level for now)
        }
    return out


# ── Contradiction guard: keep the reading's activity chips in step with the rows ──
_CHIP_DOMAIN = [
    ("purchase", "money"), ("buying", "money"), ("selling", "money"), ("spend", "money"),
    ("money", "money"), ("risky", "money"), ("signing", "money"),
    ("love", "love"), ("romance", "love"), ("wedding", "love"), ("tender start", "love"),
    ("pending work", "work"), ("hard problem", "work"),
]


def _chip_domain(chip: str):
    c = (chip or "").lower()
    for sub, dom in _CHIP_DOMAIN:
        if sub in c:
            return dom
    return None


def reconcile_chips(good_for: list, go_easy: list, areas: dict):
    """Drop any chip that would contradict its life-area tone:
      • a "good for X" chip whose domain is mixed/low → dropped,
      • a "go easy on X" chip whose domain is good → dropped.
    Never strips a list to empty (falls back to the original)."""
    def tone(dom):
        return (areas.get(dom) or {}).get("tone")

    g = [c for c in (good_for or [])
         if not (_chip_domain(c) and tone(_chip_domain(c)) in ("mixed", "low"))]
    e = [c for c in (go_easy or [])
         if not (_chip_domain(c) and tone(_chip_domain(c)) == "good")]
    return (g or list(good_for or []), e or list(go_easy or []))
