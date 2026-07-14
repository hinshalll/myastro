"""shared.astro.muhurta — Event Timing Planner ("best dates & times to do X")
for the mobile Explore tab.

FREE + cheap by design (cost rule): pure MATH + a pre-baked STATIC lookup of
classical Muhurta (electional astrology) rules. NO live AI call, NO new
dependencies. Date- and LOCATION-based (panchanga + sunrise/sunset) — NO birth
chart needed.

For each day in a range we score how well its panchanga (the five limbs —
tithi, nakshatra, yoga, karana, vara/weekday) suits the chosen event, using
SOURCED classical rules, then pick the best clear time window that day (Abhijit
Muhurta or a "good" Choghadiya), making sure it sidesteps Rahu Kaal / Yamaganda /
Gulika Kaal. We return the strongest few days; if nothing in the range scores
well we say so plainly rather than forcing a weak pick.

SOURCES (verified across multiple reputable references — Brihat Samhita /
Muhurta Chintamani tradition, drikpanchang, mpanchang, astrobix, astroccult,
astrosight, anytimeastro):
  • Universal AVOID — Rikta tithis (4 Chaturthi, 9 Navami, 14 Chaturdashi) and
    Amavasya (new moon); the Vishti (Bhadra) karana; the Vyatipata & Vaidhriti
    yogas (with a milder caution for other harsh yogas).
  • Per-event favourable NAKSHATRAS, weekdays — see _EVENT_RULES (each with a
    source note). These intersect what multiple panchang services publish.
  • Abhijit Muhurta = the 8th of 15 daytime muhurtas (around local noon), the
    near-universal "good window"; Choghadiya Amrit/Shubh/Labh = good segments.

Framing rule (blueprint §2): warm, plain, beginner-friendly. No jargon in the
main lines; Sanskrit/technical terms live ONLY in `why` / `sanskrit`.
"""

from datetime import date as _date, timedelta

from shared.astro.constants import PLANETS, NAKSHATRAS, NAK_NATURES
from shared.astro.astro_calc import (
    local_to_julian_day, get_planet_longitude_and_speed, get_panchanga,
    nakshatra_info, sun_rise_set, daily_timing_windows,
)
from shared.astro.forecast import _NAK_DEVANAGARI


# ── Per-event classical rules. `nakshatras` = favourable lunar mansions for that
#    event (the classical CORE gate); `good_wd` / `avoid_wd` = weekdays by Python
#    weekday() (Mon=0 .. Sun=6). Tithi / yoga / karana rules are universal (below).
#    Easy to expand: add an entry here. Each carries a short source note.
_EVENT_RULES: dict[str, dict] = {
    # Yatra — light/movable & gentle stars (astroccult, astrobix). Tue weaker.
    "travel": {
        "label": "travel or a journey",
        "nakshatras": {"Ashwini", "Mrigashira", "Punarvasu", "Pushya", "Hasta",
                       "Anuradha", "Shravana", "Dhanishta", "Revati", "Mula"},
        "good_wd": {0, 2, 3, 4}, "avoid_wd": {1},
    },
    # Business / contracts — Pushya (king of stars) + the steady Uttaras
    # (astrosight, astroccult). Thu/Fri strongest; Sun avoided.
    "signing": {
        "label": "signing a deal or starting a business",
        "nakshatras": {"Pushya", "Ashwini", "Hasta", "Chitra", "Swati", "Anuradha",
                       "Uttara Phalguni", "Uttara Ashadha", "Uttara Bhadrapada", "Revati"},
        "good_wd": {0, 2, 3, 4}, "avoid_wd": {1, 6},
    },
    # Namkaran — soft + steady stars (mpanchang, astrosage, astroccult).
    "naming": {
        "label": "a naming ceremony",
        "nakshatras": {"Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
                       "Hasta", "Chitra", "Swati", "Anuradha", "Uttara Phalguni",
                       "Uttara Ashadha", "Uttara Bhadrapada", "Shravana",
                       "Dhanishta", "Shatabhisha", "Revati"},
        "good_wd": {0, 2, 3, 4}, "avoid_wd": {1, 5, 6},
    },
    # Vehicle — movable stars favoured (drikpanchang, mpanchang, anytimeastro).
    # Sunday is accepted for vehicles; Tue/Sat weaker.
    "vehicle": {
        "label": "buying a vehicle",
        "nakshatras": {"Ashwini", "Mrigashira", "Punarvasu", "Pushya", "Chitra",
                       "Hasta", "Swati", "Anuradha", "Uttara Ashadha",
                       "Uttara Bhadrapada", "Revati", "Dhanishta", "Shravana",
                       "Shatabhisha"},
        "good_wd": {0, 2, 3, 4, 6}, "avoid_wd": {1, 5},
    },
    # Griha Pravesh — the fixed/Dhruva stars + soft ones (drikpanchang,
    # togetherbuying). Avoid Sun/Sat/Tue.
    "housewarming": {
        "label": "a housewarming",
        "nakshatras": {"Rohini", "Mrigashira", "Chitra", "Anuradha", "Pushya",
                       "Uttara Phalguni", "Uttara Ashadha", "Uttara Bhadrapada",
                       "Shravana", "Dhanishta", "Revati"},
        "good_wd": {0, 2, 3, 4}, "avoid_wd": {1, 5, 6},
    },
    # Vivaha — the classical wedding stars (drikpanchang authoritative list,
    # mpanchang, ganeshaspeaks). Mon/Wed/Thu/Fri favoured; Tue/Sat/Sun avoided.
    # NOTE: panchanga-based auspicious DATES; a real wedding muhurat also weighs
    # both charts + guna milan (our matchmaking tool), so we frame these as
    # "generally auspicious wedding days".
    "marriage": {
        "label": "a wedding",
        "nakshatras": {"Rohini", "Mrigashira", "Magha", "Uttara Phalguni", "Hasta",
                       "Swati", "Anuradha", "Mula", "Uttara Ashadha",
                       "Uttara Bhadrapada", "Revati"},
        "good_wd": {0, 2, 3, 4}, "avoid_wd": {1, 5, 6},
    },
    # Surgery / operation — the SPECIAL case that INVERTS the universal rules
    # (Muhurta-for-surgery texts; starspeak, reliableastrology, clickastro,
    # indiadivine): the sharp/Tikshna stars (Ardra, Ashlesha, Jyeshtha, Mula) for
    # the "cutting", Tuesday (Mars = surgery) & Saturday (Saturn = disease) are
    # BEST, and the Rikta tithis (4/9/14) are FAVOURABLE here, not avoided. Hence
    # `rikta_ok`. Framed as gentle guidance — surgery timing is best confirmed with
    # a doctor and an astrologer.
    "surgery": {
        "label": "surgery or an operation",
        "nakshatras": {"Ardra", "Ashlesha", "Jyeshtha", "Mula"},
        "good_wd": {1, 5}, "avoid_wd": set(),
        "rikta_ok": True,
    },
    # Starting medical treatment / medicine (distinct from cutting) — the healing
    # set led by Ashwini (star of the divine physicians), plus the soft/steady
    # stars (clickastro, truthstar). Mon/Wed/Thu/Fri; Saturn's day eased off.
    "medical": {
        "label": "starting treatment",
        "nakshatras": {"Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
                       "Hasta", "Chitra", "Swati", "Anuradha", "Shravana",
                       "Dhanishta", "Shatabhisha", "Uttara Bhadrapada", "Revati"},
        "good_wd": {0, 2, 3, 4}, "avoid_wd": {5},
    },
    # Vidyarambha — starting studies (drikpanchang, astrosage, ganeshaspeaks):
    # Ashwini/Rohini/Punarvasu/Hasta/Swati/Anuradha/Mula/Uttara Bhadrapada + the
    # learning stars. Wed/Thu/Fri (Mercury/Jupiter/Venus) favoured; Tue/Sat eased.
    "education": {
        "label": "starting studies",
        "nakshatras": {"Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
                       "Hasta", "Chitra", "Swati", "Anuradha", "Mula", "Shravana",
                       "Revati", "Uttara Bhadrapada"},
        "good_wd": {2, 3, 4}, "avoid_wd": {1, 5},
    },
    # Buying property / land (drikpanchang, mpanchang, anytimeastro): the fixed
    # (Dhruva) stars anchor immovable assets, plus soft ones. Tue (Mars = land) /
    # Thu / Fri favoured; Sat/Sun eased. (Panchak caution is nakshatra-based and
    # partly captured by the star set.)
    "property": {
        "label": "buying property or land",
        "nakshatras": {"Rohini", "Mrigashira", "Uttara Phalguni", "Uttara Ashadha",
                       "Uttara Bhadrapada", "Chitra", "Swati", "Anuradha",
                       "Dhanishta", "Shatabhisha", "Revati"},
        "good_wd": {1, 3, 4}, "avoid_wd": {5, 6},
    },
    # Joining a new job (astrotales, ganeshaspeaks, indastro): the mild/friendly
    # stars for a lasting livelihood. Sun/Mon/Wed/Thu/Fri auspicious; Tue/Sat eased.
    "job": {
        "label": "starting a new job",
        "nakshatras": {"Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
                       "Hasta", "Chitra", "Swati", "Anuradha", "Uttara Phalguni",
                       "Uttara Ashadha", "Uttara Bhadrapada", "Revati"},
        "good_wd": {0, 2, 3, 4, 6}, "avoid_wd": {1, 5},
    },
    # Mundan / Chudakarana — a child's first haircut (drikpanchang, astrosage,
    # 99pandit): movable + gentle + short stars, and Jyeshtha. Mon/Wed/Thu/Fri.
    "mundan": {
        "label": "a mundan (first haircut)",
        "nakshatras": {"Ashwini", "Mrigashira", "Punarvasu", "Pushya", "Hasta",
                       "Chitra", "Swati", "Jyeshtha", "Shravana", "Dhanishta",
                       "Shatabhisha", "Revati"},
        "good_wd": {0, 2, 3, 4}, "avoid_wd": {1, 5, 6},
    },
    # Annaprashana — a baby's first solid food (drikpanchang, clickastro,
    # ganeshaspeaks): the nourishing stars (Pushya/Rohini/Shravana/Revati foremost).
    # Mon/Wed/Thu/Fri; Shukla paksha and Purnima especially good.
    "annaprashana": {
        "label": "a baby's first-food ceremony",
        "nakshatras": {"Rohini", "Mrigashira", "Punarvasu", "Pushya", "Hasta",
                       "Chitra", "Swati", "Anuradha", "Shravana", "Dhanishta",
                       "Uttara Phalguni", "Uttara Ashadha", "Uttara Bhadrapada",
                       "Revati"},
        "good_wd": {0, 2, 3, 4}, "avoid_wd": {1, 5, 6},
    },
    # General — the broadly auspicious set (Pushya foremost).
    "general": {
        "label": "an important new start",
        "nakshatras": {"Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
                       "Hasta", "Chitra", "Swati", "Anuradha", "Uttara Phalguni",
                       "Uttara Ashadha", "Uttara Bhadrapada", "Shravana",
                       "Dhanishta", "Revati"},
        "good_wd": {0, 2, 3, 4}, "avoid_wd": {1, 5},
    },
}


# Free-text → the nearest event rule-set (for the "type a custom thing" box).
# Deterministic keyword match, NO AI. Specific categories are checked before the
# generic "signing" bucket so "buy a car" → vehicle, "buy a house" → housewarming.
# Order matters — the FIRST matching set wins, so specific life-events are listed
# before the broad "signing" (business) net. Baby ceremonies (mundan/annaprashana)
# come before "naming" so "baby's first haircut" isn't caught by a naming keyword.
_EVENT_KEYWORDS = [
    ("travel", ("travel", "trip", "journey", "flight", "vacation", "holiday",
                "yatra", "pilgrimage", "tour", "visit abroad")),
    ("vehicle", ("car", "bike", "scooter", "vehicle", "truck", "auto", "motorcycle",
                 "new ride")),
    ("marriage", ("wedding", "marry", "married", "marriage", "shaadi", "shadi",
                  "vivah", "vivaah", "betroth", "engagement", "sagai", "roka",
                  "nuptial")),
    ("property", ("property", "land", "plot", "real estate", "real-estate",
                  "registry", "registration", "buy a house", "buy house",
                  "buy a flat", "buy flat", "buy a home", "buy home", "buy land",
                  "purchase property", "buy property", "buy a plot", "site")),
    ("housewarming", ("housewarming", "house warming", "griha pravesh", "griha",
                      "pravesh", "move in", "moving in", "move into",
                      "shift to", "new house pooja", "new home pooja")),
    ("surgery", ("surgery", "operation", "operate", "operated", "surgical",
                 "transplant", "c-section", "cesarean", "caesarean")),
    ("medical", ("treatment", "medicine", "medication", "therapy", "chemo",
                 "dialysis", "start medicine", "begin treatment", "healing",
                 "recovery start", "physiotherapy")),
    ("education", ("education", "study", "studies", "school", "college",
                   "admission", "exam", "course", "tuition", "vidyarambh",
                   "vidyarambha", "aksharabhyasa", "learning", "degree", "class")),
    ("mundan", ("mundan", "mundana", "tonsure", "first haircut", "chudakaran",
                "choodakaran", "choodakarana", "chudakarana", "choula",
                "shave head", "hair cutting ceremony")),
    ("annaprashana", ("annaprashan", "annaprashana", "first food", "first rice",
                      "rice ceremony", "feeding ceremony", "weaning",
                      "first solid")),
    ("naming", ("naming", "namkaran", "namakaran", "name ceremony", "baby name",
                "name my baby", "newborn", "christening", "cradle")),
    ("job", ("job", "joining", "interview", "promotion", "appraisal",
             "employment", "new role", "offer letter", "join office", "new job",
             "resume", "placement")),
    ("signing", ("business", "deal", "contract", "agreement", "sign",
                 "office", "startup", "company", "shop", "invest", "buy",
                 "purchase", "loan", "launch", "open", "venture", "money",
                 "raise", "salary")),
]


def classify_event(text: str) -> str:
    """Map a free-text event ('start a YouTube channel', 'buy a bike') to the
    nearest classical rule-set, or 'general'. Deterministic, no AI."""
    t = (text or "").lower()
    for event, kws in _EVENT_KEYWORDS:
        if any(k in t for k in kws):
            return event
    return "general"


# Universal tithi rules (apply to every event).
_RIKTA_TITHIS = {4, 9, 14}                       # "empty" days — avoid
_AUSPICIOUS_TITHIS = {1, 2, 3, 5, 7, 10, 11, 13}  # broadly supportive

# Universal yoga rules.
_STRONG_AVOID_YOGAS = {"Vyatipata", "Vaidhriti"}
_HARSH_YOGAS = {"Vishkambha", "Atiganda", "Soola", "Ganda", "Vyaghata", "Vajra", "Parigha"}
_AUSPICIOUS_YOGAS = {"Siddhi", "Subha", "Sukarma", "Priti", "Saubhagya", "Sobhana",
                     "Ayushman", "Dhriti", "Vriddhi", "Dhruva", "Harshana", "Brahma",
                     "Indra", "Siddha", "Sadhya", "Sukla", "Variyan"}

# Reverse nakshatra → nature label (e.g. "Fixed (Dhruva)") for warm copy.
_NAK_TO_NATURE = {n: label for label, names in NAK_NATURES.items() for n in names}

_MIN_SCORE = 0.60   # a day must clear this (and carry a favourable star) to be recommended
_MAX_DAYS = 370     # safety cap on the scanned range


def _ampm(hm: str) -> str:
    h, m = (int(x) for x in hm.split(":"))
    return f"{h % 12 or 12}:{m:02d} {'am' if h < 12 else 'pm'}"


def _to_min(hm: str) -> int:
    h, m = (int(x) for x in hm.split(":"))
    return h * 60 + m


def _parse_tithi(tithi_str: str):
    """'4 Shukla (Waxing)' → (4, is_amavasya). Amavasya = Krishna 15."""
    num = int(tithi_str.split()[0])
    is_amavasya = num == 15 and "Krishna" in tithi_str
    is_purnima = num == 15 and "Shukla" in tithi_str
    return num, is_amavasya, is_purnima


def _score_day(rules: dict, nak: str, tithi_str: str, yoga: str, karana: str, wd: int):
    """Additive classical score for one day. Returns (score 0..1, favourable_star?)."""
    score = 0.45                       # neutral baseline ("ordinary day")
    fav_star = nak in rules["nakshatras"]
    if fav_star:
        score += 0.40                  # the right nakshatra is the classical core

    t_num, amavasya, purnima = _parse_tithi(tithi_str)
    if amavasya:
        score -= 0.40
    elif t_num in _RIKTA_TITHIS:
        # Rikta tithis (4/9/14) are "empty" days avoided for most events, BUT some
        # (notably surgery) classically FAVOUR them — `rikta_ok` skips the penalty.
        if not rules.get("rikta_ok"):
            score -= 0.22
    elif purnima or t_num in _AUSPICIOUS_TITHIS:
        score += 0.08

    if wd in rules["good_wd"]:
        score += 0.10
    elif wd in rules["avoid_wd"]:
        score -= 0.12

    yname = yoga.split()[0] if yoga else ""
    if yname in _STRONG_AVOID_YOGAS:
        score -= 0.35
    elif yname in _HARSH_YOGAS:
        score -= 0.10
    elif yname in _AUSPICIOUS_YOGAS:
        score += 0.06

    if "Vishti" in karana:
        score -= 0.22

    return round(min(0.99, max(0.02, score)), 2), fav_star


def _pick_window(d: _date, lat: float, lon: float, tz: str):
    """Best clear daytime window that sidesteps Rahu Kaal / Yamaganda / Gulika.
    Prefers Abhijit Muhurta, else the first 'good' daytime Choghadiya. Returns
    (name, start_hm, end_hm, clean?)."""
    win = daily_timing_windows(d, lat, lon, tz)
    avoid = [(_to_min(a["start"]), _to_min(a["end"])) for a in win["avoid"]]

    def clear(s, e):
        sm, em = _to_min(s), _to_min(e)
        return not any(sm < re and rs < em for rs, re in avoid)

    candidates = [(g["name"], g["start"], g["end"]) for g in win["good"]]  # Abhijit first
    candidates += [(c["name"], c["start"], c["end"]) for c in win["choghadiya"]
                   if c["period"] == "day" and c["quality"] == "good"]
    for name, s, e in candidates:
        if clear(s, e):
            return name, s, e, True
    # Nothing fully clear → fall back to Abhijit, flagged.
    g = win["good"][0]
    return g["name"], g["start"], g["end"], False


def plan_muhurta(event_type: str, start_date, end_date, lat: float, lon: float,
                 tz: str, top_n: int = 5) -> dict:
    """Plan the best dates+times for an event over a date range. Pure math +
    static lookup, no AI. Deterministic for the same inputs.

    Returns { event_type, event_label, range, found, message, recommendations:[
    { date, start, end, score, reason, why, sanskrit, ...debug } ] }.
    """
    # (Ephemeris adapter is always Lahiri-sidereal — no global state to set.)

    key = (event_type or "").lower()
    if key not in _EVENT_RULES:
        key = classify_event(key)          # free-text ("buy a bike") → nearest rules
    rules = _EVENT_RULES[key]
    label = rules["label"]

    start = _date.fromisoformat(start_date) if isinstance(start_date, str) else start_date
    end = _date.fromisoformat(end_date) if isinstance(end_date, str) else end_date
    if end < start:
        start, end = end, start
    span = min((end - start).days, _MAX_DAYS)

    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    scored = []
    for i in range(span + 1):
        d = start + timedelta(days=i)
        # Panchanga at LOCAL SUNRISE (the day's ruling limbs — classical din-shuddhi).
        sunrise, _sunset, _next = sun_rise_set(d, lat, lon, tz)
        jd, dtl, _ = local_to_julian_day(d, sunrise.time(), tz)
        sun_lon, _ = get_planet_longitude_and_speed(jd, PLANETS["Sun"])
        moon_lon, _ = get_planet_longitude_and_speed(jd, PLANETS["Moon"])
        pan = get_panchanga(sun_lon, moon_lon, dtl)
        nak, _lord, _pada = nakshatra_info(moon_lon)
        wd = d.weekday()

        score, fav_star = _score_day(rules, nak, pan["tithi"], pan["yoga"], pan["karana"], wd)
        _t_num, amavasya, _pur = _parse_tithi(pan["tithi"])
        if fav_star and score >= _MIN_SCORE and not amavasya:
            scored.append({"date": d, "score": score, "nak": nak, "pan": pan, "wd": wd})

    # Strongest first; ties broken by the earlier date.
    scored.sort(key=lambda r: (-r["score"], r["date"]))
    top = scored[:max(1, top_n)] if scored else []

    recs = []
    for r in top:
        d = r["date"]
        name, s, e, clean = _pick_window(d, lat, lon, tz)
        nak = r["nak"]
        pan = r["pan"]
        nature = _NAK_TO_NATURE.get(nak, "")
        _art = lambda w: ("an" if w[:1].lower() in "aeiou" else "a")  # a/an by sound
        nat_word = nature.split(' (')[0].lower() if nature else ""
        nat_phrase = f" — {_art(nat_word)} {nat_word} star" if nat_word else ""

        is_abhijit = name == "Abhijit Muhurta"
        win_phrase = "Abhijit Muhurta, the day's strongest stretch" if is_abhijit else f"{_art(name)} {name} window"
        reason = (f"{nak} is one of the welcoming stars for {label}{nat_phrase}, "
                  f"and the day lines up well. A clear time opens "
                  f"{_ampm(s)}–{_ampm(e)} ({win_phrase}).")
        if not clean:
            reason += " (This window brushes a rough patch of the day, so keep it brief.)"

        why = (
            f"On this day the Moon sits in {nak}, the kind of star classical Muhurta picks "
            f"for {label}. The lunar day ({pan['tithi']}) and weekday ({weekday_names[r['wd']]}) "
            f"are supportive, and none of the rough combinations (the Vishti/Bhadra karana, or "
            f"the Vyatipata/Vaidhriti yogas) land on it. The {_ampm(s)}–{_ampm(e)} window "
            f"{'is the Abhijit Muhurta and ' if is_abhijit else ''}steps clear of Rahu Kaal "
            f"and the other harsh patches. Treat it as gentle guidance, not a guarantee."
        )

        nak_dev = _NAK_DEVANAGARI[NAKSHATRAS.index(nak)]
        win_skt = "अभिजित् मुहूर्त" if is_abhijit else "शुभ मुहूर्त"
        sanskrit = f"{nak_dev} नक्षत्रे · {win_skt}"

        recs.append({
            "date": d.isoformat(),
            "start": s, "end": e,
            "score": r["score"],
            "reason": reason,
            "why": why,
            "sanskrit": sanskrit,
            # Transparency / debug (cheap, panchanga-based).
            "nakshatra": nak,
            "tithi": pan["tithi"],
            "weekday": weekday_names[r["wd"]],
            "yoga": pan["yoga"],
            "karana": pan["karana"],
            "window": name,
            "window_clear": clean,
        })

    if recs:
        message = (f"Here {'is the strongest day' if len(recs) == 1 else f'are the {len(recs)} strongest days'} "
                   f"for {label} in your dates.")
    else:
        message = (f"Nothing in these dates stands out as a strong, clear time for {label}. "
                   f"Try widening the range — the right stars may simply fall just outside it.")

    return {
        "event_type": (event_type or "general").lower(),
        "event_label": label,
        "range": {"start": start.isoformat(), "end": end.isoformat()},
        "found": bool(recs),
        "message": message,
        "recommendations": recs,
    }
