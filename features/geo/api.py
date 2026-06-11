"""features.geo.api — place picker for onboarding (PUBLIC, no auth).

  POST /geo/search  { query, limit? } -> { results: [{ label, lat, lon, tz }] }

The app calls this as the user types a birth place; on selection it stores
{ label, lat, lon, tz } and sends those to /me/profiles (the chart needs them).
"""
from features.geo.schemas import GeoSearchIn

try:
    from fastapi import APIRouter
    router = APIRouter()
except ImportError:  # pragma: no cover
    router = None


if router is not None:

    @router.post("/search")
    def search(req: GeoSearchIn) -> dict:
        from features.geo.service import search as do_search
        return {"results": do_search(req.query, req.limit)}
