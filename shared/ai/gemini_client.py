"""shared.ai.gemini_client — Gemini SDK wrapper.

Uses the new `google-genai` package (pip: `google-genai`, import:
`from google import genai`). The old `google-generativeai` was deprecated.

Public API (unchanged after the SDK migration):
    FREE_MODELS                          — generic fallback ladder (Gemini → DeepSeek net)
    init_gemini(api_key)                 — call ONCE at app startup
    get_ai_model_by_name(name, system_rules=None) -> _Model
        The returned object exposes .generate_content(contents, stream=False)
        for parity with how callers (consultation/view.py) iterate chunks.
    agent_worker(prompt, file_objs, model_id, custom_system_rules, retries)
    generate_content_with_fallback(prompt, knowledge_files, preferred_model)
        Universal model router with retry + cascade.
"""

from google import genai
from google.genai import types

from shared.ai import config

# The model ladder now lives in shared/ai/config.py (the one file you edit).
# FREE_MODELS is kept as the public name callers already import.
FREE_MODELS = list(config.FALLBACK_CHAIN)


_client: genai.Client | None = None


def init_gemini(api_key: str) -> None:
    """Call ONCE at app startup. Streamlit's app.py and fastapi_main.py both do this."""
    global _client
    _client = genai.Client(api_key=api_key)
    config.set_api_key("gemini", api_key)


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


def get_ai_model_by_name(model_name: str, custom_system_rules: str | None = None):
    """Build a model wrapper for the given model. Provider (Gemini / DeepSeek)
    is auto-detected from the model name. `custom_system_rules` containing the
    word 'conversational' lifts temperature to 0.5 (matches old behaviour)."""
    system_rules = custom_system_rules or _DEFAULT_SYSTEM_RULES
    is_chat = bool(custom_system_rules) and "conversational" in custom_system_rules.lower()
    temperature = 0.5 if is_chat else 0.1
    if config.detect_provider(model_name) == "deepseek":
        from shared.ai.deepseek_client import DeepSeekModel
        return DeepSeekModel(model_name, system_rules, temperature)
    return _Model(model_name, system_rules, temperature)


def get_ai_model_for_json(model_name: str, system_instruction: str,
                          temperature: float = 0.7):
    """Build a model wrapper that forces a JSON response. Used by kundli content
    prose. Provider auto-detected from the model name."""
    if config.detect_provider(model_name) == "deepseek":
        from shared.ai.deepseek_client import DeepSeekModel
        return DeepSeekModel(model_name, system_instruction, temperature,
                             response_mime_type="application/json")
    return _Model(model_name, system_instruction, temperature,
                  response_mime_type="application/json")


# ── retry / fallback helpers ──────────────────────────────────────────────────

def _ladder_with_preference(task, preferred_model=None):
    """Build the live ladder for a task: optional preferred model first, then the
    task's configured rungs, with models currently cooling-down filtered out."""
    ladder = config.ladder_for(task)
    if preferred_model:
        ladder = [preferred_model] + [m for m in ladder if m != preferred_model]
    return config.usable_models(ladder)


def agent_worker(prompt, file_objs=None, model_id=None, custom_system_rules=None, retries=3):
    """Run one oracle agent, cascading down the 'agent' ladder (Gemini → DeepSeek)
    with the circuit breaker. Returns plain text or an 'Agent Note: ...' fallback
    message — never raises. `retries` is kept for signature compatibility."""
    if file_objs is None:
        file_objs = []
    elif not isinstance(file_objs, list):
        file_objs = [file_objs]

    last_err = ""
    for m_name in _ladder_with_preference("agent", model_id):
        try:
            text = get_ai_model_by_name(m_name, custom_system_rules).generate_content(
                file_objs + [prompt]).text
            config.note_success(m_name)
            return text
        except Exception as e:
            err_str = str(e)
            last_err = err_str
            config.note_failure(m_name, err_str)   # opens breaker only on quota errors
            continue                                # instant fall to next rung
    return f"Agent Note: all models unavailable ({last_err[:80]}). Inferring from raw dossier."


def generate_content_with_fallback(prompt, knowledge_files=None, preferred_model=None,
                                    task="default"):
    """Universal model router. Walks the task's ladder (smart tasks: Gemini →
    DeepSeek), skipping any rung whose breaker is open and falling instantly to
    the next on a quota error. Records success/failure so the breaker can recover
    to free Gemini the moment its daily quota resets."""
    content_to_send = (knowledge_files + [prompt]) if knowledge_files else [prompt]

    last_error = None
    for m_name in _ladder_with_preference(task, preferred_model):
        try:
            text = get_ai_model_by_name(m_name).generate_content(content_to_send).text
            config.note_success(m_name)
            return text
        except Exception as e:
            last_error = e
            config.note_failure(m_name, str(e))   # opens breaker only on quota errors
            continue                               # token-overflow & transient errors also fall through

    raise Exception(f"All models unavailable. Last error: {last_error}. Please wait a few minutes and try again.")
