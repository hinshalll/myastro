"""features.talk.service — the Moon's spoken reply + optional Kokoro TTS.

The app does speech-to-text ON DEVICE (free) and plays the returned audio (or
does TTS on-device too). This layer only does the cheap LLM reply and, if a
self-hosted Kokoro service is configured (KOKORO_URL), the synthesis.

Voice rule: keep each turn in ONE script. 'en' replies in English; 'hi' replies
in natural conversational Hindi in Devanagari (Kokoro's Hindi voice needs
Devanagari to pronounce it correctly). Replies are SHORT because they're heard.
"""
from __future__ import annotations

import os
import re

_LANG_NAME = {"en": "English", "hi": "natural conversational Hindi (in Devanagari script)"}

_VOICE_SYSTEM = (
    "You are the Moon, a warm, gentle astrologer-companion. The user is SPEAKING "
    "to you out loud and will HEAR your reply as a voice, so it must sound like a "
    "caring friend talking, not like writing. Keep it SHORT: one to three short "
    "sentences. Warm, calm, personal. No lists, no markdown, no headings, no stage "
    "directions, no emojis. Never invent astrology; if unsure, be gently honest. "
    "Reply ONLY in {lang}."
)


def _clean_for_speech(s: str) -> str:
    s = re.sub(r"[*_#`>\[\]]", "", s or "")            # strip markdown
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _fallback(lang: str) -> str:
    return ("I'm here with you. Say that again in a moment." if lang == "en"
            else "मैं यहीं हूँ, तुम्हारे साथ। थोड़ी देर में फिर से कहना।")


def _to_english(text: str) -> str:
    """Translate a non-English utterance to English for RAG retrieval (the books +
    embedder are English-only). Cheap; returns the original on failure."""
    try:
        from shared.ai.gemini_client import generate_content_with_fallback
        t = generate_content_with_fallback(
            "Translate to English. Output ONLY the translation, nothing else:\n" + str(text),
            task="micro",
        )
        return _clean_for_speech(t) or text
    except Exception:
        return text


def reply(text, lang="en", profile=None, history=None, memory_context=None) -> str:
    """One short, warm, spoken reply, GROUNDED in the classical texts (RAG) so the
    Moon never invents astrology. Hindi turns translate-first so retrieval still
    hits the English books. Cheap; never raises."""
    lang = lang if lang in _LANG_NAME else "en"
    try:
        from shared.ai.gemini_client import generate_content_with_fallback

        # 1. Retrieval query in English (books + embedder are English-only).
        retrieval_text = text if lang == "en" else _to_english(text)

        # 2. RAG grounding — the books are the source of truth (AIs hallucinate astrology).
        ctx = ""
        try:
            from features.consultation.prompts import classify_intent
            from features.consultation.service import INTENT_RAG_BOOKS
            from shared.ai.knowledge import rag_context
            intent = classify_intent(retrieval_text)
            books = INTENT_RAG_BOOKS.get(intent, INTENT_RAG_BOOKS["GENERAL"])
            ctx = rag_context(retrieval_text, list(books), k=6)
        except Exception:
            ctx = ""

        # 3. Their chart
        dossier = ""
        try:
            if profile:
                from shared.astro.dossier_builder import generate_astrology_dossier
                dossier = generate_astrology_dossier(profile, compact=True)
        except Exception:
            dossier = ""

        hist = ""
        if history:
            tail = history[-4:]
            hist = "\n".join(f"{m.get('role', 'user')}: {m.get('text', '')}" for m in tail)

        sys = _VOICE_SYSTEM.format(lang=_LANG_NAME[lang])
        parts = [sys, ""]
        if ctx:
            parts.append("Grounding from the classical texts (rely on this; do NOT invent "
                         "astrology beyond it):\n" + ctx)
        if dossier:
            parts.append("Their chart, briefly:\n" + dossier)
        if memory_context:
            parts.append("What you remember about them:\n" + memory_context)
        if hist:
            parts.append("Recent talk:\n" + hist)
        parts.append("They just said, out loud: " + str(text))
        parts.append("Your short spoken reply in " + _LANG_NAME[lang]
                     + ", grounded in the texts above:")
        prompt = "\n\n".join(parts)

        out = _clean_for_speech(generate_content_with_fallback(prompt, task="chat") or "")
        return out or _fallback(lang)
    except Exception:
        return _fallback(lang)


def synthesize(text: str, lang: str = "en") -> bytes | None:
    """Optional server-side TTS via a self-hosted Kokoro service (KOKORO_URL).
    Returns WAV bytes, or None if not configured / on failure (then the app does
    TTS on-device, or just shows the text). Never raises."""
    url = os.environ.get("KOKORO_URL")
    if not url or not text:
        return None
    try:
        import requests
        voice = os.environ.get(f"KOKORO_VOICE_{lang.upper()}", "")
        r = requests.post(
            url.rstrip("/") + "/tts",
            json={"text": text, "lang": lang, "voice": voice},
            timeout=20,
        )
        return r.content if r.status_code == 200 else None
    except Exception:
        return None
