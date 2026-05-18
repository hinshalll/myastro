"""
shared.astro/kundli_text.py — Interpretation library for premium kundli pages.

Pure content + rule-based composers. No Streamlit, no AI calls. The PDF
templates render the structured output produced here.

Public API:
    compute_interpretations(chart) -> dict — all interpretation payloads at once
    build_house_analyses(chart)   -> dict[1..12] → dict
    build_planet_analyses(chart)  -> dict[planet] → dict
    build_life_domains(chart)     -> dict[domain] → dict
    build_lal_kitab(chart)        -> dict[1..12] → dict
    build_year_predictions(chart, n_years=5) -> list[dict]
    build_auspicious_dates(chart) -> dict

Design: hand-written classical bases + programmatic composition. Avoids
the 21,000-word combinatorial blow-up of writing every planet-in-house
× sign permutation by hand, while still producing personalised,
classically-rooted text on every page.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# ══════════════════════════════════════════════════════════════════════════
# Static interpretation tables
# ══════════════════════════════════════════════════════════════════════════

HOUSE_MEANINGS: dict[int, dict] = {
    1:  {"name":"Lagna / Tanu Bhava", "theme":"Self, body, identity, vitality",
         "signifies":["physical body","appearance","temperament","constitution","head","brain","life force"],
         "body":"head, face, brain","dharma":"dharma (the why of life)"},
    2:  {"name":"Dhana Bhava", "theme":"Wealth, family, speech, food",
         "signifies":["accumulated wealth","family of origin","speech","food","face","right eye","values","sustenance"],
         "body":"face, right eye, throat","dharma":"artha (resources)"},
    3:  {"name":"Sahaja Bhava", "theme":"Siblings, courage, communication, short trips",
         "signifies":["younger siblings","courage","communication","writing","short journeys","arms","hands","initiative"],
         "body":"arms, shoulders, ears","dharma":"kama (effort, initiative)"},
    4:  {"name":"Sukha Bhava", "theme":"Mother, home, property, inner happiness",
         "signifies":["mother","home","real estate","vehicles","emotional security","heart","general happiness","schooling"],
         "body":"chest, heart","dharma":"moksha (emotional resolution)"},
    5:  {"name":"Putra Bhava", "theme":"Children, intelligence, romance, past-life merit",
         "signifies":["children","creative intelligence","romance","speculation","mantras","past-life merit (poorva-punya)","sports","entertainment"],
         "body":"upper abdomen, stomach","dharma":"dharma (creative purpose)"},
    6:  {"name":"Ari Bhava", "theme":"Enemies, debts, disease, daily work",
         "signifies":["enemies","debts","disease","daily service","maternal uncles","pets","obstacles overcome through effort"],
         "body":"lower abdomen, intestines","dharma":"artha (work, service)"},
    7:  {"name":"Yuvati / Kalatra Bhava", "theme":"Spouse, partnerships, public",
         "signifies":["spouse","business partnerships","trade","open enemies","the public","foreign travel","contracts"],
         "body":"pelvis, kidneys","dharma":"kama (union, exchange)"},
    8:  {"name":"Ayur Bhava", "theme":"Longevity, transformation, occult, inheritance",
         "signifies":["longevity","sudden events","occult","research","inheritance","in-laws","chronic conditions","transformation"],
         "body":"genitals, organs of reproduction","dharma":"moksha (deep transformation)"},
    9:  {"name":"Bhagya Bhava", "theme":"Fortune, dharma, father, higher learning",
         "signifies":["fortune","dharma","father","guru","long journeys","higher learning","pilgrimage","philosophy","fortune that arrives"],
         "body":"thighs, hips","dharma":"dharma (the law one lives by)"},
    10: {"name":"Karma Bhava", "theme":"Career, public role, authority",
         "signifies":["career","profession","public reputation","authority","government","status","life's work","actions in the world"],
         "body":"knees","dharma":"artha (life's work)"},
    11: {"name":"Labha Bhava", "theme":"Gains, friends, aspirations, elder siblings",
         "signifies":["income","gains","friends and network","elder siblings","aspirations fulfilled","large groups"],
         "body":"calves, ankles","dharma":"kama (desire fulfilled)"},
    12: {"name":"Vyaya Bhava", "theme":"Expenses, foreign lands, liberation, sleep",
         "signifies":["expenses","losses","foreign residence","liberation (moksha)","sleep","seclusion","spiritual retreat","hidden enemies","bed-pleasures"],
         "body":"feet","dharma":"moksha (release)"},
}


SIGN_QUALITIES: dict[str, dict] = {
    "Aries":      {"element":"Fire","modality":"Movable","ruler":"Mars",   "nature":"pioneering, assertive, action-first","body":"head"},
    "Taurus":     {"element":"Earth","modality":"Fixed","ruler":"Venus",   "nature":"steady, sensual, value-driven","body":"throat, neck"},
    "Gemini":     {"element":"Air","modality":"Dual","ruler":"Mercury",   "nature":"curious, communicative, dual-natured","body":"arms, lungs"},
    "Cancer":     {"element":"Water","modality":"Movable","ruler":"Moon", "nature":"nurturing, emotional, tide-like","body":"chest, stomach"},
    "Leo":        {"element":"Fire","modality":"Fixed","ruler":"Sun",     "nature":"regal, generous, attention-loving","body":"heart, spine"},
    "Virgo":      {"element":"Earth","modality":"Dual","ruler":"Mercury", "nature":"analytical, service-oriented, precise","body":"intestines"},
    "Libra":      {"element":"Air","modality":"Movable","ruler":"Venus",  "nature":"diplomatic, partnership-seeking, aesthetic","body":"kidneys, lower back"},
    "Scorpio":    {"element":"Water","modality":"Fixed","ruler":"Mars",   "nature":"intense, secretive, transformative","body":"genitals, excretory"},
    "Sagittarius":{"element":"Fire","modality":"Dual","ruler":"Jupiter",  "nature":"philosophical, expansive, truth-seeking","body":"thighs, hips"},
    "Capricorn":  {"element":"Earth","modality":"Movable","ruler":"Saturn","nature":"disciplined, ambitious, slow-build","body":"knees, joints"},
    "Aquarius":   {"element":"Air","modality":"Fixed","ruler":"Saturn",   "nature":"humanitarian, original, group-oriented","body":"calves, ankles"},
    "Pisces":     {"element":"Water","modality":"Dual","ruler":"Jupiter", "nature":"mystical, compassionate, boundary-dissolving","body":"feet, lymphatic"},
}


PLANET_KARAKAS: dict[str, dict] = {
    "Sun": {
        "natural":"soul, father, authority, vitality, ego, government, leadership, kingship",
        "body":"heart, bones, right eye (male) / left eye (female), vitality",
        "traits":"confidence, integrity, brilliance, dignity, willpower",
        "weak_traits":"arrogance, rigidity, autocratic behavior, ego-conflicts",
        "houses_signified":"1st (self), 9th (father), 10th (authority)",
        "color":"red/orange", "day":"Sunday", "metal":"gold/copper",
        "deity":"Surya, Shri Ram",
    },
    "Moon": {
        "natural":"mind, mother, emotions, public, fluids, fertility, nourishment",
        "body":"chest, stomach, lymphatic system, fluids",
        "traits":"sensitivity, intuition, receptivity, nurturing, imagination",
        "weak_traits":"moodiness, dependency, emotional volatility, escapism",
        "houses_signified":"4th (mother, home, emotional security)",
        "color":"white/silver", "day":"Monday", "metal":"silver",
        "deity":"Chandra, Parvati",
    },
    "Mars": {
        "natural":"courage, energy, brothers, property, weapons, surgery, ambition",
        "body":"muscles, blood, bone marrow, sinews",
        "traits":"valor, drive, decisiveness, protective instinct, technical skill",
        "weak_traits":"anger, impulsiveness, aggression, accidents, conflict",
        "houses_signified":"3rd (siblings, courage), 6th (enemies overcome)",
        "color":"red", "day":"Tuesday", "metal":"copper",
        "deity":"Hanuman, Subramanya, Mangal",
    },
    "Mercury": {
        "natural":"intellect, speech, business, communication, education, writing, commerce",
        "body":"nervous system, skin, speech apparatus",
        "traits":"intelligence, articulation, adaptability, wit, learning ability",
        "weak_traits":"superficiality, indecision, anxiety, deceit",
        "houses_signified":"4th (education foundation), 10th (career-via-skill)",
        "color":"green", "day":"Wednesday", "metal":"brass",
        "deity":"Vishnu (especially as Krishna for speech), Ganesha",
    },
    "Jupiter": {
        "natural":"wisdom, teacher, husband (in female charts), children, dharma, prosperity, devotion",
        "body":"liver, fat tissue, abdomen, hips",
        "traits":"generosity, optimism, faith, scholarship, righteousness",
        "weak_traits":"complacency, dogmatism, over-indulgence, false faith",
        "houses_signified":"2nd (wealth), 5th (children, intelligence), 9th (dharma), 11th (gains)",
        "color":"yellow", "day":"Thursday", "metal":"gold",
        "deity":"Brihaspati, Vishnu, Krishna",
    },
    "Venus": {
        "natural":"love, beauty, wife (in male charts), arts, luxury, vehicles, comforts",
        "body":"reproductive organs, kidneys, complexion, throat",
        "traits":"charm, refinement, sensuality, artistic talent, diplomacy",
        "weak_traits":"hedonism, vanity, attachment, indulgence",
        "houses_signified":"7th (spouse, partnerships)",
        "color":"white/pink", "day":"Friday", "metal":"silver/platinum",
        "deity":"Lakshmi, Saraswati",
    },
    "Saturn": {
        "natural":"discipline, longevity, service, restriction, the elderly, time, karma, suffering that teaches",
        "body":"nerves, joints, teeth, skeletal structure, chronic conditions",
        "traits":"patience, perseverance, responsibility, humility, depth",
        "weak_traits":"depression, fear, delay, hardship, isolation",
        "houses_signified":"6th (service), 8th (longevity), 12th (liberation through limitation)",
        "color":"dark blue/black", "day":"Saturday", "metal":"iron",
        "deity":"Shani, Hanuman, Bhairava",
    },
    "Rahu": {
        "natural":"obsession, ambition, foreign things, technology, manipulation, illusion, sudden gains",
        "body":"nervous disorders, mysterious illness, skin",
        "traits":"innovation, boundary-breaking, hunger for experience, magnetism",
        "weak_traits":"deception, addiction, foreign troubles, paranoia, illusion",
        "houses_signified":"none classically; modern: 11th-house energy",
        "color":"smoky grey", "day":"Saturday (or eclipse days)",
        "metal":"lead/silver", "deity":"Durga, Kali, Bhairava",
    },
    "Ketu": {
        "natural":"detachment, past-life knowledge, liberation, occult, isolation, intuition, sudden losses",
        "body":"injuries, unexplained symptoms, lower spine",
        "traits":"perception, intuition, spiritual insight, mathematical genius, healing ability",
        "weak_traits":"confusion, escapism, isolation, accidents, sudden endings",
        "houses_signified":"none classically; modern: 12th-house liberation energy",
        "color":"multi-colour/smoky","day":"Tuesday (or eclipse days)",
        "metal":"silver","deity":"Ganesha, Subramanya",
    },
}


# Per-(planet, house) interpretive notes — concise classical statements. The
# composer below stitches these into full paragraphs with sign + dignity + lord
# context. Where a combination isn't listed, the composer falls back to a
# template using PLANET_KARAKAS + HOUSE_MEANINGS.

PLANET_IN_HOUSE_NOTE: dict[tuple[str, int], str] = {
    # Sun
    ("Sun",1):  "Strong sense of self and natural authority; commanding presence; tendency toward independence and a healthy ego that must be tempered with humility.",
    ("Sun",2):  "Wealth through one's own efforts and government/authority connections; speech carries weight; family pride and possibly some friction with father about money.",
    ("Sun",3):  "Courage to assert oneself; competitive drive; some friction with siblings, especially younger; talent in writing or communicating with authority.",
    ("Sun",4):  "Heart of a leader at home; status-conscious about property and vehicles; relationship with mother may have authority dynamics; chest/heart needs care.",
    ("Sun",5):  "Brilliant creative intelligence; potential for famous children; love-affairs may carry ego dynamics; talent for teaching, performance, or strategy.",
    ("Sun",6):  "Victory over enemies and competitors; success in service, government work, healthcare, or law enforcement; strong digestion but watch heart and eyes.",
    ("Sun",7):  "Spouse is dignified, authoritative, perhaps from a powerful family; partnerships need careful ego management; potential for public-facing partnerships.",
    ("Sun",8):  "Hidden authority; success through research, occult, or transformation; potential health issues with vitality/heart; longevity may need attention.",
    ("Sun",9):  "Strong father-figure influence; natural alignment with dharma; success through higher education, law, religion, or teaching; favourable for long-distance work.",
    ("Sun",10): "Excellent — career success, public recognition, government connections, leadership roles; natural visibility and authority in one's profession.",
    ("Sun",11): "Gains through powerful friends and authority figures; elder siblings may be influential; income through leadership positions.",
    ("Sun",12): "Spiritual seeking through solitude; foreign career possible; some father-related sorrow or distance; conserve vitality through rest.",
    # Moon
    ("Moon",1):  "Sensitive, intuitive, emotionally expressive personality; well-being mirrors emotional state; nurturing temperament; appearance often soft and approachable.",
    ("Moon",2):  "Sweet speech; comfort-seeking around food and family; potential for wealth that fluctuates with emotional cycles; close to mother's family.",
    ("Moon",3):  "Emotional bond with siblings; communication carries feeling; many short journeys for emotional reasons; receptive learner.",
    ("Moon",4):  "Excellent — strong bond with mother, deep love of home, emotional security in family life; capacity for inner happiness when home is stable.",
    ("Moon",5):  "Imaginative, creative, romantic; potential for daughters or sensitive children; speculative tendencies need restraint; artistic talents.",
    ("Moon",6):  "Emotional vulnerability around debts, daily work, or health; service-oriented; potential for digestive sensitivities; pets bring comfort.",
    ("Moon",7):  "Spouse is nurturing and emotionally significant; partnerships matter deeply; public sensitivity; potential business with the public.",
    ("Moon",8):  "Sensitive to deep undercurrents; psychic ability; emotional intensity around inheritance, in-laws, or transformations; careful with chronic conditions.",
    ("Moon",9):  "Devotional faith; mother often deeply religious or wise; emotional connection to dharma, teachers, or distant places.",
    ("Moon",10): "Public-facing career; emotional connection to one's work; possibly career in caregiving, food, hospitality, mother-related fields; fluctuating reputation.",
    ("Moon",11): "Emotional satisfaction through friends and groups; many female friends; income through public-facing or nurturing work; fulfilled aspirations.",
    ("Moon",12): "Deep imagination, mysticism, dream life; potential foreign residence; sleep needs care; spiritual sensitivity; emotional retreat is healing.",
    # Mars
    ("Mars",1):  "Bold, energetic, courageous personality; potential Mangal Dosha consideration; strong physical drive; tendency to lead by action; injuries possible from haste.",
    ("Mars",2):  "Sharp speech that can cut; wealth through effort and competition; family disputes possible; watch dental/oral health.",
    ("Mars",3):  "Excellent — exceptional courage, drive, and capability; younger siblings may be strong personalities; skills in writing, technical work, sports.",
    ("Mars",4):  "Potential Mangal Dosha; some friction in home or with mother; property gains through effort; chest/cardiac vigour with watchpoints.",
    ("Mars",5):  "Competitive intelligence; talent in sports, debate, strategy; impulse in romance; potential for delays/loss with children that resolve through effort.",
    ("Mars",6):  "Powerful destroyer of enemies and debts; excellence in service, surgery, defense, sports; high physical vitality.",
    ("Mars",7):  "Classic Mangal Dosha placement — partnership tension; spouse may be strong-willed; potential delays in marriage; partner-business needs maturity.",
    ("Mars",8):  "Mangal Dosha placement — sudden events possible; interest in occult, surgery, research; longevity merits careful attention; in-laws may be contentious.",
    ("Mars",9):  "Action-oriented faith; potentially contentious relationship with father or guru; success through bold long-distance ventures or martial paths.",
    ("Mars",10): "Excellent for career requiring drive — engineering, defense, sports, surgery, real estate, leadership; high professional ambition.",
    ("Mars",11): "Gains through bold action; competitive friend group; elder siblings may be strong; income through technical, engineering, or sports work.",
    ("Mars",12): "Mangal Dosha placement — covert struggles; hidden expenses through aggression or disputes; potential foreign-military or covert work; legal expenses possible.",
    # Mercury
    ("Mercury",1):  "Articulate, intelligent, youthful appearance; analytical mind; communication is a core identity tool; business acumen.",
    ("Mercury",2):  "Excellent — talent for finance, business, languages; sweet articulate speech; wealth through commerce, writing, or trade.",
    ("Mercury",3):  "Excellent — courage in communication; talent in writing, journalism, technical fields; intellectual relationship with siblings.",
    ("Mercury",4):  "Education-rich home; mother may be intellectual; comfort from books, learning, communication tools; talent for real estate negotiation.",
    ("Mercury",5):  "Brilliant intellect; talent in mathematics, mantras, writing; children may be intellectual; speculative skill (use cautiously).",
    ("Mercury",6):  "Skill in dispute resolution, law, accounting, healthcare administration; debts handled cleverly; service through intellect.",
    ("Mercury",7):  "Spouse intellectual and communicative; business partnerships favoured; trading, contracts, mediation as career.",
    ("Mercury",8):  "Research/investigative intellect; potential interest in occult, psychology, deep study; gains through partner's wealth possible.",
    ("Mercury",9):  "Philosophical intelligence; talent in teaching, publishing, law; father may be a scholar or businessperson.",
    ("Mercury",10): "Career in communication, business, IT, education, accounting, journalism, or any field requiring intellect; reputation through articulation.",
    ("Mercury",11): "Income through networks, communication, business deals; intellectual friend circle; gains from writing, technology, brokerage.",
    ("Mercury",12): "Foreign business interests; intellectual seclusion (research, study, monastic learning); sleep affected by mental activity.",
    # Jupiter
    ("Jupiter",1):  "Wise, generous, protected presence; natural teacher; some weight tendency; favoured in life through good karma and faith.",
    ("Jupiter",2):  "Excellent — wealth, family good fortune, sweet wise speech; tradition-honoring; gains through education or counsel.",
    ("Jupiter",3):  "Younger siblings prosperous and supportive; success through publishing, teaching, writing; courage rooted in faith.",
    ("Jupiter",4):  "Excellent — happiness, comfortable home, loving mother, property gains; classical Hamsa Yoga potential (if dignified).",
    ("Jupiter",5):  "Excellent — intelligent and virtuous children, creative wisdom, success in education, mantras, devotion; teaching talent.",
    ("Jupiter",6):  "Wisdom in dispute resolution; service to teachers/elders; debts cleared through faith; potential for unhealthy weight gain if undisciplined.",
    ("Jupiter",7):  "Excellent (esp. for women — husband-significator in 7th): wise, ethical spouse; business partnerships with integrity; legal/teaching career.",
    ("Jupiter",8):  "Long life; protection through hidden support; success in research/occult/teaching of esoteric subjects; in-laws may be supportive.",
    ("Jupiter",9):  "Excellent — highest placement: profound dharma, wise father/guru, long-distance success, philosophical depth, fortune itself.",
    ("Jupiter",10): "Excellent — career in teaching, law, finance, religion, counseling; high public regard; classical Hamsa Yoga if in own sign/exalted in kendra.",
    ("Jupiter",11): "Excellent — large gains, prosperous elder siblings, wise friend circle, fulfilled aspirations through wisdom.",
    ("Jupiter",12): "Expenses go toward dharma, teaching, charity; spiritual liberation through wisdom; foreign residence for higher learning possible.",
    # Venus
    ("Venus",1):  "Charming, attractive, refined presence; love of beauty and harmony; artistic sensibility; gentle persuasive personality.",
    ("Venus",2):  "Sweet speech, fine taste in food and luxury; wealth through arts/beauty/luxury; family of refined sensibility.",
    ("Venus",3):  "Artistic siblings; creative writing; short pleasure trips; communication that charms; talent in design or musical arts.",
    ("Venus",4):  "Beautiful home, vehicles, comforts; loving mother; emotional and aesthetic security; property gains through Venus-related work.",
    ("Venus",5):  "Romantic, artistic, possibly multiple love-interests; talent in performing arts, music, dance; children bring beauty.",
    ("Venus",6):  "Combust risk (when close to Sun) — Venus in 6th can struggle; service in beauty/luxury/fashion industry; relationship-via-work patterns; possible diabetes watchpoint.",
    ("Venus",7):  "Excellent (esp. for men): beautiful refined spouse; harmonious partnerships; business in arts, luxury, fashion, beauty.",
    ("Venus",8):  "Secret romantic life; potential inheritance through spouse; longevity reasonable but watch reproductive/urinary health; interest in tantric or mystic arts.",
    ("Venus",9):  "Devotional love; wise teacher in matters of love; foreign-spouse possible; success in arts, fashion, hospitality long-distance.",
    ("Venus",10): "Excellent — career in arts, beauty, fashion, luxury, hospitality, design; public charm; classical Malavya Yoga potential.",
    ("Venus",11): "Excellent — gains through arts, luxury, beautiful network; many friends including the opposite sex; aspirations through partnerships realized.",
    ("Venus",12): "Pleasures of bed, foreign romance, expenses on luxury; spiritual transcendence through love; classical 'paradise placement' (12th = bhoga sthana for Venus).",
    # Saturn
    ("Saturn",1):  "Serious, mature, disciplined presence; lean physique often; slow but steady life trajectory; old soul; some early-life challenges that build character.",
    ("Saturn",2):  "Wealth built slowly through discipline; restrained speech; some family responsibility/burden; saving rather than spending nature.",
    ("Saturn",3):  "Excellent — disciplined effort yields great results; older siblings or sibling-distance; success through patient communication, writing, technical skill.",
    ("Saturn",4):  "Heavy emotional responsibilities at home; mother may be ill or distant; property in later life; develop emotional fortitude.",
    ("Saturn",5):  "Delays in children; serious creative work; intelligence applied to long-term projects; speculation avoided; spiritual practice rewards patience.",
    ("Saturn",6):  "Excellent — masterful at overcoming obstacles, debt, enemies; service-oriented; chronic-disease management requires discipline.",
    ("Saturn",7):  "Late or serious marriage; mature, possibly older spouse; partnerships with long-term commitment; relationship-as-discipline.",
    ("Saturn",8):  "Long life; deep transformation through hardship; interest in karma, longevity research; in-laws may be a source of difficulty.",
    ("Saturn",9):  "Father may be distant or serious; traditional dharma; long-distance work after delays; teacher of patience.",
    ("Saturn",10): "Excellent — slow but immense career growth; service-leadership; classical Shasha Yoga potential; mature authority earned over time.",
    ("Saturn",11): "Excellent — gains arrive slowly but reliably; older friends, business networks; income through service-oriented or service-providing structures.",
    ("Saturn",12): "Foreign residence for work; expenses on duty and service; ashram-life or monastic tendencies; sleep disrupted; liberation through detachment.",
    # Rahu
    ("Rahu",1):  "Magnetic unconventional presence; foreign element in self-expression; sudden identity shifts; powerful ambition needing direction.",
    ("Rahu",2):  "Speech that influences masses; foreign wealth or technology-based wealth; family secrets; speak with care.",
    ("Rahu",3):  "Courage from unusual sources; foreign or unconventional siblings/communication; success in mass media, marketing, technology.",
    ("Rahu",4):  "Foreign residence or property; mother-related complexity; restless heart; need for emotional grounding practices.",
    ("Rahu",5):  "Unusual intelligence; speculative tendencies (use caution); children may be unconventional or come unexpectedly; magnetic in romance.",
    ("Rahu",6):  "Excellent — Rahu defeats enemies decisively; success in unusual service fields, foreign clients, technology; chronic conditions need watch.",
    ("Rahu",7):  "Unconventional or foreign spouse; partnership intensity; potential deceit in dealings; magnetic to public.",
    ("Rahu",8):  "Sudden transformative events; occult/research talent; in-law complexity; longevity unpredictable — health practices matter.",
    ("Rahu",9):  "Unusual dharma path; foreign-based fortune; father may have unusual story; ambivalence about traditional faith.",
    ("Rahu",10): "Excellent — exceptional career rise, foreign work, fame in unusual fields; technology, media, politics; reputation can swing.",
    ("Rahu",11): "Excellent — massive gains, large networks, foreign income, unusual friend circle; ambition fulfilled through unconventional means.",
    ("Rahu",12): "Foreign residence; hidden expenses; isolation periods; spiritual breakthroughs through illusion-piercing; addictions to avoid.",
    # Ketu
    ("Ketu",1):  "Detached personality; spiritual undertone; some confusion about identity in youth; mystical leanings.",
    ("Ketu",2):  "Few words but meaningful; some family detachment; wealth held lightly; possible past-life family karma.",
    ("Ketu",3):  "Mystical talent in communication; younger sibling distance or one significant sibling; intuitive courage.",
    ("Ketu",4):  "Detachment from home/mother (not necessarily painful — may be philosophical); chest-area sensitivity; inward emotional life.",
    ("Ketu",5):  "Talent in mantras/mysticism; children may be spiritual or delayed; past-life merit emerges as intuition; speculation avoided.",
    ("Ketu",6):  "Excellent — enemies disappear inexplicably; service through spiritual or healing work; unusual diagnostic ability; chronic conditions need attention.",
    ("Ketu",7):  "Some detachment in partnerships; spouse may be spiritual; potential late or non-traditional marriage; mystical partnership patterns.",
    ("Ketu",8):  "Excellent — deep occult ability; sudden transformations; long life through detachment; research/intuitive medicine talent.",
    ("Ketu",9):  "Non-traditional dharma; father-distance possibly; spiritual seeking that breaks orthodoxy; foreign spiritual influences.",
    ("Ketu",10): "Career in research, healing, technology, spirituality; reputation that comes and goes; non-traditional path.",
    ("Ketu",11): "Gains arrive then dissipate; teach detachment about income; spiritual friend circle; aspirations dissolve and re-form.",
    ("Ketu",12): "Excellent — natural placement for moksha; deep meditation ability; foreign residence; expenses on spiritual pursuits.",
}


# Lal Kitab summary per house (concise practical North-Indian alternate-system text)

LAL_KITAB_HOUSE: dict[int, str] = {
    1:  "The 1st house represents the soul's vessel — your body and personality. "
        "In Lal Kitab, planets here directly stamp your destiny on your face and conduct. "
        "Daily practice: speak truthfully and bathe at sunrise. A planet here that troubles "
        "you is best appeased by simple physical disciplines (early rising, exercise).",
    2:  "The 2nd house is the family's treasury and the speaker's tongue. "
        "Lal Kitab calls this 'the house of stored wealth' — what your forefathers earned "
        "and what you can preserve. Daily practice: honour parents and elders, never speak "
        "harshly about money, keep silver or jewellery in the home.",
    3:  "The 3rd is the courage well and the brotherhood house. Lal Kitab considers younger "
        "brothers and sisters here as direct extensions of your own life-force. "
        "Daily practice: maintain harmony with siblings, plant a tree, donate to younger "
        "members of the family — they amplify (or block) your effort.",
    4:  "The 4th is your mother, your home, your heart's foundation. Lal Kitab is famously "
        "strict here: a troubled 4th puts a hidden weight on the chest. "
        "Daily practice: serve your mother with food and care, keep silver at home, do not "
        "speak ill of mother-figures, install a kitchen-flame ritual.",
    5:  "The 5th carries children, your creative intelligence, and the merit you brought from "
        "your last birth. Lal Kitab calls this 'the temple of past punya'. "
        "Daily practice: chant any mantra of your istha-devata 108 times daily; feed monkeys "
        "or cows; respect children and never break a promise to one.",
    6:  "The 6th is enemies, debts, daily work, and the karmic recycler. Lal Kitab's clearest "
        "house — directly remedied by service. "
        "Daily practice: feed black dogs or crows; never refuse food to a hungry person; "
        "clear small debts before sundown; serve your maternal uncle.",
    7:  "The 7th is the spouse, partnerships, and what the public sees. Lal Kitab calls a "
        "good 7th 'the door of fortune'. "
        "Daily practice: respect spouse and partners absolutely; never lie in business; "
        "donate clothes to a widow or orphan annually.",
    8:  "The 8th is the karma you cannot escape — longevity, inheritance, hidden transformation. "
        "Lal Kitab takes this house most seriously; it's where ancestors call. "
        "Daily practice: avoid speaking of others' death; donate to a Shiva temple; "
        "keep one fast each month on Trayodashi (13th lunar day).",
    9:  "The 9th is your father, your dharma, your highest fortune. Lal Kitab places father's "
        "blessing as the single most-powerful living remedy. "
        "Daily practice: serve father personally even if difficult; touch his feet; never "
        "lie about religious matters; visit a temple weekly.",
    10: "The 10th is your karma in the world — career, fame, what you build. "
        "Daily practice: keep your workplace clean; donate the first earnings of any new "
        "venture; never undermine a superior; serve the public through your work.",
    11: "The 11th is gain, fulfilled desire, friends, and elder siblings. Lal Kitab calls this "
        "'Indra's house' — the abode of comfort received. "
        "Daily practice: keep friends and elder siblings happy; donate yellow items on "
        "Thursdays; never accept gains that cause another harm.",
    12: "The 12th is expense, exile, sleep, and ultimate liberation. Lal Kitab is gentle here: "
        "the 12th is for what you owe back to the cosmos. "
        "Daily practice: give the last portion of your meal in charity; sleep with head "
        "to east or south; meditate or pray before sleep; do not over-attend to enemies.",
}


# Domains for the "Life Domains" section — keyed to houses, planets, and significators

LIFE_DOMAIN_KEYS: dict[str, dict] = {
    "Career":    {"houses":[10,6,2], "planets":["Sun","Saturn","Mercury","Mars"],
                  "karaka":"Saturn (action) + Sun (authority) + Mercury (skill)"},
    "Wealth":    {"houses":[2,11,5,9], "planets":["Jupiter","Venus","Mercury"],
                  "karaka":"Jupiter (accumulation) + Venus (luxury) + Mercury (commerce)"},
    "Health":    {"houses":[1,6,8], "planets":["Sun","Moon","Mars","Saturn"],
                  "karaka":"Sun (vitality) + Moon (constitution) + 6th lord (acute) + 8th lord (chronic)"},
    "Marriage":  {"houses":[7,2,4,5,11], "planets":["Venus","Jupiter","Moon"],
                  "karaka":"Venus (wife/love), Jupiter (husband/wisdom in match), Moon (emotional bond)"},
    "Children":  {"houses":[5,9,11], "planets":["Jupiter","Sun","Moon"],
                  "karaka":"Jupiter (children-significator) + 5th house & lord"},
    "Education": {"houses":[2,4,5,9], "planets":["Mercury","Jupiter","Sun","Venus"],
                  "karaka":"Mercury (intellect) + Jupiter (wisdom) + 4th (foundation) + 5th (higher mind)"},
    "Travel":    {"houses":[3,9,12], "planets":["Mercury","Jupiter","Rahu","Moon"],
                  "karaka":"3rd (short) + 9th (long-distance) + 12th (foreign)"},
    "Spirituality": {"houses":[5,8,9,12], "planets":["Jupiter","Ketu","Saturn"],
                  "karaka":"Jupiter (devotion) + Ketu (liberation) + 9th (dharma) + 12th (moksha)"},
}


# ══════════════════════════════════════════════════════════════════════════
# Composer helpers
# ══════════════════════════════════════════════════════════════════════════

def _sign_lord_of(sign_idx: int) -> str:
    from shared.astro.constants import SIGN_LORDS_MAP
    return SIGN_LORDS_MAP[sign_idx]


def _house_strength(chart, h: int) -> tuple[str, str]:
    """Derive a coarse strength label for a house using SAV + occupants."""
    sav = (chart.ashtakavarga or {}).get("sav_by_house", [])
    bindus = sav[h-1] if sav and h-1 < len(sav) else 28
    label = ("Strong" if bindus >= 32 else
             "Average" if bindus >= 25 else "Weak")
    # Occupant nudge
    occ = chart.houses[h].occupants if h in chart.houses else []
    benefics = {"Jupiter","Venus","Mercury","Moon"}
    malefics = {"Sun","Mars","Saturn","Rahu","Ketu"}
    ben_count = sum(1 for p in occ if p in benefics)
    mal_count = sum(1 for p in occ if p in malefics)
    note = ""
    if ben_count > mal_count:
        note = "supported by benefic presence"
    elif mal_count > ben_count and h not in (3,6,10,11):
        note = "with malefic pressure to overcome"
    elif mal_count > 0 and h in (3,6,10,11):
        note = "with malefic energy that serves these upachaya houses"
    elif not occ:
        note = "without direct occupants — read via the lord's placement"
    return label, note


def _planet_in_house_text(planet: str, house: int, sign: str,
                           dignity: str | None) -> str:
    """Compose the planet-in-house paragraph using the brief note + sign + dignity."""
    base = PLANET_IN_HOUSE_NOTE.get((planet, house))
    sign_q = SIGN_QUALITIES.get(sign, {})
    sign_nature = sign_q.get("nature", "")
    if base is None:
        base = (f"{planet} in the {_ordinal(house)} house brings its significations "
                f"({PLANET_KARAKAS.get(planet, {}).get('natural', '—')}) into the "
                f"affairs of {HOUSE_MEANINGS[house]['theme'].lower()}.")
    sign_note = (f" The sign {sign} ({sign_nature}) colours how this energy expresses.")
    dignity_note = ""
    if dignity == "Exalted":
        dignity_note = f" Exalted dignity strongly amplifies favourable results."
    elif dignity == "Debilitated":
        dignity_note = (f" Debilitated dignity weakens the planet's standard "
                        f"output — look for cancellations (Neecha Bhanga) to "
                        f"reverse the trend.")
    elif dignity == "Own Sign":
        dignity_note = f" Own-sign placement gives stable, dependable output."
    elif dignity == "Mooltrikona":
        dignity_note = f" Mooltrikona placement gives very favourable directorial control."
    return base + sign_note + dignity_note


def _ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1:"st",2:"nd",3:"rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


# ══════════════════════════════════════════════════════════════════════════
# Builders — one per major section
# ══════════════════════════════════════════════════════════════════════════

def build_house_analyses(chart) -> dict[int, dict]:
    """One analysis per house (1..12). Returns dict keyed by house number."""
    out = {}
    for h in range(1, 13):
        meta = HOUSE_MEANINGS[h]
        house_info = chart.houses[h]
        lord_name = house_info.sign_lord
        lord_pp = chart.planets.get(lord_name)
        sign_q = SIGN_QUALITIES.get(house_info.sign, {})
        strength_label, strength_note = _house_strength(chart, h)

        # Lord placement summary
        if lord_pp:
            lord_dig = f", {lord_pp.dignity.lower()}" if lord_pp.dignity else ""
            lord_text = (f"{lord_name} (the lord of this house) sits in "
                         f"H{lord_pp.house} in {lord_pp.sign}{lord_dig}.")
            # Functional context
            lord_house_meta = HOUSE_MEANINGS.get(lord_pp.house, {})
            lord_text += (f" This routes the {meta['theme'].lower()} matters of this "
                          f"house through the affairs of the "
                          f"{lord_house_meta.get('name','house')} — "
                          f"{lord_house_meta.get('theme','').lower()}.")
        else:
            lord_text = f"The lord of this house is {lord_name}."

        # Occupants summary
        occ = house_info.occupants
        if occ:
            occ_lines = []
            for p in occ:
                pp = chart.planets[p]
                occ_lines.append(
                    _planet_in_house_text(p, h, pp.sign, pp.dignity)
                )
            occ_text = " ".join(occ_lines)
        else:
            occ_text = (f"No planet directly occupies this house. The house's "
                        f"affairs are read primarily through its lord {lord_name} "
                        f"and through aspects from elsewhere in the chart.")

        # Aspecting planets (loose — uses Rasi-drishti / Jaimini if available;
        # fallback: list planets whose drishti house equals h via classical
        # Vedic rules: every planet aspects its 7th; Mars also 4 & 8;
        # Jupiter also 5 & 9; Saturn also 3 & 10).
        aspecting = []
        for p, pp in chart.planets.items():
            ph = pp.house
            aspects = {((ph + 6) % 12) or 12}
            if p == "Mars":     aspects |= {((ph + 3) % 12) or 12, ((ph + 7) % 12) or 12}
            if p == "Jupiter":  aspects |= {((ph + 4) % 12) or 12, ((ph + 8) % 12) or 12}
            if p == "Saturn":   aspects |= {((ph + 2) % 12) or 12, ((ph + 9) % 12) or 12}
            if h in aspects and p not in occ:
                aspecting.append(p)

        out[h] = {
            "house": h,
            "name": meta["name"],
            "theme": meta["theme"],
            "signifies": meta["signifies"],
            "body": meta["body"],
            "sign": house_info.sign,
            "sign_lord": lord_name,
            "sign_nature": sign_q.get("nature", "—"),
            "sign_element": sign_q.get("element", "—"),
            "sign_modality": sign_q.get("modality", "—"),
            "occupants": occ,
            "aspecting": aspecting,
            "strength": strength_label,
            "strength_note": strength_note,
            "lord_text": lord_text,
            "occupants_text": occ_text,
        }
    return out


def build_planet_analyses(chart) -> dict[str, dict]:
    """One analysis per planet (Sun..Ketu)."""
    out = {}
    for p in ("Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"):
        pp = chart.planets[p]
        karaka = PLANET_KARAKAS[p]
        sign_q = SIGN_QUALITIES.get(pp.sign, {})
        house_meta = HOUSE_MEANINGS[pp.house]
        in_house = _planet_in_house_text(p, pp.house, pp.sign, pp.dignity)

        # Shadbala flag
        sb_flag = "—"
        if chart.shadbala:
            if p in chart.shadbala.get("strong", []):  sb_flag = "Strong"
            elif p in chart.shadbala.get("weak", []):  sb_flag = "Weak"
            else: sb_flag = "Neutral"

        out[p] = {
            "planet": p,
            "sign": pp.sign,
            "house": pp.house,
            "house_meta": house_meta,
            "degree": pp.longitude_dms,
            "nakshatra": pp.nakshatra,
            "nakshatra_lord": pp.nakshatra_lord,
            "pada": pp.pada,
            "dignity": pp.dignity or "Neutral",
            "is_retrograde": pp.is_retrograde,
            "is_combust": pp.is_combust,
            "natural_significations": karaka["natural"],
            "body_significations": karaka["body"],
            "positive_traits": karaka["traits"],
            "challenge_traits": karaka["weak_traits"],
            "deity": karaka["deity"],
            "remedy_color": karaka["color"],
            "remedy_day": karaka["day"],
            "remedy_metal": karaka["metal"],
            "sign_nature": sign_q.get("nature", ""),
            "sign_element": sign_q.get("element", ""),
            "in_house_text": in_house,
            "shadbala_status": sb_flag,
        }
    return out


def build_life_domains(chart) -> dict[str, dict]:
    """Per-domain analysis pulling from relevant houses + significators."""
    out = {}
    for domain, keys in LIFE_DOMAIN_KEYS.items():
        houses = keys["houses"]
        plist  = keys["planets"]
        # Pull strength of each relevant house
        h_data = []
        for h in houses:
            strength_label, strength_note = _house_strength(chart, h)
            hi = chart.houses[h]
            h_data.append({
                "house": h, "sign": hi.sign, "sign_lord": hi.sign_lord,
                "occupants": hi.occupants, "strength": strength_label,
                "note": strength_note,
            })
        # Pull condition of each relevant planet
        p_data = []
        for p in plist:
            if p not in chart.planets: continue
            pp = chart.planets[p]
            p_data.append({
                "planet": p, "sign": pp.sign, "house": pp.house,
                "dignity": pp.dignity or "Neutral",
                "is_retrograde": pp.is_retrograde, "is_combust": pp.is_combust,
            })

        # Overall coarse verdict
        bad_signals = sum(
            1 for h in houses
            if any(chart.planets[p].house == h
                   for p in ("Saturn","Rahu","Ketu","Mars")
                   if p in chart.planets)
        )
        good_signals = sum(
            1 for h in houses
            if any(chart.planets[p].house == h
                   for p in ("Jupiter","Venus","Moon","Mercury")
                   if p in chart.planets)
        )
        verdict = ("Generally Favourable" if good_signals >= bad_signals + 1 else
                   "Mixed — Requires Effort" if good_signals == bad_signals else
                   "Challenged — Conscious Work Required")

        out[domain] = {
            "domain": domain,
            "karaka": keys["karaka"],
            "relevant_houses": h_data,
            "relevant_planets": p_data,
            "verdict": verdict,
        }
    return out


def build_lal_kitab(chart) -> dict[int, dict]:
    """Lal Kitab house-by-house — text + per-house occupant note."""
    out = {}
    for h in range(1, 13):
        text = LAL_KITAB_HOUSE[h]
        occ = chart.houses[h].occupants
        if occ:
            extra = (f"Planets here in your chart: {', '.join(occ)}. "
                     f"The above daily practice particularly addresses the karma of "
                     f"these planets in your life.")
        else:
            extra = (f"No planet here directly — observe the daily practice as "
                     f"general support; weight increases if your dasha runs the "
                     f"lord of this house ({chart.houses[h].sign_lord}).")
        out[h] = {"house": h, "text": text, "extra": extra,
                  "lord": chart.houses[h].sign_lord,
                  "occupants": occ}
    return out


def build_year_predictions(chart, n_years: int = 5) -> list[dict]:
    """Per-year prediction for the next n_years, driven by Vimshottari MD/AD."""
    out: list[dict] = []
    vim = (chart.dashas or {}).get("Vimshottari")
    if not vim or not vim.periods:
        return out
    tz = ZoneInfo(chart.birth_data.tz)
    now = datetime.now(tz)

    for yr_offset in range(n_years):
        year_start = datetime(now.year + yr_offset, now.month, now.day, tzinfo=tz)
        year_end = datetime(now.year + yr_offset + 1, now.month, now.day, tzinfo=tz)
        # Active MD/AD on Jan 1 of that year (or year_start)
        md = next((md for md in vim.periods if md.start <= year_start <= md.end), None)
        ad = None
        if md:
            ad = next((ad for ad in md.children if ad.start <= year_start <= ad.end), None)
        if not md:
            continue
        # Theme from MD lord's karakas + AD lord's karakas
        md_k = PLANET_KARAKAS.get(md.lord, {})
        ad_k = PLANET_KARAKAS.get(ad.lord, {}) if ad else {}
        theme_lines = [
            f"**Mahadasha lord {md.lord}** — primary backdrop: {md_k.get('natural','—')}.",
        ]
        if ad:
            theme_lines.append(
                f"**Antardasha lord {ad.lord}** — year's foreground: {ad_k.get('natural','—')}."
            )
        # Coarse outlook: combine dasha lords' chart placements
        outlook_parts = []
        for plord, label in [(md.lord, "MD"), (ad.lord if ad else None, "AD")]:
            if not plord or plord not in chart.planets: continue
            pp = chart.planets[plord]
            outlook_parts.append(
                f"{label}-lord {plord} sits in your H{pp.house} ({pp.sign}, "
                f"{pp.dignity or 'neutral'}), routing this period's results through "
                f"{HOUSE_MEANINGS[pp.house]['theme'].lower()}."
            )

        out.append({
            "year": year_start.year,
            "period_label": f"{year_start.strftime('%b %Y')} → {year_end.strftime('%b %Y')}",
            "md_lord": md.lord,
            "ad_lord": ad.lord if ad else None,
            "theme_lines": theme_lines,
            "outlook": " ".join(outlook_parts),
            "focus_traits": md_k.get("traits",""),
            "challenge_traits": md_k.get("weak_traits",""),
        })
    return out


def build_auspicious_dates(chart, months: int = 12) -> dict:
    """Compact 12-month calendar of personally-favourable & cautionary days.

    Heuristic (fast, deterministic):
      - Favourable days: Vimshottari MD-lord's weekday + AD-lord's weekday
      - Cautionary days: Rahu's weekday (Saturday) + 8th-lord's weekday
      - Plus: monthly nakshatra return (Janma Nakshatra day) for big decisions
    """
    PLANET_DAY = {"Sun":"Sunday","Moon":"Monday","Mars":"Tuesday","Mercury":"Wednesday",
                  "Jupiter":"Thursday","Venus":"Friday","Saturn":"Saturday",
                  "Rahu":"Saturday","Ketu":"Tuesday"}
    tz = ZoneInfo(chart.birth_data.tz)
    now = datetime.now(tz)
    vim = (chart.dashas or {}).get("Vimshottari")
    md_lord = ad_lord = None
    if vim and vim.periods:
        md = next((md for md in vim.periods if md.start <= now <= md.end), None)
        if md:
            md_lord = md.lord
            ad = next((ad for ad in md.children if ad.start <= now <= ad.end), None)
            if ad: ad_lord = ad.lord
    h8_sign = (chart.lagna.sign_index + 7) % 12
    from shared.astro.constants import SIGN_LORDS_MAP
    h8_lord = SIGN_LORDS_MAP[h8_sign]

    favourable_days = sorted({PLANET_DAY.get(p, "") for p in (md_lord, ad_lord) if p})
    cautionary_days = sorted({PLANET_DAY.get(p, "") for p in (h8_lord, "Rahu") if p})

    janma_nak = chart.planets["Moon"].nakshatra

    # Per-month notes (next 12)
    monthly = []
    for m_off in range(months):
        dt = datetime(now.year + (now.month - 1 + m_off)//12,
                      ((now.month - 1 + m_off) % 12) + 1, 1, tzinfo=tz)
        # Most-favourable festival/anchor of the month (very coarse — first
        # weekday match within the month)
        monthly.append({
            "month": dt.strftime("%B %Y"),
            "favourable_weekdays": favourable_days,
            "cautionary_weekdays": cautionary_days,
            "janma_nakshatra_day": (f"On the day when transiting Moon is in "
                                    f"{janma_nak} (~once per month) — best for "
                                    f"major personal decisions, mantra initiation, "
                                    f"or starting projects."),
        })

    return {
        "favourable_weekdays": favourable_days,
        "cautionary_weekdays": cautionary_days,
        "janma_nakshatra": janma_nak,
        "monthly": monthly,
        "guidance": ("Favourable days suit beginning new ventures, signing contracts, "
                     "and big decisions. Cautionary days are best for completion, "
                     "rest, and avoiding sharp confrontation."),
    }


# ══════════════════════════════════════════════════════════════════════════
# Single entry point
# ══════════════════════════════════════════════════════════════════════════

def compute_interpretations(chart) -> dict:
    """Build all premium-interpretation payloads at once. Attached to chart
    by compute_chart() — see shared.astro.kundli."""
    return {
        "house_analyses":     build_house_analyses(chart),
        "planet_analyses":    build_planet_analyses(chart),
        "life_domains":       build_life_domains(chart),
        "lal_kitab":          build_lal_kitab(chart),
        "year_predictions":   build_year_predictions(chart, n_years=5),
        "auspicious_dates":   build_auspicious_dates(chart, months=12),
    }
