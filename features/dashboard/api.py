"""features.dashboard.api — FastAPI router."""

import json
from datetime import datetime, date
from zoneinfo import ZoneInfo

from features.dashboard.service import fetch_data
from features.dashboard.prompts import build_decide_prompt
from features.dashboard.schemas import (
    DashboardRequest, DashboardData, DecideRequest, DecideResponse,
)

try:
    from fastapi import APIRouter
    router = APIRouter()
except ImportError:
    router = None


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

    @router.post("/decide", response_model=DecideResponse)
    def decide(req: DecideRequest) -> DecideResponse:
        import swisseph as swe
        from math_engine.constants import PLANETS
        from math_engine.astro_calc import (
            local_to_julian_day, get_planet_longitude_and_speed, calculate_tara_bala,
        )
        from math_engine.dossier_builder import generate_astrology_dossier, get_gochara_overlay
        from ai_engine.gemini_client import generate_content_with_fallback

        prof = req.profile
        p_date = date.fromisoformat(prof["date"])
        p_time = datetime.strptime(prof["time"], "%H:%M").time()
        jd_nat, _, _ = local_to_julian_day(p_date, p_time, prof["tz"])
        natal_moon, _ = get_planet_longitude_and_speed(jd_nat, PLANETS["Moon"])
        dt_now = datetime.now(ZoneInfo("UTC"))
        jd_now = swe.julday(dt_now.year, dt_now.month, dt_now.day,
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
