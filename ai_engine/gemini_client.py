import time as time_module
import google.generativeai as genai

LIGHT_MODELS = [
    "gemini-3.1-flash-lite-preview",  # 500 RPD, 250K TPM, 1M context — PRIMARY for everything
    "gemini-2.5-flash",               #  20 RPD, 250K TPM, 1M context — second fallback
]

HEAVY_MODELS = [
    "gemma-4-31b-it",       # 1500 RPD, Unlimited TPM, 262K context — last resort
    "gemma-4-26b-a4b-it",   # 1500 RPD, Unlimited TPM, 262K context — final fallback
]

FREE_MODELS = LIGHT_MODELS + HEAVY_MODELS


def init_gemini(api_key: str):
    """
    Call this ONCE at app startup before using any model functions.
    Centralised here so the AI layer is self-contained and testable.
    """
    genai.configure(api_key=api_key)


def get_ai_model_by_name(model_name, custom_system_rules=None):
    """Directly calls a specific model with dynamic system rules."""
    default_rules = """
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

    system_rules = custom_system_rules or default_rules
    safe_config = [
        {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    is_chat = custom_system_rules and "conversational" in custom_system_rules.lower()
    gen_config = {"temperature": 0.5 if is_chat else 0.1}

    return genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_rules,
        safety_settings=safe_config,
        generation_config=gen_config,
    )


def agent_worker(prompt, file_objs=None, model_id=None, custom_system_rules=None, retries=3):
    """
    Calls a model with exponential backoff.
    Falls back gracefully on rate limits and context overflow.
    """
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
            is_rate_limit   = any(x in err_str for x in ["429", "quota", "RESOURCE_EXHAUSTED", "rate limit"])
            is_token_overflow = any(x in err_str for x in ["400", "InvalidArgument", "token count exceeds", "maximum number of tokens"])
            if is_token_overflow:
                return f"Agent Note: Content too large for {model_id} ({err_str[:80]}). Inferring from raw dossier."
            elif is_rate_limit and attempt < retries - 1:
                time_module.sleep((2 ** attempt) * 4)
                continue
            else:
                return f"Agent Note: Model {model_id} unavailable ({err_str[:80]}). Inferring from raw dossier."


def generate_content_with_fallback(prompt, knowledge_files=None, preferred_model=None):
    """
    Universal model router with automatic fallback and retry.
    Always tries Flash Lite FIRST (1M context). Falls back to Heavy models.
    """
    content_to_send = knowledge_files + [prompt] if knowledge_files else [prompt]

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
                is_rate_limit   = any(x in err_str for x in ["429", "quota", "RESOURCE_EXHAUSTED", "rate limit"])
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
