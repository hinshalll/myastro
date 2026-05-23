"""shared.ai — provider-agnostic AI front door.

New code should import from here (not from a provider-named file):

    from shared.ai import generate_content_with_fallback, get_ai_model_by_name
    from shared.ai import MODELS, model_for          # the config knobs

To change which model any task uses, edit shared/ai/config.py — that's the
only file you touch. Provider (Gemini / DeepSeek) is auto-detected from the
model name, so switching is just typing a different model string.
"""

# config first (no internal deps) so the client modules can read it during import
from shared.ai import config
from shared.ai.config import (
    MODELS, FALLBACK_CHAIN, model_for, detect_provider, set_api_key, get_api_key,
)
from shared.ai.gemini_client import (
    FREE_MODELS,
    init_gemini,
    get_ai_model_by_name,
    get_ai_model_for_json,
    agent_worker,
    generate_content_with_fallback,
)
from shared.ai.deepseek_client import init_deepseek

__all__ = [
    "config", "MODELS", "FALLBACK_CHAIN", "model_for", "detect_provider",
    "set_api_key", "get_api_key", "FREE_MODELS",
    "init_gemini", "init_deepseek",
    "get_ai_model_by_name", "get_ai_model_for_json",
    "agent_worker", "generate_content_with_fallback",
]
