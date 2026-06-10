"""features.wallet.service — server-authoritative Diya wallet.

Rules that make this safe:
  • The price ALWAYS comes from prices.py, never from the request.
  • All mutations use the SERVICE client + the atomic apply_coin_delta SQL
    function, so a client can never mint Diyas or overdraw.
  • The Plus discount is applied server-side from the subscriptions table.
"""
from __future__ import annotations

from shared.db import supabase_client as db
from features.wallet import prices


def balance(user_id: str) -> dict:
    svc = db.get_service_client()
    w = db.get_wallet(svc, user_id)
    return {
        "balance": w.get("balance", 0),
        "lifetime_earned": w.get("lifetime_earned", 0),
        "lifetime_spent": w.get("lifetime_spent", 0),
        "is_plus": db.is_plus_member(svc, user_id),
    }


def spend(user_id: str, feature: str, qty: int = 1, ref=None) -> dict:
    svc = db.get_service_client()
    is_plus = db.is_plus_member(svc, user_id)
    try:
        unit = prices.price_for(feature, is_plus)
    except KeyError:
        return {"ok": False, "error": "unknown_feature", "feature": feature}

    cost = unit * max(1, int(qty))
    if cost == 0:                                  # free for Plus (e.g. cross-ref)
        w = db.get_wallet(svc, user_id)
        return {"ok": True, "charged": 0, "balance": w.get("balance", 0), "feature": feature}

    new_balance = db.apply_coin_delta(
        svc, user_id, -cost, "spent", ref or feature,
        {"feature": feature, "qty": qty, "is_plus": is_plus},
    )
    if new_balance is None:
        cur = db.get_wallet(svc, user_id).get("balance", 0)
        return {"ok": False, "error": "insufficient_diyas",
                "needed": cost, "balance": cur, "feature": feature}
    return {"ok": True, "charged": cost, "balance": new_balance, "feature": feature}


def earn(user_id: str, source: str, ref=None) -> dict:
    svc = db.get_service_client()
    amount = prices.earn_for(source)
    if amount <= 0:
        return {"ok": False, "error": "unknown_source", "source": source}

    # Stingy: routine activity is capped per day; milestones/referrals are exempt.
    if source not in prices.EARN_CAP_EXEMPT:
        room = max(0, prices.DAILY_EARN_CAP - db.earned_today(svc, user_id))
        amount = min(amount, room)
        if amount <= 0:
            w = db.get_wallet(svc, user_id)
            return {"ok": True, "credited": 0, "capped": True, "balance": w.get("balance", 0)}

    new_balance = db.apply_coin_delta(
        svc, user_id, amount, f"earned_{source}", ref or source, {"source": source},
    )
    return {"ok": True, "credited": amount, "balance": new_balance}


def history(user_id: str, limit: int = 50) -> list[dict]:
    return db.list_coin_transactions(db.get_service_client(), user_id, limit)
