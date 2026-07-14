"""features.capsule.schemas — Time Capsule (Today → Plan) I/O."""

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object  # type: ignore


class CapsuleSuggestRequest(BaseModel):
    profile: dict                    # to compute the 3 suggested delivery moments
    today: str | None = None         # "YYYY-MM-DD"; defaults to today (server)


class CapsuleCreate(BaseModel):
    note: str                        # the message to the future self
    occasion: str = "custom"         # 'custom' | 'birthday' | 'dasha' | 'jupiter'
    deliver_on: str | None = None    # required when occasion == 'custom'
    profile: dict | None = None      # required for birthday / dasha / jupiter
    today: str | None = None         # "YYYY-MM-DD"; for resolving computed moments
