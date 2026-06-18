"""features.memory.api — THE MEMORY endpoints (JWT). Mounted at /memory.

    GET    /memory/facts          list the user's remembered facts (they own these)
    PUT    /memory/facts/{id}     edit a fact (fact / category / salience / status)
    DELETE /memory/facts/{id}     forget a fact
    POST   /memory/extract        distil durable facts from text (call after a chat)
    GET    /memory/context        the compact recall block (pass to /consultation/ask)

Chat is ephemeral; the companion "remembers" only via the distilled facts here.
"""
from __future__ import annotations

from features.memory import service
from features.memory.schemas import ExtractIn, FactEditIn
from features.me.auth import CurrentUser, get_current_user

try:
    from fastapi import APIRouter, Depends, HTTPException
    router = APIRouter()
except ImportError:  # pragma: no cover
    router = None


if router is not None:

    @router.get("/facts")
    def list_facts(user: CurrentUser = Depends(get_current_user)) -> dict:
        return {"facts": service.list_facts(user)}

    @router.put("/facts/{fact_id}")
    def edit_fact(
        fact_id: str, payload: FactEditIn,
        user: CurrentUser = Depends(get_current_user),
    ) -> dict:
        row = service.edit_fact(user, fact_id, payload.model_dump(exclude_none=True))
        if row is None:
            raise HTTPException(status_code=400,
                                detail="No editable fields, or fact not found")
        return row

    @router.delete("/facts/{fact_id}")
    def delete_fact(
        fact_id: str, user: CurrentUser = Depends(get_current_user)
    ) -> dict:
        service.delete_fact(user, fact_id)
        return {"ok": True}

    @router.post("/extract")
    def extract(
        payload: ExtractIn, user: CurrentUser = Depends(get_current_user)
    ) -> dict:
        """Distil durable facts from `text` into the user's long-term memory.
        Call this at the end of a chat session (text = the user's turns)."""
        return service.extract_and_save(user.user_id, payload.text, payload.source)

    @router.get("/context")
    def context(user: CurrentUser = Depends(get_current_user)) -> dict:
        """The compact 'what you remember about this person' block. Pass its
        `text` to /consultation/ask as `memory_context`, or use to personalize."""
        return service.build_memory_context(user)

    @router.get("/today")
    def today(
        date: str | None = None,
        user: CurrentUser = Depends(get_current_user),
    ) -> dict:
        """The Memory feeding the forecast: a deterministic personal heads-up when
        today's sky triggers one of the user's own patterns, + recent mood trend.
        The app merges `personal_note` with /dashboard/forecast. No AI."""
        return service.personalize_today(user, date)
