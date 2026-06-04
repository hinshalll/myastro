"""features.companion.api — FastAPI router for the Companion's payoffs.

Mounted at /companion in fastapi_main.py.

    POST /companion/micro-insight   the Day-1 mirror (stateless, no AI)
    GET  /companion/patterns        the Pattern Engine (JWT required)
    POST /companion/proof           "Why did that happen?" (stateless, no AI)

`/patterns` reuses the same Supabase JWT auth as /me (features.me.auth).
"""
from __future__ import annotations

from features.companion import service
from features.companion.schemas import MicroInsightRequest, ProofRequest
from features.me.auth import CurrentUser, get_current_user

try:
    from fastapi import APIRouter, Depends
    router = APIRouter()
except ImportError:  # pragma: no cover
    router = None


if router is not None:

    @router.post("/micro-insight")
    def micro_insight(req: MicroInsightRequest) -> dict:
        """The Day-1 "mirror": reads today's check-in against today's REAL Moon
        transit and says whether the felt mood runs WITH the sky or against it.

        FREE: pure math + lookup, NO AI. Makes the app feel personal from the very
        first check-in — no history needed. Same { profile } shape as
        /kundli/compute; check-in fields use the app's vocab (mood, energy,
        clarity); optional "date" (defaults to today). Returns { line, match
        (aligned/crosscurrent/neutral), why, sanskrit, ... }.
        """
        return service.micro_insight(
            req.profile, req.mood, req.energy, req.clarity, req.date
        )

    @router.get("/patterns")
    def patterns(user: CurrentUser = Depends(get_current_user)) -> dict:
        """The Pattern Engine: plain STATISTICAL correlations between your logged
        check-ins and each day's planetary state (NO ML, NO AI).

        JWT required. Reads your check-ins + 'self' birth profile, recomputes each
        day's Moon state, and contrasts your self-reports against the sky. Below
        the bar (30 check-ins) → { unlocked:false, progress:{have,need}, message }.
        At/above it → { unlocked:true, patterns:[{ pattern_text, kind, confidence,
        why, evidence }] } (newly-unlocked kinds are also stored). Every insight is
        a plain count over your own data, framed as gentle guidance.
        """
        return service.compute_patterns(user)

    @router.post("/proof")
    def proof(req: ProofRequest) -> dict:
        """"Why did that happen?": given a PAST date, the Vimshottari dasha chapter
        (Mahadasha/Antardasha) + the slow, era-defining transits (Saturn, Jupiter,
        the nodes over the birth Moon) that were running then.

        FREE: pure math + a pre-baked classical lookup, NO AI. The trust-builder —
        test the system against your own past. Same { profile } shape as
        /kundli/compute (birth time → precise; unknown time → a midday estimate +
        a plain precision note); "date" is the past day; optional "event" is your
        own words for what happened (echoed back). Returns { headline, story,
        running, transits, why, sanskrit, precision_note }.
        """
        return service.proof(req.profile, req.date, req.event)
