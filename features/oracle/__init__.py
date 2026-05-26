"""features.oracle
=================
The Oracle is a package of 6 independent features, each in its own file.

There are two ways into this package:

  • The FastAPI router — `features.oracle.api` — is pure, Streamlit-free
    backend code (the mobile app calls it over HTTP).
  • The legacy Streamlit dropdown — `show_oracle` — plus the six `show_*`
    sub-views are Streamlit UI code.

IMPORTANT (purity / hosting rule): importing the `features.oracle` package
must NOT import Streamlit, because the FastAPI backend is deployed on a server
that has no Streamlit installed. So the Streamlit `show_*` functions are loaded
LAZILY here (PEP 562 `__getattr__`) — they're only imported when the Streamlit
app actually asks for them. The legacy dropdown body lives in
`features.oracle._dropdown`.

  ┌──────────────────────────┬──────────────────────────────────────────┐
  │ Feature                  │ Module                                     │
  ├──────────────────────────┼──────────────────────────────────────────┤
  │ Full Life Reading        │ oracle.deep_analysis.show_deep_analysis    │
  │ Compatibility Match      │ oracle.matchmaking.show_matchmaking        │
  │ Destiny Marriage Matrix  │ oracle.marriage.show_marriage              │
  │ Live Transit (Gochara)   │ oracle.gochara.show_gochara                │
  │ Compare Profiles         │ oracle.compare.show_compare                │
  │ Prashna (Horary)         │ oracle.prashna.show_prashna                │
  └──────────────────────────┴──────────────────────────────────────────┘
"""

import importlib

# Maps a lazily-exported name → the submodule that defines it. Everything here
# is Streamlit code, so it's only imported on first access (never at package
# import time).
_LAZY = {
    "show_oracle":        "_dropdown",
    "show_deep_analysis": "deep_analysis",
    "show_matchmaking":   "matchmaking",
    "show_marriage":      "marriage",
    "show_gochara":       "gochara",
    "show_compare":       "compare",
    "show_prashna":       "prashna",
}


def __getattr__(name):
    """PEP 562 lazy loader — keeps `import features.oracle(.api)` Streamlit-free
    while still letting the Streamlit app do `from features.oracle import show_*`."""
    if name in _LAZY:
        mod = importlib.import_module(f"features.oracle.{_LAZY[name]}")
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_LAZY)
