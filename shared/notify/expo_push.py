"""shared.notify.expo_push — send a push notification via Expo's free push service.

The mobile app (Expo) registers for notifications and uploads its ExponentPush
token (PUT /me/push-token). To notify a CLOSED app, the server POSTs to Expo's
push API (https://exp.host/--/api/v2/push/send) — free, no Apple/Google keys
needed for Expo-managed apps. This is the ONLY way the app can hear from us while
it isn't running; known-time events (eclipse, a task, a capsule date) are better
scheduled as LOCAL notifications on-device.

Never raises — returns a small status dict; a push failure must never break a
request or a cron run.
"""
from __future__ import annotations

_EXPO_URL = "https://exp.host/--/api/v2/push/send"


def send_push(tokens, title: str, body: str, data: dict | None = None) -> dict:
    """Send one push to one or many Expo tokens. Returns {ok, sent, ...}.
    No-op (ok, sent=0) when there are no tokens."""
    toks = [t for t in (tokens if isinstance(tokens, (list, tuple)) else [tokens]) if t]
    if not toks:
        return {"ok": True, "sent": 0, "skipped": "no tokens"}
    try:
        import httpx
        messages = [{"to": t, "title": title, "body": body,
                     "sound": "default", "data": data or {}} for t in toks]
        resp = httpx.post(
            _EXPO_URL, json=messages,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=15,
        )
        return {"ok": resp.status_code == 200, "sent": len(toks),
                "status": resp.status_code}
    except Exception as e:                       # network down, bad token, etc.
        return {"ok": False, "sent": 0, "error": str(e)}
