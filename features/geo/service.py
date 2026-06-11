"""features.geo.service — city autocomplete for onboarding (place -> lat/lon/tz).

Wraps the existing geocoder (`search_places`) and adds the IANA timezone per
result (offline TimezoneFinder), so the onboarding place picker gets everything
it needs in one call and the chart can be computed without a second round-trip.
"""
from __future__ import annotations


def search(query: str, limit: int = 5) -> list[dict]:
    from shared.astro.astro_calc import search_places, timezone_for_latlon

    results = search_places(query, limit)
    for r in results:
        try:
            r["tz"] = timezone_for_latlon(r["lat"], r["lon"])
        except Exception:
            r["tz"] = None
    return results
