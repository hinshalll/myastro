"""shared.ai.gemini_client — Gemini SDK wrapper.

Uses the new `google-genai` package (pip: `google-genai`, import:
`from google import genai`). The old `google-generativeai` was deprecated.

Public API (unchanged after the SDK migration):
    FREE_MODELS                          — model id ladder (Flash Lite → Gemma fallbacks)
    init_gemini(api_key)                 — call ONCE at app startup
    get_ai_model_by_name(name, system_rules=None) -> _Model
        The returned object exposes .generate_content(contents, stream=False)
        for parity with how callers (consultation/view.py) iterate chunks.
    agent_worker(prompt, file_objs, model_id, custom_system_rules, retries)
    generate_content_with_fallback(prompt, knowledge_files, preferred_model)
        Universal model router with retry + cascade.
"""

import time as time_module

from google import genai
from google.genai import types


LIGHT_MODELS = [
    "gemini-3.1-flash-lite-preview",  # 500 RPD, 250K TPM, 1M context — PRIMARY
    "gemini-2.5-flash",               #  20 RPD, 250K TPM, 1M context — fallback
]

HEAVY_MODELS = [
    "gemma-4-31b-it",       # 1500 RPD, Unlimited TPM, 262K context — last resort
    "gemma-4-26b-a4b-it",   # 1500 RPD, Unlimited TPM, 262K context — final fallback
]

FREE_MODELS = LIGHT_MODELS + HEAVY_MODELS


_client: genai.Client | None = None


def init_gemini(api_key: str) -> None:
    """Call ONCE at app startup. Streamlit's app.py and fastapi_main.py both do this."""
    global _client
    _client = genai.Client(api_key=api_key)


def _get_client() -> genai.Client:
    if _client is None:
        raise RuntimeError("Gemini client not initialised — call init_gemini(api_key) first.")
    return _client


_DEFAULT_SYSTEM_RULES = """
<ROLE>
You are an elite, highly precise Vedic Astrologer, Numerologist, and Tarot Reader.
</ROLE>

<KNOWLEDGE_BASE_DIRECTIVES>
1. Your interpretive rules, definitions, and logic MUST come entirely from the attached Markdown files.
2. If external knowledge contradicts the attached files, the attached files win.
3. The attached files contain OCR-extracted text. Ignore broken ASCII tables, weird grids, and formatting artifacts. Do not attempt to parse tables.
4. Auto-correct typos in the prose using your context.
</KNOWLEDGE_BASE_DIRECTIVES>

<STRICT_MATH_LOCK>
You are strictly forbidden from altering, correcting, or inferring any numbers, degrees, planetary positions, or mathematical formulas. Treat all numbers in the text and user prompts as absolute, unchangeable facts.
</STRICT_MATH_LOCK>
"""


def _build_safety_settings() -> list[types.SafetySetting]:
    """All four harm categories set to BLOCK_NONE — same as the old SDK config."""
    return [
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
    ]


class _Model:
    """Thin wrapper mimicking the old `GenerativeModel.generate_content()` interface.

    Why a wrapper: lets every caller (consultation streaming, batch
    one-shot, etc.) keep using `model.generate_content(content, stream=...)`
    exactly the way they did with the deprecated SDK. The new SDK uses
    `client.models.generate_content(...)` / `generate_content_stream(...)`,
    which we forward to inside this class.
    """

    def __init__(self, model_name: str, system_instruction: str,
                 temperature: float, response_mime_type: str | None = None) -> None:
        self.model_name = model_name
        cfg_kwargs = dict(
            system_instruction=system_instruction,
            temperature=temperature,
            safety_settings=_build_safety_settings(),
        )
        if response_mime_type:
            cfg_kwargs["response_mime_type"] = response_mime_type
        self._config = types.GenerateContentConfig(**cfg_kwargs)

    def generate_content(self, contents, *, stream: bool = False):
        client = _get_client()
        if stream:
            return client.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=self._config,
            )
        return client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=self._config,
        )


def get_ai_model_by_name(model_name: str, custom_system_rules: str | None = None) -> _Model:
    """Build a model wrapper. `custom_system_rules` containing the word
    'conversational' lifts temperature to 0.5 (matches old behaviour)."""
    system_rules = custom_system_rules or _DEFAULT_SYSTEM_RULES
    is_chat = bool(custom_system_rules) and "conversational" in custom_system_rules.lower()
    temperature = 0.5 if is_chat else 0.1
    return _Model(model_name, system_rules, temperature)


def get_ai_model_for_json(model_name: str, system_instruction: str,
                          temperature: float = 0.7) -> _Model:
    """Build a model wrapper that forces a JSON response. Used by kundli content prose."""
    return _Model(model_name, system_instruction, temperature,
                  response_mime_type="application/json")


# ── retry / fallback helpers ──────────────────────────────────────────────────

def agent_worker(prompt, file_objs=None, model_id=None, custom_system_rules=None, retries=3):
    """Calls a model with exponential backoff. Returns plain text or an
    'Agent Note: ...' fallback message — never raises."""
    if file_objs is None:
        file_objs = []
    elif not isinstance(file_objs, list):
        file_objs = [file_objs]

    for attempt in range(retries):
        try:
            model = get_ai_model_by_name(model_id, custom_system_rules)
            return model.generate_content(file_objs + [prompt]).text
        except Exception as e:
            err_str = str(e)
            is_rate_limit    = any(x in err_str for x in ["429", "quota", "RESOURCE_EXHAUSTED", "rate limit"])
            is_token_overflow = any(x in err_str for x in ["400", "InvalidArgument", "token count exceeds", "maximum number of tokens"])
            if is_token_overflow:
                return f"Agent Note: Content too large for {model_id} ({err_str[:80]}). Inferring from raw dossier."
            elif is_rate_limit and attempt < retries - 1:
                time_module.sleep((2 ** attempt) * 4)
                continue
            else:
                return f"Agent Note: Model {model_id} unavailable ({err_str[:80]}). Inferring from raw dossier."


def generate_content_with_fallback(prompt, knowledge_files=None, preferred_model=None):
    """Universal model router with automatic fallback. Always tries Flash Lite
    first (1M context). Cascades through HEAVY_MODELS on failure."""
    content_to_send = (knowledge_files + [prompt]) if knowledge_files else [prompt]

    if preferred_model and preferred_model in FREE_MODELS:
        others = [m for m in FREE_MODELS if m != preferred_model]
        models_to_try = [preferred_model] + others
    else:
        models_to_try = FREE_MODELS

    last_error = None
    for m_name in models_to_try:
        for attempt in range(3):
            try:
                return get_ai_model_by_name(m_name).generate_content(content_to_send).text
            except Exception as e:
                err_str = str(e)
                is_rate_limit    = any(x in err_str for x in ["429", "quota", "RESOURCE_EXHAUSTED", "rate limit"])
                is_token_overflow = any(x in err_str for x in ["400", "InvalidArgument", "token count exceeds", "maximum number of tokens"])
                if is_token_overflow:
                    last_error = e
                    break
                elif is_rate_limit:
                    if attempt < 2:
                        time_module.sleep((2 ** attempt) * 3)
                        continue
                    else:
                        last_error = e
                        break
                else:
                    last_error = e
                    break

    raise Exception(f"All models unavailable. Last error: {last_error}. Please wait a few minutes and try again.")
