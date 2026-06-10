"""features.wallet.api — Diya wallet + the price book.

  GET  /wallet/prices    PUBLIC — the full price book (so the app shows costs)
  GET  /wallet/balance   JWT — balance + lifetime + is_plus
  POST /wallet/spend     JWT — debit for a feature (price from the server)
  POST /wallet/earn      JWT — credit for an action (capped server-side)
  GET  /wallet/history   JWT — the signed ledger
"""
from features.wallet import prices, service
from features.wallet.schemas import EarnIn, SpendIn
from features.me.auth import CurrentUser, get_current_user

try:
    from fastapi import APIRouter, Depends
    router = APIRouter()
except ImportError:  # pragma: no cover
    router = None


if router is not None:

    @router.get("/prices")
    def get_prices() -> dict:
        """Public price book — the single source of truth for the UI."""
        return {
            "prices": prices.PRICES,
            "plus_free": sorted(prices.PLUS_FREE),
            "plus_discount": prices.PLUS_DISCOUNT,
            "free_allowance": prices.FREE_ALLOWANCE,
            "earn": prices.EARN,
            "daily_earn_cap": prices.DAILY_EARN_CAP,
            "bundles": prices.BUNDLES,
            "subscription": prices.SUBSCRIPTION,
        }

    @router.get("/balance")
    def get_balance(user: CurrentUser = Depends(get_current_user)) -> dict:
        return service.balance(user.user_id)

    @router.post("/spend")
    def spend(payload: SpendIn, user: CurrentUser = Depends(get_current_user)) -> dict:
        return service.spend(user.user_id, payload.feature, payload.qty, payload.ref)

    @router.post("/earn")
    def earn(payload: EarnIn, user: CurrentUser = Depends(get_current_user)) -> dict:
        return service.earn(user.user_id, payload.source, payload.ref)

    @router.get("/history")
    def history(user: CurrentUser = Depends(get_current_user)) -> dict:
        return {"transactions": service.history(user.user_id)}
