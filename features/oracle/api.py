"""features.oracle.api — FastAPI routes for all 6 oracle sub-features.

Each endpoint mirrors the corresponding Streamlit sub-view (deep_analysis /
matchmaking / marriage / gochara / compare / prashna) but with Streamlit
state replaced by pure request/response shapes.

The business logic is duplicated minimally here because the sub-views are
tightly coupled to st.session_state, st.spinner, etc. When the mobile app
demands more endpoints, lift shared bits into a service.py file.
"""

from datetime import datetime, date
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor

from features.oracle.schemas import (
    DeepAnalysisRequest, DeepAnalysisResponse,
    MatchmakingRequest, MatchmakingResponse,
    MarriageRequest, MarriageResponse,
    GocharaRequest, GocharaResponse,
    CompareRequest, CompareResponse,
    PrashnaRequest, PrashnaResponse,
)

try:
    from fastapi import APIRouter, HTTPException
    router = APIRouter()
except ImportError:
    router = None


# ── helpers shared across endpoints ─────────────────────────────────────────

def _parse_profile(p: dict) -> dict:
    """Normalise a profile dict — keep dates/times as ISO strings (engine
    accepts both string and date/time objects)."""
    return dict(p)


def _profile_jd(p: dict) -> float:
    """Get Julian day for a profile."""
    from shared.astro.astro_calc import local_to_julian_day
    pd_ = date.fromisoformat(p["date"]) if isinstance(p["date"], str) else p["date"]
    pt_ = datetime.strptime(p["time"], "%H:%M").time() if isinstance(p["time"], str) else p["time"]
    jd, _, _ = local_to_julian_day(pd_, pt_, p["tz"])
    return jd


def _rag(query: str, books: tuple, k: int = 8) -> str:
    from shared.ai.knowledge import rag_context
    try:
        return rag_context(query, list(books), k=k)
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

if router is not None:

    # ─── /deep-analysis ──────────────────────────────────────────────────────
    @router.post("/deep-analysis", response_model=DeepAnalysisResponse)
    def deep_analysis(req: DeepAnalysisRequest) -> DeepAnalysisResponse:
        from shared.astro.dossier_builder import generate_astrology_dossier
        from shared.astro import config as astro_config
        from shared.ai.gemini_client import agent_worker, generate_content_with_fallback
        from shared.ai import config
        from shared.ai.prompts import (
            build_agent_parashari_prompt, build_agent_timing_prompt,
            build_agent_kp_prompt, build_agent_house_promise_prompt,
            build_master_synthesizer_prompt,
        )

        prof = _parse_profile(req.profile)
        dossier = generate_astrology_dossier(prof, req.include_d60)
        expert_rules = "You are an expert agent providing concise observations."

        # Third agent follows the KP toggle: KP cusp specialist when ON, classical
        # Parashari bhava-promise specialist when OFF. The feature never disappears.
        use_kp = astro_config.kp_enabled()
        third_prompt = (build_agent_kp_prompt(dossier) if use_kp
                        else build_agent_house_promise_prompt(dossier))

        # Three parallel agents
        _agent = config.model_for("agent")
        with ThreadPoolExecutor(max_workers=3) as ex:
            f_p = ex.submit(agent_worker, build_agent_parashari_prompt(dossier),
                            [], _agent, expert_rules)
            f_t = ex.submit(agent_worker, build_agent_timing_prompt(dossier),
                            [], _agent, expert_rules)
            f_k = ex.submit(agent_worker, third_prompt, [], _agent, expert_rules)
            p_notes, t_notes, k_notes = f_p.result(), f_t.result(), f_k.result()

        synth_prompt = build_master_synthesizer_prompt(
            dossier, p_notes, t_notes, k_notes, kp_mode=use_kp)
        reading = generate_content_with_fallback(synth_prompt, task="agent")
        return DeepAnalysisResponse(
            reading=reading,
            notes={"parashari": p_notes, "timing": t_notes,
                   ("kp" if use_kp else "bhava_promise"): k_notes},
        )

    # ─── /matchmaking ────────────────────────────────────────────────────────
    @router.post("/matchmaking", response_model=MatchmakingResponse)
    def matchmaking(req: MatchmakingRequest) -> MatchmakingResponse:
        from shared.astro.constants import PLANETS, SIGN_LORDS_MAP
        from shared.astro.astro_calc import (
            local_to_julian_day, get_planet_longitude_and_speed,
            sign_index_from_lon, get_lagna_and_cusps,
            check_manglik_dosha, get_manglik_cancellation_verdict,
        )
        from shared.astro.dossier_builder import generate_astrology_dossier
        from shared.astro.scoring import (
            calculate_matchmaking_synastry, calculate_compatibility_index,
        )
        from shared.ai.gemini_client import generate_content_with_fallback
        from shared.ai.prompts import build_matchmaking_prompt

        p_a = _parse_profile(req.profile_a)
        p_b = _parse_profile(req.profile_b)
        # Resolve boy/girl by gender (fall back to ordering)
        p_boy  = p_a if p_a.get("gender") == "M" else p_b
        p_girl = p_b if p_boy is p_a else p_a
        if p_boy is p_girl:
            p_boy, p_girl = p_a, p_b

        jda = _profile_jd(p_boy)
        jdb = _profile_jd(p_girl)
        pla = {pn: get_planet_longitude_and_speed(jda, pid) for pn, pid in PLANETS.items()}
        plb = {pn: get_planet_longitude_and_speed(jdb, pid) for pn, pid in PLANETS.items()}
        laga = sign_index_from_lon(get_lagna_and_cusps(jda, p_boy["lat"],  p_boy["lon"])[0])
        lagb = sign_index_from_lon(get_lagna_and_cusps(jdb, p_girl["lat"], p_girl["lon"])[0])

        ma_d = check_manglik_dosha(
            laga, sign_index_from_lon(pla["Moon"][0]),
            sign_index_from_lon(pla["Mars"][0]),
            mars_lon=pla["Mars"][0], planet_data=pla,
        )
        mb_d = check_manglik_dosha(
            lagb, sign_index_from_lon(plb["Moon"][0]),
            sign_index_from_lon(plb["Mars"][0]),
            mars_lon=plb["Mars"][0], planet_data=plb,
        )
        canc = get_manglik_cancellation_verdict(ma_d, mb_d)

        dos_a = generate_astrology_dossier(p_boy)
        dos_b = generate_astrology_dossier(p_girl)
        koota, marital_a, marital_b, kp_a, kp_b = calculate_matchmaking_synastry(
            p_boy, p_girl, pla["Moon"][0], plb["Moon"][0], jda, jdb, dos_a, dos_b,
        )
        compat = calculate_compatibility_index(
            koota, marital_a, marital_b, kp_a, kp_b,
            laga_lord=SIGN_LORDS_MAP[laga],
            lagb_lord=SIGN_LORDS_MAP[lagb],
            moon_lord_a=SIGN_LORDS_MAP[sign_index_from_lon(pla["Moon"][0])],
            moon_lord_b=SIGN_LORDS_MAP[sign_index_from_lon(plb["Moon"][0])],
            manglik_verdict=canc,
        )
        ctx = _rag(
            f"matchmaking compatibility ashta koota {koota.get('score', '')}",
            ("htrh2.md", "kp4.md"), 10,
        )
        prompt = build_matchmaking_prompt(
            dos_a, dos_b, koota, canc, p_boy, p_girl,
            marital_a, marital_b, kp_a, kp_b,
            knowledge_context=ctx, compatibility_index=compat,
        )
        return MatchmakingResponse(
            koota_score=float(koota.get("score", 0) or 0),
            manglik_verdict=str(canc.get("verdict", "") if isinstance(canc, dict) else canc),
            compatibility_index=float(
                (compat.get("score", 0) if isinstance(compat, dict) else compat) or 0
            ),
            reading=generate_content_with_fallback(prompt, task="agent"),
        )

    # ─── /marriage ───────────────────────────────────────────────────────────
    @router.post("/marriage", response_model=MarriageResponse)
    def marriage(req: MarriageRequest) -> MarriageResponse:
        from shared.astro.dossier_builder import generate_astrology_dossier
        from shared.astro.scoring import calculate_destiny_confirmation
        from shared.ai.gemini_client import generate_content_with_fallback
        from shared.ai.prompts import build_destiny_confirmation_prompt

        p_a = _parse_profile(req.profile_a)
        p_b = _parse_profile(req.profile_b) if req.profile_b else None

        dos_a = generate_astrology_dossier(p_a)
        dos_b = generate_astrology_dossier(p_b) if p_b else ""
        jda = _profile_jd(p_a)
        jdb = _profile_jd(p_b) if p_b else jda
        dest = calculate_destiny_confirmation(p_a, p_b, jda, jdb, dos_a, dos_b)

        ctx = _rag("marriage timing destiny matrix", ("htrh2.md", "kp4.md"), 10)
        prompt = build_destiny_confirmation_prompt(p_a, p_b, dos_a, dos_b, dest,
                                                    knowledge_context=ctx)
        return MarriageResponse(
            promise_score=float(dest.get("score", dest.get("promise_score", 0)) or 0),
            timing_windows=list(dest.get("timing_windows", []) or []),
            reading=generate_content_with_fallback(prompt, task="agent"),
        )

    # ─── /gochara ────────────────────────────────────────────────────────────
    @router.post("/gochara", response_model=GocharaResponse)
    def gochara(req: GocharaRequest) -> GocharaResponse:
        from shared.astro.dossier_builder import generate_astrology_dossier, get_gochara_overlay
        from shared.ai.gemini_client import generate_content_with_fallback
        from shared.ai.prompts import build_transit_prompt

        prof = _parse_profile(req.profile)
        dossier = generate_astrology_dossier(prof, req.include_d60)
        overlay = get_gochara_overlay(prof)
        ctx = _rag("gochara transit current planetary activation",
                   ("bphs2.md", "htrh2.md"), 10)
        prompt = build_transit_prompt(dossier, overlay, knowledge_context=ctx)
        return GocharaResponse(reading=generate_content_with_fallback(prompt, task="agent"))

    # ─── /compare ────────────────────────────────────────────────────────────
    @router.post("/compare", response_model=CompareResponse)
    def compare(req: CompareRequest) -> CompareResponse:
        if not 2 <= len(req.profiles) <= 10:
            raise HTTPException(status_code=400,
                                detail="compare requires 2 to 10 profiles")
        from shared.astro.dossier_builder import generate_astrology_dossier
        from shared.astro.scoring import calculate_and_rank_profiles
        from shared.ai.gemini_client import generate_content_with_fallback
        from shared.ai.prompts import build_comparison_prompt

        profiles = [_parse_profile(p) for p in req.profiles]
        dossiers = [generate_astrology_dossier(p) for p in profiles]
        # 3-tuple form: (name, dossier, profile) — preferred
        profiles_dossiers = [
            (p.get("name", f"Person {i+1}"), d, p)
            for i, (p, d) in enumerate(zip(profiles, dossiers))
        ]
        rankings = calculate_and_rank_profiles(profiles_dossiers, req.criteria)
        ctx = _rag(" ".join(req.criteria), ("htrh1.md", "htrh2.md"), 8)
        prompt = build_comparison_prompt(dossiers, req.criteria, knowledge_context=ctx)
        return CompareResponse(
            rankings=rankings if isinstance(rankings, list) else [rankings],
            reading=generate_content_with_fallback(prompt, task="agent"),
        )

    # ─── /prashna ────────────────────────────────────────────────────────────
    @router.post("/prashna", response_model=PrashnaResponse)
    def prashna(req: PrashnaRequest) -> PrashnaResponse:
        from shared.astro.astro_calc import geocode_place, timezone_for_latlon
        from shared.astro.dossier_builder import generate_astrology_dossier
        from shared.astro.scoring import get_prashna_python_verdict
        from shared.ai.gemini_client import generate_content_with_fallback
        from shared.ai.prompts import build_prashna_prompt

        if req.lat is None or req.lon is None or req.tz is None:
            if not req.place.strip():
                raise HTTPException(status_code=400,
                                    detail="Provide either place OR lat+lon+tz")
            geo = geocode_place(req.place.strip())
            if not geo:
                raise HTTPException(status_code=400, detail=f"Could not geocode: {req.place}")
            lat, lon, _ = geo
            tz = timezone_for_latlon(lat, lon)
            place_label = req.place
        else:
            lat, lon, tz, place_label = req.lat, req.lon, req.tz, (req.place or "Manual")

        now = datetime.now(ZoneInfo(tz))
        prof = {
            "name": "Prashna",
            "date": now.date().isoformat(),
            "time": now.strftime("%H:%M"),
            "place": place_label, "lat": lat, "lon": lon, "tz": tz,
        }
        dossier = generate_astrology_dossier(prof)
        try:
            verdict = get_prashna_python_verdict(req.question, dossier)
        except Exception:
            verdict = "UNCLEAR"
        ctx = _rag(req.question, ("kp6.md",), 8)
        prompt = build_prashna_prompt(req.question, dossier, knowledge_context=ctx)
        return PrashnaResponse(
            verdict=str(verdict),
            reading=generate_content_with_fallback(prompt, task="agent"),
        )
