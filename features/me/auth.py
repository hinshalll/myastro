"""features.me.auth — verify a Supabase JWT and resolve the current user.

The mobile app signs the user in client-side (Supabase Auth) and sends the
resulting JWT as `Authorization: Bearer <token>`. This dependency verifies that
token against Supabase and hands the route a `CurrentUser` whose `.client` is a
user-scoped Supabase client (RLS enforces ownership on every query).

Reusable: any future feature router that needs an authenticated user can
`from features.me.auth import get_current_user`.
"""
from __future__ import annotations

from shared.db.supabase_client import get_user_client, get_user_id_from_token

try:
    from fastapi import Header, HTTPException
except ImportError:  # pragma: no cover - backend-only dependency
    Header = None  # type: ignore
    HTTPException = Exception  # type: ignore


class CurrentUser:
    """The authenticated user + a lazily-built, RLS-scoped Supabase client."""

    def __init__(self, user_id: str, token: str):
        self.user_id = user_id
        self.token = token
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = get_user_client(self.token)
        return self._client


def get_current_user(authorization: str = Header(default=None)) -> CurrentUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    token = authorization.split(" ", 1)[1].strip()
    user_id = get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return CurrentUser(user_id=user_id, token=token)
