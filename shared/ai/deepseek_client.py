"""shared/ai/deepseek_client.py — DeepSeek adapter.

Mirrors the exact interface of the Gemini `_Model` wrapper so the rest of the
app can't tell which provider is running. DeepSeek exposes an OpenAI-compatible
HTTP API (https://api.deepseek.com/chat/completions), which we call with httpx
(already a dependency via FastAPI / google-genai).

Public surface used by gemini_client's dispatch:
    init_deepseek(api_key)                  — store the key (call once at startup)
    DeepSeekModel(model, system, temp, ...) — .generate_content(contents, stream=)

The returned object exposes:
    .generate_content(contents, stream=False) -> response with .text
    .generate_content(contents, stream=True)  -> iterator of chunks with .text
so streaming consultation, one-shot readings, and JSON callers all just work.

NOTE on vision: this adapter CAN encode images (PIL images or raw bytes) into the
OpenAI-compatible image_url blocks DeepSeek's multimodal endpoint expects. It is
future-ready, but DeepSeek's public API does not yet document image input, so the
"vision" task ladder in config.py stays Gemini-only. When DeepSeek officially
ships vision, add "deepseek-v4-flash" to that ladder — no change needed here.
"""

import io as _io
import json as _json
import base64 as _b64

import httpx

from shared.ai import config

_API_URL = "https://api.deepseek.com/chat/completions"
_TIMEOUT = 120.0


def init_deepseek(api_key: str | None) -> None:
    """Store the DeepSeek key. Safe to call with None (just does nothing)."""
    config.set_api_key("deepseek", api_key)


def _require_key() -> str:
    key = config.get_api_key("deepseek")
    if not key:
        raise RuntimeError(
            "DeepSeek key not set — add DEEPSEEK_API_KEY to your secrets and "
            "call init_deepseek(key) at startup."
        )
    return key


def _encode_image_part(part):
    """Return an OpenAI-style image_url block for a PIL image or raw bytes,
    else None if `part` is not an image we can encode."""
    data = None
    try:
        import PIL.Image
        if isinstance(part, PIL.Image.Image):
            buf = _io.BytesIO()
            part.convert("RGB").save(buf, format="PNG")
            data = buf.getvalue()
    except Exception:
        pass
    if data is None and isinstance(part, (bytes, bytearray)):
        data = bytes(part)
    if data is None:
        return None
    b64 = _b64.b64encode(data).decode("ascii")
    return {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}


def _build_user_content(contents):
    """Flatten a Gemini-style contents list into OpenAI chat content.

    All-text input collapses to a single string (simplest form). If any image
    part is present, returns the list-of-blocks form DeepSeek's multimodal
    endpoint expects. Truly un-encodable parts raise, so the fallback ladder
    skips to a Gemini model.
    """
    if isinstance(contents, str):
        return contents

    blocks: list = []
    has_image = False
    for part in contents:
        if isinstance(part, str):
            blocks.append({"type": "text", "text": part})
            continue
        img = _encode_image_part(part)
        if img is not None:
            blocks.append(img)
            has_image = True
            continue
        if isinstance(part, dict) and part.get("type") in ("text", "image_url"):
            blocks.append(part)
            has_image = has_image or part.get("type") == "image_url"
            continue
        raise RuntimeError(
            f"DeepSeek adapter can't encode a content part of type "
            f"{type(part).__name__}."
        )

    if not has_image:
        return "\n\n".join(b["text"] for b in blocks if b.get("type") == "text")
    return blocks


class _Resp:
    """Minimal stand-in for the Gemini response object (only .text is used)."""
    def __init__(self, text: str) -> None:
        self.text = text


class _Chunk:
    """Minimal stand-in for a streamed chunk (only .text is used)."""
    def __init__(self, text: str) -> None:
        self.text = text


class DeepSeekModel:
    """Drop-in replacement for gemini_client._Model, backed by DeepSeek."""

    def __init__(self, model_name: str, system_instruction: str,
                 temperature: float, response_mime_type: str | None = None) -> None:
        self.model_name = model_name
        self.system_instruction = system_instruction
        self.temperature = temperature
        self.response_mime_type = response_mime_type

    def _payload(self, contents, stream: bool) -> dict:
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": _build_user_content(contents)},
            ],
            "temperature": self.temperature,
            "stream": stream,
        }
        if self.response_mime_type == "application/json":
            payload["response_format"] = {"type": "json_object"}
        return payload

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {_require_key()}",
            "Content-Type": "application/json",
        }

    def generate_content(self, contents, *, stream: bool = False):
        if stream:
            return self._stream(contents)
        resp = httpx.post(
            _API_URL, headers=self._headers(),
            json=self._payload(contents, stream=False), timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"] or ""
        return _Resp(text)

    def _stream(self, contents):
        with httpx.stream(
            "POST", _API_URL, headers=self._headers(),
            json=self._payload(contents, stream=True), timeout=_TIMEOUT,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                chunk = line[len("data:"):].strip()
                if chunk == "[DONE]":
                    break
                try:
                    delta = _json.loads(chunk)["choices"][0]["delta"].get("content")
                except (KeyError, IndexError, _json.JSONDecodeError):
                    continue
                if delta:
                    yield _Chunk(delta)
