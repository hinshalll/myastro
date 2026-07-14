"""features.capsule.service — resolve a Time Capsule's future delivery moment.

Four kinds of moment:
  • custom   — a date the user picks.
  • birthday — the next anniversary of their birth date.
  • dasha    — the next Vimshottari chapter change (the current antardasha's end),
               Moon-nakshatra based, so it works at every birth-time tier.
  • jupiter  — the next time transiting Jupiter enters a classically supportive
               house from the natal Moon (favourable Guru gochara: 2,5,7,9,11),
               i.e. the next fresh onset strictly after today.

Pure-ish: birthday is calendar math; dasha + jupiter use the frozen engine
(no AI). All return (deliver_on: date, label: str).
"""

from datetime import date as _date, datetime, timedelta, time as _time

from shared.astro import ephemeris
from shared.astro.astro_calc import sign_index_from_lon, build_vimshottari_timeline
from shared.astro.forecast import _natal_moon_lon

_JUP_GOOD_HOUSES = {2, 5, 7, 9, 11}     # favourable Guru gochara from the natal Moon


def _house_from(planet_sign: int, moon_sign: int) -> int:
    return ((planet_sign - moon_sign) % 12) + 1


def _birth_dt(profile: dict) -> datetime:
    """Naive local birth datetime (unknown time → noon; fine for year-scale dasha)."""
    d = profile["date"]
    d = _date.fromisoformat(d) if isinstance(d, str) else d
    raw = profile.get("time")
    if raw in (None, ""):
        t = _time(12, 0)
    elif isinstance(raw, str):
        p = raw.split(":")
        t = _time(int(p[0]), int(p[1]), int(p[2]) if len(p) > 2 else 0)
    else:
        t = raw
    return datetime(d.year, d.month, d.day, t.hour, t.minute)


def _bump_year(d: _date, year: int) -> _date:
    """d moved to `year`, guarding Feb 29 → Feb 28 in non-leap years."""
    try:
        return d.replace(year=year)
    except ValueError:
        return _date(year, d.month, 28)


def next_birthday(profile: dict, today: _date) -> tuple[_date, str]:
    bd = profile["date"]
    bd = _date.fromisoformat(bd) if isinstance(bd, str) else bd
    nb = _bump_year(bd, today.year)
    if nb <= today:
        nb = _bump_year(bd, today.year + 1)
    return nb, "your next birthday"


def next_dasha_change(profile: dict, today: _date) -> tuple[_date, str]:
    moon_lon = _natal_moon_lon(profile)
    di = build_vimshottari_timeline(_birth_dt(profile), moon_lon, datetime.now())
    end = di["ad_end"]
    end_date = end.date() if isinstance(end, datetime) else end
    # Guard against a boundary that has effectively already passed.
    if end_date <= today:
        end_date = today + timedelta(days=1)
    label = f"the start of your next chapter (end of your {di['current_md']}/{di['current_ad']} period)"
    return end_date, label


def _jupiter_house(d: _date, moon_sign: int) -> int:
    jd = ephemeris.julday(d.year, d.month, d.day, 12.0)
    jl = ephemeris.planet_lon(jd, "Jupiter")
    return _house_from(sign_index_from_lon(jl), moon_sign)


def next_jupiter_favour(profile: dict, today: _date) -> tuple[_date, str]:
    """First future onset (weekly scan, capped ~6 yrs) of Jupiter entering a
    supportive house from the natal Moon. Jupiter moves ~1 sign/year, so a weekly
    step never skips a house ingress."""
    moon_sign = sign_index_from_lon(_natal_moon_lon(profile))
    prev_good = _jupiter_house(today, moon_sign) in _JUP_GOOD_HOUSES
    d = today + timedelta(days=7)
    for _ in range(314):                 # ~6 years of weeks
        good = _jupiter_house(d, moon_sign) in _JUP_GOOD_HOUSES
        if good and not prev_good:        # a fresh onset
            return d, "the next time Jupiter turns supportive for you"
        prev_good = good
        d += timedelta(days=7)
    # Fallback (shouldn't happen within 6 yrs): the next birthday.
    return next_birthday(profile, today)


def resolve_occasion(occasion: str, profile: dict | None, today: _date,
                     deliver_on: str | None = None) -> tuple[_date, str]:
    if occasion == "custom":
        if not deliver_on:
            raise ValueError("a custom capsule needs a deliver_on date")
        d = _date.fromisoformat(deliver_on)
        if d <= today:
            raise ValueError("deliver_on must be in the future")
        return d, "a date you chose"
    if not profile:
        raise ValueError("this delivery moment needs the user's birth profile")
    if occasion == "birthday":
        return next_birthday(profile, today)
    if occasion == "dasha":
        return next_dasha_change(profile, today)
    if occasion == "jupiter":
        return next_jupiter_favour(profile, today)
    raise ValueError(f"unknown occasion: {occasion}")


def suggest_moments(profile: dict, today: _date) -> list[dict]:
    """The 3 computed 'or pick a moment' options for the create sheet."""
    out = []
    for occ in ("birthday", "dasha", "jupiter"):
        try:
            d, label = resolve_occasion(occ, profile, today)
            out.append({"occasion": occ, "deliver_on": d.isoformat(), "label": label})
        except Exception:
            continue
    return out
