"""features.horoscopes — Western (sun sign) + Vedic (moon sign) daily forecasts.

Empty __init__ on purpose: backend code that needs the forecast functions
should import features.horoscopes.service directly so importing prompts/service
never pulls in the Streamlit view (which would cause circular imports).

To get the Streamlit page: `from features.horoscopes.view import show_horoscopes`.
"""
