"""shared.sms — the ONE place the app sends an SMS from.

THE SEAM. Nothing outside this package may know who actually delivers a message.
Callers do `from shared.sms import send_sms` and never import a provider directly —
the same rule the ephemeris adapter follows (the app never calls `swe` directly).

Why it matters here: the sender is expected to change at least twice.
    dev  → TextBee   (free; sends from the owner's own Android phone)
    live → Truecaller's free flow, or HanuOTP (~Rs 0.25) if that falls through

Because delivery is server-side, swapping the provider is one env var and ZERO
mobile-app changes — the app only ever calls our /auth/otp/* endpoints and never
learns who sent the text.

Pick a provider with SMS_PROVIDER (env or secrets.toml). Default: textbee.
"""
from __future__ import annotations

from .base import SmsResult, SmsSender

_CACHE: dict[str, SmsSender] = {}


def get_sender(name: str | None = None) -> SmsSender:
    """Return the configured sender. `name` overrides config (used by tests)."""
    from shared.db.secrets import get_secret

    provider = (name or get_secret("SMS_PROVIDER") or "textbee").strip().lower()
    if provider in _CACHE:
        return _CACHE[provider]

    if provider == "textbee":
        from .textbee import TextBeeSender
        sender: SmsSender = TextBeeSender()
    elif provider == "console":
        # dev escape hatch: prints instead of sending, so the OTP flow can be
        # exercised end to end without burning a real SMS off the owner's SIM.
        from .console import ConsoleSender
        sender = ConsoleSender()
    else:
        raise ValueError(f"Unknown SMS_PROVIDER {provider!r} (expected: textbee, console)")

    _CACHE[provider] = sender
    return sender


def send_sms(phone: str, message: str, *, provider: str | None = None) -> SmsResult:
    """Send `message` to `phone` (E.164, e.g. +919876543210). Never raises."""
    return get_sender(provider).send(phone, message)


__all__ = ["send_sms", "get_sender", "SmsSender", "SmsResult"]
