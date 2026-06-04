"""shared.astro.config — backend feature toggles (server-side switches).

These are kept in the BACKEND on purpose: the API retains full capability even
when the frontend chooses to hide a feature. Removing a toggle from the UI never
removes the math — flip the switch here (or via env var) and it's back.

Override any toggle with an environment variable (read fresh each call, so tests
and a running server can change them without a restart):

  KP_ENABLED = 1 | true | yes | on     -> turn KP (Placidus / sub-lord) ON
  NODE_TYPE  = mean | true              -> Rahu/Ketu node model

Defaults (locked, see docs/ephemeris-decision.md + MOBILE_APP_BLUEPRINT.md):
  * KP is OFF  — whole-sign houses are the app default; KP is an advanced opt-in.
                 The KP MATH stays in the engine; this only gates whether it is
                 surfaced/used. The deep AI consultation can still opt in
                 explicitly (it passes include_kp=True).
  * Node is MEAN — matches Indian panchangs / B.V. Raman tradition. "true"
                 (osculating) node is a future build: the seam exists in
                 ephem_skyfield.true_node_* (free engine) and works today only
                 under the swisseph provider.
"""
from __future__ import annotations

import os

_TRUTHY = {"1", "true", "yes", "on", "y", "t"}


def kp_enabled() -> bool:
    """Is KP (Placidus cusps + sub-lord) surfaced? Default False (whole-sign)."""
    v = os.environ.get("KP_ENABLED")
    if v is None:
        return False
    return v.strip().lower() in _TRUTHY


def node_type() -> str:
    """Lunar node model for Rahu/Ketu: 'mean' (default) or 'true'."""
    v = (os.environ.get("NODE_TYPE") or "mean").strip().lower()
    return "true" if v == "true" else "mean"
