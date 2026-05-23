"""shared/ai/config.py — THE ONE FILE to change AI models.

============================================================================
HOW TO USE (for non-coders):
============================================================================
1. To switch ANY task to a different model, just change the model-name string
   in the MODELS dict below. Examples:
       "gemini-3.1-flash-lite-preview"   -> runs on Gemini
       "deepseek-v4-flash"               -> runs on DeepSeek
       "deepseek-chat"                   -> runs on DeepSeek
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

# ── 1. Which model each kind of task uses ───────────────────────────────────
#    Change the string on the right. That's it.
MODELS: dict[str, str] = {
    "default": "gemini-3.1-flash-lite-preview",  # general text readings (tarot, numerology, horoscopes, dashboard...)
    "chat":    "gemini-3.1-flash-lite-preview",  # consultation room (streaming chat)
    "json":    "gemini-3.1-flash-lite-preview",  # structured JSON output (kundli content)
    "agent":   "gemini-3.1-flash-lite-preview",  # oracle parallel expert agents
    "vision":  "gemini-3.1-flash-lite-preview",  # palm + face image reading
}

# ── 2. Fallback ladder — tried in order if the chosen model is busy / over quota
#    You can mix providers here too. If a DeepSeek model is listed but no
#    DeepSeek key is set, it's skipped automatically and the next one is tried.
FALLBACK_CHAIN: list[str] = [
    "gemini-3.1-flash-lite-preview",  # PRIMARY  (1M context)
    "gemini-2.5-flash",               # fallback
    "gemma-4-31b-it",                 # last resort (unlimited TPM)
    "gemma-4-26b-a4b-it",             # final fallback
]

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
    """Return the configured model name for a task type (falls back to 'default')."""
    return MODELS.get(task, MODELS["default"])


# ── 4. API key registry (provider-neutral, no Streamlit import — purity rule) ─
#    The app layer calls set_api_key(...) once at startup; adapters read it.
_API_KEYS: dict[str, str] = {}


def set_api_key(provider: str, key: str | None) -> None:
    if key:
        _API_KEYS[provider] = key


def get_api_key(provider: str) -> str | None:
    return _API_KEYS.get(provider)
