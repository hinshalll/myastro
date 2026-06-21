"""voice/kokoro_service.py — tiny self-hosted Kokoro TTS service (CPU only).

Run this SEPARATELY from the main API (it pulls heavy ML deps you do not want in
the main app image). The main `/talk` endpoint calls it over HTTP via KOKORO_URL.

  POST /tts  { text, lang('en'|'hi'), voice? }  ->  audio/wav

Setup (on a small CPU box, e.g. a $5 VPS or a separate Render service):
    pip install kokoro soundfile numpy fastapi "uvicorn[standard]"
    # Kokoro also needs espeak-ng on the system:  apt-get install -y espeak-ng
Run:
    uvicorn voice.kokoro_service:app --host 0.0.0.0 --port 8080
Then set KOKORO_URL=http://<that-host>:8080 on the main API.

NOTE (verify on first deploy): Kokoro language codes are 'a' = American English,
'h' = Hindi. Hindi expects DEVANAGARI text. Voice names below are sensible warm
defaults; list the installed voices and pick the warmest, then set
KOKORO_VOICE_EN / KOKORO_VOICE_HI on the main API to override.
"""
from __future__ import annotations

from io import BytesIO

try:
    from fastapi import FastAPI, Response
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    FastAPI = None  # type: ignore

# One Kokoro pipeline per language, created lazily on first use.
_PIPELINES: dict[str, object] = {}
_LANG_CODE = {"en": "a", "hi": "h"}                       # Kokoro lang codes
_DEFAULT_VOICE = {"en": "af_heart", "hi": "hf_alpha"}     # warm defaults; tune on deploy
_SAMPLE_RATE = 24000


def _pipeline(lang: str):
    code = _LANG_CODE.get(lang, "a")
    if code not in _PIPELINES:
        from kokoro import KPipeline
        _PIPELINES[code] = KPipeline(lang_code=code)
    return _PIPELINES[code]


def synthesize_wav(text: str, lang: str = "en", voice: str | None = None) -> bytes:
    import numpy as np
    import soundfile as sf

    pipe = _pipeline(lang)
    v = voice or _DEFAULT_VOICE.get(lang, "af_heart")
    chunks = []
    for _gs, _ps, audio in pipe(text, voice=v):          # Kokoro yields (graphemes, phonemes, audio)
        chunks.append(audio)
    data = np.concatenate(chunks) if chunks else np.zeros(1, dtype="float32")
    buf = BytesIO()
    sf.write(buf, data, _SAMPLE_RATE, format="WAV")
    buf.seek(0)
    return buf.read()


if FastAPI is not None:
    app = FastAPI(title="Kokoro TTS", version="1.0.0")

    class TtsIn(BaseModel):
        text: str
        lang: str = "en"
        voice: str | None = None

    @app.get("/")
    def health() -> dict:
        return {"ok": True, "service": "kokoro-tts"}

    @app.post("/tts")
    def tts(req: TtsIn):
        wav = synthesize_wav(req.text, req.lang if req.lang in _LANG_CODE else "en", req.voice)
        return Response(content=wav, media_type="audio/wav")
