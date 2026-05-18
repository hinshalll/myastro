import swisseph as swe
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

PLANETS = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,
           "Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN}

# Outer planets — modern additions (not part of classical Vedic 9-graha set).
# Used for chart display (some apps include them) and Western appendix.
# Yoga / dasha / dignity detection skips them automatically since they
# aren't in DASHA_ORDER / SIGN_LORDS_MAP / OWN_SIGNS.
OUTER_PLANETS = {"Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO}

DIGNITIES = {"Sun":(0,6),"Moon":(1,7),"Mars":(9,3),"Mercury":(5,11),
             "Jupiter":(3,9),"Venus":(11,5),"Saturn":(6,0)}

OWN_SIGNS = {"Sun":[4],"Moon":[3],"Mars":[0,7],"Mercury":[2,5],
             "Jupiter":[8,11],"Venus":[1,6],"Saturn":[9,10]}

SIGN_LORDS_MAP = {0:"Mars",1:"Venus",2:"Mercury",3:"Moon",4:"Sun",5:"Mercury",
                  6:"Venus",7:"Mars",8:"Jupiter",9:"Saturn",10:"Saturn",11:"Jupiter"}

COMBUST_DEGREES = {"Mercury":14,"Venus":10,"Mars":17,"Jupiter":11,"Saturn":15}

NAKSHATRAS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu",
              "Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta",
              "Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha",
              "Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
              "Uttara Bhadrapada","Revati"]

NAKSHATRA_LORDS = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]*3

NAK_NATURES = {
    "Fixed (Dhruva)":  ["Rohini","Uttara Phalguni","Uttara Ashadha","Uttara Bhadrapada"],
    "Movable (Chara)": ["Punarvasu","Swati","Shravana","Dhanishta","Shatabhisha"],
    "Fierce (Ugra)":   ["Bharani","Magha","Purva Phalguni","Purva Ashadha","Purva Bhadrapada"],
    "Mixed (Mishra)":  ["Krittika","Vishakha"],
    "Swift (Kshipra)": ["Ashwini","Pushya","Hasta"],
    "Tender (Mridu)":  ["Mrigashira","Chitra","Anuradha","Revati"],
    "Sharp (Tikshna)": ["Ardra","Ashlesha","Jyeshtha","Mula"],
}

NAK_ADVICE = {
    "Fixed (Dhruva)":  "Best for long-term commitments, buying property, and starting permanent things.",
    "Movable (Chara)": "Great for travel, change, buying vehicles, or beginning new chapters.",
    "Fierce (Ugra)":   "Intense energy — good for assertive action, cutting through obstacles.",
    "Mixed (Mishra)":  "Average day — stick to routine tasks and pending work.",
    "Swift (Kshipra)": "High-pace energy — ideal for quick tasks, trading, and fast decisions.",
    "Tender (Mridu)":  "Soft, creative day — perfect for romance, arts, and new friendships.",
    "Sharp (Tikshna)": "Focused energy — excellent for research, analysis, and ending bad habits.",
}

DASHA_YEARS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,
               "Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}

DASHA_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]

YOGA_NAMES = ["Vishkambha","Priti","Ayushman","Saubhagya","Sobhana","Atiganda","Sukarma",
              "Dhriti","Soola","Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra",
              "Siddhi","Vyatipata","Variyan","Parigha","Siva","Siddha","Sadhya","Subha",
              "Sukla","Brahma","Indra","Vaidhriti"]

# YEAR_DAYS = length of one Vimshottari "year" in solar days.
# Standardised on 365.25 (Julian year) to match Astrosage, Parashara's Light,
# and Jagannatha Hora. Previously 365.2425 (Gregorian average) which produced
# ~3-day drift over a 120-year cycle vs. industry-standard dasha tables.
YEAR_DAYS=365.25; MOVABLE_SIGNS={0,3,6,9}; FIXED_SIGNS={1,4,7,10}

DEB_SIGN_LORDS={"Sun":"Venus","Moon":"Mars","Mars":"Moon","Mercury":"Jupiter",
                "Jupiter":"Saturn","Venus":"Mercury","Saturn":"Mars"}

EXALT_LORD_IN_DEB_SIGN={"Sun":"Saturn","Moon":None,"Mars":"Jupiter","Mercury":"Venus",
                         "Jupiter":"Mars","Venus":"Mercury","Saturn":"Sun"}

PYTH_MAP={'a':1,'b':2,'c':3,'d':4,'e':5,'f':6,'g':7,'h':8,'i':9,'j':1,'k':2,'l':3,
          'm':4,'n':5,'o':6,'p':7,'q':8,'r':9,'s':1,'t':2,'u':3,'v':4,'w':5,'x':6,'y':7,'z':8}

CHALDEAN_MAP={'a':1,'b':2,'c':3,'d':4,'e':5,'f':8,'g':3,'h':5,'i':1,'j':1,'k':2,'l':3,
              'm':4,'n':5,'o':7,'p':8,'q':1,'r':2,'s':3,'t':4,'u':6,'v':6,'w':6,'x':5,'y':1,'z':7}

# FULL_TAROT_DECK moved to features/tarot/constants.py
COMPARISON_CRITERIA = ["Wealth Potential — Who builds the most wealth?",
    "Relationship Quality — Who has the best marriage/love life?",
    "Career Success — Who reaches the highest professional position?",
    "Karmic Intensity — Who faces the most karmic obstacles?",
    "Health & Longevity — Who has the strongest constitution?",
    "Happiness & Contentment — Who lives the most fulfilled life?",
    "Luck & Fortune — Who is the most naturally fortunate?",
    "Spiritual Depth — Who is the most spiritually evolved?",
    "Hidden Pitfalls — Who faces the most unexpected structural problems?"]

PERSONAL_YEAR_MEANINGS = {1:"New beginnings, independence, leadership.",
    2:"Partnership, patience, diplomacy.", 3:"Creativity, expression, social energy.",
    4:"Hard work, foundations, discipline.", 5:"Freedom, change, adventure.",
    6:"Home, family, responsibility.", 7:"Reflection, spirituality, inner growth.",
    8:"Power, ambition, material success.", 9:"Completion, release, transformation.",
    11:"Intuition, spiritual awakening, inspiration (Master Number).",
    22:"Mastery, large-scale building, legacy (Master Number).",
    33:"Compassion, teaching, healing (Master Number)."}

# CELTIC_CROSS_POSITIONS and TAROT_BASE moved to features/tarot/constants.py

NAV_PAGES = ["Dashboard", "Consultation Room", "The Oracle", "Mystic Tarot", "Horoscopes", "Numerology", "Palm Reading", "Kundli", "Saved Profiles"]

PLANET_RE = r"(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)"

NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}

NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

DUSTHANAS = {6, 8, 12}

KENDRAS = {1, 4, 7, 10}

TRIKONAS = {1, 5, 9}

SIGN_INDEX = {name: i for i, name in enumerate(SIGNS)}