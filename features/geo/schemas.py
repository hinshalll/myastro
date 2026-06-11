"""features.geo.schemas — request model for the place picker."""

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    BaseModel = object  # type: ignore


class GeoSearchIn(BaseModel):
    query: str
    limit: int = 5
