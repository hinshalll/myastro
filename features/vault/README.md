# Vault

Saved profiles — create, edit, delete, star-as-default, import/export JSON backup.

## What's in this folder

| File | What it holds |
|---|---|
| `service.py` | Pure helpers — profile validation, duplicate detection (no Streamlit) |
| `schemas.py` | Pydantic profile model |
| `view.py`    | Streamlit page (the UI users see) |
| `api.py`     | FastAPI router (mobile app + website) |

## Storage

Browser localStorage on the web side. Per-user database in the mobile app.

Profile schema:
```json
{
  "name": "string",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "place": "Mumbai, India" | "Manual Coordinates",
  "lat": 19.07, "lon": 72.87, "tz": "Asia/Kolkata",
  "gender": "M" | "F",
  "exact_time": true | false
}
```

## AI

None. This is a pure CRUD feature.

## Editing tips

- New profile field → add to schema in `schemas.py`, the form in `view.py`, and the API in `api.py`.
- Profile validation → `service.py` `is_duplicate_in_db`.
