"""
ui_streamlit/views/kundli.py
============================

Kundli page — two modes:

    Free Kundli   — full in-app scrollable chart (D1 + all 15 other vargas,
                    Avakahada, Panchanga, planetary positions, houses,
                    Vimshottari MD-AD, yogas, doshas, Shadbala, SAV,
                    Sudarshan, remedies). Optional PDF download.

    Premium PDF   — themed PDF with cover, AI narrative, decade
                    predictions, Western appendix. Free in this prototype;
                    paid in the mobile app.

All heavy lifting lives in math_engine.kundli + pdf_engine — this view is
a thin Streamlit shim. When the mobile app ships, the equivalent layer
there imports the same backend.
"""

import streamlit as st
import base64

from math_engine.kundli import (
    BirthData, compute_chart, yoga_audit, sade_sati_timeline,
)
from pdf_engine import build_kundli_pdf, THEMES
from pdf_engine.kundli_pdf import render as render_chart_svg
from features.kundli.content import (
    generate_kundli_content, is_available as ai_is_available,
)

from ui_streamlit.components import render_profile_form, resolve_profile


CHART_STYLES = [
    ("north_indian", "🪔 North Indian (Diamond)",
     "Lagna at the top center; signs rotate clockwise. Most common in North & Central India."),
    ("south_indian", "🛕 South Indian (Square)",
     "Fixed sign positions; planets move. Most common in Tamil Nadu, Karnataka, Andhra & Kerala."),
    ("east_indian", "🌺 East Indian (Bengali)",
     "Variation of South with corner diamonds. Common in Bengal & Odisha."),
]

LANGUAGES = [
    ("en", "English"),
    ("hi", "हिन्दी (Hindi)"),
    ("ta", "தமிழ் (Tamil)"),
    ("te", "తెలుగు (Telugu)"),
    ("mr", "मराठी (Marathi)"),
    ("bn", "বাংলা (Bengali)"),
    ("gu", "ગુજરાતી (Gujarati)"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Theme card (Premium)
# ─────────────────────────────────────────────────────────────────────────────

def _theme_card(slug: str, theme: dict, selected: bool) -> str:
    border = f"3px solid {theme['accent']}" if selected else f"1px solid {theme['muted']}"
    return f"""
    <div style="
      border: {border};
      border-radius: 12px;
      padding: 14px 16px;
      background: {theme['paper']};
      color: {theme['ink']};
      margin: 4px 0;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    ">
      <div style="font-family: 'Cinzel', serif; font-size: 1.1rem;
                  color: {theme['primary']}; letter-spacing: 0.08em;">
        {theme['name']}
      </div>
      <div style="font-style: italic; font-size: 0.85rem; color: {theme['muted']}; margin-top: 4px;">
        {theme.get('cover_subtitle', '')}
      </div>
    </div>
    """


# ─────────────────────────────────────────────────────────────────────────────
# Free Kundli — inline scrollable view
# ─────────────────────────────────────────────────────────────────────────────

# Subtle dark-theme-friendly palette for the inline SVG charts.
_FREE_SVG_THEME = {
    "frame_color":        "#D4AF37",
    "frame_width":        2,
    "bg_color":           "#1A1A24",
    "house_text":         "#C8B98A",
    "sign_text":          "#C8B98A",
    "planet_text":        "#F4ECD8",
    "muted":              "#8A7E5E",
    "title_color":        "#D4AF37",
    "lagna_marker_color": "#FF6B6B",
    "retro_color":        "#FF6B6B",
    "planet_font_size":   14,
    "house_font_size":    10,
    "title_font_size":    14,
}


def _svg_centered(svg_str: str, max_width: int = 380) -> str:
    """Wrap an SVG in a centered flex container so Streamlit doesn't full-width it."""
    return (f'<div style="display:flex;justify-content:center;'
            f'align-items:center;margin:8px 0;">'
            f'<div style="max-width:{max_width}px;width:100%;">{svg_str}</div></div>')


def _render_free_kundli(chart, chart_style: str):
    """Render the complete free in-app kundli (no PDF needed)."""

    bd = chart.birth_data
    retrograde = {p for p, pp in chart.planets.items() if pp.is_retrograde}
    combust    = {p for p, pp in chart.planets.items() if pp.is_combust}
    d1_degrees = {p: pp.longitude % 30 for p, pp in chart.planets.items()}

    # ── Identity strip ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center; padding: 10px 0 4px;">
      <div style="font-family:'Cinzel',serif; font-size:1.4rem;
                  color:#D4AF37; letter-spacing:0.1em;">{bd.name}</div>
      <div style="opacity:0.7; font-size:0.9rem;">
        {bd.date.strftime('%d %B %Y')} · {bd.time.strftime('%H:%M')} · {bd.place}
      </div>
      <div style="opacity:0.55; font-size:0.85rem; margin-top:4px;">
        <strong>{chart.lagna.sign} Lagna</strong> · Moon in {chart.planets['Moon'].sign}
        ({chart.planets['Moon'].nakshatra} Pada {chart.planets['Moon'].pada}) ·
        Sun in {chart.planets['Sun'].sign} ·
        Atmakaraka: {chart.chara_karakas.atmakaraka}
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── D1 (Lagna chart) — hero placement, big size, with caption ──────────
    st.markdown(
        f"<h3 style='text-align:center;color:#D4AF37;margin-bottom:4px;'>"
        f"🪔 Lagna Chart (D1 Rasi)</h3>"
        f"<div style='text-align:center;opacity:0.65;font-size:0.85rem;"
        f"margin-bottom:10px;'>The foundation chart — read this for "
        f"identity, life path, personality, and overall destiny. "
        f"Every other section refers back to this.</div>",
        unsafe_allow_html=True,
    )
    d1 = chart.divisional_charts.get(1)
    if d1:
        svg = render_chart_svg(
            style=chart_style,
            lagna_sign_idx=d1.lagna_sign_index,
            planet_signs=d1.planet_signs,
            theme=_FREE_SVG_THEME,
            size=460, title="",
            retrograde=retrograde, combust=combust,
            planet_degrees=d1_degrees,   # every planet's degree shown
            show_house_numbers=True,     # H1..H12 visible per cell
        )
        st.markdown(_svg_centered(svg, 460), unsafe_allow_html=True)
        st.caption(
            "Planets shown with degree within sign (e.g. 'Mo 16°'). "
            "House numbers H1–H12 labelled per cell. R = retrograde, "
            "© = combust. Includes outer planets (Ur, Ne, Pl) as modern additions."
        )

    # ── Panchanga + Functional Profile ─────────────────────────────────────
    pan_col, fp_col = st.columns(2)
    with pan_col:
        st.markdown("#### 🌗 Panchanga at Birth")
        pan = chart.panchanga
        st.markdown(f"""
        - **Tithi** — {pan.tithi}
        - **Paksha** — {pan.paksha}
        - **Vara** — {pan.weekday}
        - **Nakshatra** — {chart.planets['Moon'].nakshatra} (Pada {chart.planets['Moon'].pada})
        - **Yoga** — {pan.yoga}
        - **Karana** — {pan.karana}
        """)
    with fp_col:
        st.markdown("#### 🧭 Functional Profile (for your Lagna)")
        f = chart.functional
        if f.yogakarakas:
            st.markdown(f"- **Yogakaraka(s):** {', '.join(f.yogakarakas)}")
        if f.benefics:
            st.markdown(f"- **Functional Benefics:** {', '.join(f.benefics)}")
        if f.malefics:
            st.markdown(f"- **Functional Malefics:** {', '.join(f.malefics)}")
        if f.neutrals:
            st.markdown(f"- **Neutrals:** {', '.join(f.neutrals)}")

    # ── Avakahada Chakra ────────────────────────────────────────────────────
    if chart.nakshatra_profile:
        st.markdown("#### 🪷 Avakahada Chakra")
        rows = chart.nakshatra_profile.get("avakahada_chakra", [])
        if rows:
            half = (len(rows) + 1) // 2
            ac1, ac2 = st.columns(2)
            with ac1:
                for k, v in rows[:half]:
                    st.markdown(f"**{k}:** {v}")
            with ac2:
                for k, v in rows[half:]:
                    st.markdown(f"**{k}:** {v}")

    st.markdown("---")

    # ── Planetary positions table ───────────────────────────────────────────
    st.markdown("#### 🌟 Planetary Positions")
    pp_rows = []
    for pname, pp in chart.planets.items():
        flags = []
        if pp.is_retrograde: flags.append("R")
        if pp.is_combust:    flags.append("C")
        if pp.dignity:       flags.append(pp.dignity[0])
        pp_rows.append({
            "Planet":    pname,
            "Sign":      pp.sign,
            "House":     pp.house,
            "Degrees":   pp.longitude_dms,
            "Nakshatra": f"{pp.nakshatra} (P{pp.pada})",
            "Nak Lord":  pp.nakshatra_lord,
            "Sub-Lord":  pp.sub_lord,
            "Dignity":   pp.dignity or "—",
            "Flags":     " · ".join(flags) if flags else "—",
        })
    st.dataframe(pp_rows, use_container_width=True, hide_index=True)

    # ── 16 Divisional Charts in a 4-column grid ────────────────────────────
    with st.expander("🔮 All 16 Divisional Charts (Shodashavarga)", expanded=False):
        st.caption("Each divisional chart focuses on one specific life area. "
                   "Click any chart to read its purpose below.")
        items = list(chart.divisional_charts.items())
        for i in range(0, len(items), 4):
            row = items[i:i+4]
            cols = st.columns(4)
            for col, (n, varga) in zip(cols, row):
                with col:
                    svg = render_chart_svg(
                        style=chart_style,
                        lagna_sign_idx=varga.lagna_sign_index,
                        planet_signs=varga.planet_signs,
                        theme=_FREE_SVG_THEME,
                        size=220, title="",
                        retrograde=retrograde, combust=combust,
                        planet_degrees=(d1_degrees if n == 1 else None),
                        show_house_numbers=True,
                    )
                    st.markdown(
                        f'<div style="text-align:center;font-size:0.85rem;'
                        f'color:#D4AF37;margin-bottom:4px;">D{n} — {varga.name.split(" ", 1)[1]}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(_svg_centered(svg, 220), unsafe_allow_html=True)
                    st.caption(varga.purpose)

    # ── Vimshottari Dasha ──────────────────────────────────────────────────
    vim = chart.dashas.get("Vimshottari") if chart.dashas else None
    if vim and vim.periods:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo(bd.tz))
        st.markdown("#### 🌀 Vimshottari Dasha")
        # Current MD
        current_md = next((md for md in vim.periods if md.start <= now <= md.end), None)
        if current_md:
            elapsed_yrs = (now - current_md.start).days / 365.25
            total_yrs = (current_md.end - current_md.start).days / 365.25
            st.markdown(
                f"**Currently running:** {current_md.lord} Mahadasha "
                f"({current_md.start.strftime('%d %b %Y')} → "
                f"{current_md.end.strftime('%d %b %Y')}) — "
                f"{elapsed_yrs:.1f} of {total_yrs:.1f} years elapsed."
            )
            # Current AD
            current_ad = next((ad for ad in current_md.children
                               if ad.start <= now <= ad.end), None)
            if current_ad:
                st.markdown(
                    f"**Current Antardasha:** {current_md.lord}–{current_ad.lord} "
                    f"({current_ad.start.strftime('%d %b %Y')} → "
                    f"{current_ad.end.strftime('%d %b %Y')})"
                )
        # MD timeline table
        md_rows = []
        for md in vim.periods[:9]:
            md_rows.append({
                "Mahadasha": md.lord,
                "Start": md.start.strftime("%d %b %Y"),
                "End": md.end.strftime("%d %b %Y"),
                "Duration (yrs)": round((md.end - md.start).days / 365.25, 2),
                "Status": ("Past" if md.end < now else
                           "Active" if md.start <= now <= md.end else "Future"),
            })
        st.dataframe(md_rows, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Yogas — SAME FORMAT AS DOSHAS: inline name + category + description,
    #            then full audit table at the end. NOT in expanders. ───────
    try:
        audit_yogas = yoga_audit(chart)
    except Exception:
        audit_yogas = []
    present_yogas = [y for y in audit_yogas if y["present"]]

    if present_yogas:
        st.markdown(f"#### ✨ Yogas — {len(present_yogas)} active")
        for y in present_yogas:
            st.markdown(
                f"**{y['name']}** · "
                f'<span style="color:#D4AF37">{y["category"]}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(f"_{y['description']}_")
            st.markdown("")  # spacing

    # Audit shows only the yogas PRESENT in this chart (user request).
    if present_yogas:
        with st.expander(
            f"Yoga audit — {len(present_yogas)} present in your chart",
            expanded=False,
        ):
            y_rows = []
            for y in present_yogas:
                y_rows.append({
                    "Yoga": y["name"].replace(" Yoga", ""),
                    "Category": y["category"],
                    "Note": y["description"] if y["description"] != "—" else "",
                })
            st.dataframe(y_rows, use_container_width=True, hide_index=True)

    # ── Doshas (audit + active) ────────────────────────────────────────────
    active = [d for d in chart.doshas if d.present]
    if active:
        st.markdown(f"#### ⚡ Doshas — {len(active)} active")
        for d in active:
            sev_color = {"full":"#FF6B6B","partial":"#F0A500",
                         "cancelled":"#5BC0BE","varies":"#A4A4F4"}.get(d.severity, "#999")
            st.markdown(
                f"**{d.name}** · "
                f'<span style="color:{sev_color}">Severity: {d.severity}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(f"_{d.cause}_")
            if d.cancellations:
                st.caption("Cancellations: " + " · ".join(d.cancellations))
            st.markdown("")

    # Audit shows only the doshas PRESENT in this chart.
    if active:
        with st.expander(
            f"Dosha audit — {len(active)} present in your chart",
            expanded=False,
        ):
            d_rows = []
            for d in active:
                d_rows.append({
                    "Dosha": d.name,
                    "Severity": d.severity,
                    "Cause": d.cause[:120] + ("…" if len(d.cause) > 120 else ""),
                })
            st.dataframe(d_rows, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Sade Sati timeline ─────────────────────────────────────────────────
    try:
        sade_windows = sade_sati_timeline(chart, years_back=40, years_forward=25)
    except Exception:
        sade_windows = []
    if sade_windows:
        from datetime import datetime as _dt
        from zoneinfo import ZoneInfo as _Tz
        now = _dt.now(_Tz(bd.tz))
        current = [w for w in sade_windows if w["is_current"]]
        st.markdown("#### 🌑 Sade Sati Timeline")
        if current:
            cw = current[0]
            end_label = cw["end"].strftime("%d %b %Y") if cw["end"] else "ongoing"
            st.markdown(
                f"**Currently in Sade Sati — {cw['phase']}**  \n"
                f"Saturn is transiting **{cw['sign_name']}** "
                f"(from {cw['start'].strftime('%d %b %Y')} → {end_label}). "
            )
        else:
            past_recent = [w for w in sade_windows
                           if w["end"] and w["end"] < now]
            future = [w for w in sade_windows if w["start"] > now]
            note = "**Not currently in Sade Sati.**"
            if past_recent:
                last = past_recent[-1]
                note += (f"  Last phase ended "
                         f"{last['end'].strftime('%b %Y')} "
                         f"({last['phase']}).")
            if future:
                nxt = future[0]
                note += (f"  Next Sade Sati phase begins "
                         f"{nxt['start'].strftime('%b %Y')} "
                         f"({nxt['phase']}).")
            st.markdown(note)

        # Full timeline table
        with st.expander(f"Full Sade Sati timeline "
                          f"({len(sade_windows)} phase windows, -40y to +25y)",
                          expanded=False):
            ss_rows = []
            for w in sade_windows:
                end_str = w["end"].strftime("%d %b %Y") if w["end"] else "—"
                status = ("Active" if w["is_current"]
                          else "Past" if (w["end"] and w["end"] < now)
                          else "Future")
                ss_rows.append({
                    "Phase":     w["phase"],
                    "Saturn in": w["sign_name"],
                    "Start":     w["start"].strftime("%d %b %Y"),
                    "End":       end_str,
                    "Status":    status,
                })
            st.dataframe(ss_rows, use_container_width=True, hide_index=True)
            st.caption("Saturn completes one orbit every ~29.5 years, so most "
                       "people experience 2-3 Sade Sati cycles in a lifetime. "
                       "Each cycle lasts ~7.5 years, divided into three "
                       "~2.5-year phases (Rising · Peak · Setting).")

    # ── Shadbala ────────────────────────────────────────────────────────────
    if chart.shadbala:
        st.markdown("#### 💪 Shadbala — Six-Fold Strength")
        sb_rows = []
        sb = chart.shadbala
        for p, rupas in sb["totals"].items():
            minimum = sb["minimums"].get(p, "—")
            status = ("✓ Strong" if p in sb["strong"] else
                      "✗ Weak"   if p in sb["weak"]   else "— Neutral")
            sb_rows.append({
                "Planet": p,
                "Total (Rupas)": f"{rupas:.2f}",
                "Minimum Required": minimum,
                "Status": status,
                "Vimshopaka (max 20)": f"{sb['vimshopaka'].get(p, 0):.2f}",
            })
        st.dataframe(sb_rows, use_container_width=True, hide_index=True)
        st.markdown(
            f"**Strongest:** {sb['strongest'][0]} ({sb['strongest'][1]:.2f} Rupas) · "
            f"**Weakest:** {sb['weakest'][0]} ({sb['weakest'][1]:.2f} Rupas)"
        )

    # ── Ashtakavarga (SAV grid) ─────────────────────────────────────────────
    if chart.ashtakavarga:
        st.markdown("#### 🎯 Sarvashtakavarga (SAV) — by House")
        sav = chart.ashtakavarga.get("sav_by_house", [])
        if sav and len(sav) == 12:
            sav_cols = st.columns(12)
            for h in range(1, 13):
                with sav_cols[h-1]:
                    bindus = sav[h-1]
                    intensity = min(bindus / 56.0, 1.0)
                    bg = f"rgba(212, 175, 55, {intensity:.2f})"
                    st.markdown(
                        f'<div style="text-align:center;padding:8px 0;border-radius:6px;'
                        f'background:{bg};border:1px solid #D4AF37;">'
                        f'<div style="font-size:0.7rem;opacity:0.7;">H{h}</div>'
                        f'<div style="font-size:1.1rem;font-weight:bold;">{bindus}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
            st.caption("Each house's strength via Sarvashtakavarga bindus (0-56). "
                       "Higher = more favourable for that house's significations.")

    # ── Sudarshan Chakra ────────────────────────────────────────────────────
    if chart.sudarshan_chakra:
        sc = chart.sudarshan_chakra
        with st.expander("🌀 Sudarshan Chakra — triple view (Lagna · Moon · Sun)", expanded=False):
            st.caption("Reads each planet's house from three reference points "
                       "simultaneously. Triple-strong = the planet manifests "
                       "fully; triple-weak = needs conscious effort.")
            sc_rows = []
            for p, v in sc["planet_views"].items():
                tag = ("★ Triple-Strong" if p in sc["triple_strong"]
                       else "✗ Triple-Weak" if p in sc["triple_weak"] else "—")
                sc_rows.append({
                    "Planet": p,
                    "From Lagna": f"H{v['from_lagna']}",
                    "From Moon":  f"H{v['from_moon']}",
                    "From Sun":   f"H{v['from_sun']}",
                    "": tag,
                })
            st.dataframe(sc_rows, use_container_width=True, hide_index=True)

    # ── Remedies summary ───────────────────────────────────────────────────
    if chart.remedies:
        rem = chart.remedies
        st.markdown("#### 🪔 Remedies — Top Priorities")
        priority = rem.get("priority_planets", [])[:3]
        if priority:
            st.markdown(f"**Focus planets:** {' · '.join(priority)}")
        st.markdown("**Daily practice:**")
        for line in rem.get("daily_practice", []):
            st.markdown(f"- {line}")
        with st.expander("Per-planet remedies (Beej mantra, ratna, yantra, daan...)",
                          expanded=False):
            for p in priority:
                info = rem.get("per_planet", {}).get(p, {})
                if not info: continue
                ratna = info.get("ratna", {})
                st.markdown(f"##### {p}")
                st.markdown(f"- **Beej Mantra:** _{info.get('beej_mantra','—')}_ "
                            f"(japa {info.get('japa_count','—')})")
                st.markdown(f"- **Ratna:** {ratna.get('primary','—')} "
                            f"(substitute: {ratna.get('substitute','—')}) — "
                            f"{ratna.get('finger','—')} finger, "
                            f"{ratna.get('day_to_wear','—')}")
                st.markdown(f"- **Yantra:** {info.get('yantra','—')} · "
                            f"**Rudraksha:** {info.get('rudraksha','—')}")
                st.markdown(f"- **Daan ({info.get('daan_day','—')}):** "
                            f"{', '.join(info.get('daan',[]))}")
                st.markdown("")

    st.markdown("---")

    # ── Bhava Bala (House Strength) ────────────────────────────────────────
    if chart.bhava_bala:
        st.markdown("#### 🏠 Bhava Bala — House Strength")
        st.caption("Composite strength of each of the 12 houses, derived from "
                   "Sarvashtakavarga bindus, the house-lord's own Shadbala, and "
                   "the effect of planets occupying or aspecting the house.")
        bb_cols = st.columns(12)
        for h in range(1, 13):
            with bb_cols[h-1]:
                v = chart.bhava_bala.get(h, 0)
                norm = max(0, min(v / 12.0, 1.0))
                bg = f"rgba(212, 175, 55, {norm:.2f})"
                st.markdown(
                    f'<div style="text-align:center;padding:8px 0;border-radius:6px;'
                    f'background:{bg};border:1px solid #D4AF37;">'
                    f'<div style="font-size:0.7rem;opacity:0.7;">H{h}</div>'
                    f'<div style="font-size:1.0rem;font-weight:bold;">{v:.1f}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # ── Lucky Factors (from remedies + nakshatra profile) ──────────────────
    if chart.remedies and chart.nakshatra_profile:
        st.markdown("#### 🍀 Your Lucky Factors")
        np_data = chart.nakshatra_profile
        rem = chart.remedies
        # Pick the strongest/most-supportive planet for the native
        sb = chart.shadbala or {}
        focus_planet = (rem.get("priority_planets", []) or [None])[0]
        # Lucky day = focus planet's weekday
        from math_engine.kundli import PLANET_REMEDIES
        focus_info = PLANET_REMEDIES.get(focus_planet, {}) if focus_planet else {}

        lk1, lk2, lk3 = st.columns(3)
        with lk1:
            st.markdown(f"**Naam-akshar (Name letter):** {np_data.get('naam_akshar','—')}")
            st.markdown(f"**Gana:** {np_data.get('gana','—')}")
            st.markdown(f"**Yoni:** {np_data.get('yoni',['—','—'])[0]} ({np_data.get('yoni',['—','—'])[1] if np_data.get('yoni') else '—'})")
        with lk2:
            st.markdown(f"**Nadi:** {np_data.get('nadi','—')}")
            st.markdown(f"**Varna:** {np_data.get('varna','—')}")
            st.markdown(f"**Vashya:** {np_data.get('vashya','—')}")
        with lk3:
            st.markdown(f"**Tatva (Element):** {np_data.get('tatva','—')}")
            st.markdown(f"**Guna:** {np_data.get('guna','—')}")
            if focus_planet:
                st.markdown(f"**Focus planet:** {focus_planet} (deity: {focus_info.get('deity','—')})")
        if focus_info:
            st.caption(
                f"Day: {focus_info.get('vrat','—')} · "
                f"Colour: {', '.join(focus_info.get('colors', ['—']))} · "
                f"Metal: {focus_info.get('ratna', {}).get('metal','—')} · "
                f"Gemstone: {focus_info.get('ratna', {}).get('primary','—')}"
            )

    # ── Manglik & Kaal Sarp dedicated cards (most important doshas) ────────
    mangal = next((d for d in chart.doshas if "Mangal" in d.name), None)
    kaal = next((d for d in chart.doshas if "Kaal Sarp" in d.name), None)
    if mangal:
        st.markdown("#### 🔴 Manglik (Mangal Dosha) Analysis")
        if mangal.present:
            sev_color = {"full":"#FF6B6B","partial":"#F0A500","cancelled":"#5BC0BE"}.get(mangal.severity, "#999")
            st.markdown(
                f'**Status:** <span style="color:{sev_color}">Present · Severity: {mangal.severity}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                "Mars (Mangal) sits in a house that classically creates friction "
                "in married life — slowing matchmaking, requiring more patience "
                "from the partner, or sometimes triggering health watchpoints for "
                "spouses. The traditional approach: marriage to another Manglik, "
                "or specific remedies before the wedding (Kumbh Vivah, Hanuman "
                "Chalisa daily, Tuesday fasts)."
            )
            st.caption(f"Detection: {mangal.cause}")
            if mangal.cancellations:
                st.success("Mitigations present: " + " · ".join(mangal.cancellations))
        else:
            st.success("**No Manglik dosha** — Mars sits in a benign house for marriage.")
            st.caption(f"Detection rule: {mangal.cause}")

    if kaal:
        st.markdown("#### 🐍 Kaal Sarp Yoga Analysis")
        if kaal.present:
            sev_color = {"full":"#FF6B6B","partial":"#F0A500"}.get(kaal.severity, "#999")
            st.markdown(
                f"**Type:** {kaal.name} · "
                f'<span style="color:{sev_color}">Severity: {kaal.severity}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                "All seven classical planets sit on one side of the Rahu–Ketu axis, "
                "creating a karmic 'compressed' pattern. The native often feels life "
                "moves in waves of intensity — long periods of effort followed by "
                "breakthrough moments. The specific Kaal Sarp variant shapes which "
                "life area is most affected."
            )
            st.caption(f"Detection: {kaal.cause}")
            if kaal.cancellations:
                st.success("Mitigations: " + " · ".join(kaal.cancellations))
        else:
            st.success("**No Kaal Sarp yoga** — planets distributed on both sides of the Rahu–Ketu axis.")

    # ── Friendship Table (compatibility between planets) ────────────────────
    with st.expander("🤝 Planetary Friendship Table (Naisargika)", expanded=False):
        st.caption("Classical permanent friendship — who supports whom by nature. "
                   "Used when reading dasha sub-period results.")
        friendship = {
            "Sun":     {"friend": ["Moon","Mars","Jupiter"], "enemy": ["Venus","Saturn"], "neutral": ["Mercury"]},
            "Moon":    {"friend": ["Sun","Mercury"], "enemy": [], "neutral": ["Mars","Jupiter","Venus","Saturn"]},
            "Mars":    {"friend": ["Sun","Moon","Jupiter"], "enemy": ["Mercury"], "neutral": ["Venus","Saturn"]},
            "Mercury": {"friend": ["Sun","Venus"], "enemy": ["Moon"], "neutral": ["Mars","Jupiter","Saturn"]},
            "Jupiter": {"friend": ["Sun","Moon","Mars"], "enemy": ["Mercury","Venus"], "neutral": ["Saturn"]},
            "Venus":   {"friend": ["Mercury","Saturn"], "enemy": ["Sun","Moon"], "neutral": ["Mars","Jupiter"]},
            "Saturn":  {"friend": ["Mercury","Venus"], "enemy": ["Sun","Moon","Mars"], "neutral": ["Jupiter"]},
        }
        fr_rows = []
        for p in ("Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"):
            f = friendship[p]
            fr_rows.append({
                "Planet":  p,
                "Friends": ", ".join(f["friend"]) or "—",
                "Enemies": ", ".join(f["enemy"]) or "—",
                "Neutral": ", ".join(f["neutral"]) or "—",
            })
        st.dataframe(fr_rows, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # AI PERSONALIZED READINGS — at the END, behind a button (only loads if
    # the user explicitly asks for it; otherwise no AI cost is incurred)
    # ════════════════════════════════════════════════════════════════════════
    if ai_is_available():
        st.markdown("#### 🔮 Personalised AI Readings")
        st.caption(
            "**Optional.** AI-generated paragraphs based on YOUR chart's "
            "specific placements — Career, Health, Marriage, Wealth, etc. "
            "These are not generic horoscopes. Click the button below to "
            "generate. **Cost ~₹0.10 per kundli.**"
        )

        ai_cache_key = f"_ai_content::{chart.birth_data.name}::{chart.birth_data.date}::{chart.birth_data.time}"
        already_loaded = (
            st.session_state.get("_ai_content_key") == ai_cache_key
            and st.session_state.get("_ai_content")
        )

        if not already_loaded:
            if st.button("🔮 Generate My Personalised AI Readings (~₹0.10)",
                          type="primary", use_container_width=True,
                          key="ai_btn_free"):
                with st.spinner("Reading your chart with AI… ~15 seconds"):
                    try:
                        ai_content = generate_kundli_content(
                            chart, tier="free", language="en",
                        )
                        st.session_state._ai_content_key = ai_cache_key
                        st.session_state._ai_content = ai_content
                        st.rerun()
                    except Exception as e:
                        st.error(f"AI readings failed: {type(e).__name__}: {e}")
        else:
            ai_content = st.session_state.get("_ai_content", {})
            st.success("AI readings loaded for this chart.")
            topic_titles = {
                "personality": "🧘 Your Personality & Character",
                "career":      "💼 Career & Profession",
                "health":      "🌿 Health & Constitution",
                "wealth":      "💰 Wealth & Finance",
                "marriage":    "💑 Marriage & Partnership",
                "education":   "📚 Education & Learning",
                "family":      "👪 Family & Relationships",
                "spirituality":"🪔 Spirituality & Inner Path",
            }
            for topic, title in topic_titles.items():
                prose = ai_content.get(topic)
                if not prose:
                    continue
                with st.expander(title, expanded=False):
                    st.markdown(prose)
            if st.button("🔄 Regenerate AI Readings (~₹0.10)",
                          use_container_width=True, key="ai_regen_free"):
                st.session_state._ai_content_key = None
                st.session_state._ai_content = None
                st.rerun()

    st.markdown("---")

    # ── PDF download offer ─────────────────────────────────────────────────
    st.markdown("#### 📥 Take it offline")
    st.caption("Generate a simple PDF of this free kundli (one click, no theming, "
               "no AI narrative — for the full themed premium PDF, see the "
               "**Premium PDF** tab).")

    if st.button("Generate Free Kundli PDF",
                  type="secondary", use_container_width=True,
                  key="free_kundli_pdf_btn"):
        with st.spinner("Building PDF…"):
            try:
                data = build_kundli_pdf(
                    chart, theme_name="classic_vedic",
                    chart_style=chart_style, language="en",
                    include_western_appendix=False,
                    include_ai_narrative=False,
                )
                is_pdf = data[:4] == b"%PDF"
                ext = "pdf" if is_pdf else "html"
                fname = f"{bd.name.replace(' ','_')}_FreeKundli.{ext}"
                mime = "application/pdf" if is_pdf else "text/html"
                st.success(f"Generated ({len(data):,} bytes).")
                if not is_pdf:
                    st.warning("WeasyPrint unavailable — got HTML; print to PDF from your browser.")
                st.download_button(
                    f"⬇️ Download {ext.upper()}",
                    data=data, file_name=fname, mime=mime,
                    use_container_width=True, key="free_dl_btn",
                )
            except Exception as e:
                st.error(f"PDF generation failed: {type(e).__name__}: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Premium PDF — themed wizard (existing flow)
# ─────────────────────────────────────────────────────────────────────────────

def _render_premium_pdf(profile, chart_style: str):
    st.caption("Premium Kundli — full themed PDF with cover, AI narrative, "
               "decade-by-decade predictions, and optional Western appendix. "
               "Free during prototyping; paid in the mobile app.")

    # Theme picker
    st.markdown("##### Theme")
    selected_theme = st.session_state.get("kundli_theme", "classic_vedic")
    cols = st.columns(4)
    for i, slug in enumerate(THEMES.keys()):
        with cols[i % 4]:
            theme = THEMES[slug]
            st.markdown(_theme_card(slug, theme, slug == selected_theme),
                        unsafe_allow_html=True)
            if st.button("Select" if slug != selected_theme else "✓ Selected",
                         key=f"theme_{slug}",
                         type="primary" if slug == selected_theme else "secondary",
                         use_container_width=True):
                st.session_state.kundli_theme = slug
                st.rerun()

    # Language + options
    st.markdown("##### Language & options")
    c1, c2 = st.columns([2, 1])
    with c1:
        lang_codes = [code for code, _ in LANGUAGES]
        lang_labels = [label for _, label in LANGUAGES]
        lang_idx = lang_codes.index(st.session_state.get("kundli_lang", "en"))
        new_lang = st.selectbox("Generation language", lang_labels, index=lang_idx,
                                help="Section headers + static interpretation text. Math is language-neutral.")
        st.session_state.kundli_lang = lang_codes[lang_labels.index(new_lang)]
    with c2:
        st.session_state.kundli_western = st.checkbox(
            "Include Western Appendix", value=True,
            help="2-3 pages: tropical positions, Sun/Moon/Rising, Ptolemaic aspects.")
        st.session_state.kundli_ai = st.checkbox(
            "Include AI narrative", value=True,
            help="Karmic Story + decade predictions. One Gemini call (~₹5 budget).")

    st.markdown("---")

    if not st.button("✨ Generate Premium Kundli PDF",
                      type="primary", use_container_width=True):
        return

    with st.spinner("Building premium kundli…"):
        try:
            bd = BirthData.from_profile(profile)
            chart = compute_chart(bd)
            data = build_kundli_pdf(
                chart,
                theme_name=st.session_state.get("kundli_theme", "classic_vedic"),
                chart_style=chart_style,
                language=st.session_state.get("kundli_lang", "en"),
                include_western_appendix=st.session_state.get("kundli_western", True),
                include_ai_narrative=st.session_state.get("kundli_ai", True),
            )
        except Exception as e:
            st.error(f"Generation failed: {type(e).__name__}: {e}")
            return

    is_pdf = data[:4] == b"%PDF"
    ext = "pdf" if is_pdf else "html"
    fname = f"{profile['name'].replace(' ','_')}_Premium_Kundli.{ext}"
    mime = "application/pdf" if is_pdf else "text/html"

    st.success(f"Premium kundli generated ({len(data):,} bytes).")
    if not is_pdf:
        st.warning("PDF requires WeasyPrint + GTK3 — until installed, you get HTML. "
                   "Open in browser → Print → Save as PDF for identical result.")
    st.download_button(f"⬇️ Download {ext.upper()}", data=data,
                       file_name=fname, mime=mime,
                       use_container_width=True, key="premium_dl_btn")

    if not is_pdf:
        with st.expander("Inline preview", expanded=False):
            b64 = base64.b64encode(data).decode("ascii")
            st.markdown(
                f'<iframe src="data:text/html;base64,{b64}" '
                f'style="width:100%;height:720px;border:1px solid #444;border-radius:8px;"></iframe>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Main view
# ─────────────────────────────────────────────────────────────────────────────

def show_kundli():
    st.markdown("""
    <div style="text-align:center; margin: 0.5rem 0 1.5rem;">
      <h1 style="font-family: 'Cinzel', serif; letter-spacing: 0.1em; margin-bottom: 0;
                 color: #D4AF37;">📜 Janma Kundli</h1>
      <p style="opacity: 0.7; margin-top: 4px;">
        Complete Vedic birth chart — every divisional, every dasha, every dosha,
        all real math, beautifully presented.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Profile picker (shared across both tabs) ────────────────────────────
    st.markdown("##### Whose chart?")
    pi = render_profile_form("kundli", show_d60=False)
    if pi["type"] == "empty_saved":
        st.info("Enter or select a profile above to continue.")
        return

    # ── Chart style picker (shared) ────────────────────────────────────────
    st.markdown("##### Chart style")
    cs_cols = st.columns(3)
    chart_style = st.session_state.get("kundli_chart_style", "north_indian")
    for col, (slug, label, desc) in zip(cs_cols, CHART_STYLES):
        with col:
            is_sel = chart_style == slug
            if st.button(label, key=f"cs_{slug}",
                         type="primary" if is_sel else "secondary",
                         use_container_width=True):
                st.session_state.kundli_chart_style = slug
                st.rerun()
    chart_style = st.session_state.get("kundli_chart_style", "north_indian")

    # ── Resolve profile once for both tabs ─────────────────────────────────
    try:
        profile, _ = resolve_profile(pi)
    except Exception as e:
        st.error(f"Profile resolution failed: {type(e).__name__}: {e}")
        return

    st.markdown("---")

    # ── Two tabs: Free Kundli (inline) vs Premium PDF ──────────────────────
    tab_free, tab_premium = st.tabs(["📜 Free Kundli (in-app)", "✨ Premium PDF"])

    with tab_free:
        # Compute once and cache in session, keyed by profile signature.
        cache_key = f"_kundli_chart::{profile.get('name','')}::{profile.get('date','')}::{profile.get('time','')}"
        if st.session_state.get("_kundli_cache_key") != cache_key:
            with st.spinner("Computing your chart…"):
                try:
                    bd = BirthData.from_profile(profile)
                    chart = compute_chart(bd)
                    st.session_state._kundli_cache_key = cache_key
                    st.session_state._kundli_chart = chart
                except Exception as e:
                    st.error(f"Chart computation failed: {type(e).__name__}: {e}")
                    return
        chart = st.session_state._kundli_chart

        # BTR note if exact_time is False
        if not chart.birth_data.exact_time:
            st.info("Birth time marked as approximate. Use Birth-Time "
                    "Rectification (in Premium PDF tab) for better accuracy.")

        _render_free_kundli(chart, chart_style)

    with tab_premium:
        _render_premium_pdf(profile, chart_style)
