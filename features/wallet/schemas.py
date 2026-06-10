"""features.wallet.schemas — request models for the Diya wallet."""

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    BaseModel = object  # type: ignore


class SpendIn(BaseModel):
    feature: str                 # a key in prices.PRICES (server looks up the cost)
    qty: int = 1                 # e.g. number of chat messages
    ref: str | None = None       # optional context, e.g. which person's kundli


class EarnIn(BaseModel):
    source: str                  # a key in prices.EARN (checkin/ritual/streak_7/...)
    ref: str | None = None
