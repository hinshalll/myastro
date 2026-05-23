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

NOTE on vision: DeepSeek does not accept Gemini file/image handles. If a caller
passes non-text parts (palm/face images uploaded as Gemini objects), this
adapter raises a clear error so the fallback ladder skips to a Gemini model.
Pointing the "vision" task at a DeepSeek model therefore needs provider-neutral
image bytes — left for when you actually want to experiment there.
"""

import json as _json

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


def _contents_to_text(contents) -> str:
    """Flatten a Gemini-style contents list into a single user-message string.

    Strings are kept; anything non-text (image/file objects) means a vision
    payload DeepSeek can't take here, so we fail loudly for the fallback ladder.
    """
    if isinstance(contents, str):
        return contents
    parts: list[str] = []
    for part in contents:
        if isinstance(part, str):
            parts.append(part)
        else:
            raise RuntimeError(
                "DeepSeek adapter received a non-text part (likely an image). "
                "Keep image/vision tasks on a Gemini model for now."
            )
    return "\n\n".join(parts)


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
                {"role": "user", "content": _contents_to_text(contents)},
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
