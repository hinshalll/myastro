"""shared.timeloc — the ONE place "today" and "now" are decided for a user.

**NEVER call `date.today()` or `datetime.now()` without a timezone for anything a user sees.**

Why this module exists. The server runs in **UTC** (Render). India is **UTC+5:30**. So every day
between **00:00 and 05:30 IST**, a bare `date.today()` returns **YESTERDAY** for every Indian
user. That is ~23% of every day, wrong, for the entire userbase — not a traveller edge case.
It shipped in `moon/api.py`, `capsule/api.py` and `notify/service.py`, and the schema comment
even documented it ("defaults to today (server)") without anyone noticing that "server" meant
"a machine in a different country from every user".

**UTC IS NOT ALWAYS A BUG — do not "fix" the ephemeris.**
`datetime.now(ZoneInfo("UTC"))` feeding `ephemeris.julday(...)` is **CORRECT**. A Julian Day is a
universal instant, and planetary longitudes are global facts; converting to a local zone there
would BREAK the maths. `dashboard/api.py` does this correctly for Tara-Bala (natal Moon vs
transiting Moon) — leave it alone.

The difference:
  - "what INSTANT is it, universally?"  → UTC → julday. **Correct.**
  - "what DAY is it for this human?"    → their tz. `date.today()` here is the bug.

The rule (see LOCATION_TIME_AUDIT.md):
  - **A · NATAL**   → birth tz. Fixed forever.
  - **B · SUNRISE** → current lat/lon.
  - **C · GLOBAL**  → no location.
  - **D · DISPLAY / SCHEDULING** → the user's CURRENT tz. "Today" lives here. So does anything
    scheduled: push notifications, capsule delivery, streak boundaries.

`user_today()` is bucket **D**. Pass the user's CURRENT timezone whenever the client knows it
(the client always does); fall back to their stored profile tz for server-side jobs (push), where
there is no client to ask.
"""
from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

# India-first product: if we truly do not know, IST is a far better guess than UTC, which is
# wrong for 100% of Indian users. This is a last resort, not a default to rely on.
FALLBACK_TZ = "Asia/Kolkata"


def safe_zone(tz: str | None) -> ZoneInfo:
    """A ZoneInfo that never raises. Unknown/blank tz → FALLBACK_TZ."""
    try:
        if tz:
            return ZoneInfo(tz)
    except Exception:
        pass
    return ZoneInfo(FALLBACK_TZ)


def user_now(tz: str | None = None) -> datetime:
    """Timezone-aware 'now' for this user. Use instead of datetime.now()."""
    return datetime.now(safe_zone(tz))


def user_today(tz: str | None = None) -> date:
    """Today's date IN THE USER'S TIMEZONE. Use instead of date.today()."""
    return user_now(tz).date()


def user_today_iso(tz: str | None = None) -> str:
    """Today as 'YYYY-MM-DD' in the user's timezone."""
    return user_today(tz).isoformat()


def resolve_today(explicit: str | None, tz: str | None = None) -> date:
    """The standard endpoint pattern: trust an explicit client date, else derive it from tz.

    The client is the best authority on what day it is for the user (it knows where they are
    right now), so an explicit `today` always wins. `tz` is the fallback for server-side jobs.
    """
    if explicit:
        try:
            return date.fromisoformat(explicit)
        except Exception:
            pass
    return user_today(tz)


def profile_tz(profile: dict | None) -> str | None:
    """The tz stored on a profile dict (birth OR db shape). For server-side jobs only.

    NOTE this is the BIRTH timezone, so it is only a fallback for scheduling — if the user has
    moved, it is wrong. Prefer a tz sent by the client.
    """
    if not profile:
        return None
    return profile.get("tz") or profile.get("timezone") or None
