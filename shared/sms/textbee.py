"""shared.sms.textbee — DEV-STAGE sender. Sends SMS from the owner's own Android phone.

TextBee turns a phone running their gateway app into an SMS gateway, so OTPs cost
nothing and need no DLT registration (it is person-to-person traffic off a normal
SIM, not a commercial A2P route).

DEV ONLY — DO NOT SHIP. It sends off the owner's personal SIM, which means:
  - carriers rate-limit and eventually block a SIM that behaves like a bulk sender
  - the owner's phone must be powered on, online, and not out of battery
  - the recipient sees the owner's personal number
  - the device applies its own smsSendDelaySeconds (5s) between messages
That is all fine while the owner is the only tester, and unacceptable at launch.
At launch this module is replaced via SMS_PROVIDER without touching the app.

API (verified against the live account 2026-07-16):
    POST {BASE}/gateway/devices/{DEVICE_ID}/send-sms
    header: x-api-key: <key>
    body:   {"recipients": ["+919876543210"], "message": "..."}
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from shared.db.secrets import get_secret
from .base import SmsResult, is_e164

_BASE = "https://api.textbee.dev/api/v1"
_TIMEOUT = 20


class TextBeeSender:
    name = "textbee"

    def __init__(self) -> None:
        # Read lazily-ish but once: these live in .streamlit/secrets.toml (gitignored)
        # or env on Render. NEVER in the mobile app — an API key in the app is a key
        # anyone can pull out of the bundle and use to send SMS off the owner's phone.
        self._key = get_secret("TEXTBEE_API_KEY")
        self._device = get_secret("TEXTBEE_DEVICE_ID")

    def configured(self) -> bool:
        return bool(self._key and self._device)

    def send(self, phone: str, message: str) -> SmsResult:
        if not self.configured():
            return SmsResult(False, self.name, "TEXTBEE_API_KEY / TEXTBEE_DEVICE_ID not set")
        if not is_e164(phone):
            return SmsResult(False, self.name, f"not E.164: {phone!r}")

        url = f"{_BASE}/gateway/devices/{self._device}/send-sms"
        body = json.dumps({"recipients": [phone], "message": message}).encode()
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Content-Type": "application/json", "x-api-key": self._key},
        )
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
                raw = r.read().decode("utf-8", "replace")
                if 200 <= r.status < 300:
                    pid = None
                    try:
                        d = json.loads(raw).get("data") or {}
                        pid = d.get("smsBatchId") or d.get("_id")
                    except Exception:
                        pass
                    return SmsResult(True, self.name, "queued on device", pid)
                return SmsResult(False, self.name, f"HTTP {r.status}: {raw[:200]}")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:200] if e.fp else str(e)
            return SmsResult(False, self.name, f"HTTP {e.code}: {detail}")
        except Exception as e:  # network down, phone offline, DNS, timeout
            return SmsResult(False, self.name, f"{type(e).__name__}: {e}")
