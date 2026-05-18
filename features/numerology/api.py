"""features.numerology.api — FastAPI router."""

from features.numerology.service import (
    calculate_numerology_core, get_personal_year, get_personal_month,
    get_personal_day, get_pinnacle_cycles,
)
from features.numerology.prompts import build_full_report_prompt, build_cycles_prompt
from features.numerology.schemas import (
    FullReportRequest, FullReportResponse, CyclesRequest, CyclesResponse,
)

try:
    from fastapi import APIRouter
    router = APIRouter()
except ImportError:
    router = None


def _generate(prompt: str) -> str:
    from shared.ai.gemini_client import generate_content_with_fallback
    return generate_content_with_fallback(prompt, knowledge_files=None)


def _rag(query: str, books: tuple, k: int) -> str:
    from shared.ai.knowledge import rag_context
    try:
        return rag_context(query, list(books), k=k)
    except Exception:
        return ""


if router is not None:

    @router.post("/full-report", response_model=FullReportResponse)
    def full_report(req: FullReportRequest) -> FullReportResponse:
        lp, dest, soul, pers = calculate_numerology_core(req.name, req.dob, req.system)

        dossier = None
        if req.profile:
            from shared.astro.dossier_builder import generate_astrology_dossier
            dossier = generate_astrology_dossier(req.profile, req.include_d60)

        books = ("inum1.md",) if "Vedic" in req.system else ("wnum.md",)
        ctx = _rag(
            f"life path {lp} destiny {dest} soul urge {soul} personality {pers} numerology meaning",
            books, k=10,
        )
        prompt = build_full_report_prompt(
            req.name, req.dob, lp, dest, soul, pers,
            dossier, req.question, req.system, knowledge_context=ctx,
        )
        return FullReportResponse(
            life_path=lp, destiny=dest, soul_urge=soul, personality=pers,
            reading=_generate(prompt),
        )

    @router.post("/cycles", response_model=CyclesResponse)
    def cycles(req: CyclesRequest) -> CyclesResponse:
        lp, _, _, _ = calculate_numerology_core(req.name, req.dob, req.system)
        py = get_personal_year(req.dob)
        pm = get_personal_month(req.dob)
        pd_ = get_personal_day(req.dob)
        pinnacles = list(get_pinnacle_cycles(req.dob))
        prompt = build_cycles_prompt(req.name, req.dob, lp, py, pm, pd_, pinnacles, system=req.system)
        books = ("inum1.md",) if "Vedic" in req.system else ("wnum.md",)
        ctx = _rag(
            "personal year pinnacle challenge cycle numerology life path meaning",
            books, k=8,
        )
        if ctx:
            prompt = (
                f"<KNOWLEDGE_CONTEXT>\n{ctx}\n</KNOWLEDGE_CONTEXT>\n"
                "<RULES>Use only the numerology passages above for cycle/pinnacle/challenge "
                "doctrine. Do not invent meanings outside them.</RULES>\n\n"
                + prompt
            )
        return CyclesResponse(
            life_path=lp, personal_year=py, personal_month=pm, personal_day=pd_,
            pinnacles=[list(p) for p in pinnacles],
            reading=_generate(prompt),
        )
