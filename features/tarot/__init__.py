"""features.tarot — Mystic Tarot feature (4 modes + birth card).

This __init__ is intentionally empty: importing `features.tarot.prompts` or
`features.tarot.service` from the backend should NOT pull in the Streamlit
view (which would create circular imports with shared.ai.forecasts).

To get the Streamlit page: `from features.tarot.view import show_tarot`.
"""
