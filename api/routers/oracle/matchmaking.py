"""
api/routers/oracle/matchmaking.py — /api/v1/oracle/matchmaking
================================================================
Ashta Koota + Manglik + Compatibility Index for two profiles.
"""

from datetime import date as _date, datetime as _dt
from fastapi import APIRouter, HTTPException

from math_engine.constants import PLANETS, SIGN_LORDS_MAP
from math_engine.astro_calc import (
    local_to_julian_day, get_planet_longitude_and_speed,
    sign_index_from_lon, get_lagna_and_cusps,
    check_manglik_dosha, get_manglik_cancellation_verdict,
)
from math_engine.dossier_builder import generate_astrology_dossier, calculate_matchmaking_synastry
from math_engine.scoring import calculate_compatibility_index
from ai_engine.gemini_client import generate_content_with_fallback
from ai_engine.prompts import build_matchmaking_prompt
from ai_engine.knowledge import build_topic_query, rag_context
from api.schemas import MatchmakingRequest, ReadingResponse

router = APIRouter(prefix="/oracle", tags=["oracle"])


def _moon_lon(profile_dict):
    """Compute moon longitude for a profile dict."""
    d = _date.fromisoformat(profile_dict["date"])
    t = _dt.strptime(profile_dict["time"], "%H:%M").time()
    jd, _, _ = local_to_julian_day(d, t, profile_dict["tz"])
    lon, _ = get_planet_longitude_and_speed(jd, PLANETS["Moon"])
    return lon


@router.post("/matchmaking", response_model=ReadingResponse)
async def oracle_matchmaking(req: MatchmakingRequest):
    """Full compatibility match between two profiles."""
    try:
        p_boy_d  = req.boy.dict()
        p_girl_d = req.girl.dict()

        ma = _moon_lon(p_boy_d); mb = _moon_lon(p_girl_d)
        jda, _, _ = local_to_julian_day(
            _date.fromisoformat(p_boy_d["date"]),
            _dt.strptime(p_boy_d["time"], "%H:%M").time(), p_boy_d["tz"])
        jdb, _, _ = local_to_julian_day(
            _date.fromisoformat(p_girl_d["date"]),
            _dt.strptime(p_girl_d["time"], "%H:%M").time(), p_girl_d["tz"])
        pla   = {pn: get_planet_longitude_and_speed(jda, pid) for pn, pid in PLANETS.items()}
        plb   = {pn: get_planet_longitude_and_speed(jdb, pid) for pn, pid in PLANETS.items()}
        laga  = sign_index_from_lon(get_lagna_and_cusps(jda, p_boy_d["lat"],  p_boy_d["lon"])[0])
        lagb  = sign_index_from_lon(get_lagna_and_cusps(jdb, p_girl_d["lat"], p_girl_d["lon"])[0])

        ma_d = check_manglik_dosha(
            laga, sign_index_from_lon(pla["Moon"][0]),
            sign_index_from_lon(pla["Mars"][0]),
            mars_lon=pla["Mars"][0], planet_data=pla)
        mb_d = check_manglik_dosha(
            lagb, sign_index_from_lon(plb["Moon"][0]),
            sign_index_from_lon(plb["Mars"][0]),
            mars_lon=plb["Mars"][0], planet_data=plb)
        canc = get_manglik_cancellation_verdict(ma_d, mb_d)

        dos_a = generate_astrology_dossier(p_boy_d)
        dos_b = generate_astrology_dossier(p_girl_d)
        koota_data, marital_a, marital_b, kp_a, kp_b = calculate_matchmaking_synastry(
            p_boy_d, p_girl_d, ma, mb, jda, jdb, dos_a, dos_b)

        compat_index = calculate_compatibility_index(
            koota_data, marital_a, marital_b, kp_a, kp_b,
            laga_lord=SIGN_LORDS_MAP[laga],
            lagb_lord=SIGN_LORDS_MAP[lagb],
            moon_lord_a=SIGN_LORDS_MAP[sign_index_from_lon(pla["Moon"][0])],
            moon_lord_b=SIGN_LORDS_MAP[sign_index_from_lon(plb["Moon"][0])],
            manglik_verdict=canc)

        match_ctx = rag_context(
            build_topic_query(topic="match", extras={"score": str(koota_data.get("score", ""))}),
            ("htrh2.md", "kp4.md"), k=10)
        final = build_matchmaking_prompt(
            dos_a, dos_b, koota_data, canc, p_boy_d, p_girl_d,
            marital_a, marital_b, kp_a, kp_b,
            knowledge_context=match_ctx, compatibility_index=compat_index)
        result = generate_content_with_fallback(final, knowledge_files=None)

        return ReadingResponse(
            feature="oracle_matchmaking",
            markdown=result,
            metadata={
                "koota_score":      koota_data.get("score"),
                "manglik_verdict":  canc,
                "compatibility_index": compat_index,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
