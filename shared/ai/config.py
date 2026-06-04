"""shared/ai/config.py — THE ONE FILE to change AI models.

============================================================================
HOW TO USE (for non-coders):
============================================================================
1. To switch ANY task to a different model, edit its LADDER in TASK_LADDERS
   below. The first name is the primary; the rest are fallbacks tried in order
   only when the one above runs out of free quota. Examples of model names:
       "gemini-3.1-flash-lite"           -> runs on Gemini
       "deepseek-v4-flash"               -> runs on DeepSeek
       "gemma-4-31b-it"                  -> runs on Gemma (free, lighter)
   The provider is auto-detected from the name. You never touch any other file.

2. When a NEW model comes out in the future, just type its name here. As long
   as the name starts with "gemini"/"gemma" (Google) or "deepseek" (DeepSeek),
   it routes automatically. No code changes needed.

3. Each TASK TYPE has its own model, so you can experiment freely — e.g. put
   chat on DeepSeek (cheap) but keep vision on Gemini, or try DeepSeek on
   vision to compare. Mix and match.

4. API keys are read by the app layer (Streamlit / FastAPI) from env vars or
   .streamlit/secrets.toml and handed to init_gemini() / init_deepseek().
   Add DEEPSEEK_API_KEY next to GEMINI_API_KEY in your secrets — done.
============================================================================
"""

import time as _time

# ── 1. Per-task model LADDERS (the one place you tune the brain) ─────────────
#    Each task has an ORDERED ladder. We always try the 1st model; only if it is
#    out of free quota (HTTP 429 / "RESOURCE_EXHAUSTED") do we fall to the next,
#    and so on. The LAST rung is always DeepSeek — paid, but it never runs dry,
#    so the app can never go fully down.
#
#    THE MODELS WE USE (chosen for their RPM + RPD free-tier limits):
#      • gemini-3.1-flash-lite   — smartest free model (intelligence tier)
#      • gemma-4-31b-it          — free, capable (less-dumb readings tier)
#      • gemma-4-26b-a4b-it      — free, lightest, highest limits (micro tier)
#      • gemma-4-31b-it          — also serves as the free VISION fallback
#      • gemini-2.5-flash        — VISION-only middle fallback (no other use)
#      • deepseek-v4-flash       — PAID net, never runs dry (last rung on text)
#
#    THREE-TIER RULE by how much intelligence a task needs:
#      • INTELLIGENCE  → gemini-3.1-flash-lite → deepseek.  (NO Gemma — quality.)
#      • LESS-DUMB     → gemma-4-31b-it → deepseek.         (readings: tarot etc.)
#      • DUMBEST/HIGH-VOLUME → gemma-4-26b-a4b-it → gemma-4-31b-it → deepseek.
#        (cheap tasks climb the FREE Gemma tiers before ever paying DeepSeek.)
#    Vision is special: DeepSeek can't see, so its ladder is all-free Gemini→Gemma.
TASK_LADDERS: dict[str, list[str]] = {
    # ── INTELLIGENCE (Gemini → DeepSeek; never Gemma) ──
    "chat":    ["gemini-3.1-flash-lite", "deepseek-v4-flash"],  # consultation room (streaming)
    "agent":   ["gemini-3.1-flash-lite", "deepseek-v4-flash"],  # oracle agents + deep readings/synthesis
    "json":    ["gemini-3.1-flash-lite", "deepseek-v4-flash"],  # structured JSON (kundli content/narrative)
    # ── LESS-DUMB readings (Gemma-31b → DeepSeek) ──
    "default": ["gemma-4-31b-it", "deepseek-v4-flash"],         # tarot, numerology, horoscope readings, gochara
    # ── DUMBEST / high-volume (climb free Gemmas → DeepSeek) ──
    "micro":   ["gemma-4-26b-a4b-it", "gemma-4-31b-it", "deepseek-v4-flash"],  # dashboard tiles, daily blurbs
    # ── VISION (palm/face). DeepSeek has no vision (HTTP 400 on images), so all free. ──
    "vision":  ["gemini-3.1-flash-lite", "gemini-2.5-flash", "gemma-4-31b-it"],
}

# Primary model per task (first rung) — kept as MODELS for backward-compat with
# everything that calls config.model_for(task).
MODELS: dict[str, str] = {task: ladder[0] for task, ladder in TASK_LADDERS.items()}

# Generic fallback tail used by callers that don't pass a task. Mirrors the
# "default" smart ladder (Gemini → Gemini → DeepSeek).
FALLBACK_CHAIN: list[str] = list(TASK_LADDERS["default"])

# ── 3. Provider detection (you usually never touch this) ────────────────────
#    Maps a model-name PREFIX to its provider. Add a prefix here only if a
#    brand-new provider appears.
_PROVIDER_PREFIXES: dict[str, str] = {
    "gemini":   "gemini",
    "gemma":    "gemini",
    "deepseek": "deepseek",
}

_DEFAULT_PROVIDER = "gemini"


def detect_provider(model_name: str | None) -> str:
    """Return the provider ('gemini' / 'deepseek') for a model name, by prefix."""
    name = (model_name or "").lower()
    for prefix, provider in _PROVIDER_PREFIXES.items():
        if name.startswith(prefix):
            return provider
    return _DEFAULT_PROVIDER


def model_for(task: str) -> str:
    """Return the configured PRIMARY model name for a task (falls back to 'default')."""
    return MODELS.get(task, MODELS["default"])


def ladder_for(task: str) -> list[str]:
    """Return the full ordered model ladder for a task (primary first, paid net
    last). Falls back to the 'default' smart ladder for unknown tasks."""
    return list(TASK_LADDERS.get(task, TASK_LADDERS["default"]))


# ── Circuit breaker: instant failover + automatic recovery ───────────────────
#    When a model returns a quota / rate error we "open the breaker" for it for
#    COOLDOWN_SECONDS. While open, callers skip it and go straight to the next
#    rung — instant, no wasted retry. After the cooldown we re-probe it once; the
#    moment Google's daily quota resets, that probe succeeds and we are back on
#    the free model automatically. Smaller COOLDOWN_SECONDS = faster return to
#    free Google (at the cost of slightly more probe attempts during an outage).
COOLDOWN_SECONDS: float = 180.0   # re-probe an exhausted Google model ~every 3 min
_cooldown_until: dict[str, float] = {}

_RATE_LIMIT_MARKERS = ("429", "quota", "resource_exhausted", "rate limit", "too many requests")


def is_rate_limit_error(err: str) -> bool:
    """True only for quota / rate-limit style errors (not token-overflow or other)."""
    e = (err or "").lower()
    return any(m in e for m in _RATE_LIMIT_MARKERS)


def note_failure(model_name: str, err: str = "") -> None:
    """Open the breaker for a model — but ONLY on a genuine quota / rate error."""
    if model_name and is_rate_limit_error(err):
        _cooldown_until[model_name] = _time.time() + COOLDOWN_SECONDS


def note_success(model_name: str) -> None:
    """Model answered — close its breaker so we return to it on the next call."""
    if model_name:
        _cooldown_until.pop(model_name, None)


def is_cooling(model_name: str) -> bool:
    """True while a model is still inside its cooldown window."""
    return _time.time() < _cooldown_until.get(model_name, 0.0)


def usable_models(models: list[str]) -> list[str]:
    """Filter a ladder down to models not currently cooling down. Never returns
    empty: if every rung is cooling, keep the LAST rung (the paid net) so a call
    still goes out."""
    if not models:
        return []
    live = [m for m in models if not is_cooling(m)]
    return live or [models[-1]]


# ── 4. API key registry (provider-neutral, no Streamlit import — purity rule) ─
#    The app layer calls set_api_key(...) once at startup; adapters read it.
_API_KEYS: dict[str, str] = {}


def set_api_key(provider: str, key: str | None) -> None:
    if key:
        _API_KEYS[provider] = key


def get_api_key(provider: str) -> str | None:
    return _API_KEYS.get(provider)
