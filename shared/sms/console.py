"""shared.sms.console — prints instead of sending. Set SMS_PROVIDER=console.

Lets the whole phone → OTP flow be exercised end to end without burning a real SMS
off the owner's SIM (TextBee's free-ness is capped by carrier patience, not billing).
Read the code off the backend log and type it into the app.
"""
from __future__ import annotations

from .base import SmsResult, is_e164


class ConsoleSender:
    name = "console"

    def send(self, phone: str, message: str) -> SmsResult:
        if not is_e164(phone):
            return SmsResult(False, self.name, f"not E.164: {phone!r}")
        print(f"\n[sms:console] to {phone}\n[sms:console] {message}\n", flush=True)
        return SmsResult(True, self.name, "printed to stdout")
