import re
import math
import json
from functools import lru_cache
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo
from geopy.geocoders import Photon
from timezonefinder import TimezoneFinder
from shared.astro.constants import *
from shared.astro import ephemeris  # the swappable ephemeris adapter (Skyfield default)

def safe_json(text_response, fallback_dict):
    try:
        clean_text = text_response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(clean_text)
    except json.JSONDecodeError:
        return fallback_dict


def sign_name(i): return SIGNS[i%12]


def sign_index_from_lon(lon): return int(lon//30)%12


def format_dms(angle):
    angle%=360; d=int(angle); mf=(angle-d)*60; m=int(mf); s=int(round((mf-m)*60))
    if s==60: s,m=0,m+1
    if m==60: m,d=0,d+1
    return f"{d:02d}°{m:02d}'"


def nakshatra_info(lon):
    ns=360/27; idx=min(int((lon%360)//ns),26)
    return NAKSHATRAS[idx],NAKSHATRA_LORDS[idx],int(((lon%360%ns)//(ns/4)))+1


def get_baladi_avastha(lon):
    si=int(lon//30)%12; states=["Infant","Youth","Adult","Old","Dead"]
    if si%2!=0: states=states[::-1]
    return states[int((lon%30)//6)]


def get_panchanga(sun_lon,moon_lon,dt_local):
    tv=(moon_lon-sun_lon)%360; tn=int(tv/12)+1
    paksha="Shukla (Waxing)" if tv<180 else "Krishna (Waning)"; td=tn if tn<=15 else tn-15
    yn=min(int(((moon_lon+sun_lon)%360)/(360/27)),26); ki=int(tv/6)
    if ki==0: kn="Kintughna (Fixed)"
    elif 1<=ki<=56: kn=f"{['Bava','Balava','Kaulava','Taitila','Gara','Vanija','Vishti'][(ki-1)%7]} (Movable)"
    elif ki==57: kn="Sakuni (Fixed)"
    elif ki==58: kn="Chatushpada (Fixed)"
    else: kn="Naga (Fixed)"
    return {"tithi":f"{td} {paksha}","yoga":YOGA_NAMES[yn],"karana":kn,
            "weekday":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][dt_local.weekday()]}


# ══════════════════════════════════════════════════════════════════════════
# DAILY MUHURTA / KAAL WINDOWS  (date + location based — NOT birth-chart based)
# Powers the mobile "Today → Good / Avoid times" strip. Pure math: Swiss
# Ephemeris sunrise/sunset + classical weekday segment rules. No AI, no deps.
# ══════════════════════════════════════════════════════════════════════════

# Each value is the 1-based index (1..8) of the eight equal DAYTIME parts
# (sunrise→sunset) that the period occupies, keyed by Python weekday() (Mon=0..Sun=6).
_RAHU_SEGMENT      = {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}
_YAMAGANDA_SEGMENT = {0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6, 6: 5}
_GULIKA_SEGMENT    = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 7}

# Successive order of the seven Choghadiya (ruled by Sun/Venus/Mercury/Moon/
# Saturn/Jupiter/Mars). Day and night both walk forward through this wheel.
CHOGHADIYA_WHEEL = ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"]
# First daytime Choghadiya of the day = the weekday lord's, by weekday() (Mon=0..Sun=6).
_CHOGHADIYA_DAY_START = {0: 3, 1: 6, 2: 2, 3: 5, 4: 1, 5: 4, 6: 0}
CHOGHADIYA_QUALITY = {
    "Amrit": "good", "Shubh": "good", "Labh": "good",
    "Char": "neutral",
    "Udveg": "avoid", "Kaal": "avoid", "Rog": "avoid",
}
# Plain-English guidance so the Today "Good/Avoid times" strip reads clearly.
_AVOID_TIP = {
    "Rahu Kaal":   "Best to avoid starting anything important.",
    "Yamaganda":   "Not a window for big decisions or new beginnings.",
    "Gulika Kaal": "Hold off on signing, buying, or committing.",
}
_GOOD_TIP = "The day's strongest stretch — good to act, sign, or begin."
_CHOG_TIP = {
    "good":    "Fine to act.",
    "neutral": "Ordinary — nothing for or against.",
    "avoid":   "Better to wait.",
}


def _jd_ut_to_local(jd_ut, tz_name):
    """UT Julian Day → tz-aware local datetime (engine-independent calendar math)."""
    return ephemeris.jd_to_utc(jd_ut).astimezone(ZoneInfo(tz_name))


def sun_rise_set(d, lat, lon, tz_name):
    """Sunrise, sunset and the NEXT day's sunrise for a date+location.
    Returns three tz-aware local datetimes: (sunrise, sunset, next_sunrise).

    Delegates to the ephemeris adapter (Skyfield: validated to ≤21s vs Swiss
    Ephemeris's standard upper-limb-with-refraction definition)."""
    return ephemeris.sun_rise_set(d, lat, lon, tz_name)


def _hm(dt): return dt.strftime("%H:%M")


def _ampm(dt):
    h = dt.hour % 12 or 12
    return f"{h}:{dt.minute:02d} {'am' if dt.hour < 12 else 'pm'}"


def daily_timing_windows(d, lat, lon, tz_name):
    """Display-ready auspicious/inauspicious windows for a given date + location.

    Date- and location-based (depends on weekday + sunrise/sunset), NOT on a
    birth chart. Returns:
      avoid       — Rahu Kaal, Yamaganda, Gulika Kaal: {name, start, end} (24h HH:MM)
      good        — Abhijit Muhurta: {name, start, end}
      choghadiya  — 8 day + 8 night segments tiling sunrise→next sunrise,
                    each {name, start, end, quality, period}
      summary     — one-line plain-English hint
      plus sunrise / sunset / weekday for display.
    """
    sunrise, sunset, next_sunrise = sun_rise_set(d, lat, lon, tz_name)
    wd = d.weekday()
    day_len = sunset - sunrise

    def _day_seg(i):  # 0-based index into the 8 equal daytime parts
        step = day_len / 8
        return sunrise + step * i, sunrise + step * (i + 1)

    def _win(name, s, e, tip=None):
        w = {"name": name, "start": _hm(s), "end": _hm(e)}
        if tip:
            w["tip"] = tip
        return w

    rk_s, rk_e = _day_seg(_RAHU_SEGMENT[wd] - 1)
    avoid = [
        _win("Rahu Kaal", rk_s, rk_e, _AVOID_TIP["Rahu Kaal"]),
        _win("Yamaganda", *_day_seg(_YAMAGANDA_SEGMENT[wd] - 1), tip=_AVOID_TIP["Yamaganda"]),
        _win("Gulika Kaal", *_day_seg(_GULIKA_SEGMENT[wd] - 1), tip=_AVOID_TIP["Gulika Kaal"]),
    ]

    # Abhijit Muhurta — the 8th of 15 daytime muhurtas (centred on local noon).
    midday = sunrise + day_len / 2
    half = day_len / 30
    ab_s, ab_e = midday - half, midday + half
    good = [_win("Abhijit Muhurta", ab_s, ab_e, _GOOD_TIP)]

    choghadiya = []
    day_start = _CHOGHADIYA_DAY_START[wd]
    for i in range(8):
        s, e = _day_seg(i)
        name = CHOGHADIYA_WHEEL[(day_start + i) % 7]
        q = CHOGHADIYA_QUALITY[name]
        choghadiya.append({"name": name, "start": _hm(s), "end": _hm(e),
                           "quality": q, "tip": _CHOG_TIP[q], "period": "day"})
    night_len = next_sunrise - sunset
    night_start = (day_start + 5) % 7  # night begins with the 5th-from-weekday lord
    for i in range(8):
        step = night_len / 8
        s, e = sunset + step * i, sunset + step * (i + 1)
        name = CHOGHADIYA_WHEEL[(night_start + i) % 7]
        q = CHOGHADIYA_QUALITY[name]
        choghadiya.append({"name": name, "start": _hm(s), "end": _hm(e),
                           "quality": q, "tip": _CHOG_TIP[q], "period": "night"})

    summary = (f"Strong window {_ampm(ab_s)}–{_ampm(ab_e)} (Abhijit Muhurta); "
               f"soft dip {_ampm(rk_s)}–{_ampm(rk_e)} (Rahu Kaal).")

    return {
        "weekday": ["Monday", "Tuesday", "Wednesday", "Thursday",
                    "Friday", "Saturday", "Sunday"][wd],
        "sunrise": _hm(sunrise),
        "sunset": _hm(sunset),
        "avoid": avoid,
        "good": good,
        "choghadiya": choghadiya,
        "summary": summary,
    }


# ══════════════════════════════════════════════════════════════════════════
# "TODAY" HEADS-UP CARDS  (date based, Moon/Sun only — no birth time needed)
#   • chandra_sandhi_window : Moon at a sign junction = weak/reflective window
#   • next_eclipse          : soonest upcoming Surya/Chandra Grahan from a date
# Pure Swiss-Ephemeris math. No AI, no new deps. NOTE: kundli._detect_grahan is
# a NATAL eclipse-axis dosha — unrelated to these upcoming-calendar events.
# ══════════════════════════════════════════════════════════════════════════

# How close (in degrees) to a 30° sign boundary counts as Chandra Sandhi.
_SANDHI_ORB_DEG = 1.0


def _moon_lon_sidereal(dt_utc):
    jd = ephemeris.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                          dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)
    return ephemeris.planet_lon(jd, "Moon")


def chandra_sandhi_window(d, tz_name, orb_deg=_SANDHI_ORB_DEG):
    """Find today's Chandra Sandhi window — the Moon within `orb_deg` of a 30°
    sign boundary (last ~1° of a sign or first ~1° of the next). The Moon crosses
    at most one sign boundary in a day, so there is at most one window.

    Returns a display-ready dict (24h HH:MM local) or {"present": False}.
    """
    # (Adapter is always Lahiri-sidereal; no global state to set.)
    lz = ZoneInfo(tz_name)
    day_start = datetime(d.year, d.month, d.day, 0, 0, tzinfo=lz)

    # Sample the day at 2-min resolution (Moon moves ~13°/day → fine for HH:MM).
    step = timedelta(minutes=2)
    n_steps = (24 * 60) // 2
    in_window = False
    win_start = win_end = None
    boundary_lon = None
    for i in range(n_steps + 1):
        dt_local = day_start + step * i
        lon = _moon_lon_sidereal(dt_local.astimezone(ZoneInfo("UTC")))
        dist = min(lon % 30, 30 - (lon % 30))  # degrees to nearest sign boundary
        if dist <= orb_deg:
            if not in_window:
                in_window = True
                win_start = dt_local
            win_end = dt_local
            boundary_lon = round(lon / 30.0) * 30.0  # nearest 30° boundary
        elif in_window:
            break  # first contiguous window of the day is the one we report

    if not in_window:
        return {"present": False}

    b = int(round(boundary_lon)) % 360
    from_sign = sign_name(int(b / 30 - 1) % 12)
    to_sign = sign_name(int(b / 30) % 12)
    return {
        "present": True,
        "start": win_start.strftime("%H:%M"),
        "end": win_end.strftime("%H:%M"),
        "from_sign": from_sign,
        "to_sign": to_sign,
        "label": "Low window",
        "note": "A low/reflective window — better for calm tasks; avoid big commitments.",
        "why": (f"The Moon is crossing the junction (Chandra Sandhi) between {from_sign} "
                f"and {to_sign}. At a sign boundary the Moon is considered weak, so this "
                f"is a softer, more reflective stretch rather than a time to push."),
        "sanskrit": "चन्द्र सन्धि",
    }


def next_eclipse(d, tz_name="UTC", lat=None, lon=None, horizon_days=30):
    """Soonest upcoming solar OR lunar eclipse on/after date `d` (whichever is
    sooner). Delegates to the ephemeris adapter — Skyfield default (eclipse
    DATES are exact vs Swiss Ephemeris). `present` is True only if the eclipse
    falls within `horizon_days` (else the app hides the card).

    Sutak (traditional): begins ~12h before a solar / ~9h before a lunar eclipse.
    """
    ev = ephemeris.next_eclipse(d, horizon_days=horizon_days)
    if not ev["type"]:
        # No eclipse in search horizon — return a safe "hide the card" payload.
        return {"present": False, "type": None, "date": None,
                "days_until": None, "sutak_start": None, "sutak_note": "",
                "why": "", "sanskrit": ""}

    if ev["type"] == "Surya Grahan":
        sanskrit = "सूर्य ग्रहण"
        why = ("A solar eclipse is coming up — traditionally a time to pause new "
               "beginnings, keep things low-key and turn inward.")
    else:
        sanskrit = "चन्द्र ग्रहण"
        why = ("A lunar eclipse is coming up — emotions can run high, so it's a time "
               "for rest, reflection and gentle routines.")

    # Eclipse date from the adapter is UTC. Anchor sutak window to local-midnight
    # of that date so the time-of-day label stays meaningful even though we don't
    # carry the eclipse maximum's HH:MM through the adapter (day-level UI only).
    ecl_local_midnight = datetime(ev["date"].year, ev["date"].month, ev["date"].day,
                                  tzinfo=ZoneInfo(tz_name))
    sutak_start = ecl_local_midnight - timedelta(hours=ev["sutak_hours"])
    return {
        "present": ev["present"],
        "type": ev["type"],
        "date": ev["date"].isoformat(),
        "days_until": ev["days_until"],
        "sutak_start": sutak_start.strftime("%Y-%m-%d %H:%M"),
        "sutak_note": (f"Sutak (the caution period) traditionally begins about "
                       f"{ev['sutak_hours']} hours before, around "
                       f"{sutak_start.strftime('%d %b %H:%M')}."),
        "why": why,
        "sanskrit": sanskrit,
    }


def whole_sign_house(ls,ps): return ((ps-ls)%12)+1


def get_western_sign(month,day):
    cusps=[(1,19,"Capricorn"),(2,18,"Aquarius"),(3,20,"Pisces"),(4,19,"Aries"),(5,20,"Taurus"),
           (6,20,"Gemini"),(7,22,"Cancer"),(8,22,"Leo"),(9,22,"Virgo"),(10,22,"Libra"),
           (11,21,"Scorpio"),(12,21,"Sagittarius")]
    for em,ed,sign in cusps:
        if month<em or (month==em and day<=ed): return sign
    return "Capricorn"


def get_western_transits_today():
    """Live Tropical (Western) transits via the ephemeris adapter (Skyfield)."""
    dt_now = datetime.now(ZoneInfo("UTC"))
    jd = ephemeris.julday(dt_now.year, dt_now.month, dt_now.day,
                          dt_now.hour + dt_now.minute / 60.0)

    western_pos = {}
    for pname in PLANETS:
        lon = ephemeris.planet_lon_tropical(jd, pname)
        sidx = int(lon // 30) % 12
        western_pos[pname] = SIGNS[sidx]

    return western_pos


def geocode_place(pt):
    try: 
        # Using Photon to bypass Streamlit Cloud IP blocks
        loc = Photon(user_agent="astro_suite_cloud").geocode(pt, exactly_one=True, timeout=10)
        return (loc.latitude, loc.longitude, loc.address) if loc else None
    except Exception as e: 
        print(f"Geocoding Error: {e}")
        return None


def timezone_for_latlon(lat,lon): return TimezoneFinder().timezone_at(lat=lat,lng=lon)


def local_to_julian_day(d, t, tz_name):
    """Local (date+time, tz) → (UT Julian Day, local datetime, UTC datetime).
    Pure calendar math via the ephemeris adapter's julday helper."""
    lz = ZoneInfo(tz_name)
    dtl = datetime.combine(d, t).replace(tzinfo=lz)
    dtu = dtl.astimezone(ZoneInfo("UTC"))
    jd = ephemeris.julday(dtu.year, dtu.month, dtu.day,
                          dtu.hour + dtu.minute / 60 + dtu.second / 3600)
    return jd, dtl, dtu


def get_lagna_and_cusps(jd, lat, lon, mode="lahiri"):
    """(sidereal Lagna longitude, whole-sign cusps) — Vedic main chart.
    Whole-sign houses are the locked convention (see docs/ephemeris-decision.md);
    Placidus is exposed separately via get_placidus_cusps for the KP toggle.
    `mode` selects the ayanamsha (default lahiri)."""
    asc = ephemeris.ascendant(jd, lat, lon, mode=mode)
    cusps = ephemeris.houses(jd, lat, lon, system="whole_sign", mode=mode)
    return asc % 360, cusps


def get_planet_longitude_and_speed(jd, planet, mode="lahiri"):
    """(sidereal longitude deg, speed deg/day). `planet` is a NAME string
    ("Moon", "Mars", ...) per the post-migration constants.PLANETS values.
    `mode` selects the ayanamsha (default lahiri)."""
    return ephemeris.planet_lon_speed(jd, planet, mode=mode)


def get_planet_lon_lat(jd, planet, mode="lahiri"):
    """(sidereal longitude, ecliptic latitude, speed). Used where the consumer
    also needs ecliptic latitude (e.g. Graha Yuddha winner determination)."""
    lon, spd = ephemeris.planet_lon_speed(jd, planet, mode=mode)
    lat = ephemeris.planet_lat(jd, planet)
    return lon, lat, spd


def get_rahu_longitude(jd, mode="lahiri"):
    """Sidereal Rahu longitude — MEAN node (locked Vedic convention).
    Previously used TRUE_NODE; unified to MEAN to match scoring.py and the
    ephemeris-decision.md convention. Ketu = +180. `mode` selects the ayanamsha."""
    return ephemeris.node_lon(jd, mode=mode)


def get_placidus_cusps(jd, lat, lon, mode="lahiri"):
    """12 sidereal Placidus house cusps — used by the KP sub-lord computation
    (Vedic default chart stays whole-sign). Validated to 0.00\" vs SE.
    `mode` selects the ayanamsha (default lahiri)."""
    return ephemeris.houses(jd, lat, lon, system="placidus", mode=mode)


def get_live_cosmic_weather():
    """Snapshot of today's sky for the daily cosmic-weather card."""
    dt_now = datetime.now(ZoneInfo("UTC"))
    jd = ephemeris.julday(dt_now.year, dt_now.month, dt_now.day,
                          dt_now.hour + dt_now.minute / 60.0)
    moon_lon = ephemeris.planet_lon(jd, "Moon")
    sun_lon = ephemeris.planet_lon(jd, "Sun")
    moon_sidx = sign_index_from_lon(moon_lon); sun_sidx = sign_index_from_lon(sun_lon)
    nak, _, _ = nakshatra_info(moon_lon); panch = get_panchanga(sun_lon, moon_lon, dt_now)
    retrogrades = []
    for pname in ["Mars","Mercury","Jupiter","Venus","Saturn"]:
        _, spd = get_planet_longitude_and_speed(jd, pname)
        if spd < 0: retrogrades.append(pname)
    nature_type = "Mixed (Mishra)"; advice = NAK_ADVICE["Mixed (Mishra)"]
    for nt, naks in NAK_NATURES.items():
        if nak in naks: nature_type = nt; advice = NAK_ADVICE[nt]; break
    all_pos = {}
    for pname in PLANETS:
        lon, _ = get_planet_longitude_and_speed(jd, pname)
        all_pos[pname] = sign_name(sign_index_from_lon(lon))
    # Rahu/Ketu — MEAN node (unified Vedic convention)
    r_lon = get_rahu_longitude(jd)
    all_pos["Rahu"] = sign_name(sign_index_from_lon(r_lon))
    all_pos["Ketu"] = sign_name(sign_index_from_lon((r_lon + 180) % 360))
    return {"moon_sign":sign_name(moon_sidx),"sun_sign":sign_name(sun_sidx),"nakshatra":nak,
            "tithi":panch["tithi"],"yoga":panch["yoga"],"retrogrades":retrogrades,
            "nature":nature_type,"advice":advice,"all_pos":all_pos}


def get_kp_sub_lord(lon):
    ns=360/27; idx=int((lon%360)//ns); nak_lord=NAKSHATRA_LORDS[idx]
    deg=lon%360-idx*ns; si=DASHA_ORDER.index(nak_lord); seq=DASHA_ORDER[si:]+DASHA_ORDER[:si]
    acc=0.0
    for sl in seq:
        acc+=(DASHA_YEARS[sl]/120.0)*ns
        if deg<=acc+1e-9: return sl
    return seq[-1]


def get_planet_lon_helper(pname,planet_data,r_lon,k_lon):
    if pname in planet_data: return planet_data[pname][0]
    if pname=="Rahu": return r_lon
    if pname=="Ketu": return k_lon


def get_planet_house(pname,ls,planet_data,r_lon,k_lon):
    lon=get_planet_lon_helper(pname,planet_data,r_lon,k_lon)
    return whole_sign_house(ls,sign_index_from_lon(lon)) if lon is not None else None


def get_lagna_lord_chain(ls,planet_data,r_lon,k_lon):
    ll=SIGN_LORDS_MAP[ls]; ll_lon=get_planet_lon_helper(ll,planet_data,r_lon,k_lon)
    ll_sidx=sign_index_from_lon(ll_lon); ll_house=whole_sign_house(ls,ll_sidx)
    tags=[]
    if ll in DIGNITIES:
        if ll_sidx==DIGNITIES[ll][0]: tags.append("Exalted")
        elif ll_sidx==DIGNITIES[ll][1]: tags.append("Debilitated")
    if ll in OWN_SIGNS and ll_sidx in OWN_SIGNS[ll]: tags.append("Own Sign")
    if ll in planet_data and planet_data[ll][1]<0: tags.append("Retrograde")
    tag_str=f" [{', '.join(tags)}]" if tags else ""
    disp=SIGN_LORDS_MAP[ll_sidx]; disp_h=get_planet_house(disp,ls,planet_data,r_lon,k_lon)
    return f"{ll} → H{ll_house} ({sign_name(ll_sidx)}{tag_str}) → dispositor {disp} in H{disp_h}"


def get_conjunctions(ls,planet_data,r_lon,k_lon):
    all_p={}
    for pn,(plon,_) in planet_data.items(): h=whole_sign_house(ls,sign_index_from_lon(plon)); all_p.setdefault(h,[]).append(pn)
    for pn,plon in [("Rahu",r_lon),("Ketu",k_lon)]: h=whole_sign_house(ls,sign_index_from_lon(plon)); all_p.setdefault(h,[]).append(pn)
    return [f"{' + '.join(plist)} conjunct in H{h} ({sign_name((ls+h-1)%12)})" for h,plist in all_p.items() if len(plist)>=2]


def get_mutual_aspects(ls,planet_data,r_lon,k_lon):
    spec={"Mars":[4,7,8],"Jupiter":[5,7,9],"Saturn":[3,7,10],"Rahu":[7],"Ketu":[7]}
    def asp(pn,h): return {((h+j-2)%12)+1 for j in spec.get(pn,[7])}
    houses={pn:whole_sign_house(ls,sign_index_from_lon(planet_data[pn][0])) for pn in planet_data}
    houses["Rahu"]=whole_sign_house(ls,sign_index_from_lon(r_lon))
    houses["Ketu"]=whole_sign_house(ls,sign_index_from_lon(k_lon))
    plist=list(houses.keys()); mutual=[]
    for i,p1 in enumerate(plist):
        for p2 in plist[i+1:]:
            h1,h2=houses[p1],houses[p2]
            if h1!=h2 and h2 in asp(p1,h1) and h1 in asp(p2,h2): mutual.append(f"{p1}(H{h1}) ↔ {p2}(H{h2})")
    return mutual


def detect_graha_yuddha(jd_ut, planet_data):
    """Planetary war detection — within 0.5° → use ecliptic LATITUDE to pick
    the winner (the body higher above the ecliptic wins; classical Vedic rule)."""
    eligible = ["Mars","Mercury","Jupiter","Venus","Saturn"]
    plist = list(eligible); wars = []
    for i, p1 in enumerate(plist):
        for p2 in plist[i+1:]:
            l1 = planet_data[p1][0]; l2 = planet_data[p2][0]
            diff = abs(l1 - l2); diff = min(diff, 360 - diff)
            if diff <= 0.5:
                try:
                    lat1 = ephemeris.planet_lat(jd_ut, p1)
                    lat2 = ephemeris.planet_lat(jd_ut, p2)
                    winner = p1 if lat1 > lat2 else p2
                    loser  = p2 if lat1 > lat2 else p1
                except Exception:
                    # Lon-only fallback (last-ditch — should never trigger in practice)
                    winner = p1 if l1 > l2 else p2
                    loser  = p2 if l1 > l2 else p1
                wars.append((winner, loser, round(diff, 3)))
    return wars


def get_functional_planets(ls):
    # Classify each planet by its functional nature for the given Lagna.
    #
    # Per BPHS / Phaladeepika (practical Parashara's Light / JH convention):
    #
    #   Yogakaraka  — rules at least one PURE trikona in {5, 9} AND at least
    #                 one kendra in {1, 4, 7, 10}. The 1st house alone counts
    #                 as a kendra (not a trikona) for this rule, so ruling only
    #                 {1, 10}-type pairs does NOT make a yogakaraka. This
    #                 produces the canonical 6 yogakaraka Lagnas (Cancer/Leo
    #                 → Mars, Taurus/Libra → Saturn, Capricorn/Aquarius → Venus).
    #   Functional Benefic — rules a trikona (1, 5, 9) but is not a yogakaraka.
    #   Functional Malefic — rules a dusthana (6, 8, 12) WITHOUT also ruling
    #                 a trikona (trikona lordship neutralises dusthana lordship).
    #   Neutral     — anything else.
    trikona_pure={5,9}; trikona_full={1,5,9}; kendra={1,4,7,10}; trika={6,8,12}
    house_lords={}
    for h in range(1,13): lord=SIGN_LORDS_MAP[(ls+h-1)%12]; house_lords.setdefault(lord,[]).append(h)
    yks=[]; bens=[]; mals=[]; neu=[]
    for planet,houses in house_lords.items():
        rules_trikona_5_9=any(h in trikona_pure for h in houses)
        rules_trikona=any(h in trikona_full for h in houses)
        rules_kendra=any(h in kendra for h in houses)
        rules_dusthana=any(h in trika for h in houses)
        if rules_trikona_5_9 and rules_kendra: yks.append(planet)
        elif rules_trikona: bens.append(planet)
        elif rules_dusthana: mals.append(planet)
        else: neu.append(planet)
    return bens,mals,yks,neu


def get_planet_house_significations(pname, ls, planet_data, r_lon, k_lon):
    lon = get_planet_lon_helper(pname, planet_data, r_lon, k_lon)
    if lon is None: return set()
    sigs = set()
    psidx = sign_index_from_lon(lon)
    sigs.add(whole_sign_house(ls, psidx))                          
    for sidx, lord in SIGN_LORDS_MAP.items():                      
        if lord == pname: sigs.add(whole_sign_house(ls, sidx))
    _, sl, _ = nakshatra_info(lon)                                  
    if sl != pname:
        sl_lon = get_planet_lon_helper(sl, planet_data, r_lon, k_lon)
        if sl_lon:
            sigs.add(whole_sign_house(ls, sign_index_from_lon(sl_lon)))
            for sidx, lord in SIGN_LORDS_MAP.items():
                if lord == sl: sigs.add(whole_sign_house(ls, sidx))
    return sigs


def get_house_strength_summary(ls,planet_data,r_lon,k_lon,placidus_cusps):
    key_houses={
        1:("Self & Vitality",{1,11}),
        2:("Wealth & Family",{2,11}),
        3:("Siblings, Courage & Communication",{3,6,11}),
        4:("Home & Happiness",{4,11}),
        5:("Intelligence & Children",{5,11}),
        6:("Health & Struggles",{6,11}),
        7:("Marriage & Spouse",{2,7,11}),
        8:("Longevity & Obstacles",{8,11}),
        9:("Luck & Dharma",{9,11}),
        10:("Career & Status",{1,6,10,11}),
        11:("Gains & Desires",{3,6,11}),
        12:("Spiritual Depth & Expenditure",{12,11})
    }
    summaries=[]
    for h,(theme,ev_houses) in key_houses.items():
        h_sidx=(ls+h-1)%12; h_lord=SIGN_LORDS_MAP[h_sidx]
        lord_house=get_planet_house(h_lord,ls,planet_data,r_lon,k_lon)
        lord_sidx=sign_index_from_lon(get_planet_lon_helper(h_lord,planet_data,r_lon,k_lon))
        flags=[]
        if h_lord in DIGNITIES:
            if lord_sidx==DIGNITIES[h_lord][0]: flags.append("Lord Exalted")
            elif lord_sidx==DIGNITIES[h_lord][1]: flags.append("Lord Debilitated")
        if h_lord in OWN_SIGNS and lord_sidx in OWN_SIGNS[h_lord]: flags.append("Lord Own Sign")
        if lord_house in {6,8,12}: flags.append(f"Lord in dusthana H{lord_house}")
        elif lord_house in {1,4,7,10}: flags.append(f"Lord in Kendra H{lord_house}")
        kp_sl=get_kp_sub_lord(placidus_cusps[h-1])
        sigs=get_planet_house_significations(kp_sl,ls,planet_data,r_lon,k_lon)
        matched=sigs&ev_houses
        verdict="STRONGLY PROMISED (Base Score: 3)" if len(matched)>=2 or (max(ev_houses) in matched) else ("WEAKLY PROMISED (Base Score: 2)" if len(matched)==1 else "NOT CLEARLY PROMISED (Base Score: 1)")
        flag_str=" | ".join(flags) if flags else "Neutral"
        summaries.append(f"H{h} ({theme}): Lord={h_lord}(H{lord_house}) [{flag_str}] | KP SL={kp_sl}: {verdict}")
    return summaries


def check_neecha_bhanga(pname,ls,moon_sidx,planet_data,r_lon,k_lon):
    if pname not in DIGNITIES: return None
    p_sidx=sign_index_from_lon(planet_data[pname][0])
    if p_sidx!=DIGNITIES[pname][1]: return None
    kendra={1,4,7,10}
    def hf(ref,pn):
        lon=get_planet_lon_helper(pn,planet_data,r_lon,k_lon)
        return whole_sign_house(ref,sign_index_from_lon(lon)) if lon else None
    conds=[]
    dsl=DEB_SIGN_LORDS.get(pname)
    if dsl:
        h=hf(ls,dsl)
        if h in kendra: conds.append(f"dispositor ({dsl}) in Kendra H{h} from Lagna")
        h=hf(moon_sidx,dsl)
        if h in kendra: conds.append(f"dispositor ({dsl}) in Kendra H{h} from Moon")
    exl=EXALT_LORD_IN_DEB_SIGN.get(pname)
    if exl:
        h=hf(ls,exl)
        if h in kendra: conds.append(f"exaltation-sign lord ({exl}) in Kendra H{h} from Lagna")
    hfm=whole_sign_house(moon_sidx,p_sidx)
    if hfm in kendra: conds.append(f"debilitated planet in Kendra H{hfm} from Moon")
    hfl=whole_sign_house(ls,p_sidx)
    if hfl in kendra: conds.append(f"debilitated planet in Kendra H{hfl} from Lagna")
    return conds if conds else None


def get_chara_karakas(planet_data):
    planets_for_ck = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
    deg = {pn: planet_data[pn][0] % 30 for pn in planets_for_ck}
    ranked = sorted(deg, key=deg.get, reverse=True)
    karaka_names = ["Atmakaraka (AK)","Amatyakaraka (AmK)","Bhratrukaraka (BK)",
                    "Matrukaraka (MK)","Pitrukaraka (PiK)","Putrakaraka (PuK)","Darakaraka (DK)"]
    karaka_chain = {karaka_names[i]: (ranked[i], round(deg[ranked[i]],2)) for i in range(len(ranked))}
    ak, ak_deg = ranked[0], deg[ranked[0]]
    amk, amk_deg = ranked[1], deg[ranked[1]]
    return ak, ak_deg, amk, amk_deg, karaka_chain


def calculate_ashtakavarga(ls, planet_data, r_lon, k_lon):
    BAV_RULES = {
        "Sun":     [1,2,4,7,8,9,10,11],   
        "Moon":    [3,6,10,11],             
        "Mars":    [1,2,4,7,8,10,11],
        "Mercury": [1,3,5,6,9,10,11,12],
        "Jupiter": [1,2,3,4,7,8,10,11],
        "Venus":   [1,2,3,4,5,8,9,11,12],
        "Saturn":  [3,5,6,11],
    }
    FULL_BAV = {
        "Sun": {
            "Sun":[1,2,4,7,8,9,10,11], "Moon":[3,6,10,11], "Mars":[1,2,4,7,8,9,10,11],
            "Mercury":[3,5,6,9,10,11,12], "Jupiter":[5,6,9,11], "Venus":[6,7,12],
            "Saturn":[1,2,4,7,8,9,10,11], "Lagna":[3,4,6,10,11,12]
        },  # total 48
        "Moon": {
            "Sun":[3,6,7,8,10,11], "Moon":[1,3,6,7,10,11], "Mars":[2,3,5,6,9,10,11],
            "Mercury":[1,3,4,5,7,8,10,11], "Jupiter":[1,4,7,8,10,11,12],
            "Venus":[3,4,5,7,9,10,11], "Saturn":[3,5,6,11], "Lagna":[3,6,10,11]
        },  # total 49
        "Mars": {
            "Sun":[3,5,6,10,11], "Moon":[3,6,11], "Mars":[1,2,4,7,8,10,11],
            "Mercury":[3,5,6,11], "Jupiter":[6,10,11,12], "Venus":[6,8,11,12],
            "Saturn":[1,4,7,8,9,10,11], "Lagna":[1,3,6,10,11]
        },  # total 39
        "Mercury": {
            "Sun":[5,6,9,11,12], "Moon":[2,4,6,8,10,11], "Mars":[1,2,4,7,8,9,10,11],
            "Mercury":[1,3,5,6,9,10,11,12], "Jupiter":[6,8,11,12],
            "Venus":[1,2,3,4,5,8,9,11], "Saturn":[1,2,4,7,8,9,10,11], "Lagna":[1,2,4,6,8,10,11]
        },
        "Jupiter": {
            "Sun":[1,2,3,4,7,8,9,10,11], "Moon":[2,5,7,9,11],
            "Mars":[1,2,4,7,8,10,11], "Mercury":[1,2,4,5,6,9,10,11],
            "Jupiter":[1,2,3,4,7,8,10,11], "Venus":[2,5,6,9,10,11],
            "Saturn":[3,5,6,11], "Lagna":[1,2,4,5,6,7,9,10,11]
        },
        "Venus": {
            "Sun":[8,11,12], "Moon":[1,2,3,4,5,8,9,11,12],
            "Mars":[3,4,6,9,11,12], "Mercury":[3,5,6,9,11],
            "Jupiter":[5,8,9,10,11], "Venus":[1,2,3,4,5,8,9,11,12],
            "Saturn":[3,4,5,8,9,10,11], "Lagna":[1,2,3,4,5,8,9,11]
        },
        "Saturn": {
            "Sun":[1,2,4,7,8,10,11], "Moon":[3,6,11],
            "Mars":[3,5,6,10,11,12], "Mercury":[6,8,9,10,11,12],
            "Jupiter":[5,6,11,12], "Venus":[6,11,12],
            "Saturn":[3,5,6,11], "Lagna":[1,3,4,6,10,11]
        },  # total 39
    }

    def get_ref_house(ref_name):
        if ref_name == "Lagna": return ls
        lon = get_planet_lon_helper(ref_name, planet_data, r_lon, k_lon)
        return sign_index_from_lon(lon) if lon is not None else ls

    bav = {}
    for planet, rules in FULL_BAV.items():
        bindus = [0] * 12
        ref_names = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Lagna"]
        for ref in ref_names:
            ref_sidx = get_ref_house(ref)
            offsets = rules.get(ref, [])
            for offset in offsets:
                target_sidx = (ref_sidx + offset - 1) % 12
                target_house = whole_sign_house(ls, target_sidx)
                bindus[target_house - 1] += 1
        bav[planet] = bindus
    return bav


def format_ashtakavarga_summary(bav, ls):
    lines = ["ASHTAKAVARGA (Planetary Strength per House — bindus/8):"]
    total_sav = [0] * 12
    for planet, bindus in bav.items():
        for i in range(12): total_sav[i] += bindus[i]
        house_str = " ".join(f"H{i+1}:{bindus[i]}" for i in range(12))
        lines.append(f"  {planet:9s}: {house_str}")
    sav_str = " ".join(f"H{i+1}:{total_sav[i]}" for i in range(12))
    lines.append(f"  SAV TOTAL: {sav_str}  (28+ = strong house, <25 = weak house)")
    strong = [f"H{i+1}({total_sav[i]})" for i in range(12) if total_sav[i] >= 30]
    weak   = [f"H{i+1}({total_sav[i]})" for i in range(12) if total_sav[i] <= 22]
    if strong: lines.append(f"  STRONG HOUSES (≥30 SAV bindus): {', '.join(strong)}")
    if weak:   lines.append(f"  WEAK HOUSES (≤22 SAV bindus):   {', '.join(weak)}")
    return "\n".join(lines)


def detect_yogas(ls,moon_sidx,planet_data,r_lon,k_lon):
    def ho(pn):
        lon=get_planet_lon_helper(pn,planet_data,r_lon,k_lon)
        return whole_sign_house(ls,sign_index_from_lon(lon)) if lon else None
    def si(pn):
        lon=get_planet_lon_helper(pn,planet_data,r_lon,k_lon)
        return sign_index_from_lon(lon) if lon is not None else None
    def ink(h1,h2): return (h2-h1)%12 in {0,3,6,9}
    yogas=[]; absent=[]
    mh,jh=ho("Moon"),ho("Jupiter")
    if mh and jh and ink(mh,jh): yogas.append(("Gajakesari Yoga",f"Moon(H{mh})+Jupiter(H{jh}) mutual Kendra — intelligence, fame, stability"))
    else: absent.append("Gajakesari Yoga — Moon+Jupiter not in mutual Kendra")
    for planet,(yname,ex_sidx) in {"Mars":("Ruchaka",9),"Mercury":("Bhadra",5),"Jupiter":("Hamsa",3),"Venus":("Malavya",11),"Saturn":("Shasha",6)}.items():
        psidx=sign_index_from_lon(planet_data[planet][0]); ph=whole_sign_house(ls,psidx)
        own=planet in OWN_SIGNS and psidx in OWN_SIGNS[planet]
        if (own or psidx==ex_sidx) and ph in {1,4,7,10}:
            yogas.append((f"{yname} Yoga",f"{planet} in {'own' if own else 'exaltation'} in Kendra H{ph} — Pancha Mahapurusha"))
        else: absent.append(f"{yname} Yoga — {planet} not in own/exalt+Kendra")
    if ho("Sun")==ho("Mercury"): yogas.append(("Budha-Aditya Yoga",f"Sun+Mercury conjunct H{ho('Sun')} — intellect, communication, reputation"))
    else: absent.append("Budha-Aditya Yoga — Sun+Mercury not conjunct")
    if ho("Moon")==ho("Mars"): yogas.append(("Chandra-Mangala Yoga",f"Moon+Mars conjunct H{ho('Moon')} — entrepreneurial drive"))
    else: absent.append("Chandra-Mangala Yoga — Moon+Mars not conjunct")
    mh2=ho("Moon")
    if mh2:
        t6=((mh2-1+5)%12)+1; t7=((mh2-1+6)%12)+1; t8=((mh2-1+7)%12)+1
        ben=[b for b in ["Mercury","Jupiter","Venus"] if ho(b) in {t6,t7,t8}]
        if len(ben)>=2: yogas.append(("Adhi Yoga",f"{', '.join(ben)} in 6/7/8 from Moon — leadership, longevity"))
        else: absent.append("Adhi Yoga — <2 benefics in 6/7/8 from Moon")
    tri_lords={SIGN_LORDS_MAP[(ls+h-1)%12] for h in [1,5,9]}
    ken_lords={SIGN_LORDS_MAP[(ls+h-1)%12] for h in [1,4,7,10]}
    rj=[]
    for tl in tri_lords:
        for kl in ken_lords:
            if tl!=kl:
                th,kh=ho(tl),ho(kl)
                if th and kh and th==kh: rj.append(f"{tl}+{kl} in H{th}")
    if rj: yogas.append(("Raja Yoga",f"Trikona+Kendra lords conjunct: {'; '.join(rj[:2])} — power, high status"))
    else: absent.append("Raja Yoga — no Trikona+Kendra lord conjunction")

    h9_lord = SIGN_LORDS_MAP[(ls+8)%12]; h10_lord = SIGN_LORDS_MAP[(ls+9)%12]
    if h9_lord != h10_lord:
        h9h = ho(h9_lord); h10h = ho(h10_lord)
        if h9h and h10h and h9h == h10h:
            yogas.append(("Dharma-Karma Adhipati Yoga", f"9th lord ({h9_lord}) + 10th lord ({h10_lord}) conjunct H{h9h} — peak career success, dharmic profession"))
        else:
            absent.append(f"Dharma-Karma Adhipati Yoga — H9 lord ({h9_lord}) and H10 lord ({h10_lord}) not conjunct")
    
    para=[]
    all_planets_para=["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
    for i,p1 in enumerate(all_planets_para):
        for p2 in all_planets_para[i+1:]:
            s1=si(p1); s2=si(p2)
            if s1 is None or s2 is None: continue
            p1_in_p2_sign = p2 in OWN_SIGNS and s1 in OWN_SIGNS[p2]
            p2_in_p1_sign = p1 in OWN_SIGNS and s2 in OWN_SIGNS[p1]
            if p1_in_p2_sign and p2_in_p1_sign:
                h1=ho(p1); h2=ho(p2)
                para.append(f"{p1}(H{h1})↔{p2}(H{h2})")
    if para: yogas.append(("Parivartana Yoga",f"Mutual sign exchange: {'; '.join(para)} — planets act as if conjunct, mutually empowered"))
    
    dust_lords=[SIGN_LORDS_MAP[(ls+h-1)%12] for h in [6,8,12]]
    dust_in=[dl for dl in dust_lords if ho(dl) in {6,8,12}]
    if len(dust_in)>=2: yogas.append(("Viparita Raja Yoga",f"Dusthana lords ({', '.join(dust_in)}) in dusthana — rise after adversity"))
    else: absent.append("Viparita Raja Yoga — insufficient dusthana lords in dusthana")
    
    if mh2:
        h2m=((mh2-1+1)%12)+1; h12m=((mh2-1-1)%12)+1
        all_h={pn:ho(pn) for pn in list(planet_data.keys())+["Rahu","Ketu"] if pn!="Moon"}
        flanking=[pn for pn,h in all_h.items() if h in {h2m,h12m} and pn not in {"Rahu","Ketu"}]
        moon_in_kendra = mh2 in {1,4,7,10} 
        if not flanking and not moon_in_kendra:
            yogas.append(("Kemadruma Yoga (Negative)",f"No planets flanking Moon in H{h2m}/H{h12m}, Moon not in Kendra — emotional isolation tendency"))
        elif not flanking and moon_in_kendra:
            absent.append(f"Kemadruma Yoga CANCELLED — Moon in Kendra H{mh2} (classical cancellation)")

    h9_lord = SIGN_LORDS_MAP[(ls+8)%12]; h9_lord_h = ho(h9_lord)
    ven_sidx = si("Venus"); ven_h = ho("Venus")
    ven_strong = ven_sidx is not None and (ven_sidx == DIGNITIES["Venus"][0] or ("Venus" in OWN_SIGNS and ven_sidx in OWN_SIGNS["Venus"]))
    if h9_lord_h in {1,4,5,7,9,10} and ven_h in {1,4,5,7,9,10} and ven_strong:
        yogas.append(("Lakshmi Yoga", f"H9 lord ({h9_lord}) in H{h9_lord_h} + Venus strong in H{ven_h} — wealth, fortune, prosperity"))
    else: absent.append("Lakshmi Yoga — conditions not met")

    svs = {1,2,4,5,7,9,10}
    jh_s=ho("Jupiter"); vh_s=ho("Venus"); mh_s=ho("Mercury")
    if jh_s in svs and vh_s in svs and mh_s in svs:
        yogas.append(("Saraswati Yoga", f"Jupiter(H{jh_s})+Venus(H{vh_s})+Mercury(H{mh_s}) in favorable houses — learning, wisdom, eloquence"))
    else: absent.append("Saraswati Yoga — Jupiter/Venus/Mercury not all in favorable houses")

    # ── Dhana Yoga (broadened) — BPHS lists multiple wealth-house-lord combos.
    # Classical conditions: any of (2L, 5L, 9L, 11L) in mutual conjunction /
    # mutual aspect / mutual kendra. We previously only checked 2L+11L which
    # misses most real Dhana Yoga configurations. Now we check all 6 pairs of
    # the {2L, 5L, 9L, 11L} wealth-lord set and report the strongest match.
    wealth_lord_houses = {h: SIGN_LORDS_MAP[(ls + h - 1) % 12] for h in (2, 5, 9, 11)}
    wealth_lord_pos = {h: ho(lord) for h, lord in wealth_lord_houses.items()}
    dhana_hits = []
    _checked_pairs = set()
    for h_a in (2, 5, 9, 11):
        for h_b in (2, 5, 9, 11):
            if h_a >= h_b or (h_a, h_b) in _checked_pairs: continue
            _checked_pairs.add((h_a, h_b))
            la, lb = wealth_lord_houses[h_a], wealth_lord_houses[h_b]
            la_h, lb_h = wealth_lord_pos[h_a], wealth_lord_pos[h_b]
            if la == lb:
                dhana_hits.append(f"{la} lords both H{h_a} and H{h_b}")
                continue
            if not (la_h and lb_h): continue
            if la_h == lb_h:
                dhana_hits.append(f"H{h_a}-lord ({la}) + H{h_b}-lord ({lb}) conjunct in H{la_h}")
            elif ((lb_h - la_h) % 12) in {3, 6, 9}:
                dhana_hits.append(f"H{h_a}-lord ({la}) H{la_h} + H{h_b}-lord ({lb}) H{lb_h} in mutual kendra")
    if dhana_hits:
        yogas.append(("Dhana Yoga", "; ".join(dhana_hits[:3]) + " — wealth-house-lord sambandha"))
    else:
        absent.append("Dhana Yoga — no 2/5/9/11 lord sambandha detected")

    # ── Akhand Samrajya Yoga (Brihat Parashara) — "uninterrupted sovereignty",
    # the great wealth-+-status yoga. Classical conditions:
    #   1. Lords of 2nd, 9th, and 11th are ALL in own/exaltation/friendly signs.
    #   2. Jupiter is strong (in own/exalt/kendra/trikona from Lagna).
    # When this fires the chart has lifetime financial sovereignty.
    h2_lord  = wealth_lord_houses[2]
    h11_lord = wealth_lord_houses[11]
    h9_lord_a = SIGN_LORDS_MAP[(ls + 8) % 12]
    akhand_lords = (h2_lord, h9_lord_a, h11_lord)
    def _is_own_or_exalt_or_friendly(planet_name):
        ps = si(planet_name)
        if ps is None: return False
        if planet_name in DIGNITIES and ps == DIGNITIES[planet_name][0]: return True   # exalted
        if planet_name in OWN_SIGNS and ps in OWN_SIGNS[planet_name]: return True      # own sign
        # Friendly = sign whose lord is a natural friend
        # (Approximation: planet is in mooltrikona-friendly sign — checked via
        # whether the sign's lord is a natural friend.)
        sign_lord = SIGN_LORDS_MAP.get(ps)
        friends_map = {
            "Sun":     {"Moon", "Mars", "Jupiter"},
            "Moon":    {"Sun", "Mercury"},
            "Mars":    {"Sun", "Moon", "Jupiter"},
            "Mercury": {"Sun", "Venus"},
            "Jupiter": {"Sun", "Moon", "Mars"},
            "Venus":   {"Mercury", "Saturn"},
            "Saturn":  {"Mercury", "Venus"},
        }
        return sign_lord in friends_map.get(planet_name, set())
    all_lords_strong = all(_is_own_or_exalt_or_friendly(L) for L in akhand_lords if L)
    jup_sidx = si("Jupiter")
    jup_h_for_ak = ho("Jupiter")
    jup_strong = (
        jup_sidx is not None and (
            (jup_sidx == DIGNITIES["Jupiter"][0]) or
            ("Jupiter" in OWN_SIGNS and jup_sidx in OWN_SIGNS["Jupiter"]) or
            jup_h_for_ak in {1, 4, 5, 7, 9, 10}
        )
    )
    if all_lords_strong and jup_strong:
        yogas.append(("Akhand Samrajya Yoga",
                      f"Lords of H2 ({h2_lord}), H9 ({h9_lord_a}), H11 ({h11_lord}) all in "
                      f"own/exalt/friendly signs + Jupiter strong — uninterrupted lifetime sovereignty"))
    else:
        absent.append("Akhand Samrajya Yoga — 2/9/11 lords not all in own/exalt/friendly OR Jupiter not strong")

    # ── Mahabhagya Yoga (Phaladeepika) — "great fortune". For a chart born by
    # DAY with Sun, Moon, Lagna all in odd signs (or by NIGHT with all in even
    # signs). We don't carry day-of-birth gender, so we accept either condition;
    # the classical interpretation note tells the AI to apply day/night context.
    sun_sidx_mb = si("Sun"); moon_sidx_mb = si("Moon")
    if sun_sidx_mb is not None and moon_sidx_mb is not None:
        all_odd = (ls % 2 == 0) and (sun_sidx_mb % 2 == 0) and (moon_sidx_mb % 2 == 0)
        all_even = (ls % 2 == 1) and (sun_sidx_mb % 2 == 1) and (moon_sidx_mb % 2 == 1)
        if all_odd:
            yogas.append(("Mahabhagya Yoga",
                          "Sun, Moon, and Lagna all in odd signs — great fortune (day-birth classical reading)"))
        elif all_even:
            yogas.append(("Mahabhagya Yoga",
                          "Sun, Moon, and Lagna all in even signs — great fortune (night-birth classical reading)"))
        else:
            absent.append("Mahabhagya Yoga — Sun/Moon/Lagna not aligned in same parity")

    # ── Sankha Yoga (Phaladeepika) — wealth-through-fame yoga. Two classical
    # versions:
    #   v1: Lords of 5th and 6th in mutual kendra, with Lagna lord strong.
    #   v2: Lagna lord in kendra/trikona + 9th lord in kendra/trikona + 10th
    #       lord strong (less standard, skip).
    # We implement v1 (the BPHS-aligned version).
    h5_lord = SIGN_LORDS_MAP[(ls + 4) % 12]
    h6_lord = SIGN_LORDS_MAP[(ls + 5) % 12]
    h1_lord_sk = SIGN_LORDS_MAP[ls]
    h5_lord_h = ho(h5_lord); h6_lord_h = ho(h6_lord); h1_lord_h_sk = ho(h1_lord_sk)
    if h5_lord_h and h6_lord_h and h1_lord_h_sk:
        # Mutual kendra (distance 0/3/6/9 in houses)
        mutual_kendra_56 = ((h6_lord_h - h5_lord_h) % 12) in {0, 3, 6, 9}
        # Lagna lord strong = in own/exalt OR in kendra/trikona
        h1l_sidx = si(h1_lord_sk)
        h1l_strong = h1l_sidx is not None and (
            (h1_lord_sk in DIGNITIES and h1l_sidx == DIGNITIES[h1_lord_sk][0]) or
            (h1_lord_sk in OWN_SIGNS and h1l_sidx in OWN_SIGNS[h1_lord_sk]) or
            h1_lord_h_sk in {1, 4, 5, 7, 9, 10}
        )
        if mutual_kendra_56 and h1l_strong:
            yogas.append(("Sankha Yoga",
                          f"H5 lord ({h5_lord}) + H6 lord ({h6_lord}) in mutual kendra, "
                          f"Lagna lord ({h1_lord_sk}) strong — wealth through fame/longevity"))
        else:
            absent.append("Sankha Yoga — H5/H6 lords not in mutual kendra or Lagna lord weak")

    # ── Kahala Yoga (Phaladeepika) — leadership-wealth yoga. Lords of 4th and
    # 9th in mutual kendra OR conjunct, with Lagna lord strong.
    h4_lord = SIGN_LORDS_MAP[(ls + 3) % 12]
    h9_lord_k = h9_lord_a   # reuse from Akhand block
    h4_lord_h = ho(h4_lord); h9_lord_h = ho(h9_lord_k)
    if h4_lord_h and h9_lord_h and h1_lord_h_sk:
        kahala_conn = (h4_lord_h == h9_lord_h) or (((h9_lord_h - h4_lord_h) % 12) in {3, 6, 9})
        h1l_sidx_k = si(h1_lord_sk)
        h1l_strong_k = h1l_sidx_k is not None and (
            (h1_lord_sk in DIGNITIES and h1l_sidx_k == DIGNITIES[h1_lord_sk][0]) or
            (h1_lord_sk in OWN_SIGNS and h1l_sidx_k in OWN_SIGNS[h1_lord_sk]) or
            h1_lord_h_sk in {1, 4, 5, 7, 9, 10}
        )
        if kahala_conn and h1l_strong_k:
            yogas.append(("Kahala Yoga",
                          f"H4 lord ({h4_lord}) + H9 lord ({h9_lord_k}) connected "
                          f"+ Lagna lord ({h1_lord_sk}) strong — leadership, command over resources"))
        else:
            absent.append("Kahala Yoga — H4/H9 lords not connected or Lagna lord weak")

    h10_occ = [pn for pn in list(planet_data.keys())+["Rahu","Ketu"] if ho(pn)==10]
    if h10_occ and all(p in {"Jupiter","Venus","Mercury","Moon"} for p in h10_occ):
        yogas.append(("Amala Yoga", f"Only benefics ({', '.join(h10_occ)}) in H10 — spotless reputation, ethical career"))
    else: absent.append("Amala Yoga — H10 empty or contains malefics")

    if mh2:
        m_h2 = ((mh2-1+1)%12)+1; m_h12 = ((mh2-1-1)%12)+1
        sun_excluded = {"Sun","Rahu","Ketu"}
        sunapha_p = [pn for pn in planet_data if pn not in sun_excluded and ho(pn)==m_h2]
        anapha_p = [pn for pn in planet_data if pn not in sun_excluded and ho(pn)==m_h12]
        if sunapha_p and anapha_p:
            yogas.append(("Durudhura Yoga", f"Planets in H2({', '.join(sunapha_p)}) and H12({', '.join(anapha_p)}) from Moon — wealth, fame, generosity"))
        elif sunapha_p:
            yogas.append(("Sunapha Yoga", f"{', '.join(sunapha_p)} in H2 from Moon — self-made wealth, resourcefulness"))
        elif anapha_p:
            yogas.append(("Anapha Yoga", f"{', '.join(anapha_p)} in H12 from Moon — spiritual depth, generosity"))

    sun_h = ho("Sun")
    if sun_h:
        s_h2 = ((sun_h-1+1)%12)+1; s_h12 = ((sun_h-1-1)%12)+1
        node_moon = {"Moon","Rahu","Ketu"}
        veshi_p = [pn for pn in planet_data if pn not in node_moon and pn!="Sun" and ho(pn)==s_h2]
        voshi_p = [pn for pn in planet_data if pn not in node_moon and pn!="Sun" and ho(pn)==s_h12]
        if veshi_p and voshi_p:
            yogas.append(("Ubhayachari Yoga", f"Planets flanking Sun: H2({', '.join(veshi_p)})+H12({', '.join(voshi_p)}) — regal bearing, authority"))
        elif veshi_p:
            yogas.append(("Veshi Yoga", f"{', '.join(veshi_p)} in H2 from Sun — status, truthfulness"))
        elif voshi_p:
            yogas.append(("Voshi Yoga", f"{', '.join(voshi_p)} in H12 from Sun — learned, charitable"))

    nb = {"Jupiter","Venus","Mercury","Moon"}
    h2_all = [pn for pn in list(planet_data.keys())+["Rahu","Ketu"] if ho(pn)==2]
    h12_all = [pn for pn in list(planet_data.keys())+["Rahu","Ketu"] if ho(pn)==12]
    if any(p in nb for p in h2_all) and any(p in nb for p in h12_all):
        yogas.append(("Shubha Kartari Yoga", "Natural benefics flank Lagna — protection, good fortune, auspicious life"))
    else: absent.append("Shubha Kartari Yoga — benefics do not flank Lagna")

    for pname_nb in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        p_nb_sidx = si(pname_nb)
        if p_nb_sidx is not None and pname_nb in DIGNITIES and p_nb_sidx == DIGNITIES[pname_nb][1]:
            conds_nb = check_neecha_bhanga(pname_nb, ls, moon_sidx, planet_data, r_lon, k_lon)
            if conds_nb:
                yogas.append(("Neecha Bhanga Raja Yoga", f"{pname_nb} debilitated but cancelled — rise through adversity, hidden power"))

    return yogas,absent


def calculate_sade_sati(natal_moon_sidx):
    utc = datetime.now(ZoneInfo("UTC"))
    jd = ephemeris.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute / 60.0)
    sat_lon, _ = ephemeris.planet_lon_speed(jd, "Saturn")
    sat_sidx = sign_index_from_lon(sat_lon); diff = (sat_sidx - natal_moon_sidx) % 12
    phases={11:"ACTIVE — Phase 1 (Rising)",0:"ACTIVE — Phase 2 (Peak — most intense)",1:"ACTIVE — Phase 3 (Setting)"}
    if diff in phases: return f"{phases[diff]}: Saturn in {sign_name(sat_sidx)}, natal Moon in {sign_name(natal_moon_sidx)}."
    return f"NOT ACTIVE (Saturn is {diff} signs from natal Moon in {sign_name(natal_moon_sidx)})."


def check_manglik_dosha(ls, moon_sidx, mars_sidx, mars_lon=None, planet_data=None):
    """
    Classical Kuja (Manglik) Dosha verdict with dignity + aspect cancellations.

    Manglik houses (counted from Lagna AND from Moon): 1, 4, 7, 8, 12.

    Classical cancellations applied (when planet_data is supplied):
      • Mars in own sign (Aries / Scorpio) — dosha CANCELLED
      • Mars exalted (Capricorn) — dosha CANCELLED
      • Mars debilitated (Cancer) — dosha INTENSIFIED
      • Jupiter or Venus aspect / conjunction with Mars — MITIGATED
      • Saturn conjunct Mars (same sign) — MITIGATED

    Older 3-argument call sites still work — cancellations simply aren't
    evaluated unless mars_lon + planet_data are passed.
    """
    mh_l = whole_sign_house(ls, mars_sidx)
    mh_m = whole_sign_house(moon_sidx, mars_sidx)
    il = mh_l in [1, 4, 7, 8, 12]
    im = mh_m in [1, 4, 7, 8, 12]

    if not il and not im:
        return "NOT MANGLIK — No Kuja Dosha"

    cancellations = []
    if mars_sidx in (0, 7):        # Aries / Scorpio = Mars's own signs
        cancellations.append("Mars in own sign")
    if mars_sidx == 9:             # Capricorn = exalted
        cancellations.append("Mars exalted")
    debilitated = (mars_sidx == 3) # Cancer

    if planet_data is not None and mars_lon is not None:
        def _signed_sep(a, b):
            sep = abs(((a - b) + 360) % 360)
            return min(sep, 360 - sep)

        for benefic in ("Jupiter", "Venus"):
            entry = planet_data.get(benefic)
            if entry is None: continue
            b_lon = entry[0] if isinstance(entry, (tuple, list)) else entry
            sep = _signed_sep(mars_lon, b_lon)
            if sep <= 8.0:
                cancellations.append(f"{benefic} conjunct Mars")
            elif abs(sep - 180) <= 8.0:
                cancellations.append(f"{benefic} opposes Mars")

        sat_entry = planet_data.get("Saturn")
        if sat_entry is not None:
            sat_lon = sat_entry[0] if isinstance(sat_entry, (tuple, list)) else sat_entry
            if sign_index_from_lon(sat_lon) == mars_sidx:
                cancellations.append("Saturn conjunct Mars")

    if cancellations:
        tag = "WEAK" if not (il and im) else "MILD"
        return f"{tag} MANGLIK (cancellations: {', '.join(cancellations)}) — significantly mitigated"

    if debilitated:
        if il and im:
            return "VERY HIGH MANGLIK — Mars debilitated in Manglik house from both Lagna and Moon"
        return "HIGH MANGLIK — Mars debilitated in Manglik house"

    if il and im:
        return "HIGH MANGLIK — Mars in Manglik house from both Ascendant and Moon"
    elif il:
        return "MILD MANGLIK — Mars in Manglik house from Ascendant only"
    return "MILD MANGLIK — Mars in Manglik house from Moon only"


def get_manglik_cancellation_verdict(ma, mb):
    """
    Pairwise Manglik verdict aware of severity tiers introduced above:
    NOT MANGLIK / WEAK / MILD / HIGH / VERY HIGH.
    """
    def severity(m):
        if "NOT MANGLIK" in m:  return 0
        if "VERY HIGH" in m:    return 4
        if "HIGH MANGLIK" in m: return 3
        if "MILD" in m:         return 2
        if "WEAK" in m:         return 1
        return 2

    sa, sb = severity(ma), severity(mb)

    if sa == 0 and sb == 0:
        return "No Manglik Dosha in either chart."

    if sa > 0 and sb > 0:
        if max(sa, sb) <= 2:
            return "MANGLIK DOSHA CANCELLED — Both partners have mild Manglik (mutual classical cancellation). No remedy required."
        return ("MANGLIK BALANCED — Both partners are Manglik (mutual classical cancellation), "
                "but at least one severity is high. Muhurta + remedy still advisable.")

    who = f"Person 1 ({ma})" if sa > 0 else f"Person 2 ({mb})"
    return f"MANGLIK IMBALANCE — {who} is Manglik, the other is not. Carefully chosen Muhurta and remedies advisable."


def calculate_arudha_lagna(ls, planet_data, r_lon, k_lon):
    ll_planet = SIGN_LORDS_MAP[ls]
    ll_house = get_planet_house(ll_planet, ls, planet_data, r_lon, k_lon)
    distance = ll_house - 1
    al_house = ((ll_house - 1 + distance) % 12) + 1
    if al_house == 1: al_house = 4
    elif al_house == 7: al_house = 10
    al_sidx = (ls + al_house - 1) % 12
    return al_house, al_sidx


def calculate_indu_lagna(ls, moon_sidx):
    rays = {"Sun":30, "Moon":16, "Mars":6, "Mercury":8, "Jupiter":10, "Venus":12, "Saturn":1}
    l9_lord = SIGN_LORDS_MAP[(ls + 8) % 12]
    m9_lord = SIGN_LORDS_MAP[(moon_sidx + 8) % 12]
    total_rays = rays.get(l9_lord, 0) + rays.get(m9_lord, 0)
    rem = total_rays % 12
    if rem == 0: rem = 12
    indu_sidx = (moon_sidx + rem - 1) % 12
    return indu_sidx


def get_kp_cusp_promise(house_num, ls, planet_data, r_lon, k_lon, placidus_cusps):
    if house_num < 1 or house_num > 12: return "Invalid house number"
    
    cusp_lon = placidus_cusps[house_num - 1]
    cusp_sl = get_kp_sub_lord(cusp_lon)
    cusp_sigs = get_planet_house_significations(cusp_sl, ls, planet_data, r_lon, k_lon)
    
    kp_house_rules = {
        7:  {"name": "Marriage", "required": {2,7,11}, "deny": {1,6,10},
             "desc": "2-7-11 must be signified (family bond + partner + fulfilment)"},
        10: {"name": "Career/Profession", "required": {6,10,11}, "deny": {5,8,12},
             "desc": "6-10-11 for service; 2-7-10-11 for business"},
        6:  {"name": "Service/Employment", "required": {2,6,11}, "deny": {5,8,12},
             "desc": "2-6-11 for entering/continuing service"},
        5:  {"name": "Children", "required": {2,5,11}, "deny": {1,4,10},
             "desc": "2-5-11 must be signified for progeny"},
        4:  {"name": "Property/Vehicle", "required": {4,11}, "deny": {3,12},
             "desc": "4-11 for acquisition; 4-12 for loss/sale"},
        2:  {"name": "Wealth/Finance", "required": {2,11}, "deny": {6,8,12},
             "desc": "2-11 for wealth accumulation; 6-12 for debts"},
        11: {"name": "Gains/Desires", "required": {11}, "deny": {6,8,12},
             "desc": "11 signified for gains; 6-8-12 deny"},
        9:  {"name": "Luck/Higher Studies/Foreign", "required": {9,11}, "deny": {6,8,12},
             "desc": "9-11 for luck and higher studies"},
        12: {"name": "Foreign Settlement/Moksha", "required": {9,12}, "deny": {1,5},
             "desc": "9-12 for foreign connection; 12 alone for loss/hospital"},
        1:  {"name": "Self/Longevity", "required": {1,11}, "deny": {2,7},
             "desc": "1-11 for recovery; 2-7 are Maraka (death-inflicting)"},
        8:  {"name": "Longevity/Legacy/Research", "required": {8,11}, "deny": {1,2,7},
             "desc": "8-11 for legacy receipt; 1-2-7 Maraka configuration"},
        3:  {"name": "Siblings/Short Travel/Communication", "required": {3,11}, "deny": {8,12},
             "desc": "3-11 for sibling gains and short travel"},
    }
    
    rule = kp_house_rules.get(house_num, {"name": f"H{house_num}", "required": set(), "deny": set(), "desc": ""})
    required = rule["required"]
    deny_houses = rule["deny"]
    
    fulfilled = cusp_sigs & required
    denied = cusp_sigs & deny_houses
    
    if len(fulfilled) >= len(required):
        verdict = "STRONGLY PROMISED"
    elif len(fulfilled) >= len(required) - 1:
        verdict = "PARTIALLY PROMISED"
    else:
        verdict = "NOT PROMISED / DENIED"
    
    if denied and "NOT PROMISED" not in verdict:
        verdict += f" (but DELAYED/OBSTRUCTED — SL also signifies deny houses {denied})"
    
    return (f"H{house_num} KP Promise ({rule['name']}): SL of H{house_num} cusp = {cusp_sl} | "
            f"SL signifies houses: {sorted(cusp_sigs)} | "
            f"Required: {sorted(required)} → Matched: {sorted(fulfilled)} | "
            f"VERDICT: {verdict}")


def get_kp_marriage_timing_clues(ls, planet_data, r_lon, k_lon, placidus_cusps, dasha_info):
    h7_promise = get_kp_cusp_promise(7, ls, planet_data, r_lon, k_lon, placidus_cusps)
    
    marriage_houses = {2, 7, 11}
    all_planets_and_nodes = list(planet_data.keys()) + ["Rahu", "Ketu"]
    
    sig_list = []
    for pname in all_planets_and_nodes:
        sigs = get_planet_house_significations(pname, ls, planet_data, r_lon, k_lon)
        if sigs & marriage_houses:
            matched = sigs & marriage_houses
            sig_list.append(f"{pname}(H{sorted(matched)})")
    
    md = dasha_info.get('current_md', 'Unknown')
    ad = dasha_info.get('current_ad', 'Unknown')
    md_sigs = get_planet_house_significations(md, ls, planet_data, r_lon, k_lon) if md != 'Unknown' else set()
    ad_sigs = get_planet_house_significations(ad, ls, planet_data, r_lon, k_lon) if ad != 'Unknown' else set()
    
    md_supports = bool(md_sigs & marriage_houses)
    ad_supports = bool(ad_sigs & marriage_houses)
    
    timing_verdict = ""
    if md_supports and ad_supports:
        timing_verdict = f"ACTIVE WINDOW — Both {md} MD and {ad} AD signify marriage houses. Current period is ACTIVE for marriage."
    elif md_supports:
        timing_verdict = f"PARTIAL — {md} MD supports marriage (signifies {md_sigs & marriage_houses}), but {ad} AD does not directly support."
    elif ad_supports:
        timing_verdict = f"PARTIAL — {ad} AD supports marriage (signifies {ad_sigs & marriage_houses}), but {md} MD does not directly support."
    else:
        timing_verdict = f"INACTIVE WINDOW — Neither {md} MD nor {ad} AD strongly signifies marriage houses 2-7-11."
    
    return {
        "h7_promise": h7_promise,
        "significators": sig_list,
        "timing_verdict": timing_verdict,
        "md_marriage_sigs": sorted(md_sigs & marriage_houses),
        "ad_marriage_sigs": sorted(ad_sigs & marriage_houses)
    }


def build_vimshottari_timeline(dt_birth,moon_lon,dt_now):
    ns=360/27; idx=int((moon_lon%360)//ns); lord=NAKSHATRA_LORDS[idx]
    bal=DASHA_YEARS[lord]*(1-((moon_lon%360%ns)/ns))
    si=DASHA_ORDER.index(lord); seq=DASHA_ORDER[si:]+DASHA_ORDER[:si]
    dc=dt_birth; mdl=[(seq[0],bal)]+[(l,DASHA_YEARS[l]) for l in seq[1:]]
    for ml,my in mdl:
        nmd=dc+timedelta(days=my*YEAR_DAYS)
        if dt_now<nmd:
            ac=dc; aseq=DASHA_ORDER[DASHA_ORDER.index(ml):]+DASHA_ORDER[:DASHA_ORDER.index(ml)]
            for al in aseq:
                ay=(my*DASHA_YEARS[al])/120.0; nad=ac+timedelta(days=ay*YEAR_DAYS)
                if dt_now<nad:
                    pc=ac; pseq=DASHA_ORDER[DASHA_ORDER.index(al):]+DASHA_ORDER[:DASHA_ORDER.index(al)]
                    for pl in pseq:
                        py=(ay*DASHA_YEARS[pl])/120.0; npd=pc+timedelta(days=py*YEAR_DAYS)
                        if dt_now<npd:
                            return {"birth_nakshatra":NAKSHATRAS[idx],"start_lord":lord,"balance_years":bal,
                                    "current_md":ml,"current_ad":al,"current_pd":pl,"md_total_years":my,
                                    "md_start":dc,"md_end":nmd,"ad_start":ac,"ad_end":nad,"pd_start":pc,"pd_end":npd}
                        pc=npd
                ac=nad
        dc=nmd
    n=datetime.now()
    return {"birth_nakshatra":"Unknown","start_lord":"Unknown","balance_years":0,"current_md":"Unknown",
            "current_ad":"Unknown","current_pd":"Unknown","md_total_years":0,
            "md_start":n,"md_end":n,"ad_start":n,"ad_end":n,"pd_start":n,"pd_end":n}


def get_antardasha_table(di):
    ml=di['current_md']; my=di['md_total_years']
    if ml=="Unknown" or my==0: return []
    mi=DASHA_ORDER.index(ml); aseq=DASHA_ORDER[mi:]+DASHA_ORDER[:mi]
    cursor=di['md_start']; lines=[]; cur_al=di['current_ad']
    for al in aseq:
        ay=(my*DASHA_YEARS[al])/120.0; ad_end=cursor+timedelta(days=ay*YEAR_DAYS)
        lines.append(f"  {ml}/{al}: {cursor.strftime('%b %Y')} → {ad_end.strftime('%b %Y')}{'  ◀ NOW' if al==cur_al else ''}")
        cursor=ad_end
    return lines


def d2_si(lon):
    s = sign_index_from_lon(lon); d = lon % 30
    if s % 2 == 0: 
        return 4 if d < 15 else 3  
    else:
        return 3 if d < 15 else 4  


def d3_si(lon): return (sign_index_from_lon(lon)+int((lon%30)//10)*4)%12


def d4_si(lon): return (sign_index_from_lon(lon)+int((lon%30)//7.5)*3)%12


def d7_si(lon):
    s = sign_index_from_lon(lon); slot = int((lon % 30) // (30 / 7))
    start = s if s % 2 == 0 else (s + 6) % 12  
    return (start + slot) % 12


def d9_si(lon):
    s=sign_index_from_lon(lon); slot=int((lon%360%30)//(30/9))
    start=s if s in MOVABLE_SIGNS else ((s+8)%12 if s in FIXED_SIGNS else (s+4)%12)
    return (start+slot)%12


def d10_si(lon):
    s=sign_index_from_lon(lon); slot=int((lon%360%30)//3)
    return ((s if s%2==0 else (s+8)%12)+slot)%12


def d12_si(lon): return (sign_index_from_lon(lon)+int((lon%360%30)//2.5))%12


def d30_si(lon):
    s = sign_index_from_lon(lon); d = lon % 30
    if s % 2 == 0:  
        if d < 5: return 0      
        if d < 10: return 10    
        if d < 18: return 8     
        if d < 25: return 2     
        return 6                
    else:           
        if d < 5: return 1      
        if d < 12: return 5     
        if d < 20: return 11    
        if d < 25: return 9     
        return 7                


def d60_si(lon):
    # D60 Shashtiamsha — BPHS Ch.7 / Jagannatha Hora convention:
    # 60 parts of 0°30' each, count forward from the sign itself for all signs.
    #     D60_sign = (natal_sign + part_number) % 12
    # Previously this function used a non-BPHS variant (count from Aries for
    # odd / backward from Pisces for even). Standardised to match the
    # Parashara's Light / JH default — most rigorous open reference.
    s = sign_index_from_lon(lon)
    part = min(int((lon % 30) / 0.5), 59)
    return (s + part) % 12


def get_placidus_house(lon, cusps):
    for i in range(12):
        c1=cusps[i]; c2=cusps[(i+1)%12]
        if c1<c2:
            if c1<=lon<c2: return i+1
        else:
            if lon>=c1 or lon<c2: return i+1
    return 1


def get_kp_4step(pname, ls, planet_data, r_lon, k_lon):
    lon=get_planet_lon_helper(pname,planet_data,r_lon,k_lon)
    if lon is None: return ""
    _,nl,_=nakshatra_info(lon)
    nl_lon=get_planet_lon_helper(nl,planet_data,r_lon,k_lon)
    nl_occ=whole_sign_house(ls,sign_index_from_lon(nl_lon)) if nl_lon else None
    nl_own=[h for h in range(1,13) if SIGN_LORDS_MAP[(ls+h-1)%12]==nl]
    p_occ=whole_sign_house(ls,sign_index_from_lon(lon))
    p_own=[h for h in range(1,13) if SIGN_LORDS_MAP[(ls+h-1)%12]==pname]
    
    sigs=[]
    if nl_occ: sigs.append(f"L1(NL in H{nl_occ})")
    sigs.append(f"L2(In H{p_occ})")
    if nl_own: sigs.append(f"L3(NL owns H{','.join(map(str,nl_own))})")
    if p_own: sigs.append(f"L4(Owns H{','.join(map(str,p_own))})")
    return " | ".join(sigs)


def reduce_num(n,keep=True):
    if keep and n in [11,22,33]: return n
    while n>9:
        if keep and n in [11,22,33]: return n
        n=sum(int(d) for d in str(n))
    return n


def calculate_numerology_core(name,dob_str,system="Western (Pythagorean)"):
    y,m,d=map(int,dob_str.split('-'))
    nm=PYTH_MAP if system=="Western (Pythagorean)" else CHALDEAN_MAP
    lp=reduce_num(reduce_num(y)+reduce_num(m)+reduce_num(d))
    clean=name.lower().replace(" ",""); vowels=set('aeiou')
    ds=su=ps=0
    for ch in clean:
        if ch in nm:
            val=nm[ch]; ds+=val
            if ch in vowels: su+=val
            else: ps+=val
    return reduce_num(lp),reduce_num(ds),reduce_num(su),reduce_num(ps)


def get_personal_year(dob_str,for_year=None):
    if for_year is None: for_year=datetime.now(ZoneInfo("Asia/Kolkata")).year
    y,m,d=map(int,dob_str.split('-'))
    return reduce_num(reduce_num(m)+reduce_num(d)+reduce_num(for_year))


def get_personal_month(dob_str,tz="Asia/Kolkata"):
    py=get_personal_year(dob_str); cm=datetime.now(ZoneInfo(tz)).month  
    return reduce_num(py+reduce_num(cm))


def get_personal_day(dob_str,tz="Asia/Kolkata"):
    pm=get_personal_month(dob_str,tz); cd=datetime.now(ZoneInfo(tz)).day  
    return reduce_num(pm+reduce_num(cd))


def get_pinnacle_cycles(dob_str):
    y,m,d=map(int,dob_str.split('-'))
    lp,_,_,_=calculate_numerology_core("",dob_str)
    p1=reduce_num(reduce_num(m)+reduce_num(d)); p2=reduce_num(reduce_num(d)+reduce_num(y))
    p3=reduce_num(p1+p2); p4=reduce_num(reduce_num(m)+reduce_num(y))
    c1=abs(reduce_num(m,keep=False)-reduce_num(d,keep=False))
    c2=abs(reduce_num(d,keep=False)-reduce_num(y,keep=False))
    c3=abs(c1-c2)
    c4=abs(reduce_num(m,keep=False)-reduce_num(y,keep=False))
    d1e=36-lp
    r1=(y,y+d1e,p1,c1); r2=(y+d1e,y+d1e+9,p2,c2)
    r3=(y+d1e+9,y+d1e+18,p3,c3); r4=(y+d1e+18,y+100,p4,c4)
    return r1,r2,r3,r4


# get_tarot_birth_card moved to features/tarot/service.py as get_birth_card.


def extract_base_score(dossier_text, house_number):
    match = re.search(rf"H{house_number} \([^)]+\):.*?Base Score: (\d)", dossier_text)
    return int(match.group(1)) if match else 1


def extract_ashtakavarga_score(dossier_text, house_number):
    pattern = rf"SAV TOTAL:.*?H{house_number}:(\d+)"
    match = re.search(pattern, dossier_text)
    if match:
        bindus = int(match.group(1))
        if bindus >= 30: return 3
        if bindus >= 25: return 2
        return 1
    return 2 


def check_affliction(dossier_text, affliction_type):
    if affliction_type == "Sade Sati": return "Sade Sati: ACTIVE" in dossier_text or "ACTIVE (Phase" in dossier_text
    elif "Graha Yuddha" in affliction_type: return "WINS (higher ecliptic latitude)" in dossier_text
    return False


def score_planet_in_house(p_house, good_houses, bad_houses):
    if p_house in good_houses: return 2
    if p_house in bad_houses: return -1
    return 1


def clamp_val(value, low=0, high=100):
    return max(low, min(high, value))


def score_positive(parts):
    total = 0
    weight = 0
    for value, w in parts:
        total += clamp_val(value) * w
        weight += w
    return clamp_val(total / weight if weight else 50)


def split_csv_ints(raw):
    return {int(x) for x in re.findall(r"\d+", raw or "")}


def criterion_key(label):
    text = str(label).strip()
    known = [
        "Wealth Potential", "Relationship Quality", "Career Success",
        "Life Struggles", "Health & Longevity", "Happiness & Contentment",
        "Luck & Fortune", "Spiritual Depth", "Hidden Pitfalls",
    ]
    for key in known:
        if text.startswith(key):
            return key
    for sep in [" — ", " â€” ", " - ", " -- ", " – "]:
        if sep in text:
            return text.split(sep, 1)[0].strip()
    return text


def section_between(text, start_marker, end_marker=None):
    start = text.find(start_marker)
    if start < 0: return ""
    if end_marker is None:
        return text[start:]
    end = text.find(end_marker, start + len(start_marker))
    return text[start:] if end < 0 else text[start:end]


def kp_score_from_verdict(verdict):
    v = (verdict or "").upper()
    if "STRONGLY PROMISED" in v: return 3
    if "PARTIALLY PROMISED" in v: return 2
    if "DENIED" in v or "NOT PROMISED" in v: return 0
    return 1


def house_norm(base_score):
    return {1: 38, 2: 62, 3: 84}.get(base_score, 50)


def sav_norm(bindus):
    if bindus is None: return 50
    return clamp_val(50 + (bindus - 28) * 3.2, 25, 85)


def kp_norm(kp_score):
    return {0: 25, 1: 50, 2: 68, 3: 86}.get(kp_score, 50)


def parse_varga_line(dossier_text, label):
    match = re.search(rf"{label}[^:]*:\s*([^\n]+)", dossier_text)
    if not match: return {}
    out = {}
    for part in match.group(1).split(","):
        if ":" not in part: continue
        planet, sign = [x.strip() for x in part.split(":", 1)]
        sign = re.sub(r"[^A-Za-z ]", "", sign).strip()
        if planet and sign: out[planet] = sign
    return out


def extract_present_yogas(dossier_text):
    present = {}
    section = section_between(dossier_text, "[Yogas", "[Jaimini")
    for line in section.splitlines():
        if "Yoga" not in line or "ABSENT" in line.upper(): continue
        match = re.search(r"([A-Za-z][A-Za-z\-\s]+Yoga(?:\s*\(Negative\))?):\s*(.*)", line)
        if match:
            present[re.sub(r"\s+", " ", match.group(1)).strip()] = match.group(2).strip()
    return present


@lru_cache(maxsize=100)
def parse_chart_facts(dossier_text):
    facts = {
        "houses": {},
        "house_lords": {},
        "planets": {},
        "sav": {},
        "kp": {},
        "yogas": extract_present_yogas(dossier_text),
        "vargas": {
            "D2": parse_varga_line(dossier_text, "D2 Hora"),
            "D9": parse_varga_line(dossier_text, "D9 Navamsa"),
            "D10": parse_varga_line(dossier_text, "D10 Dasamsa"),
            "D12": parse_varga_line(dossier_text, "D12"),
            "D30": parse_varga_line(dossier_text, "D30"),
        },
        "karakas": {},
        "neecha_bhanga": set(),
        "weak_sav_houses": set(),
        "strong_sav_houses": set(),
        "manglik": "NOT MANGLIK",
        "arudha_lagna": {"house": 0, "sign": ""},
        "indu_lagna": {"sign": ""},
    }

    al_match = re.search(r"Arudha Lagna \(AL\):\s*([A-Za-z]+)\s*\(H(\d+)\)", dossier_text)
    if al_match:
        facts["arudha_lagna"] = {"sign": al_match.group(1), "house": int(al_match.group(2))}
        
    indu_match = re.search(r"Indu Lagna \(Wealth\):\s*([A-Za-z]+)", dossier_text)
    if indu_match:
        facts["indu_lagna"] = {"sign": indu_match.group(1)}

    for h, theme, lord, lord_house, flags, kp_sl, base in re.findall(
        r"H(\d{1,2}) \(([^)]+)\): Lord=([A-Za-z]+)\(H(\d{1,2})\) \[([^\]]*)\] \| KP SL=([A-Za-z]+): .*?Base Score: (\d)",
        dossier_text
    ):
        hnum = int(h)
        facts["houses"][hnum] = {"theme": theme, "base": int(base), "kp_sl": kp_sl, "flags": flags, "occupants": []}
        facts["house_lords"][hnum] = {"planet": lord, "house": int(lord_house), "flags": flags}

    for h, sign, lord, lord_house, occ in re.findall(
        r"H(\d{2})\(([A-Za-z]+)\): Lord=([A-Za-z]+)\(H(\d{1,2})\) \| ([^\n]+)",
        dossier_text
    ):
        hnum = int(h)
        facts["house_lords"].setdefault(hnum, {"planet": lord, "house": int(lord_house), "flags": ""})
        facts["houses"].setdefault(hnum, {"theme": sign, "base": extract_base_score(dossier_text, hnum), "kp_sl": "", "flags": "", "occupants": []})
        facts["houses"][hnum]["occupants"] = [x.strip() for x in occ.split(",") if x.strip() and x.strip() != "Empty"]

    planet_pat = re.compile(
        rf"^\s*{PLANET_RE}: H(\d{{1,2}})\s+([A-Za-z]+)\s+.*?(?:\[(.*?)\])?.*?(?:Avastha:([^|]+)\|)?\s*Nak:([^(]+)\(NL:([A-Za-z]+)\s+SL:([A-Za-z]+)",
        re.MULTILINE
    )
    for match in planet_pat.finditer(dossier_text):
        planet, house, sign, tags_raw, avastha, nak, nl, sl = match.groups()
        tags = {t.strip() for t in (tags_raw or "").split(",") if t.strip()}
        facts["planets"][planet] = {
            "house": int(house),
            "sign": sign,
            "tags": tags,
            "avastha": (avastha or "").strip(),
            "nak": nak.strip(),
            "nak_lord": nl,
            "sub_lord": sl,
            "kp_sigs": set(),
            "war": "",
        }

    for planet, sig_text in re.findall(rf"{PLANET_RE}.*?KP 4-Step:\s*([^\n]+)", dossier_text):
        facts["planets"].setdefault(planet, {"house": 0, "tags": set(), "kp_sigs": set(), "war": ""})
        facts["planets"][planet]["kp_sigs"] = split_csv_ints(sig_text)

    sav_match = re.search(r"SAV TOTAL:\s*([^\n]+)", dossier_text)
    if sav_match:
        for h, bindus in re.findall(r"H(\d{1,2}):(\d+)", sav_match.group(1)):
            facts["sav"][int(h)] = int(bindus)
    for h, bindus in re.findall(r"H(\d{1,2})\((\d+)\)", section_between(dossier_text, "WEAK HOUSES")):
        if int(bindus) <= 22: facts["weak_sav_houses"].add(int(h))
    for h, bindus in re.findall(r"H(\d{1,2})\((\d+)\)", section_between(dossier_text, "STRONG HOUSES")):
        if int(bindus) >= 30: facts["strong_sav_houses"].add(int(h))

    for h, sigs, matched, verdict in re.findall(
        r"H(\d{1,2}) KP Promise.*?SL signifies houses:\s*\[([^\]]*)\].*?Matched:\s*\[([^\]]*)\].*?VERDICT:\s*([^\n]+)",
        dossier_text
    ):
        hnum = int(h)
        facts["kp"][hnum] = {
            "sigs": split_csv_ints(sigs),
            "matched": split_csv_ints(matched),
            "verdict": verdict.strip(),
            "score": kp_score_from_verdict(verdict),
        }

    for kname, planet in re.findall(r"(Atmakaraka|Amatyakaraka|Darakaraka)[^:]*:\s*([A-Za-z]+)", dossier_text):
        facts["karakas"][kname] = planet

    for planet in re.findall(r"([A-Za-z]+)\s+.*?NEECHA BHANGA APPLIES", dossier_text):
        if planet in PLANETS: facts["neecha_bhanga"].add(planet)

    for winner, loser in re.findall(r"([A-Za-z]+) vs ([A-Za-z]+).*?WINS", dossier_text):
        facts["planets"].setdefault(winner, {"house": 0, "tags": set(), "kp_sigs": set(), "war": ""})["war"] = "WINNER"
        facts["planets"].setdefault(loser, {"house": 0, "tags": set(), "kp_sigs": set(), "war": ""})["war"] = "LOSER"

    m = re.search(r"Manglik:\s*([^\n]+)", dossier_text)
    if m: facts["manglik"] = m.group(1).strip()

    return facts


def planet_house(facts, planet):
    return facts["planets"].get(planet, {}).get("house", 0)


def planet_strength(facts, planet):
    if not planet: return 50
    data = facts["planets"].get(planet, {})
    tags = data.get("tags", set())
    score = 52
    if any(t == "Exalted" or t.startswith("Exalted") for t in tags): score += 24
    if any("Own Sign" in t for t in tags): score += 16
    if any("VARGOTTAMA" in t.upper() for t in tags): score += 10
    if any("D9-Exalted" in t for t in tags): score += 9
    if any("D9-Own Sign" in t for t in tags): score += 6
    if any("D9-Debilitated" in t for t in tags): score -= 10
    if any("Debilitated" in t for t in tags):
        score -= 22
        if planet in facts["neecha_bhanga"]: score += 24
    if any("Combust" in t for t in tags): score -= 11
    if any("GANDANTA" in t for t in tags): score -= 8
    if any("PAPA-KARTARI" in t for t in tags): score -= 10
    if data.get("war") == "LOSER": score -= 14
    if data.get("avastha") in {"Adult", "Youth"}: score += 5
    elif data.get("avastha") == "Old": score -= 4
    elif data.get("avastha") == "Dead": score -= 13
    
    nak_lord = data.get("nak_lord")
    if nak_lord and nak_lord in facts["planets"]:
        nl_tags = facts["planets"][nak_lord].get("tags", set())
        if any(t == "Exalted" or t.startswith("Exalted") for t in nl_tags): score += 6
        if any("Own Sign" in t for t in nl_tags): score += 3
        if any("Debilitated" in t for t in nl_tags): score -= 6

    if planet in {"Rahu", "Ketu"}:
        score = 50
        if any("VARGOTTAMA" in t.upper() for t in tags): score += 8
        if any("GANDANTA" in t for t in tags): score -= 10
    return clamp_val(score, 10, 95)


def varga_sign_strength(facts, chart, planet):
    if not planet: return 50
    sign = facts["vargas"].get(chart, {}).get(planet)
    if not sign: return 50
    sidx = SIGN_INDEX.get(sign)
    if sidx is None: return 50
    score = 50
    if planet in DIGNITIES:
        if sidx == DIGNITIES[planet][0]: score += 24
        elif sidx == DIGNITIES[planet][1]: score -= 24
    if planet in OWN_SIGNS and sidx in OWN_SIGNS[planet]: score += 16
    if planet in {"Rahu", "Ketu"} and sign in {"Gemini", "Virgo", "Sagittarius", "Pisces", "Scorpio"}:
        score += 6
    return clamp_val(score, 20, 88)


def house_score(facts, house):
    base = house_norm(facts["houses"].get(house, {}).get("base", 1))
    sav = sav_norm(facts["sav"].get(house))
    lord = facts["house_lords"].get(house, {}).get("planet")
    lord_strength = planet_strength(facts, lord) if lord else 50
    lord_house = facts["house_lords"].get(house, {}).get("house")
    placement_bonus = 0
    if lord_house in KENDRAS or lord_house in TRIKONAS: placement_bonus += 5
    if lord_house in DUSTHANAS: placement_bonus -= 7
    return clamp_val(base * 0.45 + sav * 0.20 + lord_strength * 0.30 + 5 + placement_bonus, 15, 95)


def topic_yoga_score(facts, names, planet_data=None, ls=None, lagna_lon=None, jd_ut=None):
    """Sum the weights of yogas in `names` that are present in the chart, with
    each weight scaled by `yoga_strength_multiplier()` — so a Dhana Yoga with
    debilitated lords contributes less than one with exalted lords.

    The multiplier is clamped to [0.4, 1.3] to keep wealth yogas from going
    to zero on weak charts (classical doctrine: yoga always promises something)
    AND from inflating beyond ~1.3× of raw weight (prevents stacking-bloat).

    Falls back to raw flat-add when planet_data/ls/lagna_lon are not provided
    (older call sites).
    """
    total = 0.0
    have_context = planet_data is not None and ls is not None and lagna_lon is not None and jd_ut is not None
    for name, weight in names.items():
        if name not in facts["yogas"]: continue
        if have_context:
            mult = yoga_strength_multiplier(name, facts, planet_data, ls, lagna_lon, jd_ut)
            mult = max(0.4, min(1.3, mult))
        else:
            mult = 1.0
        total += weight * mult
    return total


def topic_house_connection(facts, planets, houses):
    houses = set(houses)
    score = 0
    for planet in planets:
        if not planet: continue
        pdata = facts["planets"].get(planet, {})
        if pdata.get("house") in houses: score += 4
        matched = pdata.get("kp_sigs", set()) & houses
        score += min(6, len(matched) * 2)
    return score


def affliction_count(facts, planets=None, houses=None):
    planets = set(planets or facts["planets"].keys())
    houses = set(houses or range(1, 13))
    count = 0
    for planet in planets:
        if not planet: continue
        pdata = facts["planets"].get(planet, {})
        if pdata.get("house") not in houses: continue
        tags = pdata.get("tags", set())
        if any("Debilitated" in t for t in tags) and planet not in facts["neecha_bhanga"]: count += 1
        if any("Combust" in t for t in tags): count += 1
        if any("GANDANTA" in t for t in tags): count += 1
        if any("PAPA-KARTARI" in t for t in tags): count += 1
        if pdata.get("war") == "LOSER": count += 1
        if pdata.get("avastha") == "Dead": count += 1
    return count


def malefic_pressure(facts, houses):
    houses = set(houses)
    score = 0
    for planet in NATURAL_MALEFICS:
        h = planet_house(facts, planet)
        if h in houses:
            score += 6 if planet in {"Rahu", "Ketu", "Saturn", "Mars"} else 3
    return score


def benefic_support(facts, houses):
    houses = set(houses)
    return sum(5 for planet in NATURAL_BENEFICS if planet_house(facts, planet) in houses)


def extract_kp_promise(dossier_text, house_number):
    """Read the KP H{n} sub-lord verdict score (0/1/2/3) from a dossier.

    Returns -1 instead of the silent `1` fallback when the dossier doesn't
    expose the KP section at all — that way upstream scorers can detect
    "we have no KP signal" vs. "the chart's KP signal is genuinely neutral".
    A console warning is printed so format-drift bugs surface immediately.
    """
    facts = parse_chart_facts(dossier_text)
    if house_number in facts["kp"]:
        return facts["kp"][house_number]["score"]
    pattern = rf"H{house_number} KP Promise[^|]+\| VERDICT: ([^\n]+)"
    match = re.search(pattern, dossier_text)
    if match:
        return kp_score_from_verdict(match.group(1))
    import sys
    print(f"[extract_kp_promise] WARNING: no KP promise found for H{house_number} "
          f"— dossier may be malformed or KP section missing.", file=sys.stderr)
    return 1   # neutral fallback (preserves existing call-site behaviour)


def extract_planet_dignity(dossier_text, planet_name):
    strength = planet_strength(parse_chart_facts(dossier_text), planet_name)
    if strength >= 78: return 3
    if strength >= 65: return 2
    if strength >= 54: return 1
    if strength <= 35: return -2
    return 0


def extract_yoga_presence(dossier_text, yoga_name):
    return 1 if yoga_name in parse_chart_facts(dossier_text)["yogas"] else 0


def extract_yogas(dossier_text):
    return len(parse_chart_facts(dossier_text)["yogas"])


def extract_planet_house(dossier_text, planet_name):
    return planet_house(parse_chart_facts(dossier_text), planet_name)


def recalc_math_from_profile(profile):
    """
    Build the same chart-math tuple as recalc_math() but compute it DIRECTLY
    from a BirthData profile dict instead of regex-parsing the printed dossier.

    Eliminates the silent 50.0 fallback class of bugs: when the dossier-text
    format drifts even slightly, regex recalc_math returns None and every
    Compare Profile scorer falls back to neutral. Direct computation from
    profile primitives can't drift.

    profile must contain: date (ISO or date), time (HH:MM or time), tz, lat, lon.
    """
    from datetime import date as _date, datetime as _datetime
    d = profile["date"]
    if isinstance(d, str): d = _date.fromisoformat(d)
    t = profile["time"]
    if isinstance(t, str): t = _datetime.strptime(t, "%H:%M").time()

    jd_ut, _, _ = local_to_julian_day(d, t, profile["tz"])
    lagna_lon, _ = get_lagna_and_cusps(jd_ut, profile["lat"], profile["lon"])
    ls = sign_index_from_lon(lagna_lon)
    placidus_cusps = get_placidus_cusps(jd_ut, profile["lat"], profile["lon"])
    planet_data = {pn: get_planet_longitude_and_speed(jd_ut, pid) for pn, pid in PLANETS.items()}
    r_lon = get_rahu_longitude(jd_ut)
    k_lon = (r_lon + 180.0) % 360
    planet_data["Rahu"] = (r_lon, -0.05)
    planet_data["Ketu"] = (k_lon, -0.05)
    return ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon


def recalc_math(dossier, profile=None):
    """Recover the chart's Julian Day + planet longitudes + cusps.

    PREFERRED PATH: pass `profile` (the BirthData dict) — direct computation,
    no regex, no silent fallback.

    LEGACY PATH: only `dossier` provided — regex-parses the printed report.
    Returns None on parse failure and logs a clear stderr warning so the
    50.0 fallback in calculate_*_score() is visible.
    """
    if profile is not None:
        try:
            return recalc_math_from_profile(profile)
        except Exception as e:
            import sys
            print(f"[recalc_math] WARNING: profile path failed ({e}); falling back to regex.",
                  file=sys.stderr)

    import sys
    time_match = re.search(r"Time:\s*(.*?)\s*\(", dossier)
    coord_match = re.search(r"Coordinates:\s*([0-9.]+)([NS]),\s*([0-9.]+)([EW])\s*\|\s*Timezone:\s*([^\s\n]+)", dossier)
    if not time_match or not coord_match:
        print(f"[recalc_math] WARNING: failed to parse Time/Coordinates from dossier "
              f"(time_match={bool(time_match)}, coord_match={bool(coord_match)}). "
              f"Scoring functions will fall back to neutral 50.0 — outputs unreliable.",
              file=sys.stderr)
        return None
    dt_str = time_match.group(1).strip()
    try:
        dt_local = datetime.strptime(dt_str, "%d %b %Y, %I:%M %p")
    except Exception as e:
        print(f"[recalc_math] WARNING: time parse failed for '{dt_str}': {e}", file=sys.stderr)
        return None
    lat_val, lat_dir, lon_val, lon_dir, tz_name = coord_match.groups()
    lat = float(lat_val) if lat_dir == 'N' else -float(lat_val)
    lon = float(lon_val) if lon_dir == 'E' else -float(lon_val)
    
    jd_ut, _, _ = local_to_julian_day(dt_local.date(), dt_local.time(), tz_name)
    lagna_lon, _ = get_lagna_and_cusps(jd_ut, lat, lon)
    ls = sign_index_from_lon(lagna_lon)
    placidus_cusps = get_placidus_cusps(jd_ut, lat, lon)
    planet_data = {pn: get_planet_longitude_and_speed(jd_ut, pid) for pn, pid in PLANETS.items()}
    r_lon = get_rahu_longitude(jd_ut)
    k_lon = (r_lon + 180.0) % 360
    planet_data["Rahu"] = (r_lon, -0.05)
    planet_data["Ketu"] = (k_lon, -0.05)
    return ls, lagna_lon, planet_data, placidus_cusps, jd_ut, r_lon, k_lon


def calculate_shadbala(pname, p_lon, p_spd, lagna_lon, ls, f, planet_data, jd_ut):
    if pname in {"Rahu", "Ketu"}: return 5.0
    sthana = 0
    deep_exaltation = {"Sun": 10, "Moon": 33, "Mars": 298, "Mercury": 165, "Jupiter": 95, "Venus": 357, "Saturn": 200}
    if pname in deep_exaltation:
        neecha = (deep_exaltation[pname] + 180) % 360
        dist = abs(p_lon - neecha)
        dist = min(dist, 360 - dist)
        sthana += dist / 3.0 
    p_sign = int(p_lon // 30) % 12
    varga_str = planet_strength(f, pname) 
    sthana += (varga_str / 95.0) * 112.5 
    if p_sign % 2 == 0:
        if pname in {"Sun", "Mars", "Jupiter", "Saturn", "Mercury"}: sthana += 15
    else:
        if pname in {"Venus", "Moon"}: sthana += 15
    p_house = ((p_sign - ls) % 12) + 1
    if p_house in {1, 4, 7, 10}: sthana += 60
    elif p_house in {2, 5, 8, 11}: sthana += 30
    else: sthana += 15
    drekkana = int((p_lon % 30) // 10)
    if drekkana == 0 and pname in {"Sun", "Mars", "Jupiter"}: sthana += 15
    elif drekkana == 1 and pname in {"Mercury", "Saturn"}: sthana += 15
    elif drekkana == 2 and pname in {"Moon", "Venus"}: sthana += 15
    dig_peak_house = {"Jupiter": 1, "Mercury": 1, "Sun": 10, "Mars": 10, "Saturn": 7, "Moon": 4, "Venus": 4}
    dig = 0
    if pname in dig_peak_house:
        peak_lon = ((ls + dig_peak_house[pname] - 1) * 30 + 15) % 360
        dist = abs(p_lon - peak_lon)
        dist = min(dist, 360 - dist)
        dig = (180 - dist) / 3.0 
    sun_lon = planet_data.get("Sun", (0,0))[0]
    sun_dist = (sun_lon - lagna_lon) % 360
    time_fraction = (sun_dist + 90) % 360 / 360.0
    if pname in {"Moon", "Mars", "Saturn"}: nath = (1.0 - abs(time_fraction - 0.5) * 2) * 60
    elif pname in {"Sun", "Jupiter", "Venus"}: nath = (abs(time_fraction - 0.5) * 2) * 60
    else: nath = 60 
    moon_lon = planet_data.get("Moon", (0,0))[0]
    moon_sun_diff = (moon_lon - sun_lon) % 360
    if pname in {"Moon", "Venus", "Jupiter", "Mercury"}:
        paksha = moon_sun_diff / 3.0 if moon_sun_diff <= 180 else (360 - moon_sun_diff) / 3.0
    else:
        paksha = (180 - (moon_sun_diff if moon_sun_diff <= 180 else (360 - moon_sun_diff))) / 3.0
    if pname == "Moon": paksha *= 2
    kala = nath + paksha
    chesta = 0
    if p_spd < 0: chesta = 60 
    elif pname in {"Sun", "Moon"}:
        if pname == "Sun": chesta = 30
        if pname == "Moon" and paksha > 30: chesta = 30
    else: chesta = 15 
    naisargika = {"Sun": 60, "Moon": 51.4, "Venus": 42.8, "Jupiter": 34.2, "Mercury": 25.7, "Mars": 17.1, "Saturn": 8.5}
    nais = naisargika.get(pname, 0)
    drig = 0
    for op, (olon, ospd) in planet_data.items():
        if op == pname or op in {"Rahu", "Ketu"}: continue
        drishti = calc_drishti(olon, p_lon, op)
        if op in {"Jupiter", "Venus", "Mercury", "Moon"}: drig += drishti / 4.0
        else: drig -= drishti / 4.0
    return max(0.1, (sthana + dig + kala + chesta + nais + drig) / 60.0)


def calculate_argala(house_idx, f):
    argala_houses = [(house_idx + offset - 1) % 12 + 1 for offset in [2, 4, 5, 11]]
    virodha_houses = [(house_idx + offset - 1) % 12 + 1 for offset in [3, 10, 12]]
    net_argala = 0
    for h in argala_houses:
        occupants = f["houses"].get(h, {}).get("occupants", [])
        for occ in occupants:
            if occ in {"Jupiter", "Venus", "Moon", "Mercury"}: net_argala += 4
            elif occ in {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}: net_argala += 2
    for h in virodha_houses:
        occupants = f["houses"].get(h, {}).get("occupants", [])
        for occ in occupants:
            if occ in {"Jupiter", "Venus", "Moon", "Mercury"}: net_argala -= 3
            elif occ in {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}: net_argala -= 2
    return net_argala


def yoga_strength_multiplier(yoga_name, facts, planet_data, ls, lagna_lon, jd_ut):
    """Scale a yoga's contribution by the mean strength of its constituent
    planets. A Dhana Yoga with debilitated lords contributes less than one
    with exalted lords. Returned value is roughly in [0.4, 1.3] after clamp;
    1.0 = constituents at neutral 75-Shadbala baseline.
    """
    def _ps(p): return get_p_str(p, planet_data, ls, facts, lagna_lon, jd_ut)
    def _avg(planets):
        ps = [_ps(p) for p in planets if p]
        return (sum(ps) / len(ps)) / 75.0 if ps else 1.0

    # House-lord helpers for wealth yogas
    h2_lord  = facts.get("house_lords", {}).get(2,  {}).get("planet")
    h4_lord  = facts.get("house_lords", {}).get(4,  {}).get("planet")
    h5_lord  = facts.get("house_lords", {}).get(5,  {}).get("planet")
    h6_lord  = facts.get("house_lords", {}).get(6,  {}).get("planet")
    h9_lord  = facts.get("house_lords", {}).get(9,  {}).get("planet")
    h11_lord = facts.get("house_lords", {}).get(11, {}).get("planet")
    h1_lord  = facts.get("house_lords", {}).get(1,  {}).get("planet")

    # Pancha Mahapurusha + Gajakesari + Chandra-Mangala (existing)
    if   yoga_name == "Gajakesari Yoga":     return _avg(["Jupiter", "Moon"])
    elif yoga_name == "Hamsa Yoga":          return _avg(["Jupiter"])
    elif yoga_name == "Malavya Yoga":        return _avg(["Venus"])
    elif yoga_name in {"Ruchaka Yoga", "Chandra-Mangala Yoga"}:
                                              return _avg(["Mars"])
    elif yoga_name == "Bhadra Yoga":         return _avg(["Mercury"])
    elif yoga_name == "Shasha Yoga":         return _avg(["Saturn"])

    # Wealth yogas — scale by mean strength of constituent planets
    elif yoga_name == "Dhana Yoga":
        return _avg([h2_lord, h5_lord, h9_lord, h11_lord])
    elif yoga_name == "Lakshmi Yoga":
        return _avg([h9_lord, "Venus"])
    elif yoga_name == "Akhand Samrajya Yoga":
        return _avg([h2_lord, h9_lord, h11_lord, "Jupiter"])
    elif yoga_name == "Mahabhagya Yoga":
        return _avg(["Sun", "Moon", h1_lord])
    elif yoga_name == "Sankha Yoga":
        return _avg([h5_lord, h6_lord, h1_lord])
    elif yoga_name == "Kahala Yoga":
        return _avg([h4_lord, h9_lord, h1_lord])

    # Raja Yoga, Parivartana, Viparita Raja — scale by Lagna lord as a proxy
    # for "is this person's chart structurally healthy enough to use this"
    elif yoga_name in {"Raja Yoga", "Parivartana Yoga", "Viparita Raja Yoga",
                       "Dharma-Karma Adhipati Yoga"}:
        return _avg([h1_lord])

    return 1.0


def calc_drishti(p1_lon, p2_lon, p1_name):
    diff = (p2_lon - p1_lon) % 360
    aspects = [180]
    if p1_name == "Mars": aspects += [90, 210]
    elif p1_name in {"Jupiter", "Rahu", "Ketu"}: aspects += [120, 240]
    elif p1_name == "Saturn": aspects += [60, 270]
    max_strength = 0
    for asp in aspects:
        orb = abs(diff - asp)
        orb = min(orb, 360 - orb)
        if orb <= 15:
            strength = 100 - (orb * 6.66)
            if strength > max_strength: max_strength = strength
    return max_strength


def get_bhava_bala(house_idx, ls, planet_data, f, lagna_lon, jd_ut):
    bindus = f["sav"].get(house_idx, 28)
    base_score = sav_norm(bindus) 
    lord = f["house_lords"].get(house_idx, {}).get("planet")
    lord_strength = get_p_str(lord, planet_data, ls, f, lagna_lon, jd_ut) 
    argala = calculate_argala(house_idx, f)
    return max(0, min(100, base_score * 0.45 + lord_strength * 0.40 + argala * 1.5))


def get_kp_sub_lord_score(house_idx, placidus_cusps, planet_data, r_lon, k_lon, ls, required_houses, deny_houses):
    cusp_lon = placidus_cusps[house_idx - 1]
    sl = get_kp_sub_lord(cusp_lon)
    sigs = get_planet_house_significations(sl, ls, {pn: (plon, 0) for pn, (plon, pspd) in planet_data.items() if pn not in ["Rahu","Ketu"]}, r_lon, k_lon)
    score = 50
    req_match = len(sigs & required_houses)
    deny_match = len(sigs & deny_houses)
    score += (req_match * 15)
    score -= (deny_match * 15)
    return max(0, min(100, score))


def get_p_str(p, planet_data, ls, f, lagna_lon, jd_ut):
    if not p or p not in planet_data: return 50
    plon, pspd = planet_data[p]
    rupas = calculate_shadbala(p, plon, pspd, lagna_lon, ls, f, planet_data, jd_ut)
    return clamp_val(50 + (rupas - 6.0) * 12.5)


def calculate_tara_bala(natal_moon_lon, transit_moon_lon):
    ns = 360 / 27
    natal_idx = int((natal_moon_lon % 360) // ns)
    transit_idx = int((transit_moon_lon % 360) // ns)
    
    tara_value = ((transit_idx - natal_idx) % 9) + 1
    
    tara_meanings = {
        1: {"tara": "Janma (Birth)", "color": "🟡 YELLOW", "status": "Caution", "advice": "Your mind may feel restless or overwhelmed today. Stick to routine tasks and avoid making impulsive decisions."},
        2: {"tara": "Sampat (Wealth)", "color": "🟢 GREEN", "status": "Go", "advice": "Highly favorable for finances and resources. Excellent day to ask for a raise, make investments, or close a deal."},
        3: {"tara": "Vipat (Danger)", "color": "🔴 RED", "status": "Stop", "advice": "Obstacles and sudden losses are likely. Keep a very low profile today. Do not start new projects or argue with authority."},
        4: {"tara": "Kshema (Well-being)", "color": "🟢 GREEN", "status": "Go", "advice": "A day of peace, healing, and stability. Perfect for self-care, finalizing plans, and nurturing relationships."},
        5: {"tara": "Pratyak (Obstacles)", "color": "🔴 RED", "status": "Stop", "advice": "You will face resistance and delays. People may oppose your ideas. Focus on patience and do not force outcomes today."},
        6: {"tara": "Sadhaka (Achievement)", "color": "🟢 GREEN", "status": "Go", "advice": "Cosmic green light for ambition. Your efforts will yield direct success today. Push hard on your biggest goals."},
        7: {"tara": "Naidhana (Destruction)", "color": "🔴 RED", "status": "Stop", "advice": "Severe cosmic friction. Avoid travel, signing contracts, or taking risks. Use today strictly for cleaning up old messes."},
        8: {"tara": "Mitra (Friendship)", "color": "🟢 GREEN", "status": "Go", "advice": "Support from others is highlighted. Great day for networking, collaborating, and asking for favors."},
        9: {"tara": "Parama Mitra (Great Joy)", "color": "🟢 GREEN", "status": "Go", "advice": "Extremely auspicious. Things will easily go your way. Take bold actions and enjoy the cosmic tailwind!"}
    }
    return tara_meanings[tara_value]
   
def get_moon_lon_from_profile(profile):
    d = date.fromisoformat(profile['date']) if isinstance(profile['date'], str) else profile['date']
    t = datetime.strptime(profile['time'], "%H:%M").time() if isinstance(profile['time'], str) else profile['time']
    jd, _, __ = local_to_julian_day(d, t, profile['tz'])
    lon, _ = get_planet_longitude_and_speed(jd, PLANETS["Moon"])
    return lon


# ─────────────────────────────────────────────────────────────────────────────
# EVENT TIMING ATLAS — Lifetime Vimshottari sequence + per-event activation
# windows. Solves the "at what age will I..." class of consultation questions
# by handing the AI precomputed answers instead of asking it to infer.
# ─────────────────────────────────────────────────────────────────────────────

# Classical karaka maturation ages (Bhrigu / Brihat Parashara). The age at which
# each planet's significations "lock in" as durable life results.
KARAKA_MATURATION = {
    "Jupiter": 16,   # wisdom, children, dharma
    "Sun":     22,   # authority, father, soul-purpose
    "Moon":    24,   # mind, mother, public-facing self
    "Venus":   25,   # marriage, partnerships, refinement
    "Mars":    28,   # courage, action, technical mastery
    "Mercury": 32,   # commerce, intellect, profession
    "Saturn":  36,   # career permanence, discipline, responsibility
    "Rahu":    42,   # foreign / non-classical gains
    "Ketu":    48,   # detachment, moksha-orientation
}

# Houses that govern each major life event (Parashari + KP combined).
# Significator = a planet that (a) owns one of these houses, (b) occupies one,
# (c) has its nakshatra-lord in one, or (d) is a natural karaka.
EVENT_HOUSE_MAP = {
    "Earning / Income":   {"houses": {2, 10, 11},      "karakas": {"Sun", "Mercury", "Saturn"}},
    "Marriage / Spouse":  {"houses": {2, 7, 11},       "karakas": {"Venus", "Jupiter"}},
    "Career / Profession":{"houses": {1, 6, 10, 11},   "karakas": {"Sun", "Saturn", "Mercury"}},
    "Children":           {"houses": {2, 5, 11},       "karakas": {"Jupiter"}},
    "Property / Home":    {"houses": {4, 11},          "karakas": {"Mars", "Moon"}},
    "Education":          {"houses": {2, 4, 5, 9},     "karakas": {"Mercury", "Jupiter"}},
    "Foreign / Travel":   {"houses": {3, 9, 12},       "karakas": {"Rahu", "Moon"}},
    "Health / Longevity": {"houses": {1, 8},           "karakas": {"Sun", "Saturn"}},
    "Spiritual / Moksha": {"houses": {5, 8, 9, 12},    "karakas": {"Ketu", "Jupiter", "Saturn"}},
    "Fame / Recognition": {"houses": {1, 5, 9, 10, 11},"karakas": {"Sun", "Jupiter"}},
}


def build_lifetime_dasha_sequence(dt_birth, moon_lon):
    """Full Vimshottari Mahadasha sequence from birth through ~120 years.

    Returns list of dicts:
      [{"lord": str, "years": float, "start": datetime, "end": datetime,
        "start_age": float, "end_age": float, "is_balance": bool}, ...]
    The first entry is the partial-balance MD of the nakshatra-starting lord.
    """
    ns = 360.0 / 27
    idx = int((moon_lon % 360) // ns)
    start_lord = NAKSHATRA_LORDS[idx]
    balance = DASHA_YEARS[start_lord] * (1 - ((moon_lon % 360 % ns) / ns))
    si = DASHA_ORDER.index(start_lord)
    seq = DASHA_ORDER[si:] + DASHA_ORDER[:si]
    md_list = [(seq[0], balance, True)] + [(l, float(DASHA_YEARS[l]), False) for l in seq[1:]]

    out = []
    cursor = dt_birth
    for lord, yrs, is_bal in md_list:
        end = cursor + timedelta(days=yrs * YEAR_DAYS)
        out.append({
            "lord": lord,
            "years": yrs,
            "start": cursor,
            "end": end,
            "start_age": (cursor - dt_birth).days / YEAR_DAYS,
            "end_age":   (end    - dt_birth).days / YEAR_DAYS,
            "is_balance": is_bal,
        })
        cursor = end
    return out


def _planet_signifies_houses(pname, target_houses, ls, planet_data, r_lon, k_lon):
    """True if `pname` is a classical significator of any house in `target_houses`.
    Combines: occupied house + owned houses + nakshatra-lord chain.
    """
    sigs = get_planet_house_significations(pname, ls, planet_data, r_lon, k_lon)
    return bool(sigs & set(target_houses))


def _get_md_significator_role(lord, event_houses, event_karakas, ls, planet_data, r_lon, k_lon):
    """Classify HOW a given MD lord activates an event area, or '' if it doesn't.
    Roles in descending priority:
      'house_lord'   — owns one of the event houses (strongest, structural)
      'house_occupy' — sits in one of the event houses
      'karaka'       — natural karaka of the event
      'kp_signify'   — signifies via nakshatra-lord chain only
    """
    if lord in ("Unknown", None) or lord not in planet_data and lord not in ("Rahu", "Ketu"):
        return ""

    # Own houses (rashi ownership)
    owned_houses = {whole_sign_house(ls, sidx) for sidx, l in SIGN_LORDS_MAP.items() if l == lord}
    if owned_houses & set(event_houses):
        return "house_lord"

    # Occupancy
    lon = get_planet_lon_helper(lord, planet_data, r_lon, k_lon)
    if lon is not None:
        occ_h = whole_sign_house(ls, sign_index_from_lon(lon))
        if occ_h in event_houses:
            return "house_occupy"

    if lord in event_karakas:
        return "karaka"

    # Nakshatra-lord chain (KP-style)
    if _planet_signifies_houses(lord, event_houses, ls, planet_data, r_lon, k_lon):
        return "kp_signify"

    return ""


def _format_md_window(md_entry, role, event_name, ls, planet_data, r_lon, k_lon, event_houses):
    """One-line description of why this MD activates the event area."""
    lord = md_entry["lord"]
    sa, ea = md_entry["start_age"], md_entry["end_age"]
    sy, ey = md_entry["start"].strftime("%b %Y"), md_entry["end"].strftime("%b %Y")

    owned = sorted({whole_sign_house(ls, sidx) for sidx, l in SIGN_LORDS_MAP.items() if l == lord})
    owned_str = f"owns H{','.join(str(h) for h in owned if h in event_houses)}" if (set(owned) & event_houses) else ""

    lon = get_planet_lon_helper(lord, planet_data, r_lon, k_lon)
    occ_h = whole_sign_house(ls, sign_index_from_lon(lon)) if lon is not None else None
    occ_str = f"in H{occ_h}" if occ_h in event_houses else ""

    role_label = {
        "house_lord":   "STRONG (house-lord)",
        "house_occupy": "MODERATE (occupies event house)",
        "karaka":       "MODERATE (natural karaka)",
        "kp_signify":   "WEAK (KP nakshatra-chain only)",
    }.get(role, "")

    reason_bits = [b for b in (owned_str, occ_str) if b]
    reason = "; ".join(reason_bits) if reason_bits else f"karaka of {event_name}"

    return (f"    • {lord:<8} MD — age {sa:5.1f} → {ea:5.1f}  "
            f"({sy} → {ey})  [{role_label}; {reason}]")


def build_event_timing_atlas(profile, dasha_info, ls, planet_data, r_lon, k_lon, placidus_cusps):
    """The Event Timing Atlas — precomputed timing windows for major life events.

    This is the answer-source for "at what age will I..." consultation questions.
    Returns a multi-line string ready to drop into the dossier.

    Methodology (classical Parashari + KP confirmation):
      1. Build the lifetime Mahadasha sequence with ages.
      2. For each event area (earning, marriage, career, …), find every MD
         whose lord significantly activates that area (lord/occupy/karaka/KP).
      3. For the CURRENT MD only, also walk its antardashas and flag any AD
         whose lord activates the area (within-MD precision).
      4. Mention karaka maturation ages overlapping the lifetime.
    """
    # 1. Parse birth datetime from profile.
    pd_date = date.fromisoformat(profile['date']) if isinstance(profile['date'], str) else profile['date']
    pd_time = datetime.strptime(profile['time'], "%H:%M").time() if isinstance(profile['time'], str) else profile['time']
    _, dt_birth, _ = local_to_julian_day(pd_date, pd_time, profile['tz'])

    # 2. Now-time in the user's local zone (for "today's age" framing).
    dt_now_local = datetime.now(ZoneInfo(profile['tz']))
    current_age = (dt_now_local - dt_birth).days / YEAR_DAYS

    # 3. Lifetime MD sequence.
    moon_lon = planet_data["Moon"][0]
    lifetime = build_lifetime_dasha_sequence(dt_birth, moon_lon)

    lines = []
    lines.append("EVENT TIMING ATLAS — Lifetime Vimshottari + Karaka Maturation")
    lines.append("(Pre-computed activation windows — cite these directly for 'when/what age' questions.)")
    lines.append(f"Birth: {dt_birth.strftime('%d %b %Y, %H:%M')} ({profile['tz']}) | Now: {dt_now_local.strftime('%d %b %Y')} | Current age: {current_age:.1f}")
    lines.append("")

    # 4. Lifetime MD sequence table.
    lines.append("LIFETIME MAHADASHA SEQUENCE (lord, age window, calendar window):")
    for md in lifetime:
        marker = "  ◀ NOW" if md["start_age"] <= current_age < md["end_age"] else ""
        bal = " [partial-balance from birth]" if md["is_balance"] else ""
        lines.append(f"  {md['lord']:<8} : age {md['start_age']:5.1f} → {md['end_age']:5.1f}   "
                     f"({md['start'].strftime('%b %Y')} → {md['end'].strftime('%b %Y')}){marker}{bal}")
    lines.append("")

    # 5. Karaka maturation table (filter to ones in the user's possible lifespan).
    lines.append("KARAKA MATURATION AGES (the age at which each planet's signification 'locks in'):")
    for planet, age in sorted(KARAKA_MATURATION.items(), key=lambda kv: kv[1]):
        passed = "✓ already matured" if current_age >= age else f"matures in {age - current_age:.1f} yrs"
        lines.append(f"  {planet:<8} matures at age {age:>2}  ({passed})")
    lines.append("")

    # 6. Per-event activation windows.
    lines.append("PER-EVENT ACTIVATION WINDOWS (which MDs activate which life areas):")
    for event_name, spec in EVENT_HOUSE_MAP.items():
        houses, karakas = spec["houses"], spec["karakas"]

        # Identify the house lords for the event houses
        house_lords = sorted({SIGN_LORDS_MAP[(ls + h - 1) % 12] for h in houses})

        lines.append("")
        lines.append(f"  ── {event_name} ──")
        lines.append(f"    Required houses : {sorted(houses)}   |   "
                     f"House-lords in this chart: {', '.join(house_lords)}   |   "
                     f"Natural karakas: {', '.join(sorted(karakas))}")

        # Walk lifetime MDs and flag activators
        activator_lines = []
        for md in lifetime:
            # Skip MDs entirely in the past beyond ~5 years (they're history but
            # still worth showing — user said past windows are also useful).
            role = _get_md_significator_role(
                md["lord"], houses, karakas, ls, planet_data, r_lon, k_lon
            )
            if role:
                activator_lines.append(
                    _format_md_window(md, role, event_name, ls, planet_data, r_lon, k_lon, houses)
                )

        if activator_lines:
            for ln in activator_lines:
                lines.append(ln)
        else:
            lines.append("    • (no lifetime MD strongly activates this area — event hinges on transits/yogas)")

        # Within-current-MD antardasha precision
        cur_md = dasha_info.get("current_md", "Unknown")
        if cur_md != "Unknown":
            cur_md_years = dasha_info.get("md_total_years", 0)
            if cur_md_years > 0:
                mi = DASHA_ORDER.index(cur_md)
                aseq = DASHA_ORDER[mi:] + DASHA_ORDER[:mi]
                ad_cursor = dasha_info["md_start"]
                ad_hits = []
                for al in aseq:
                    ay = (cur_md_years * DASHA_YEARS[al]) / 120.0
                    ad_end = ad_cursor + timedelta(days=ay * YEAR_DAYS)
                    role = _get_md_significator_role(
                        al, houses, karakas, ls, planet_data, r_lon, k_lon
                    )
                    if role and role in ("house_lord", "house_occupy", "karaka"):
                        marker = " ◀ NOW" if dasha_info["ad_start"] <= ad_cursor < dasha_info["ad_end"] else ""
                        ad_hits.append(
                            f"      ↳ {cur_md}/{al} AD: "
                            f"{ad_cursor.strftime('%b %Y')} → {ad_end.strftime('%b %Y')}  "
                            f"[{role}]{marker}"
                        )
                    ad_cursor = ad_end
                if ad_hits:
                    lines.append(f"    Within current {cur_md} MD — fine-grained antardasha hits:")
                    for h in ad_hits[:6]:  # cap noise
                        lines.append(h)

    lines.append("")
    lines.append("READING RULES (apply when user asks 'when/what age'):")
    lines.append("  1. Cite the earliest STRONG window the user has not yet aged out of.")
    lines.append("  2. If asked about a past event, identify which STRONG/MODERATE window it fell into.")
    lines.append("  3. Karaka maturation is a secondary anchor — mention if it falls inside a STRONG MD/AD window.")
    lines.append("  4. KP cusp 'NOT PROMISED' verdicts mean 'the cusp gate is weak', NOT 'the event won't happen'.")
    lines.append("     Dasha activation can still trigger the event with classical-style effort.")
    lines.append("  5. NEVER refuse a timing question. The Atlas above always has at least one window per event.")

    return "\n".join(lines)
