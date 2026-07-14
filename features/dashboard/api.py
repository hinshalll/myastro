"""features.dashboard.api — FastAPI router."""

import json
from datetime import datetime, date
from zoneinfo import ZoneInfo

from features.dashboard.service import fetch_data
from features.dashboard.prompts import build_decide_prompt
from features.dashboard.schemas import (
    DashboardRequest, DashboardData, DecideRequest, DecideResponse, TimingRequest,
    ForecastRequest, WeekRequest, DayAlertsRequest, RelationshipWeatherRequest, MuhurtaRequest,
    PanchangRequest, HoraRequest, CalendarCheckRequest,
)

try:
    from fastapi import APIRouter
    router = APIRouter()
except ImportError:
    router = None


def _resolve_muhurta_event(event_type: str) -> str:
    """Resolve a Muhurat event to one of the classical rule-sets, for ANY input.

    A preset chip already IS a category (e.g. "marriage") → used as-is, no AI. For
    a free-text query the AI reader understands it in any language / phrasing
    (shared.ai.understanding), mapping it to the nearest of the 14 sourced
    categories; with no API key it falls back to the keyword classifier, then to
    "general". So the tool answers anything and never errors. The AI only
    CLASSIFIES — plan_muhurta does all the date/time astrology."""
    from shared.astro.muhurta import _EVENT_RULES, classify_event
    from shared.ai.understanding import classify_muhurta_event
    key = (event_type or "").strip().lower()
    if key in _EVENT_RULES:
        return key
    return classify_muhurta_event(key, classify_event)["event"]


if router is not None:

    @router.post("/data", response_model=DashboardData)
    def data(req: DashboardRequest) -> DashboardData:
        prof_json = json.dumps(req.profile, sort_keys=True)
        d = fetch_data(prof_json, req.today)
        return DashboardData(
            greeting=d.get("GREETING", ""), energy=d.get("ENERGY", ""),
            focus=d.get("FOCUS", ""),       caution=d.get("CAUTION", ""),
            window=d.get("WINDOW", ""),     summary=d.get("SUMMARY", ""),
        )

    @router.post("/forecast")
    def forecast(req: ForecastRequest) -> dict:
        """Daily "Cosmic Weather" hero for the mobile Today tab.

        FREE + cheap: pure math + a pre-baked meaning lookup, NO AI call.
        Moon-based, so it works at every birth-time tier (unknown time → noon
        placeholder). Same { profile } contract as /kundli/compute; optional
        "date" (defaults to today). Deterministic for a given profile+date.
        """
        from shared.astro.forecast import daily_moon_forecast
        out = daily_moon_forecast(req.profile, req.date)
        out["ok"] = True
        return out

    @router.post("/life-areas")
    def life_areas(req: ForecastRequest) -> dict:
        """Love / Work / Money rows for the Today reading. Same { profile } +
        optional date as /forecast. Derived from the SAME Moon transit as the
        reading (chandra_house + band), so it can't contradict it. FREE, no AI,
        NO scores (honest, planet-named).
        """
        from shared.astro.life_areas import life_areas as _life_areas
        return {"ok": True, **_life_areas(req.profile, req.date)}

    @router.post("/today")
    def today(req: ForecastRequest) -> dict:
        """The Read tab's ONE bundle: the reading + Love/Work/Money, computed
        TOGETHER so the reading's activity chips and the life-area rows always
        agree (the contradiction guard reconciles them). Same { profile } +
        optional date as /forecast. FREE, deterministic, no AI. (The strongest-
        window footer + live Hora come from /dashboard/timing + /dashboard/hora;
        the personal line from /memory/today.)
        """
        from shared.astro.forecast import daily_moon_forecast
        from shared.astro.life_areas import life_areas as _life_areas, reconcile_chips
        reading = daily_moon_forecast(req.profile, req.date)
        areas = _life_areas(req.profile, req.date)
        g, e = reconcile_chips(reading.get("good_for", []), reading.get("go_easy", []), areas)
        reading["good_for"], reading["go_easy"] = g, e
        return {"ok": True, "reading": reading, "life_areas": areas}

    @router.post("/week")
    def week(req: WeekRequest) -> dict:
        """Next-N-days forecast rail for the mobile Today tab (default 7 days).

        FREE: pure math + lookup, NO AI. Reuses the daily "Cosmic Weather"
        forecast for each day and adds a coarse `band` (good/neutral/difficult)
        for the rail's colour + an `is_today` flag. Same { profile } contract as
        /forecast; optional "start_date" (defaults to today, profile's tz).
        Tapping a day in the app shows that entry's full forecast (already here).
        """
        from shared.astro.forecast import weekly_moon_forecast
        out = weekly_moon_forecast(req.profile, req.start_date, req.days)
        out["ok"] = True
        return out

    @router.post("/relationship-weather")
    def relationship_weather(req: RelationshipWeatherRequest) -> dict:
        """Daily "relationship weather" between the user and one saved person.

        FREE: pure math + a pre-baked meaning lookup, NO AI, no new deps.
        Ashta Koota baseline (how the two mesh) + a Moon-based daily Tara layer
        (how today feels between them). All Moon-based, so it works even when
        either person's birth time is unknown. Both profiles use the
        /kundli/compute shape; optional "date" (defaults to today). Deterministic
        for the same two profiles + date.
        Returns { tone_word, summary, good_for, avoid, score (0..1), why,
        sanskrit, ... } (plus debug fields).
        """
        from shared.astro.relationship_weather import daily_relationship_weather
        out = daily_relationship_weather(req.profile_a, req.profile_b, req.date)
        out["ok"] = True
        return out

    @router.post("/day-alerts")
    def day_alerts(req: DayAlertsRequest) -> dict:
        """Two "Today" heads-up cards: Chandra Sandhi low-window + upcoming eclipse.

        Pure math (Swiss Ephemeris), Moon/Sun based — no birth time, no AI.
        Returns { chandra_sandhi: {...}|present:false, eclipse: {...}|present:false }.
        """
        from datetime import date as _date
        from shared.astro.astro_calc import chandra_sandhi_window, next_eclipse
        d = _date.fromisoformat(req.date)
        return {
            "ok": True,
            "chandra_sandhi": chandra_sandhi_window(d, req.tz),
            "eclipse": next_eclipse(d, req.tz, req.lat, req.lon),
        }

    @router.post("/muhurta")
    def muhurta(req: MuhurtaRequest) -> dict:
        """Event Timing Planner — best dates+times to do X over a date range.

        FREE: pure math + a pre-baked classical Muhurta lookup, NO AI, no new
        deps. Date- and location-based (panchanga + sunrise/sunset), NO birth
        chart needed. Scores each day's five panchanga limbs against sourced
        rules for the event, then picks the best clear window (Abhijit / good
        Choghadiya) avoiding Rahu Kaal etc. Returns the top few days, or says
        plainly when nothing in the range is strongly auspicious. Deterministic.
        """
        from shared.astro.muhurta import plan_muhurta
        event = _resolve_muhurta_event(req.event_type)   # preset | keyword | cheap-AI | 'general'
        out = plan_muhurta(event, req.start_date, req.end_date,
                           req.lat, req.lon, req.tz, req.top_n)
        out["resolved_event"] = event
        out["ok"] = True
        return out

    @router.post("/panchang")
    def panchang(req: PanchangRequest) -> dict:
        """Daily Panchang for the Today → Plan tab: the today+next-2-days strip
        and the full-month grid.

        FREE: pure math + lookup, NO AI. Each day carries the sunrise tithi /
        nakshatra / yoga / karana, the PERSONAL day-colour (good/mixed/low — the
        SAME `day_quality` the Today reading uses, so the calendar and the reading
        can never disagree), festival markers (Ekadashi / Purnima / Amavasya) and
        Grahan days, plus the day's strongest window. `days`=3 → the strip; ~31-35
        → the month grid. `full` defaults to detailed for <=7 days, light beyond.
        Day-naming uses the classical Udaya Tithi (tithi-at-sunrise) rule.
        """
        from datetime import datetime as _dt
        from zoneinfo import ZoneInfo as _zi
        from shared.astro.panchang import panchang_range
        start = req.start_date or _dt.now(_zi(req.tz)).date().isoformat()
        full = req.full if req.full is not None else (req.days <= 7)
        out = panchang_range(req.profile, start, req.days, req.lat, req.lon, req.tz, full=full)
        out["ok"] = True
        return out

    @router.post("/hora")
    def hora(req: HoraRequest) -> dict:
        """Live greeting context for the Today → Read header: the current
        planetary hour (Hora) as a plain 'good stretch for X' line, plus tonight's
        Moon phase.

        FREE: pure math, no AI. Date + location based, no birth chart. The hora
        uses the classical sunrise→sunset / sunset→sunrise 12+12 split with the
        weekday-lord first hora and the Chaldean sequence (sourced in astro_calc).
        """
        from shared.astro.astro_calc import current_hora, moon_phase
        from shared.astro.festivals import festival_for
        today = datetime.now(ZoneInfo(req.tz)).date().isoformat()
        return {
            "ok": True,
            "hora": current_hora(req.lat, req.lon, req.tz),
            "moon_phase": moon_phase(tz_name=req.tz),
            "festival": festival_for(today),   # {name, greeting, date} or None → header "Happy X"
        }

    @router.post("/decide-quick")
    def decide_quick(req: DecideRequest) -> dict:
        """AI-FREE quick yes/no for "should I do X right now?".

        Pure Tara-Bala math (today's Moon read from the natal Moon, at the current
        moment) + a templated plain-English line — NO Gemini call, so it's instant
        and free. Powers the Ask sheet's one-tap "quick yes/no" mode. The deeper,
        question-aware answer is the AI Ask (/decide or /consultation). Moon-based,
        so it works even when the birth time is unknown. The `question` is optional
        and only echoed back (the verdict is the day's Moon quality, not parsed).
        """
        from datetime import datetime
        from zoneinfo import ZoneInfo
        from shared.astro import ephemeris
        from shared.astro.constants import PLANETS
        from shared.astro.astro_calc import get_planet_longitude_and_speed, calculate_tara_bala
        from shared.astro.forecast import _natal_moon_lon  # unknown-time-safe natal Moon

        natal = _natal_moon_lon(req.profile)
        now = datetime.now(ZoneInfo("UTC"))
        jd_now = ephemeris.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0)
        transit, _ = get_planet_longitude_and_speed(jd_now, PLANETS["Moon"])
        tara = calculate_tara_bala(natal, transit)

        verdict = {"Go": "Yes", "Stop": "Wait", "Caution": "Proceed gently"}.get(tara["status"], "Proceed gently")
        reason = {
            "Yes": "The day's flow is with you right now — a fine moment to go ahead.",
            "Wait": "The timing leans against you at the moment — better to give it a little while.",
            "Proceed gently": "It's a mixed moment — you can move ahead, just gently and without forcing it.",
        }[verdict]
        quality = {"Go": "a favourable", "Stop": "a challenging", "Caution": "a mixed"}.get(tara["status"], "a mixed")
        why = (f"Right now the Moon sits in {tara['tara']} — {quality} day-star counted from the "
               f"one you were born under. That's the classical Tara Bala read of this moment.")

        return {
            "ok": True,
            "verdict": verdict,            # Yes / Wait / Proceed gently
            "reason": reason,              # one warm plain-English line
            "why": why,                    # the astrology, plain
            "sanskrit": "तारा बल",
            "question": req.question,      # echoed for the UI
            "tara": tara["tara"],
        }

    @router.post("/timing")
    def timing(req: TimingRequest) -> dict:
        """Today's auspicious / inauspicious windows for a date + location.

        Date- and location-based (weekday + sunrise/sunset), NOT birth-chart based.
        Pure math — no AI. Powers the mobile "Today → Good / Avoid times" strip.
        """
        from shared.astro.astro_calc import daily_timing_windows
        d = date.fromisoformat(req.date)
        out = daily_timing_windows(d, req.lat, req.lon, req.tz)
        out["ok"] = True
        return out

    @router.post("/calendar-check")
    def calendar_check(req: CalendarCheckRequest) -> dict:
        """Calendar Doctor: given the user's upcoming events (times only — the app
        reads them on-device via expo-calendar), flag any that sit in a weak window
        and suggest a better slot the same day. FREE, pure math, no AI. The server
        never stores the events; titles are optional and only echoed back for the UI.
        """
        from shared.astro.calendar_doctor import check_events
        events = [e.model_dump() for e in req.events]
        return {"ok": True, "events": check_events(events, req.lat, req.lon, req.tz)}

    @router.post("/decide", response_model=DecideResponse)
    def decide(req: DecideRequest) -> DecideResponse:
        from shared.astro import ephemeris
        from shared.astro.constants import PLANETS
        from shared.astro.astro_calc import (
            local_to_julian_day, get_planet_longitude_and_speed, calculate_tara_bala,
        )
        from shared.astro.dossier_builder import generate_astrology_dossier, get_gochara_overlay
        from shared.ai.gemini_client import generate_content_with_fallback

        prof = req.profile
        p_date = date.fromisoformat(prof["date"])
        p_time = datetime.strptime(prof["time"], "%H:%M").time()
        jd_nat, _, _ = local_to_julian_day(p_date, p_time, prof["tz"])
        natal_moon, _ = get_planet_longitude_and_speed(jd_nat, PLANETS["Moon"])
        dt_now = datetime.now(ZoneInfo("UTC"))
        jd_now = ephemeris.julday(dt_now.year, dt_now.month, dt_now.day,
                                  dt_now.hour + dt_now.minute / 60.0)
        transit_moon, _ = get_planet_longitude_and_speed(jd_now, PLANETS["Moon"])
        tara = calculate_tara_bala(natal_moon, transit_moon)
        py_verdict = "YES" if tara["status"] == "Go" else ("WAIT" if tara["status"] == "Stop" else "PROCEED CAUTIOUSLY")

        dossier = generate_astrology_dossier(prof, False, compact=True)
        transits = get_gochara_overlay(prof)
        prompt = build_decide_prompt(dossier, transits, req.question, py_verdict, tara["advice"])
        raw = generate_content_with_fallback(prompt)
        try:
            out = json.loads(raw.strip().replace("```json", "").replace("```", "").strip())
        except Exception:
            out = {"VERDICT": py_verdict, "WHY": "Cosmic signals processed.", "ALTERNATIVE": tara["advice"]}
        return DecideResponse(
            verdict=out.get("VERDICT", py_verdict),
            why=out.get("WHY", ""),
            alternative=out.get("ALTERNATIVE", tara["advice"]),
        )
