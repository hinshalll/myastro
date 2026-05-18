"""
ui_streamlit/cache.py

Every @st.cache_data wrapper lives here and nowhere else.
Core functions (in ai_engine/ and math_engine/) have zero Streamlit imports —
these thin wrappers are the ONLY place Streamlit's cache decorator touches them.

Why a separate file?
- When you switch to FastAPI, you delete this entire file and replace with Redis/dict cache.
- The underlying functions never change.
- Easy to find and tune TTLs in one place.
"""

from datetime import timedelta
import streamlit as st

from math_engine.astro_calc import geocode_place, timezone_for_latlon
from math_engine.dossier_builder import get_live_cosmic_weather
from ai_engine.knowledge import rag_context
from ai_engine.forecasts import (
    generate_western_forecast,
    generate_vedic_forecast,
    fetch_dashboard_data,
    fetch_daily_tarot,
)


@st.cache_data(show_spinner=False)
def geocode_place_cached(place_text: str):
    return geocode_place(place_text)


@st.cache_data(show_spinner=False)
def timezone_for_latlon_cached(lat: float, lon: float):
    return timezone_for_latlon(lat, lon)


@st.cache_data(ttl=3600, show_spinner=False)
def get_live_cosmic_weather_cached():
    return get_live_cosmic_weather()


@st.cache_data(ttl=timedelta(hours=24), show_spinner=False)
def rag_context_cached(query: str, books_tuple: tuple, k: int = 8) -> str:
    return rag_context(query, list(books_tuple), k=k)


@st.cache_data(ttl=timedelta(hours=24), show_spinner=False)
def generate_western_forecast_cached(sun_sign: str, today_str: str):
    return generate_western_forecast(sun_sign, today_str)


@st.cache_data(ttl=timedelta(hours=24), show_spinner=False)
def generate_vedic_forecast_cached(prof_json: str, timeframe: str, today_str: str):
    return generate_vedic_forecast(prof_json, timeframe, today_str)


@st.cache_data(ttl=timedelta(hours=24), show_spinner=False)
def fetch_dashboard_data_cached(prof_json: str, today_str: str):
    return fetch_dashboard_data(prof_json, today_str)


@st.cache_data(ttl=timedelta(hours=24), show_spinner=False)
def fetch_daily_tarot_cached(prof_json: str, today_str: str, daily_card: str, daily_state: str):
    return fetch_daily_tarot(prof_json, today_str, daily_card, daily_state)
