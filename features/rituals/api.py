"""features.rituals.api — FastAPI router for the Rituals tab.

  POST /remedies   Chart-derived remedies (pure math, no AI):
                   priority planets + free practices + optional gemstone tiers.
"""

from features.rituals.schemas import RemediesRequest

try:
    from fastapi import APIRouter
    router = APIRouter()
except ImportError:  # pragma: no cover
    router = None


if router is not None:

    @router.post("/remedies")
    def remedies(req: RemediesRequest) -> dict:
        from features.rituals.service import build_remedies
        return build_remedies(req.profile)
