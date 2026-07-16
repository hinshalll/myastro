"""shared.sms.base — the contract every SMS provider implements.

Keep this interface boring and small. Anything provider-specific (device ids,
route names, template ids) stays inside that provider's module, because the whole
point of the seam is that swapping TextBee for HanuOTP touches one file.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

# E.164: a +, a non-zero country digit, then up to 14 more digits.
_E164 = re.compile(r"^\+[1-9]\d{7,14}$")


def is_e164(phone: str) -> bool:
    return bool(_E164.match((phone or "").strip()))


def is_india(phone: str) -> bool:
    """True for a valid +91 number. This is the ONLY routing question we ask.

    We gate on the number the user TYPED, never on their detected location: the
    number is a fact, location is a guess. Geo-gating actively causes the bug we
    are avoiding (an American in Mumbai geo-resolves to India, so we would try to
    SMS a +1 number at Rs 1+; an NRI in London on a +91 number would be wrongly
    blocked from the cheap route that works fine for them).

    There is deliberately NO general country_code() helper here. Country codes are
    variable-length (+1, +44, +971) and cannot be parsed by grabbing N digits — the
    first draft of this file did exactly that and confidently returned "141" for a
    US number. India is the only route we support, so "is it +91" is the only
    question worth answering, and it is answerable exactly. If we ever add a paid
    international provider, add `phonenumbers` rather than hand-rolling a table.
    """
    return is_e164(phone) and (phone or "").strip().startswith("+91")


@dataclass(frozen=True)
class SmsResult:
    ok: bool
    provider: str
    detail: str = ""          # human-readable; safe to log, never contains the OTP
    provider_id: str | None = None


class SmsSender(Protocol):
    name: str

    def send(self, phone: str, message: str) -> SmsResult:
        """Deliver `message` to `phone`. MUST NOT raise — return SmsResult(ok=False)."""
        ...
