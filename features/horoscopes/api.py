"""features.horoscopes.api — FastAPI router for mobile + website."""

import json

from features.horoscopes.service import generate_western_forecast, generate_vedic_forecast
from features.horoscopes.schemas import (
    WesternRequest, WesternResponse, VedicRequest, VedicResponse,
)

try:
    from fastapi import APIRouter
    router = APIRouter()
except ImportError:
    router = None


if router is not None:

    @router.post("/western", response_model=WesternResponse)
    def western(req: WesternRequest) -> WesternResponse:
        reading = generate_western_forecast(req.sun_sign, req.today)
        return WesternResponse(reading=reading)

    @router.post("/vedic", response_model=VedicResponse)
    def vedic(req: VedicRequest) -> VedicResponse:
        from math_engine.astro_calc import (
            local_to_julian_day, get_planet_longitude_and_speed,
            sign_index_from_lon, sign_name, nakshatra_info,
        )
        from math_engine.constants import PLANETS
        from datetime import datetime, date

        p_date = date.fromisoformat(req.profile["date"])
        p_time = datetime.strptime(req.profile["time"], "%H:%M").time()
        jd, _, _ = local_to_julian_day(p_date, p_time, req.profile["tz"])
        moon_lon, _ = get_planet_longitude_and_speed(jd, PLANETS["Moon"])
        rashi = sign_name(sign_index_from_lon(moon_lon))
        nak, _, _ = nakshatra_info(moon_lon)

        reading = generate_vedic_forecast(
            json.dumps(req.profile, sort_keys=True), req.timeframe, req.today,
        )
        return VedicResponse(rashi=rashi, nakshatra=nak, reading=reading)
