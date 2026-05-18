# ui_streamlit/pages/__init__.py
# Marks this folder as a Python package.
# Import each page's show_* function for convenient use in app.py.

from ui_streamlit.views.dashboard    import show_dashboard
from ui_streamlit.views.consultation import show_consultation_room
from ui_streamlit.views.oracle       import show_oracle
# tarot has moved to features.tarot — see features/tarot/view.py
from features.tarot.view             import show_tarot
from ui_streamlit.views.horoscopes   import show_horoscopes
from ui_streamlit.views.numerology   import show_numerology
from ui_streamlit.views.vault        import show_vault
