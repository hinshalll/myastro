"""
api/routers/profiles.py — /api/v1/profiles/*
==============================================
Profile validation utility endpoints. Real CRUD (save / list / delete)
will hit Supabase once auth is wired in — for now these helpers just
geocode and validate birth data so the mobile/web client can show
correct location and timezone.
"""

from fastapi import APIRouter, HTTPException

from math_engine.astro_calc import geocode_place, timezone_for_latlon
from api.schemas import BirthProfile

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("/validate")
async def validate_profile(profile: BirthProfile):
    """Validate a birth profile. Returns the canonicalised version."""
    return {"valid": True, "profile": profile.dict()}


@router.get("/geocode")
async def geocode(place: str):
    """Look up lat/lon + display name for a place query string.

    Example: GET /api/v1/profiles/geocode?place=Mumbai,India
    """
    try:
        result = geocode_place(place)
        if not result:
            raise HTTPException(status_code=404, detail=f"Place not found: {place}")
        lat, lon, name = result
        tz = timezone_for_latlon(lat, lon)
        return {"lat": lat, "lon": lon, "name": name, "tz": tz}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
