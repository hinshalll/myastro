# features/ — one folder per user-visible feature.
#
# To edit a feature, open features/<feature>/ and you have everything:
#   constants.py  — only-used-by-this-feature constants
#   prompts.py    — the prompts this feature sends to the LLM
#   service.py    — pure-Python business logic (no Streamlit, no FastAPI)
#   view.py       — the Streamlit page
#   api.py        — the FastAPI router (mobile app + website use this)
#   schemas.py    — Pydantic I/O models
#   README.md     — what this feature does, in plain English
