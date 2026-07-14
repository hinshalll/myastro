"""shared.ai.understanding — AI-first "read the user's words" layer.

Turns free-text (English / Hindi / Hinglish / mixed) into a small STRUCTURED label
that the deterministic engine consumes. The AI classifies ONLY; it never predicts,
answers, or does astrology. Every function degrades GRACEFULLY to a keyword/heuristic
fallback when no API key is set or the AI errors, so the features work offline too
(just less robustly on unusual phrasing / other languages).

Cost: tiny prompts, small JSON out, low-frequency actions → negligible. Uses the
`json` ladder (free Gemini primary → cheap DeepSeek overflow); models live in
shared/ai/config.py TASK_LADDERS (never hardcode).
"""

import json
import re

from shared.ai import understanding_prompts as P

_VALID_MUHURTA = (
    "marriage", "travel", "vehicle", "property", "housewarming", "surgery",
    "medical", "education", "job", "signing", "naming", "mundan",
    "annaprashana", "general",
)
_HORA_PLANETS = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}
_TASK = "json"   # free Gemini primary → DeepSeek overflow; good at JSON + Hinglish


def _ai(prompt: str) -> str:
    """One classifier call. Returns '' on any failure (no key, quota, error)."""
    try:
        from shared.ai.gemini_client import generate_content_with_fallback
        return (generate_content_with_fallback(prompt, task=_TASK) or "").strip()
    except Exception:
        return ""


def _json(raw: str) -> dict | None:
    """Pull the first JSON object out of a model reply, defensively."""
    if not raw:
        return None
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


# ── Ask the Moment (Prashna) ────────────────────────────────────────────────
def _keyword_house(text: str) -> int:
    """Offline fallback: map a question to a house by keywords (verified groups).
    Used ONLY when the AI is unavailable."""
    t = (text or "").lower()
    pairs = [
        (("promotion", "appraisal", "career growth", "own business", "profession"), 10),
        (("job", "naukri", "employ", "interview", "service", "hired", "hiring"), 6),
        (("marry", "married", "marriage", "shaadi", "shadi", "spouse", "wedding",
          "life partner", "engagement"), 7),
        (("child", "kid", "baby", "pregnan", "conceive", "santaan"), 5),
        (("loan", "debt", "litigation", "court", "lawsuit", "case", "enemy",
          "disease", "illness", "sick", "recover from"), 6),
        (("surgery", "operation", "life risk", "critical"), 8),
        (("savings", "enough money", "in hand"), 2),
        (("money", "wealth", "gain", "profit", "income", "earn", "recover money",
          "paisa", "kamai"), 11),
        (("house", "property", "land", "plot", "flat", "vehicle", "car", "makaan"), 4),
        (("abroad", "foreign", "visa", "settle"), 12),
        (("travel", "trip", "journey", "yatra"), 9),
        (("study", "studies", "exam", "education", "course", "degree", "padhai"), 5),
        (("spiritual", "moksha", "guru", "dharma"), 9),
    ]
    for kws, h in pairs:
        if any(k in t for k in kws):
            return h
    return 1


def read_prashna_question(text: str) -> dict:
    """Question -> {house 1-12, topic, interpreted (positive event phrasing), via}.
    AI-first; keyword fallback offline. Classifies only — the engine answers."""
    text = (text or "").strip()
    if not text:
        return {"house": 1, "topic": "general",
                "interpreted": "will this go well?", "via": "empty"}
    obj = _json(_ai(P.PRASHNA_HOUSE_PROMPT + f'\nQuestion: "{text}"'))
    if obj is not None:
        try:
            h = int(obj.get("house"))
            if 1 <= h <= 12:
                return {
                    "house": h,
                    "topic": str(obj.get("topic", ""))[:40],
                    "interpreted": (str(obj.get("interpreted", "")).strip() or text)[:180],
                    "via": "ai",
                }
        except (TypeError, ValueError):
            pass
    return {"house": _keyword_house(text), "topic": "", "interpreted": text, "via": "fallback"}


# ── Muhurat ─────────────────────────────────────────────────────────────────
def classify_muhurta_event(text: str, keyword_fallback) -> dict:
    """Activity -> {event, via}. AI-first; `keyword_fallback(text)->category` runs
    offline. Result is always one of the valid categories."""
    text = (text or "").strip()
    if not text:
        return {"event": "general", "via": "empty"}
    raw = _ai(P.MUHURTA_EVENT_PROMPT + f'"{text}"').lower()
    for c in _VALID_MUHURTA:
        if c in raw:
            return {"event": c, "via": "ai"}
    try:
        return {"event": keyword_fallback(text), "via": "fallback"}
    except Exception:
        return {"event": "general", "via": "fallback"}


# ── My Day ──────────────────────────────────────────────────────────────────
def read_day_task(text: str, default_importance: str = "normal") -> dict:
    """To-do -> {importance, hora:[planets], nature, via}. AI-first; heuristic
    fallback offline. Classifies only — the engine places the task."""
    text = (text or "").strip()
    if not text:
        return {"importance": default_importance, "hora": [], "nature": "", "via": "empty"}
    obj = _json(_ai(P.DAY_TASK_PROMPT + f'"{text}"'))
    if obj is not None:
        imp = str(obj.get("importance", "")).lower()
        imp = imp if imp in ("important", "normal") else default_importance
        hora = [p for p in obj.get("hora", []) if p in _HORA_PLANETS] \
            if isinstance(obj.get("hora"), list) else []
        return {"importance": imp, "hora": hora[:3],
                "nature": str(obj.get("nature", ""))[:40], "via": "ai"}
    return {"importance": default_importance, "hora": [], "nature": "", "via": "fallback"}
