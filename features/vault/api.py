"""features.vault.api — FastAPI router for the mobile app + website.

The Streamlit view stores profiles in browser localStorage. The mobile/web
versions store them per-user; this router exposes the CRUD endpoints.

Storage is intentionally pluggable — the implementation here uses an
in-process dict keyed by user_id. Swap for a real DB later.
"""

from features.vault.schemas import Profile, ProfileList

try:
    from fastapi import APIRouter, HTTPException
    router = APIRouter()
except ImportError:
    router = None


# Placeholder in-memory store — replace with real DB binding.
_STORE: dict[str, list[Profile]] = {}
_DEFAULT_IDX: dict[str, int] = {}


def _user_profiles(user_id: str) -> list[Profile]:
    return _STORE.setdefault(user_id, [])


if router is not None:

    @router.get("/{user_id}", response_model=ProfileList)
    def list_profiles(user_id: str) -> ProfileList:
        return ProfileList(
            profiles=_user_profiles(user_id),
            default_idx=_DEFAULT_IDX.get(user_id),
        )

    @router.post("/{user_id}", response_model=Profile)
    def add_profile(user_id: str, profile: Profile) -> Profile:
        _user_profiles(user_id).append(profile)
        return profile

    @router.put("/{user_id}/{idx}", response_model=Profile)
    def update_profile(user_id: str, idx: int, profile: Profile) -> Profile:
        profiles = _user_profiles(user_id)
        if not (0 <= idx < len(profiles)):
            raise HTTPException(status_code=404, detail="Profile not found")
        profiles[idx] = profile
        return profile

    @router.delete("/{user_id}/{idx}")
    def delete_profile(user_id: str, idx: int) -> dict:
        profiles = _user_profiles(user_id)
        if not (0 <= idx < len(profiles)):
            raise HTTPException(status_code=404, detail="Profile not found")
        profiles.pop(idx)
        return {"ok": True}

    @router.post("/{user_id}/default/{idx}")
    def set_default(user_id: str, idx: int) -> dict:
        _DEFAULT_IDX[user_id] = idx
        return {"ok": True}

    @router.delete("/{user_id}/default")
    def clear_default(user_id: str) -> dict:
        _DEFAULT_IDX.pop(user_id, None)
        return {"ok": True}
