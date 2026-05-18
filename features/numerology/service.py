"""features.numerology.service — pure numerology helpers.

The core math (Life Path, Destiny, Soul Urge, Personality, Personal cycles,
Pinnacles, Challenges) lives in shared.astro/astro_calc.py and is shared
across views. This service file is a thin convenience wrapper.
"""

from shared.astro.astro_calc import (
    calculate_numerology_core, get_personal_year, get_personal_month,
    get_personal_day, get_pinnacle_cycles,
)


__all__ = [
    "calculate_numerology_core",
    "get_personal_year", "get_personal_month", "get_personal_day",
    "get_pinnacle_cycles",
]
