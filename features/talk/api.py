"""features.talk.api — the voice companion endpoint. Mounted at /talk.

    POST /talk  { text, lang('en'|'hi'), profile?, history?, memory_context? }
                -> { reply_text, audio_b64|null, lang }

Flow: the app transcribes speech ON DEVICE (free), posts the text here, gets a
short warm reply (and audio if a Kokoro service is wired), and plays it. Public
(no JWT) so it works like /consultation/ask; pass memory_context from
GET /memory/context to make the Moon remember.
"""
from __future__ import annotations

import base64

from features.talk import service
from features.talk.schemas import TalkIn, TalkOut

try:
    from fastapi import APIRouter
    router = APIRouter()
except ImportError:  # pragma: no cover
    router = None


if router is not None:

    @router.post("", response_model=TalkOut)
    def talk(req: TalkIn) -> TalkOut:
        lang = req.lang if req.lang in ("en", "hi") else "en"
        reply_text = service.reply(
            req.text, lang, req.profile, req.history, req.memory_context
        )
        audio_b64 = None
        audio = service.synthesize(reply_text, lang)
        if audio:
            audio_b64 = base64.b64encode(audio).decode("ascii")
        return TalkOut(reply_text=reply_text, audio_b64=audio_b64, lang=lang)
