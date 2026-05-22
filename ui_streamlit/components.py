import streamlit as st
import base64
import secrets
import time as time_module
from datetime import datetime, date, time

import streamlit.components.v1 as components

from features.tarot.constants import TAROT_BASE
from shared.astro.astro_calc import geocode_place, timezone_for_latlon
from shared.ai.gemini_client import FREE_MODELS, get_ai_model_by_name

# ── state helpers — no more monkey patching ──────────────────────────────────
from ui_streamlit.state import (
    sync_db,
    is_duplicate_in_db,
    get_default_profile,
    sorted_profile_options,
    format_date_ui,
    get_filename,
)

APP_NAME = "ASTRO SUITE beta"


# ── Share / PDF ───────────────────────────────────────────────────────────────

def render_share_buttons(text, title="Astro Suite", image_b64=None):
    """Universal PDF Generator: Includes CSS Page Break Fixes."""
    import base64
    import streamlit.components.v1 as components

    b64_text = base64.b64encode(text.encode("utf-8")).decode("utf-8")
    safe_title    = title.replace("'", "\\'")
    safe_filename = title.replace(" ", "_") + "_Report.pdf"
    img_b64_str   = image_b64 if image_b64 else ""

    html_template = """
<div style="font-family:'Source Sans Pro',sans-serif;display:flex;gap:10px;padding:5px;">
    <button id="pdfBtn" style="flex:1;padding:.5rem 1rem;background:linear-gradient(135deg,rgba(144,98,222,0.3),rgba(205,140,80,0.3));color:#fff;border:1px solid rgba(205,140,80,.5);border-radius:.5rem;cursor:pointer;font-size:1rem;font-weight:bold;display:flex;align-items:center;justify-content:center;gap:8px;transition:all .2s"
        onmouseover="this.style.borderColor='#ff4b4b';this.style.color='#ff4b4b'"
        onmouseout="this.style.borderColor='rgba(205,140,80,.5)';this.style.color='#fff'">
        📄 Save as PDF
    </button>
    <button id="shareBtn" style="flex:1;padding:.5rem 1rem;background:transparent;color:#fff;border:1px solid rgba(250,250,250,.2);border-radius:.5rem;cursor:pointer;font-size:1rem;display:flex;align-items:center;justify-content:center;gap:8px;transition:all .2s">
        Share Reading
    </button>
</div>
<div id="msg" style="text-align:center;font-size:.8rem;margin-top:5px;color:#999;opacity:0;transition:opacity .3s"></div>

<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
<script>
var raw_text = decodeURIComponent(escape(window.atob('B64_PLACEHOLDER')));
var b64_img = 'IMG_PLACEHOLDER';
var msg = document.getElementById('msg');
function showMsg(t) { msg.innerText = t; msg.style.opacity = 1; setTimeout(function(){ msg.style.opacity = 0; }, 3000); }

document.getElementById('pdfBtn').addEventListener('click', function() {
    showMsg('Generating PDF...');
    var parsedHTML = marked.parse(raw_text);
    var wrapper = document.createElement('div');
    
    wrapper.style.padding = '30px';
    wrapper.style.backgroundColor = '#ffffff'; 
    wrapper.style.color = '#1a1a1a'; 
    wrapper.style.fontFamily = 'Helvetica, Arial, sans-serif';
    wrapper.style.lineHeight = '1.6';
    
    var imgHtml = b64_img ? '<div style="text-align:center;margin-bottom:20px;"><img src="data:image/jpeg;base64,' + b64_img + '" style="max-height:300px;border-radius:10px;border:2px solid #D4AF37;"></div>' : '';

    wrapper.innerHTML =
        '<style>.pdf-content p, .pdf-content li, .pdf-content h1, .pdf-content h2, .pdf-content h3 { page-break-inside: avoid; break-inside: avoid; margin-bottom: 12px; }</style>'
        + '<div style="text-align:center;margin-bottom:30px;border-bottom:2px solid rgba(212, 175, 55, 0.5);padding-bottom:20px;">'
        + '<h1 style="color:#1a1a1a;font-size:28px;letter-spacing:2px;margin:0;">TITLE_PLACEHOLDER</h1>'
        + '<p style="color:#555555;font-size:12px;letter-spacing:1px;text-transform:uppercase;margin-top:5px;">Personalized Cosmic Reading</p>'
        + '</div>'
        + imgHtml
        + '<div class="pdf-content" style="font-size:14px;color:#1a1a1a;">' + parsedHTML + '</div>'
        + '<div style="margin-top:40px;text-align:center;font-size:10px;color:#999;border-top:1px solid #eeeeee;padding-top:15px;">Generated securely by Astro Suite Engine</div>';

    var opt = {
        margin: [15, 15, 15, 15],
        filename: 'FILENAME_PLACEHOLDER',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, backgroundColor: '#ffffff' },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
        pagebreak: { mode: ['css', 'legacy'] }
    };
    html2pdf().set(opt).from(wrapper).save().then(function() { showMsg('PDF Downloaded!'); });
});
</script>
"""
    html = (html_template
            .replace("B64_PLACEHOLDER",      b64_text)
            .replace("TITLE_PLACEHOLDER",    safe_title)
            .replace("FILENAME_PLACEHOLDER", safe_filename)
            .replace("IMG_PLACEHOLDER",      img_b64_str))

    import streamlit as st
    st.markdown("<br>", unsafe_allow_html=True)
    components.html(html, height=100)


# ── CSS injection ─────────────────────────────────────────────────────────────

def inject_nebula_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
html,body,.stApp{background:radial-gradient(circle at 15% 50%,#1a0f2e,#0c0814 60%,#050308 100%)!important;font-family:'Inter',sans-serif!important;color:#e2e0ec!important}
#MainMenu,footer{visibility:hidden!important;height:0!important}
[data-testid="stHeader"]{background:transparent!important}
h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif!important;color:#fff}
.block-container{padding:1rem 1.25rem 5rem!important;max-width:960px!important}
[data-testid="stVerticalBlockBorderWrapper"]{background:rgba(255,255,255,0.03)!important;backdrop-filter:blur(12px)!important;border:1px solid rgba(255,255,255,0.08)!important;border-radius:16px!important;box-shadow:0 8px 32px rgba(0,0,0,0.3)!important}
.stTextInput>div>div>input,.stNumberInput>div>div>input,.stSelectbox>div>div,.stDateInput>div>div>input,.stTextArea>div>div>textarea{background:rgba(255,255,255,0.04)!important;border:1px solid rgba(255,255,255,0.1)!important;border-radius:10px!important;color:#eceaf4!important}
div[data-testid="stButton"]>button{border-radius:10px!important;font-weight:600!important;transition:all .3s ease!important;border:1px solid rgba(255,255,255,0.1)!important;font-family:'Inter',sans-serif!important}
div[data-testid="stButton"]>button[kind="primary"]{background:linear-gradient(135deg,rgba(144,98,222,0.8),rgba(205,140,80,0.8))!important;border:none!important;color:#fff!important}
div[data-testid="stButton"]>button[kind="primary"]:hover{transform:translateY(-2px)!important;box-shadow:0 8px 20px rgba(144,98,222,0.4)!important}
div[data-testid="stButton"]>button:not([kind="primary"]){background:rgba(255,255,255,0.05)!important;color:#fff!important}
div[data-testid="stButton"]>button:not([kind="primary"]):hover{background:rgba(255,255,255,0.1)!important}
.stLinkButton>a{background:rgba(255,255,255,0.05)!important;border:1px solid rgba(255,255,255,0.1)!important;border-radius:10px!important;color:#fff!important;transition:all .3s!important}
.stLinkButton>a:hover{background:rgba(255,255,255,0.1)!important}
[data-testid="stExpander"]{border:1px solid rgba(255,255,255,0.1)!important;border-radius:12px!important;background:rgba(0,0,0,0.2)!important}
.stCodeBlock{border-radius:12px!important;border:1px solid rgba(255,255,255,0.1)!important;max-height:300px!important;overflow-y:auto!important}
[data-testid="stSidebar"]{background:rgba(5,3,15,0.98)!important;border-right:1px solid rgba(144,98,222,0.25)!important}
.weather-widget{text-align:center;padding:1.5rem;border-radius:16px;background:linear-gradient(180deg,rgba(205,140,80,0.1),rgba(144,98,222,0.05));border:1px solid rgba(205,140,80,0.2)}
.w-main{font-family:'Space Grotesk',sans-serif;font-size:1.8rem;font-weight:700;color:#fff;margin:.3rem 0;text-shadow:0 0 20px rgba(205,140,80,0.4)}
.feat-card{border-radius:14px;border:1px solid rgba(255,255,255,0.08);background:rgba(255,255,255,0.035);padding:1rem;position:relative;overflow:hidden;transition:all .2s}
.feat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--accent)}
.feat-card:hover{border-color:rgba(255,255,255,0.14);transform:translateY(-2px)}
.feat-icon{font-size:1.6rem;display:block;margin-bottom:.4rem}
.feat-title{font-family:'Space Grotesk',sans-serif;font-size:.9rem;font-weight:600;color:#fff;margin:0 0 .25rem}
.feat-desc{font-size:.76rem;color:rgba(190,185,210,0.58);margin:0;line-height:1.5}
.prof-card{background:rgba(255,255,255,0.03);border-radius:14px;padding:1rem;margin-bottom:.5rem;position:relative;overflow:hidden}
.prof-card-def{border:1px solid rgba(205,140,80,0.45)}
.prof-card-norm{border:1px solid rgba(255,255,255,0.07)}
.prof-name{font-weight:600;font-size:1rem;color:#fff;margin:0 0 .15rem}
.prof-sub{font-size:.78rem;color:rgba(190,185,210,.55);margin:0}
.def-badge{display:inline-block;background:rgba(205,140,80,0.18);border:1px solid rgba(205,140,80,0.4);color:#d4944a;font-size:.66rem;padding:1px 7px;border-radius:10px;font-weight:600;margin-bottom:.35rem;animation:badge-pulse 3s ease-in-out infinite}
@keyframes badge-pulse{0%,100%{box-shadow:0 0 0 0 rgba(205,140,80,0)}50%{box-shadow:0 0 8px 2px rgba(205,140,80,0.25)}}
.prof-banner{background:linear-gradient(135deg,rgba(144,98,222,0.15),rgba(205,140,80,0.08));border:1px solid rgba(144,98,222,0.3);border-radius:14px;padding:1.2rem 1.5rem;margin-bottom:1.5rem}
.bottom-nav{display:none;position:fixed;bottom:0;left:0;right:0;z-index:9999;background:rgba(8,4,20,0.97);backdrop-filter:blur(20px);border-top:1px solid rgba(144,98,222,0.3);padding:6px 0 max(env(safe-area-inset-bottom),6px)}
.bottom-nav-inner{display:flex;justify-content:space-around;align-items:center;max-width:640px;margin:0 auto}
.bnav-btn{display:flex;flex-direction:column;align-items:center;gap:2px;padding:4px 8px;background:none;border:none;cursor:pointer;color:rgba(200,195,220,0.5);font-family:'Inter',sans-serif;font-size:.65rem;font-weight:500;min-width:52px;border-radius:8px;transition:all .2s;text-decoration:none}
.bnav-btn.active,.bnav-btn:hover{color:#c090e0;background:rgba(144,98,222,0.12)}
.bnav-icon{font-size:1.35rem;line-height:1}
@media(max-width:768px){.bottom-nav{display:block}.block-container{padding-bottom:6rem!important}}
#more-toggle{display:none}
.bnav-dropup{display:none;position:absolute;bottom:calc(100% + 15px);right:10px;background:rgba(8,4,20,0.97);backdrop-filter:blur(20px);border:1px solid rgba(144,98,222,0.3);border-radius:12px;padding:8px 0;flex-direction:column;gap:2px;box-shadow:0 -8px 25px rgba(0,0,0,0.6);z-index:10001;min-width:160px}
#more-toggle:checked~.bnav-dropup{display:flex;animation:slideUp .2s ease-out forwards}
@keyframes slideUp{from{opacity:0;transform:translateY(15px)}to{opacity:1;transform:translateY(0)}}
.dropup-item{color:rgba(200,195,220,0.7);text-decoration:none;padding:12px 18px;font-size:.88rem;display:flex;align-items:center;gap:12px;transition:all .2s;font-family:'Inter',sans-serif;font-weight:500}
.dropup-item:hover,.dropup-item.active{color:#c090e0;background:rgba(144,98,222,0.12)}
.more-label{display:flex;flex-direction:column;align-items:center;gap:2px;padding:4px 8px;background:none;border:none;cursor:pointer;color:rgba(200,195,220,0.5);font-family:'Inter',sans-serif;font-size:.65rem;font-weight:500;min-width:52px;border-radius:8px;transition:all .2s;margin:0}
.more-label:hover,#more-toggle:checked+.more-label,.more-label.active{color:#c090e0;background:rgba(144,98,222,0.12)}
.dropup-overlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;z-index:10000}
#more-toggle:checked~.dropup-overlay{display:block}
</style>""", unsafe_allow_html=True)


# ── Navigation ────────────────────────────────────────────────────────────────

def render_bottom_nav():
    main_items = [("🌌","Home","Dashboard"),("💬","Chat","Consultation Room"),("🔮","Oracle","The Oracle"),("🃏","Tarot","Mystic Tarot")]
    more_items = [("🌟","Horoscopes","Horoscopes"),("🔢","Numerology","Numerology"),("✋","Palmistry","Palm Reading"),("🪞","Face","Face Reading"),("📜","Kundli","Kundli"),("📖","Profiles","Saved Profiles")]

    nav_html = '<div class="bottom-nav"><div class="bottom-nav-inner" style="position:relative;">'
    for icon, label, page in main_items:
        active = "active" if st.session_state.nav_page == page else ""
        nav_html += f'<a class="bnav-btn {active}" target="_self" href="?p={page.replace(" ", "%20")}" title="{label}"><span class="bnav-icon">{icon}</span><span>{label}</span></a>'

    more_active = "active" if st.session_state.nav_page in ["Horoscopes","Numerology","Palm Reading","Face Reading","Kundli","Saved Profiles"] else ""
    nav_html += f'<input type="checkbox" id="more-toggle"><label for="more-toggle" class="more-label {more_active}" title="More"><span class="bnav-icon">☰</span><span>More</span></label>'
    nav_html += '<label for="more-toggle" class="dropup-overlay"></label>'
    nav_html += '<div class="bnav-dropup">'
    for icon, label, page in more_items:
        active = "active" if st.session_state.nav_page == page else ""
        nav_html += f'<a class="dropup-item {active}" target="_self" href="?p={page.replace(" ","%20")}"><span class="bnav-icon" style="font-size:1.2rem;">{icon}</span><span>{label}</span></a>'
    nav_html += '</div></div></div>'
    st.markdown(nav_html, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;margin-bottom:1.5rem;font-size:1.3rem;'>🪐 ASTRO SUITE beta</h2>", unsafe_allow_html=True)
        
        pages = [
            ("🌌 Dashboard", "Dashboard"),
            ("💬 Consult Room", "Consultation Room"),
            ("🔮 The Oracle", "The Oracle"),
            ("🃏 Mystic Tarot", "Mystic Tarot"),
            ("🌟 Horoscopes", "Horoscopes"),
            ("🔢 Numerology", "Numerology"),
            ("✋ Palm Reading", "Palm Reading"),
            ("🪞 Face Reading", "Face Reading"),
            ("📜 Kundli", "Kundli"),
            ("📖 Saved Profiles", "Saved Profiles")
        ]
        
        for label, page in pages:
            kind = "primary" if st.session_state.nav_page == page else "secondary"
            if st.button(label, use_container_width=True, type=kind, key=f"side_{page}"):
                st.session_state.nav_page = page
                components.html("""<script>setTimeout(function(){var b=window.parent.document.querySelector('button[aria-label="Collapse sidebar"]');if(b&&window.parent.innerWidth<=768)b.click();},80);</script>""", height=0, width=0)
                st.rerun()

        dp, _ = get_default_profile()
        if dp:
            st.markdown("---")
            st.markdown(f"<p style='font-size:.72rem;color:rgba(200,190,220,.5);margin:0'>⭐ My Profile</p><p style='font-size:.88rem;color:#e0d8f0;font-weight:600;margin:0'>{dp['name']}</p>", unsafe_allow_html=True)


# ── Tarot helpers ─────────────────────────────────────────────────────────────

def tarot_reversed_help():
    return ("Optional. When this is on, each drawn card has a 50/50 chance to appear upside down. "
            "In tarot, an upside-down card usually means the card's energy is blocked, delayed, hidden, "
            "or being felt internally. Leave this off for a simpler beginner reading where every card is upright.")


def render_tarot_overlay(cards, states, layout="three"):
    cards = list(cards or [])
    if not cards: return
    states = list(states or [])
    if len(states) < len(cards): states += ["Upright"] * (len(cards) - len(states))
    states = states[:len(cards)]
    n = len(cards)
    if layout not in {"one","three","ten"}:
        layout = "one" if n == 1 else ("ten" if n == 10 else "three")

    uid = "t" + secrets.token_hex(4)
    back_url = f"{TAROT_BASE}tarotrear.png"
    vid_desk = f"{TAROT_BASE}tarotvid.mp4"
    vid_mob  = f"{TAROT_BASE}tarotvideo.mp4"

    if layout == "ten":
        container_css = f".card-row-{uid}{{display:grid;grid-template-columns:repeat(5,1fr);grid-template-rows:repeat(2,auto);gap:2% 2%;width:74%;align-items:center;justify-items:center;}}.card-row-{uid} .t-card-wrapper-{uid}{{width:100%;}}"
        mobile_layout_css = f".card-row-{uid}{{width:82%;}}"
        rise_stagger, flip_stagger, flip_start = 0.14, 0.16, 1.15
    else:
        gap = "0" if layout == "one" else "4%"
        container_css = f".card-row-{uid}{{display:flex;justify-content:center;align-items:center;gap:{gap};width:100%;}}.card-row-{uid} .t-card-wrapper-{uid}{{width:25%;max-width:138px;}}"
        mobile_layout_css = f".card-row-{uid} .t-card-wrapper-{uid}{{width:28%;max-width:none;}}"
        rise_stagger, flip_stagger, flip_start = 0.4, 0.5, 1.5

    card_blocks = ""
    for i, (card, state) in enumerate(zip(cards, states)):
        front_url = f"{TAROT_BASE}{get_filename(card)}"
        rev_class = " reversed" if state == "Reversed" else ""
        card_blocks += f"""
<div class="t-card-wrapper-{uid}" style="--rise-delay:{0.15+(i*rise_stagger):.2f}s">
  <div class="t-card-inner-{uid}" style="--flip-delay:{flip_start+(i*flip_stagger):.2f}s">
    <div class="t-card-back-{uid}"></div>
    <div class="t-card-front-{uid}{rev_class}" style="background-image:url('{front_url}')" aria-label="{card}"></div>
  </div>
</div>"""

    scroll_delay = flip_start + (max(n-1, 0) * flip_stagger) + 1.1
    html = f"""<style>
.tarot-stage-{uid}{{position:relative;width:100%;max-width:550px;margin:0 auto 2rem;border-radius:16px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,.5);background:linear-gradient(45deg,#1a0f2e,#0c0814)}}
.vid-desktop-{uid},.vid-mobile-{uid}{{width:100%;display:block;object-fit:cover;opacity:.85}}
.vid-desktop-{uid}{{aspect-ratio:1440/1678}}.vid-mobile-{uid}{{display:none;aspect-ratio:24/41}}
.card-container-{uid}{{position:absolute;bottom:8%;width:100%;display:flex;justify-content:center;perspective:1000px;z-index:2}}
{container_css}
.t-card-wrapper-{uid}{{aspect-ratio:2/3;opacity:1;transform:translateY(0);animation:tarot-rise-{uid} .9s var(--rise-delay) cubic-bezier(.16,1,.3,1) both}}
.t-card-inner-{uid}{{width:100%;height:100%;position:relative;transform-style:preserve-3d;transform:rotateY(180deg);animation:tarot-flip-{uid} .8s var(--flip-delay) cubic-bezier(.34,1.56,.64,1) both}}
.t-card-front-{uid},.t-card-back-{uid}{{position:absolute;inset:0;width:100%;height:100%;backface-visibility:hidden;-webkit-backface-visibility:hidden;border-radius:8px;box-shadow:0 5px 15px rgba(0,0,0,.8);background-size:cover;background-position:center}}
.t-card-back-{uid}{{background-image:url('{back_url}');border:2px solid rgba(205,140,80,.5)}}
.t-card-front-{uid}{{transform:rotateY(180deg);border:2px solid rgba(205,140,80,.8)}}
.t-card-front-{uid}.reversed{{transform:rotateY(180deg) rotate(180deg)}}
.scroll-prompt-{uid}{{position:absolute;bottom:2%;width:100%;text-align:center;color:rgba(255,255,255,.9);font-family:'Space Grotesk',sans-serif;font-size:.95rem;letter-spacing:1px;opacity:1;text-shadow:0 2px 5px rgba(0,0,0,.9);pointer-events:none;animation:tarot-scroll-{uid} .8s {scroll_delay:.2f}s ease both;z-index:3}}
@keyframes tarot-rise-{uid}{{from{{opacity:0;transform:translateY(50px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes tarot-flip-{uid}{{from{{transform:rotateY(0deg)}}to{{transform:rotateY(180deg)}}}}
@keyframes tarot-scroll-{uid}{{from{{opacity:0}}to{{opacity:1}}}}
@media(max-width:768px){{.vid-desktop-{uid}{{display:none}}.vid-mobile-{uid}{{display:block}}.card-container-{uid}{{bottom:10%;}}{mobile_layout_css}}}
</style>
<div class="tarot-stage-{uid}">
  <video class="vid-desktop-{uid}" autoplay loop muted playsinline><source src="{vid_desk}" type="video/mp4"></video>
  <video class="vid-mobile-{uid}" autoplay loop muted playsinline><source src="{vid_mob}" type="video/mp4"></video>
  <div class="card-container-{uid}"><div class="card-row-{uid}">{card_blocks}</div></div>
  <div class="scroll-prompt-{uid}">The cards have spoken. Scroll down for your reading.</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)


# ── Profile form ──────────────────────────────────────────────────────────────

def render_profile_form(key_prefix, show_d60=True, default_from_profile=None):
    dp, dp_idx = get_default_profile()

    if st.session_state.db:
        method = st.radio("Source", ["Enter New Details","Saved Profile"], horizontal=True,
                          key=f"rad_{key_prefix}", label_visibility="collapsed")
    else:
        method = "Enter New Details"

    with st.container(border=True):
        if method == "Enter New Details":
            pre = default_from_profile or dp
            pt = datetime.strptime(pre["time"], "%H:%M").time() if pre else None
            pre_hr = pt.hour % 12 or 12 if pt else 12
            pre_mi = pt.minute if pt else 0
            pre_ampm = 1 if pt and pt.hour >= 12 else 0
            st.session_state[f"n_{key_prefix}"] = st.text_input("Name", value=pre["name"] if pre else "", key=f"wn_{key_prefix}")
            pre_date = date.fromisoformat(pre["date"]) if pre else date(2000, 1, 1)
            st.session_state[f"d_{key_prefix}"] = st.date_input("Date of Birth", pre_date, min_value=date(1850,1,1), max_value=date(2050,12,31), key=f"wd_{key_prefix}")
            t1, t2, t3 = st.columns(3)
            with t1: st.session_state[f"hr_{key_prefix}"] = st.number_input("Hour", 1, 12, pre_hr, key=f"whr_{key_prefix}")
            with t2: st.session_state[f"mi_{key_prefix}"] = st.number_input("Min", 0, 59, pre_mi, key=f"wmi_{key_prefix}")
            with t3: st.session_state[f"ampm_{key_prefix}"] = st.selectbox("AM/PM", ["AM","PM"], index=pre_ampm, key=f"wa_{key_prefix}")
            pre_place = pre["place"] if pre and pre["place"] != "Manual Coordinates" else ""
            u_place = st.text_input("Birth Place (City, Country)", value=pre_place, key=f"wp_{key_prefix}")
            st.session_state[f"p_{key_prefix}"] = u_place
            manual = st.checkbox("Enter coordinates manually", key=f"wman_{key_prefix}")
            st.session_state[f"man_{key_prefix}"] = manual
            if u_place.strip() and not manual:
                geo = geocode_place(u_place.strip())
                if geo: st.success(f"📍 {geo[2]}")
                else: st.warning("Not found — check spelling or use manual coordinates.")
            if manual:
                c1, c2, c3 = st.columns(3)
                pre_lat = pre["lat"] if pre else 0.0
                pre_lon = pre["lon"] if pre else 0.0
                pre_tz  = pre["tz"]  if pre else "Asia/Kolkata"
                with c1: st.session_state[f"lat_{key_prefix}"] = st.number_input("Lat", value=float(pre_lat), format="%.4f", key=f"wlat_{key_prefix}")
                with c2: st.session_state[f"lon_{key_prefix}"] = st.number_input("Lon", value=float(pre_lon), format="%.4f", key=f"wlon_{key_prefix}")
                with c3: st.session_state[f"tz_{key_prefix}"]  = st.text_input("Timezone", pre_tz, key=f"wtz_{key_prefix}")
            pre_gender = pre.get("gender", "M") if pre else "M"
            st.session_state[f"gender_{key_prefix}"] = st.radio("Gender", ["M","F"], index=0 if pre_gender == "M" else 1, key=f"wg_{key_prefix}", horizontal=True)
            st.session_state[f"save_{key_prefix}"]  = st.checkbox("💾 Save this person to My Saved Profiles", key=f"wsave_{key_prefix}")
            pre_exact = pre.get("exact_time", False) if pre else False
            st.session_state[f"exact_{key_prefix}"] = st.checkbox("Birth time is exact to the minute", value=pre_exact, key=f"wexact_{key_prefix}")
            return {"type":"new","idx":key_prefix}
        else:
            opts_raw = sorted_profile_options()
            if not opts_raw:
                return {"type":"empty_saved","idx":key_prefix}
            labels = ["— Select —"] + [
                f"{'⭐ ' if i==st.session_state.default_profile_idx else ''}{p['name']} ({format_date_ui(p['date'])})"
                for i, p in opts_raw
            ]
            sel = st.selectbox("Select Profile", labels, key=f"sel_{key_prefix}", label_visibility="collapsed")
            if sel != "— Select —":
                _, p = opts_raw[labels.index(sel) - 1]
                st.success(f"Loaded: **{p['name']}** 📍 {p['place'].split(',')[0]} ({p.get('gender','M')})")
                st.session_state[f"exact_{key_prefix}"] = p.get("exact_time", False)
                return {"type":"saved","data":p,"idx":key_prefix}
            return {"type":"empty_saved","idx":key_prefix}


def resolve_profile(item):
    i = item["idx"]
    if item["type"] == "saved":
        return item["data"], item["data"].get("exact_time", False)
    if item["type"] == "empty_saved":
        st.error("Please select a valid profile.")
        st.stop()

    u_name = st.session_state.get(f"n_{i}", "")
    if not u_name.strip():
        st.error("Enter a name.")
        st.stop()

    hr   = st.session_state.get(f"hr_{i}",   12)
    mi   = st.session_state.get(f"mi_{i}",   0)
    am   = st.session_state.get(f"ampm_{i}", "AM")
    h24  = (hr + 12 if am == "PM" and hr != 12 else 0 if am == "AM" and hr == 12 else hr)
    u_time = time(h24, mi)
    u_date = st.session_state.get(f"d_{i}", date(2000, 1, 1))
    is_manual = st.session_state.get(f"man_{i}", False)

    if is_manual:
        fl  = st.session_state.get(f"lat_{i}", 0.0)
        flon= st.session_state.get(f"lon_{i}", 0.0)
        ftz = st.session_state.get(f"tz_{i}",  "")
        if fl == 0.0 and flon == 0.0: st.error("Enter valid coordinates."); st.stop()
        if not ftz.strip():           st.error("Enter a timezone.");         st.stop()
        fp = "Manual Coordinates"
    else:
        u_place = st.session_state.get(f"p_{i}", "")
        if not u_place.strip(): st.error("Enter a birth place."); st.stop()
        geo = geocode_place(u_place.strip())
        if not geo: st.error(f"'{u_place}' not found."); st.stop()
        fl, flon, fp = geo
        ftz = timezone_for_latlon(fl, flon)
        if not ftz: st.error("Timezone detection failed."); st.stop()

    u_gender = st.session_state.get(f"gender_{i}", "M")
    u_exact  = st.session_state.get(f"exact_{i}",  False)
    prof = {"name":u_name.strip(),"date":u_date.isoformat(),"time":u_time.strftime("%H:%M"),
            "place":fp,"lat":fl,"lon":flon,"tz":ftz,"gender":u_gender,"exact_time":u_exact}

    if st.session_state.get(f"save_{i}", False) and not is_duplicate_in_db(prof):
        st.session_state.db.append(prof)
        sync_db()

    return prof, u_exact


# ── Streaming AI chat (used by every page) ────────────────────────────────────

def stream_ai_with_followup(prompt, memory_key, spinner_text="Interpreting...", knowledge_files=None, preferred_model=None, image_b64=None, show_share_buttons=True, hide_user_prompt=False):
    """Universal AI Streamer: Now supports entirely hiding the user's chat bubble."""
    import streamlit as st
    from shared.ai.gemini_client import generate_content_with_fallback
    
    if memory_key not in st.session_state:
        st.session_state[memory_key] = []
        
    for msg in st.session_state[memory_key]:
        # Only render the message if it's not flagged as hidden
        if not msg.get("hidden", False):
            with st.chat_message(msg["role"], avatar="🪐" if msg["role"]=="model" else "👤"):
                st.markdown(msg.get("display", msg["parts"][-1]))
            
    # Save the prompt to memory, but mark it as hidden if requested
    st.session_state[memory_key].append({"role": "user", "parts": [prompt], "display": prompt, "hidden": hide_user_prompt})
    
    if not hide_user_prompt:
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
    with st.chat_message("model", avatar="🪐"):
        with st.spinner(spinner_text):
            response_placeholder = st.empty()
            full_response = ""
            
            ai_output = generate_content_with_fallback(prompt)
            if isinstance(ai_output, str):
                full_response = ai_output
                response_placeholder.markdown(full_response)
            else:
                for chunk in ai_output:
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
            
    st.session_state[memory_key].append({"role": "model", "parts": [full_response], "hidden": False})
    
    if st.session_state.get(memory_key):
        if show_share_buttons: 
            full_text = "\n\n---\n\n".join(
                msg["parts"][-1] for msg in st.session_state[memory_key] if msg["role"] == "model"
            )
            render_share_buttons(full_text, title=APP_NAME, image_b64=image_b64)
            
    return full_response