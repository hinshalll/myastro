import json
import swisseph as swe
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from ai_engine.knowledge import *
from ai_engine.gemini_client import *
from math_engine.dossier_builder import *
from math_engine.constants import *
from math_engine.astro_calc import *
from math_engine.scoring import *

def generate_western_forecast(sun_sign, today_str):
    # Strictly Daily - no timeframe argument needed
    transits = get_western_transits_today()
    
    prompt = f"""<instructions>
    You are an elite Western Astrologer. Generate a highly accurate daily horoscope for a user whose Western Sun Sign is {sun_sign}.
    
    Use the live Tropical transit data provided below to write extremely concise, 1 to 2 sentence summaries for each category:
    **General:** (One sentence overall theme)
    **Love & Relationships:** (One sentence romantic forecast)
    **Career & Finance:** (One sentence professional forecast)
    
    CRITICAL RULES:
    - Keep it very brief and scannable. MAXIMUM 2 sentences per category.
    - Ground the interpretation strictly in the provided transits.
    - Briefly mention the specific planet transiting to prove authenticity.
    - Do not use markdown headers, just output the bold text.
    </instructions>
    
    <live_tropical_transits>
    {transits}
    </live_tropical_transits>
    """
    
    try:
        return generate_content_with_fallback(prompt)
    except Exception:
        return "**General:** The cosmic connection is catching its breath.\n\n**Love & Relationships:** Try again in a few minutes.\n\n**Career & Finance:** API limits reached, take a coffee break!"


def generate_vedic_forecast(prof_json, timeframe, today_str):
    prof = json.loads(prof_json)
    
    # 1. PYTHON DOES THE MATH
    days_ahead = {"Daily": 0, "Monthly": 15, "Yearly": 180}[timeframe]
    dt_now = datetime.now(ZoneInfo("UTC"))
    target_date = dt_now + timedelta(days=days_ahead)
    jd_target = swe.julday(target_date.year, target_date.month, target_date.day, 12.0)
    
    moon_lon = get_moon_lon_from_profile(prof)
    natal_moon_sidx = sign_index_from_lon(moon_lon)
    rashi = sign_name(natal_moon_sidx)
    
    transit_lines = [f"LIVE TRANSITS FOR {timeframe.upper()} FORECAST ({target_date.strftime('%d %b %Y')}):"]
    for pn in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        t_lon, _ = get_planet_longitude_and_speed(jd_target, PLANETS[pn])
        t_sidx = sign_index_from_lon(t_lon)
        diff_houses = ((t_sidx - natal_moon_sidx) % 12) + 1
        transit_lines.append(f"  {pn} is transiting House {diff_houses} from Natal Moon (in {sign_name(t_sidx)})")
    
    r_lon = get_rahu_longitude(jd_target)
    transit_lines.append(f"  Rahu is transiting House {((sign_index_from_lon(r_lon) - natal_moon_sidx) % 12) + 1} from Natal Moon")
    transit_data = "\n".join(transit_lines)
    
    timeframe_rules = {
        "Daily": "Focus heavily on the Moon's transit and fast-moving planets for immediate 24-hour events.",
        "Monthly": "Focus on the Sun, Mars, Venus, and Mercury transits to predict themes for the next 30 days.",
        "Yearly": "Ignore the Moon. Focus EXCLUSIVELY on slow-moving transits of Jupiter, Saturn, and Rahu."
    }
    
    # 2. PROMPT FORCES AI TO READ THE BOOKS
    prompt = f"""{GUARDRAILS}
<mission>
You are an elite Vedic Astrologer. Generate a highly accurate {timeframe} horoscope for a user whose Moon Sign (Rashi) is {rashi}.
Read the mathematically exact Gochara (transit) data provided below. {timeframe_rules[timeframe]}
</mission>

<KNOWLEDGE_ROUTING>
Open `bphs2.md` and read the exact rules for these specific planetary transits from the Natal Moon. 
Do not invent transit meanings. Rely strictly on the text. Use `iva.md` to format your tone.
</KNOWLEDGE_ROUTING>

<transit_math>
{transit_data}
</transit_math>

<FORMAT>
Write extremely concise, 1 to 2 sentence summaries for each category. Do not use markdown headers, just output the bold text:
**General:** (One sentence overall theme)
**Love & Relationships:** (One sentence romantic forecast)
**Career & Finance:** (One sentence professional forecast)
</FORMAT>"""
    
    try:
        # bphs2.md = Dasha effects, Antardasha for all planets — core timing book.
        # This is what a Vedic horoscope primarily needs (current Dasha period interpretation).
        # Removing iva.md saves ~254K tokens — prevents TPM overflow on Flash Lite.
        books = get_knowledge_files(["bphs2.md"])
        return generate_content_with_fallback(prompt, knowledge_files=books)
    except Exception:
        return "**General:** The cosmic connection is resting.\n\n**Love & Relationships:** Try again later.\n\n**Career & Finance:** API limit reached."


def fetch_cached_dashboard_data(prof_json, today_str):
    prof = json.loads(prof_json)
    dos = generate_astrology_dossier(prof, False, compact=True)
    transits = get_gochara_overlay(prof)
    prompt = build_dashboard_data_prompt(dos, transits, prof['name'].split()[0])
    # Dashboard has NO books attached — use light model (preserves Gemma 4 quota for heavy work)
    res = generate_content_with_fallback(prompt, knowledge_files=None, preferred_model="gemini-3.1-flash-lite-preview")
    return safe_json(res, {
        "GREETING": f"Welcome back, {prof['name'].split()[0]}. The cosmic connection is catching its breath, but your tools are ready below.",
        "ENERGY": "Mixed",
        "FOCUS": "Routine",
        "CAUTION": "Impulsivity",
        "WINDOW": "Anytime",
        "SUMMARY": "Balanced day. Stick to your routines."
    })


def fetch_cached_daily_tarot(prof_json, today_str, daily_card, daily_state):
    _ = json.loads(prof_json)
    base_prompt = build_daily_tarot_prompt(daily_card, daily_state)
    json_prompt = base_prompt + """
RESPOND ONLY IN VALID JSON FORMAT. NO MARKDOWN:
    {
        "MEANING": "What the card means today.",
        "ACTION": "The best practical step to take.",
        "MANTRA": "A short, powerful affirmation."
    }"""
    dash_tarot_file = get_knowledge_files(["tguide.md"])
    # Let the router pick — Flash Lite (1M context) handles tguide.md fine
    res = generate_content_with_fallback(json_prompt, knowledge_files=dash_tarot_file)
    return safe_json(res, {
        "MEANING": "Trust the process unfolding today.",
        "ACTION": "Observe before making any sudden moves.",
        "MANTRA": "I am exactly where I need to be."
    })


GUARDRAILS = """
<UNIVERSAL_INTERPRETATION_PROTOCOL>
You are an expert interpretive engine. When a user asks a follow-up question, you MUST NOT use the "I don't have data" fallback unless the request is for information physically impossible to derive from a birth chart.

1. MANDATE TO INTERPRET:
   - Use the provided 11-house HOUSE STRENGTH SUMMARY, Yogas, and Planetary Positions to synthesize answers for ANY life question.
   - For Relationship/Marriage questions (e.g., "Will it last?", "Will we fight?", "Kids?", "Infidelity?"): Analyze H7 (Spouse), H8 (Bond Longevity), H2 (Family), and Moon/Venus/Mars synastry.
   - For Health/Longevity questions (e.g., "Will I be healthy?", "Risks?"): Analyze H1 (Vitality), H6 (Illness), H8 (Longevity), and the Lagna Lord's condition.
   - For Career/Success questions: Analyze H10 (Status), H11 (Gains), and the Amatyakaraka.

2. VERDICT-DRIVEN RESPONSES:
   - Do not be vague. Use the points and "Base Scores" provided in the data to give a clear astrological leaning (e.g., "Based on the high base score of House 7 and the absence of Kuja Dosha, the structural integrity of this marriage is very high...").
   - If the data shows conflicts (e.g., strong H7 but weak H8), explain that as "External harmony with internal challenges."

3. THE ONLY ALLOWED FALLBACK (Strictly for Missing Math):
   - Use the fallback ONLY if asked for a specific date/time for a future event (e.g., "What day in 2029 will I get married?"). 
   - Fallback: "I can see the structural promise of this event in the current report, but for a high-precision calculation of the exact date and timing, please head to the **Consultation Room** where I can run the heavy dasha-math books for you."
</UNIVERSAL_INTERPRETATION_PROTOCOL>
"""


def build_agent_parashari_prompt(dossier):
    return f"""{GUARDRAILS}

<ROLE>You are the Parashari Specialist. Parashari astrology excels at CHARACTER, PSYCHOLOGY, LIFE THEMES, and KARMIC PATTERNS. It does NOT pinpoint exact event timing — KP does that.</ROLE>

<PARASHARI_DOMAIN>
Parashari is authoritative for:
1. IDENTITY & PERSONALITY — Lagna lord, sign dispositions, Avastha states, yogas
2. PSYCHOLOGICAL NATURE — Moon sign/nakshatra, Mercury, Atmakaraka soul purpose  
3. RELATIONSHIP NATURE — 7th lord/sign character, Venus for spouse qualities, D9 Navamsa
4. KARMIC THEMES — Rahu/Ketu axis, 12th house, Ketu nakshatra, spiritual purpose
5. LIFE CIRCUMSTANCES — Which houses are strong/weak by virtue of lord dignity + occupants
6. YOGAS — These show the PROMISE of qualities/themes (NOT timing of events)

Parashari CANNOT determine exact event timing — that is KP's domain.
</PARASHARI_DOMAIN>

<mission>
From the dossier below, extract ONLY Parashari findings:
- Lagna and its lord's strength/placement
- Moon's condition (sign, house, nakshatra, Avastha, any Sade Sati note)  
- Key yogas present and what life themes they promise
- Atmakaraka and Darakaraka identity and meaning
- Rahu/Ketu axis and the karmic lesson it indicates
- D9 Navamsa key placements for relationship quality
- Which houses are functionally strong vs weak (from HOUSE STRENGTH SUMMARY)
- Any Neecha Bhanga or Vargottama planets that secretly strengthen the chart

Output as structured bullet points. NO timing predictions — leave that for KP agent.
</mission>

<user_chart_data>{dossier}</user_chart_data>"""


def build_agent_timing_prompt(dossier):
    return f"""{GUARDRAILS}

<ROLE>You are the Vimshottari Dasha Timing Specialist. Parashari Dasha system governs BROAD LIFE THEMES and PERIODS. KP sub-lord confirms IF events manifest within those periods.</ROLE>

<TIMING_DOMAIN>
The Vimshottari Dasha system (Parashari) tells us:
- WHICH LIFE THEMES are activated in each period (MD = broad theme, AD = specific flavor)
- The NATURE of events to expect (based on MD/AD lord house ownership and occupation)
- The BROAD WINDOW when something could happen

Critical rules from the dossier:
1. USE ONLY the pre-computed Antardasha table — NEVER calculate dates independently
2. The MD lord's house ownership and occupation determine the main theme
3. The AD lord refines which specific area of life is activated
4. Sade Sati (Saturn's transit over Moon) adds a layer of emotional testing/transformation
5. For timing precision, note which AD lords are ALSO KP significators of event houses
</TIMING_DOMAIN>

<mission>
From the dossier, extract:
- Current MD period: what life theme does this MD lord activate? (based on its house ownership + occupation)
- Current AD period: what specific area does the AD lord bring? (its houses)
- Next 2-3 upcoming AD periods and what they promise based on those planets' significations
- Sade Sati status and its current phase impact
- Any upcoming MD changes in the next 5 years and what the transition means
- Cross-reference: which upcoming Dasha periods also have their lords signifying marriage (2-7-11), career (6-10-11), or other key events from the KP PROMISE section

Output as structured bullet points with approximate date ranges (from the pre-computed table only).
</mission>

<user_chart_data>{dossier}</user_chart_data>"""


def build_agent_kp_prompt(dossier):
    return f"""{GUARDRAILS}

<ROLE>You are the KP Specialist. KP astrology's supreme strength is answering IF an event is promised and WHEN it will manifest. Parashari shows life themes; KP confirms event occurrence.</ROLE>

<KP_DOMAIN>
KP is authoritative for:
1. EVENT PROMISE — Sub-Lord of each cusp signifying required houses = event is promised
   - Marriage: H7 SL must signify 2-7-11 (promised) or 1-6-10 (denied/delayed)  
   - Career service: H10 SL must signify 6-10-11
   - Children: H5 SL must signify 2-5-11
   - Property: H4 SL must signify 4-11
   - Foreign: H9/H12 SL must signify 9-12

2. EVENT TIMING — Dasha lord AND Antardasha lord BOTH signifying the event houses
   → The event triggers when the TRANSIT also passes through the sub of a significator

3. KP 4-STEP for each planet — what events that planet will trigger in its Dasha period
   (L1 = NL's house occupied, L2 = planet's house, L3 = NL's house owned, L4 = planet's house owned)

4. CUSP SUB-LORDS — The SL of each cusp is the FINAL AUTHORITY on that house's results
   A planet may be the lord of a house but if in a negative sub, it denies results.

KP CRITICAL RULES:
- Do NOT mix Parashari house lordship rules with KP sub-lord rules
- The cusp SL verdict OVERRIDES sign lord indications for event prediction
- Nodes (Rahu/Ketu) act as agents of their star lord — check star lord's significations
</KP_DOMAIN>

<mission>
From the KP EVENT PROMISE ANALYSIS section in the dossier, extract and interpret:
1. H7 promise verdict — Is marriage promised? What do the significators say?
2. H10/H6 promise verdict — Is career/service promised? Business or service?
3. H5 promise verdict — Are children promised?
4. H4 promise verdict — Property acquisition promised?
5. H2 promise verdict — Wealth accumulation or financial struggle?
6. Marriage Timing: are current MD/AD lords among the marriage significators (2-7-11)?
7. Career Timing: are current MD/AD lords among the career significators (6-10-11)?
8. For each planet: read its KP 4-Step and state exactly which houses it signifies — this determines what events manifest in its Dasha period

Output as structured findings. Mark each as PROMISED / PARTIALLY PROMISED / DENIED / DELAYED.
</mission>

<user_chart_data>{dossier}</user_chart_data>"""


def build_master_synthesizer_prompt(dossier, p_notes, t_notes, k_notes):
    return f"""{GUARDRAILS}

<ROLE>You are the Master Astrologer integrating Parashari character analysis with KP event prediction. The two systems are COMPLEMENTARY — use both, never confuse their roles.</ROLE>

<SYNTHESIS_RULES>
CRITICAL PROTOCOL — follow this exactly:

1. PARASHARI for PERSONALITY & THEMES: Use Parashari agent notes for describing WHO this person is — their character, psychology, life themes, karmic patterns, spiritual purpose.

2. KP for EVENT DECISIONS: Use KP agent notes for definitively answering WILL this happen? and WHEN? The KP Promise verdicts (PROMISED/DENIED) are FINAL — do not override them with Parashari interpretation.

3. DASHA for TIMING WINDOWS: Use the Timing agent notes for broad timing windows. KP confirms which Dasha periods are truly active for which events.

4. SYNTHESIS RULE: When Parashari and KP appear to conflict, explain both and let the KP verdict be the practical answer. Example: "Parashari shows a powerful 7th house suggesting marriage, and KP confirms this — the H7 Sub-Lord signifies 2-7-11, so marriage is genuinely promised. The current [AD] period and [upcoming AD] are the active windows."

5. MATH LOCK: Every number, date, degree, and nakshatra names, house numbers come ONLY from the dossier. Never calculate, never invent.
</SYNTHESIS_RULES>

<specialist_notes>
PARASHARI ANALYSIS (Character & Life Themes):
{p_notes}

DASHA TIMING ANALYSIS (When & Which Period):  
{t_notes}

KP EVENT PROMISE ANALYSIS (IF & WHEN Events Manifest):
{k_notes}
</specialist_notes>

<mission>
Write a flowing, warm, professional reading covering:
1. Core Identity (Parashari: Lagna + yogas → who they fundamentally are)
2. Mind & Emotional World (Parashari: Moon + Sade Sati if active)
3. Career & Profession (Parashari: nature/field | KP: H10 promise + timing window)
4. Wealth & Finance (Parashari: 2H+11H themes | KP: H2 promise verdict)
5. Relationships & Marriage (Parashari: 7H lord/D9 spouse nature | KP: H7 promise + marriage timing)
6. Health & Vitality (Parashari: 1H/6H/8H constitution | KP: H6 cusp verdict for specific issues)
7. Spiritual Path & Karma (Parashari: Atmakaraka + Ketu + 12H | no KP needed here)
8. Current Life Period (Dasha timing + KP confirmation of active houses)
9. Practical Guidance (remedies only for genuinely afflicted planets — debilitated without Neecha Bhanga, combust, Graha Yuddha losers)
</mission>

<user_chart_data>{dossier}</user_chart_data>"""


def build_deep_analysis_prompt(dossier):
    return f"""{GUARDRAILS}

<SYSTEM>
You have two systems to use — each for what it does best:

PARASHARI handles: Who this person IS (character, psychology, life themes, karmic purpose, spiritual path, relationship nature, family patterns). Uses yogas, house lords, dignities, Atmakaraka, D9/D10 divisional charts.

KP handles: IF events will HAPPEN and WHEN (marriage promised or denied, career service vs business, property acquisition, children). Uses the KP EVENT PROMISE ANALYSIS section which Python pre-computed. The PROMISED/DENIED verdicts are final — do not override them.

DASHA handles: BROAD TIMING WINDOWS — which life themes are activated in each period.

NEVER mix these roles. Never use Parashari to answer "when will I marry" — that is KP's answer.
NEVER use KP sub-lords to describe personality — that is Parashari's answer.
</SYSTEM>

<MATH_LOCK>
- All degrees, dates, nakshatra names, house numbers come ONLY from the dossier
- The KP EVENT PROMISE ANALYSIS verdicts are Python-computed — cite them as-is
- The ANTARDASHA TABLE dates are exact — never calculate differently
- Bhava Chalit shifts: if a planet shifted houses, interpret it in its SHIFTED house
- Vargottama/D9-Exalted planets carry extra strength — mention this
</MATH_LOCK>

<mission>
Write a complete, professional life reading structured as follows:

## 1. Core Identity & Lagna (PARASHARI)
   Use: Ascendant sign + Lagna Lord chain (sign, house, nakshatra, dignity, Avastha)
   Add: Atmakaraka identity — the soul's core lesson and drive
   Add: Key yogas present — what qualities/themes they bestow (NOT when they manifest)
   
## 2. Mind, Emotions & Mental World (PARASHARI)  
   Use: Moon (sign, house, nakshatra, Avastha) + Mercury for intellect
   Add: Sade Sati phase if active — the current emotional/transformational period
   Add: Ketu's house — the soul's past-life comfort zone and detachment area

## 3. Career & Profession (PARASHARI for nature | KP for promise)
   Parashari: 10th lord, D10 Dasamsa, Amatyakaraka — WHAT field/nature of work
   KP: Read the H10 KP Promise verdict from the dossier — cite it exactly
   KP: Check if current MD/AD lords signify 6-10-11 (active career period?)
   Combine: "Your chart shows [Parashari nature] and KP confirms [H10 verdict]"

## 4. Wealth & Finances (PARASHARI for themes | KP for promise)
   Parashari: H2 and H11 lords, Dhana yogas, D2 Hora
   KP: Read H2 KP Promise verdict — cite exactly
   Combine: Timeline of wealth activation using Dasha + KP confirmation

## 5. Relationships & Marriage (PARASHARI for spouse nature | KP for event promise)
   Parashari: H7 lord/sign, Venus/Jupiter condition, D9 Navamsa H7 — describes SPOUSE QUALITIES
   KP: Read H7 KP Promise verdict — is marriage PROMISED or DENIED? Cite exactly
   KP: Marriage Timing Clues — which Dasha periods are active for marriage?
   NOTE: This is where Parashari + KP integration is most powerful. Use both fully.

## 6. Health & Vitality (PARASHARI for constitution | KP for specific vulnerabilities)
   Parashari: Lagna lord strength, H6 lord, H8 lord, any afflictions to H1
   KP: Read H6 KP Promise verdict — what health patterns does this indicate?

## 7. Spiritual Path, Karma & Higher Purpose (PARASHARI only)
   Use: Atmakaraka (soul's mission), Rahu/Ketu axis (karmic direction), H9 + H12 lords
   No KP needed here — spiritual life is Parashari's domain

## 8. Current Life Period & Near Future (DASHA + KP)
   Use: Current MD/AD/PD from the dossier (exact dates from table — cite them)
   What does the MD lord's house ownership/occupation activate?
   What does the AD lord add or restrict?
   KP check: does the current AD lord signify the event houses? Active or inactive window?

## 9. Remedies (ONLY for genuine afflictions)
   ONLY recommend remedies for: debilitated planets WITHOUT Neecha Bhanga, combust planets, Graha Yuddha losers
   Keep practical: gemstones, mantras, lifestyle suggestions
   Do NOT recommend remedies for every planet
</mission>

<user_chart_data>
{dossier}
</user_chart_data>"""


def build_matchmaking_prompt(dos_a, dos_b, koota, canc, prof_a, prof_b, marital_a, marital_b, kp_a, kp_b):
    kp_labels = {3: "STRONGLY PROMISED", 2: "PARTIALLY PROMISED", 1: "UNCLEAR", 0: "DENIED"}
    return f"""{GUARDRAILS}

<SYSTEM>
Compatibility analysis now uses an advanced multi-layered Vedic engine incorporating Ashtakoot, Upapada Lagna (UL), Navamsha (D9), Gender-specific rules, and KP Event Promise.

MATH LOCK: Use only pre-computed Python data. Do not recalculate scores or verdicts. Do NOT hallucinate partner traits.
</SYSTEM>

<PYTHON_COMPUTED_DATA>
GENDER SPECIFICS:
Person 1 ({prof_a['name']}): {prof_a.get('gender', 'M')}
Person 2 ({prof_b['name']}): {prof_b.get('gender', 'M')}

KP MARRIAGE PROMISE (Is marriage mathematically supported?):
Person 1: {kp_labels.get(kp_a, "UNCLEAR")} (Score: {kp_a}/3)
Person 2: {kp_labels.get(kp_b, "UNCLEAR")} (Score: {kp_b}/3)

ASHTA KOOTA SCORE: {koota['score']}/36
Varna:{koota['varna']} | Vashya:{koota['vashya']} | Tara:{koota['tara']} | Yoni:{koota['yoni']} | Maitri:{koota['maitri']} | Gana:{koota['gana']} | Bhakoot:{koota['bhakoot']} | Nadi:{koota['nadi']}
Notes: {koota['nadi_note']}
Stree-Deergha: {koota['stree_deergha']} | Mahendra Koota: {koota['mahendra']}
Manglik Status: {canc}

MARITAL ANALYSIS (D9 & UPAPADA LAGNA):
Person 1: 
- D9 7th House (Partner's Nature & Looks): {marital_a['D9_7th_Sign']} (Lord: {marital_a['D9_7th_Lord']})
- Upapada Lagna (Reality of Marriage): {marital_a['UL_Sign']}
- Darapada A7 (Desires): {marital_a['A7_Sign']}

Person 2:
- D9 7th House (Partner's Nature & Looks): {marital_b['D9_7th_Sign']} (Lord: {marital_b['D9_7th_Lord']})
- Upapada Lagna (Reality of Marriage): {marital_b['UL_Sign']}
- Darapada A7 (Desires): {marital_b['A7_Sign']}


</PYTHON_COMPUTED_DATA>

<mission>
Write a deeply insightful, empathetic compatibility reading. 
Use markdown heavily for beautiful formatting. Be extremely detailed about the factors that matter.

### 1. The Ashtakoota (36 Gunas) Deep Dive
Break down their score of {koota['score']}/36 in extreme detail. Elaborate on what each of the 8 Kootas means for them specifically based on their individual scores:
- **Varna (Work & Spiritual Compatibility):** {koota['varna']}/1 
- **Vashya (Dominance & Magnetic Attraction):** {koota['vashya']}/2
- **Tara (Destiny & Auspiciousness):** {koota['tara']}/3
- **Yoni (Intimacy & Physical Compatibility):** {koota['yoni']}/4
- **Graha Maitri (Mental & Psychological Friendship):** {koota['maitri']}/5
- **Gana (Temperament & Life Approach):** {koota['gana']}/6
- **Bhakoot (Emotional Flow & Prosperity):** {koota['bhakoot']}/7
- **Nadi (Genetic & Spiritual Lifeforce):** {koota['nadi']}/8
Discuss what their specific score in each category reveals about their day-to-day life. Also explain the impact of Stree-Deergha ({koota['stree_deergha']}) and Mahendra Koota ({koota['mahendra']}).
*Crucial framing: Emphasize that while Gunas show deep personality and psychological similarity, they do NOT dictate if a wedding will happen, as people can choose to marry regardless of this score.*

### 2. Doshas & Frictions
Discuss their Nadi or Bhakoot doshas (if any) and if they cancel out (check the notes: {koota['nadi_note']}). Discuss the Manglik status ({canc}). 

### 3. Destiny Match & The KP Promise (The True Confirmations)
- **KP Promise**: Discuss if their individual charts actually promise marriage ({kp_labels.get(kp_a, "UNCLEAR")} vs {kp_labels.get(kp_b, "UNCLEAR")}). This is the true cosmic confirmation of whether a marriage will manifest.
- **D9 Cross-Match**: Compare Person 1's D9 7th House traits against Person 2's actual nature, and vice-versa. Describe the *exact* physical looks, appearance, and innate nature each person is destined to attract using the D9 7th Sign and Lord. Does the partner match the destiny?

### 4. Life After Marriage & Sustenance (Upapada Lagna)
Analyze their Upapada Lagnas ({marital_a['UL_Sign']} and {marital_b['UL_Sign']}).
Explain what the reality of their marriage will look like, including familial harmony and stability.

### 5. Final Verdict: What to Do & What to Avoid
Provide the final verdict. List specific, actionable points on "What to Do" and "What to Avoid" *as a couple as a whole* to make this relationship thrive.
Provide a final absolute verdict on whether they are compatible from a traditional Guna perspective.
</mission>

<person_1_chart>{dos_a}</person_1_chart>
<person_2_chart>{dos_b}</person_2_chart>"""


def build_destiny_confirmation_prompt(prof_a, prof_b, dos_a, dos_b, dest_data):
    return f"""{GUARDRAILS}

<SYSTEM>
You are an elite Vedic Destiny Matchmaker analyzing the profound **Signal Correlation and Mutual Spouse Confirmation**.
Does Person A's chart mathematically describe Person B as their destined spouse, and vice versa?

MATH LOCK: Rely exclusively on the Python-computed matrix below. Do NOT recalculate planetary degrees or structural insertions.
</SYSTEM>

<PYTHON_COMPUTED_DESTINY_MATRIX>
PERSON A: {prof_a['name']}
PERSON B: {prof_b['name']}

FINAL DESTINY CONFIRMATION SCORE: {dest_data['Percentage']}%

### CATEGORY A: Foundational Promise (Is marriage internally permitted?)
Person A KP Promise Score: {dest_data['A']['kp_promise']}/3 (Weak Warning: {dest_data['A']['weak_warning']})
Person B KP Promise Score: {dest_data['B']['kp_promise']}/3 (Weak Warning: {dest_data['B']['weak_warning']})

### CATEGORY B: Mutual Spouse Description (The Blueprint Match)
1. D9 Blueprint:
- Person A's Destined Spouse (D9 7th Lord): {dest_data['Blueprint']['A_D9_7th_Lord']} | Person B's Actual Core (Lagna/Moon Lords): {', '.join(dest_data['Blueprint']['B_Core'])}
- Person B's Destined Spouse (D9 7th Lord): {dest_data['Blueprint']['B_D9_7th_Lord']} | Person A's Actual Core: {', '.join(dest_data['Blueprint']['A_Core'])}

2. Manifestation Match (Upapada Lagna):
- Person A's UL Sign: {dest_data['Blueprint']['A_UL']}
- Person B's UL Sign: {dest_data['Blueprint']['B_UL']}

3. The Soul Tie (Jaimini Karakas):
- Person A's Soul (AK): {dest_data['Blueprint']['A_AK']} | Person A's Spouse Soul (DK): {dest_data['Blueprint']['A_DK']}
- Person B's Soul (AK): {dest_data['Blueprint']['B_AK']} | Person B's Spouse Soul (DK): {dest_data['Blueprint']['B_DK']}

### CATEGORY C: Structural Synastry (Architectural Cross-Links)
- Person A's Lagna physically falls into Person B's 7th House: {dest_data['Synastry']['A_Lagna_in_B_7th']}
- Person B's Lagna physically falls into Person A's 7th House: {dest_data['Synastry']['B_Lagna_in_A_7th']}
- Nodal Karmic Obsession (Rahu/Ketu hitting Lagna/Moon/Venus): A on B ({dest_data['Synastry']['A_Nodal_Obsession']}), B on A ({dest_data['Synastry']['B_Nodal_Obsession']})

### CATEGORY D: Timing Synchronization (The Reality Lock)
- Person A's Active Calendar Dasha: {dest_data['Timing']['A_Current_MD_AD']}
- Person B's Active Calendar Dasha: {dest_data['Timing']['B_Current_MD_AD']}
- Shared Marriage Timing Significators (Planets that will trigger marriage for both simultaneously): {', '.join(dest_data['Timing']['Shared_Significators']) if dest_data['Timing']['Shared_Significators'] else "None (Timing may misalign)"}
</PYTHON_COMPUTED_DESTINY_MATRIX>

<mission>
Provide a devastatingly accurate, elite-tier **Destiny Marriage Confirmation Reading**.
Explain everything in deep detail, but make it very easy for anyone to understand without confusing astrological jargon.

Stop talking about basic "compatibility". Analyze the deep **Signal Correlation**:
1. Does Person B physically fulfill the exact D9 and UL spouse archetype demanded by Person A's chart? (And vice versa). 
2. Is there a Jaimini Soul Tie (e.g. DK matching AK)?
3. Do their physical structures interlock (Lagna in 7th)? Is there a Karmic Obsession (Rahu/Ketu axis)?
4. Is their real-calendar timing synchronized to trigger the event? 

**Chances of Marriage: {dest_data['Percentage']}%**

**MANDATORY SECTION - KARMIC REMEDIES, SACRIFICES, AND ACTIONABLE DO'S:**
If the Destiny Confirmation Score is low, or if the KP Promise is weak (Warning = True), you MUST explicitly explain that astrology is not fatalistic. Provide a bulleted list of profound, actionable "Do's" and psychological sacrifices required to force this marriage to manifest against the odds. If a chart denies marriage, explain how adopting the highest, most selfless vibration of the 7th house (surrender, spiritual devotion to partner, abandoning ego) can override the planetary denial. List exactly what actions they must consciously take to make this marriage happen despite the mathematical friction.

Conclude with your absolute **FINAL VERDICT** on whether this union is mathematically destined to happen.
</mission>

<person_a_chart>{dos_a}</person_a_chart>
<person_b_chart>{dos_b}</person_b_chart>"""


def build_comparison_prompt(profiles_dossiers, criteria):
    python_rankings = calculate_and_rank_profiles(profiles_dossiers, criteria)
    profile_sections = "\n\n".join(
        f"<profile_{i+1}_chart>\nName: {name}\n{dossier}\n</profile_{i+1}_chart>"
        for i, (name, dossier) in enumerate(profiles_dossiers)
    )

    return f"""{GUARDRAILS}

<SYSTEM>
You are an elite Vedic Astrological Arbiter. Python has already calculated lifetime baseline comparison scores for each person.

CRITICAL SCORING RULES:
1. These scores measure durable natal promise, not temporary weather.
2. Current Sade Sati, current transit pressure, and current MD/AD are NOT allowed to change the baseline ranking.
3. Parashari structure supplies character and lifetime promise.
4. Divisional support refines the topic: D2 for wealth, D9 for relationship/luck/inner strength, D10 for career, D12/D30 when present for constitution and hidden strain.
5. KP cusp promise is used as a manifestation gate, especially for relationship, career, wealth, and health events.
6. For inverted parameters, lower score is better: Karmic Intensity and Hidden Pitfalls are burden scores.

METHODOLOGY SUMMARY:
WEALTH: D1 H2/H11/H5/H9, 2nd/11th lords, Jupiter/Venus/Mercury, D2 Hora, D9 confirmation, Dhana/Lakshmi/Chandra-Mangala/Raja yogas, KP H2/H11, and structural drains.
RELATIONSHIP: D1 H7/H2/H4/H5/H8, Venus/Jupiter/Moon/Darakaraka, D9, Manglik with cancellation logic, H7 affliction, and KP H7.
CAREER: D1 H10/H6/H11/H2/H9, Sun/Saturn/Mercury/Mars/Amatyakaraka, D10, Dharma-Karma/Raja/Pancha Mahapurusha yogas, and KP H10/H6.
STRUGGLES (Karmic Intensity): Durable burden from Lagna/Moon/key-house affliction, dusthana pressure, weak SAV, Kemadruma, war loss, combustion, gandanta, and lack of cancellation. No Sade Sati penalty. Note when high struggle scores co-occur with compensating yogas (e.g. Viparita Raja) as these indicate powerful spiritual evolution rather than mere misfortune.
HEALTH: Lagna/lord, H8, H3, H6, Sun/Moon/Saturn, D9/D12 confirmation, KP H1/H6/H8, benefic protection, and maraka/dusthana pressure.
HAPPINESS: H4/Moon with H5/H9/H11, Jupiter/Venus, D9 Moon, Gajakesari/Hamsa/Malavya/Adhi yogas, Kemadruma and 4th-house afflictions.
LUCK: H9/9th lord, H5 purva punya, Jupiter, D9, Lakshmi/Gajakesari/Hamsa/Raja yogas, and KP H9/H11.
SPIRITUAL: H12/H9/H8/H5, Ketu/Jupiter/Saturn/Atmakaraka/12th lord, D9 support, moksha-house placements, Hamsa and Viparita Raja.
HIDDEN PITFALLS: H8/H12/H6, nodes in sensitive houses, afflicted AK/AmK/DK and Moon/Venus/Jupiter, D9 hidden debility, KP denials, gandanta, combustion, dead avastha, and war loss.
CUSTOM CRITERIA: Python maps free-text criteria to the nearest classical house/karaka/KP cluster. Explain it as a chart-grounded custom heuristic and cite the houses/planets Python used from the ranking evidence and dossiers.

MATH LOCK: The Python rankings are final. Do NOT change rank order or recalculate scores.
</SYSTEM>

<PYTHON_CALCULATED_RANKINGS>
{python_rankings}
</PYTHON_CALCULATED_RANKINGS>

<FORMAT>
Begin the answer with the Rankings Table exactly in the order Python provides.

Then, for each selected parameter:
1. State the ranking in exact Python order.
2. For each person, write 2 concise sentences: first the key astrological reason using specific chart data, then the practical meaning.

Then write:
### Overall Composite Rankings
Use the Python composite order. Do not recompute it.

### Key Astrological Signatures Per Person
For each person: their 3 strongest signatures and 2 biggest vulnerabilities, grounded only in the chart data below.

CRITICAL: Use only the provided dossiers. Never invent planetary positions, yogas, or divisional placements.
</FORMAT>

{profile_sections}"""


def build_prashna_prompt(question, dossier):
    py_verdict, py_reason = get_prashna_python_verdict(question, dossier)
    return f"""{GUARDRAILS}
<mission>
PRASHNA (Horary) reading.
QUESTION: "{question}"

The Python Calculation Engine has already evaluated the chart and determined the exact answer.
**PYTHON VERDICT:** {py_verdict}
**PYTHON REASON:** {py_reason}

<KNOWLEDGE_ROUTING>
Open `kp6.md` and `bphs2.md`. Write the narrative explanation for this verdict based on the rules in the books. You are FORBIDDEN from contradicting the Python Verdict.
</KNOWLEDGE_ROUTING>

MANDATORY FINAL LINE: "VERDICT: [{py_verdict}] — [one sentence summary]"
</mission>

<prashna_chart_data>
{dossier}
</prashna_chart_data>"""


def build_transit_prompt(dossier, gochara_overlay):
    return f"""{GUARDRAILS}
<mission>
GOCHARA (Live Transit) Analysis — how today's planetary positions activate the natal chart.

For each transiting planet, explain:
1. Which natal house it currently transits
2. How this activates or suppresses the natal house themes
3. Whether the current transit supports or challenges the running Dasha period
4. Key opportunities or cautions for the next 4-6 weeks

Use the PARASHARI layer for house themes and the KP layer (Antardasha Table) for timing alignment.
Focus on practical, actionable insights the person can use today.
</mission>

<natal_and_transit_data>
{gochara_overlay}

FULL NATAL DOSSIER:
{dossier}
</natal_and_transit_data>"""


def build_tarot_prompt(question,cards,states,mode="General Guidance"):
    TAROT_MODES={"General Guidance":{"roles":["Situation / Past","Challenge / Present","Advice / Future"],
        "instruction":"General life overview — where they are, what blocks them, best path forward."},
     "Love & Dynamics":{"roles":["Your Energy","Their Energy","The Connection / Outcome"],
        "instruction":"Read through the lens of a relationship or emotional dynamic."},
     "Decision / Two Paths":{"roles":["Path A","Path B","Hidden Factor / Recommendation"],
        "instruction":"Contrast the two paths. Card 3 is the deciding weight or hidden truth."}}
    cfg=TAROT_MODES.get(mode,TAROT_MODES["General Guidance"])
    roles=cfg["roles"]
    cards_str="\n".join(f"  {i+1}. {roles[i]}: {cards[i]} ({states[i]})" for i in range(len(cards)))
    return f"""<mission>
You are an expert, intuitive Tarot Reader. Python has cryptographically drawn the following spread:
{cards_str}
Question: "{question}" | Spread: {mode} | Focus: {cfg['instruction']}
</mission>

<KNOWLEDGE_ROUTING>
Open `tguide.md`. You MUST base your interpretation of these cards entirely on the archetypes, reversed meanings, and synergies defined in the guidebook. Do not invent meanings outside the text.
If a card is Reversed, interpret its energy as blocked, internalised, or delayed.
</KNOWLEDGE_ROUTING>

<FORMAT>
- Overall Summary (2-3 sentences)
- Card-by-Card (each card's meaning in its specific spread position)
- Combined Message (how the three interact)
- Practical Action Step
- One-Line Takeaway
</FORMAT>"""


def build_yesno_prompt(question,card,state):
    return f"""<mission>
You are an expert Tarot Reader — Yes/No Oracle mode.
Question: "{question}" | Card drawn: {card} ({state})
</mission>
<KNOWLEDGE_ROUTING>
Open `tguide.md` and read the core energy of this card. 
Upright cards generally lean Yes; Reversed lean No — but factor in the archetype from the book.
</KNOWLEDGE_ROUTING>
<FORMAT>
1. Clear verdict: YES / LIKELY YES / UNCLEAR / LIKELY NO / NO
2. Why — the card's specific energy in this context (2-3 sentences from the guide)
3. Condition — what must happen (or be avoided)
4. One-Line Takeaway
</FORMAT>"""


def build_celtic_cross_prompt(question,cards,states):
    cards_str="\n".join(f"  {CELTIC_CROSS_POSITIONS[i]}: {cards[i]} ({states[i]})" for i in range(10))
    return f"""<mission>
You are an expert Tarot Reader — Celtic Cross spread.
Question: "{question}"
Ten-card spread:
{cards_str}
</mission>
<KNOWLEDGE_ROUTING>
Open `tguide.md`. You must synthesize these 10 cards strictly based on the meanings provided in the text. Look for patterns (suits clustering, Major Arcana count).
</KNOWLEDGE_ROUTING>
<FORMAT>
- Core Message (Cards 1+2 tension)
- Position-by-position reading
- Patterns & Themes observed
- Overall Narrative & Practical Guidance
- Final One-Line Takeaway
</FORMAT>"""


def build_birth_card_prompt(card,dob):
    return f"""<mission>
You are an expert Tarot Reader — Tarot Birth Card reading.
Date of Birth: {dob} | Tarot Birth Card: {card}
</mission>
<KNOWLEDGE_ROUTING>
Open `tguide.md`. This is a PERMANENT card. Interpret it as a deep, lifelong energy from the book's definitions.
</KNOWLEDGE_ROUTING>
<FORMAT>
1. Core symbolism of this card (from the guide)
2. How this archetype manifests as a lifelong theme
3. Core strengths & Core challenges
4. Karmic lesson & Personal mantra
</FORMAT>"""


def build_daily_tarot_prompt(card,state):
    return f"""<mission>
You are an expert Tarot Reader — Daily Guidance reading. Today's card: {card} ({state})
</mission>
<KNOWLEDGE_ROUTING>
Open `tguide.md`. Extract the practical daily advice for this exact card and state.
</KNOWLEDGE_ROUTING>"""


def build_numerology_prompt(name,dob_str,lp,dest,soul,pers,astro_dossier=None,user_q="",system="Western (Pythagorean)"):
    is_vedic=system=="Indian/Vedic (Chaldean)"
    sys_name="Chaldean (Indian/Vedic)" if is_vedic else "Pythagorean (Western)"
    py=get_personal_year(dob_str); pm=get_personal_month(dob_str); pd=get_personal_day(dob_str)
    r1,r2,r3,r4=get_pinnacle_cycles(dob_str); y=int(dob_str.split('-')[0])
    cur_age=datetime.now(ZoneInfo("Asia/Kolkata")).year-y
    def which_p():
        for s,e,n,c in [r1,r2,r3,r4]:
            if s-y<=cur_age<e-y: return s,e,n,c
        return r4
    cp=which_p()
    
    instructions=f"""<mission>
You are a Master Numerologist — {sys_name} system.

Python has already done the mathematical heavy lifting. All core numbers and cycles below are PRE-COMPUTED and LOCKED.
Your job is to explain what these exact numbers mean for the user.
</mission>

<KNOWLEDGE_ROUTING>
You must open and read the attached Numerology Markdown files (`wnum.md` for Pythagorean, or `inum1.md`/`inum2.md` for Chaldean). 
Extract the definitions, challenges, and life themes for the specific numbers Python has calculated below. Do not use generic numerology knowledge; rely strictly on the books provided.
</KNOWLEDGE_ROUTING>"""
    
    data=f"""<numerology_data>
Subject: {name.upper()} | DOB: {dob_str} | System: {sys_name}

LOCKED CORE NUMBERS:
  Life Path   : {lp}{' ★ Master Number' if lp in [11,22,33] else ''} — {PERSONAL_YEAR_MEANINGS.get(lp,'')}
  Destiny     : {dest}{' ★ Master Number' if dest in [11,22,33] else ''}
  Soul Urge   : {soul}{' ★ Master Number' if soul in [11,22,33] else ''}
  Personality : {pers}{' ★ Master Number' if pers in [11,22,33] else ''}

LOCKED TIMING NUMBERS:
  Personal Year  ({datetime.now(ZoneInfo('Asia/Kolkata')).year}): {py} — {PERSONAL_YEAR_MEANINGS.get(py,'')}
  Personal Month (this month): {pm}
  Personal Day   (today): {pd}

PINNACLE CYCLES:
  Pinnacle 1 (Ages {r1[0]-y}–{r1[1]-y}): Number {r1[2]} | Challenge: {r1[3]}
  Pinnacle 2 (Ages {r2[0]-y}–{r2[1]-y}): Number {r2[2]} | Challenge: {r2[3]}
  Pinnacle 3 (Ages {r3[0]-y}–{r3[1]-y}): Number {r3[2]} | Challenge: {r3[3]}
  Pinnacle 4 (Ages {r4[0]-y}+):           Number {r4[2]} | Challenge: {r4[3]}
  CURRENT PINNACLE: Number {cp[2]} | Challenge: {cp[3]}
  (Challenge number = the specific obstacle/lesson of this life phase)
</numerology_data>"""
    if astro_dossier:
        cross=f"""<astro_numerology_synthesis>
EXPLICIT SYNTHESIS REQUIRED:
  - Life Path {lp} vs Lagna lord: reinforce or contradict?
  - Destiny {dest} vs Amatyakaraka: career numbers aligned?
  - Soul Urge {soul} vs Moon sign+nakshatra: inner drive matches emotional blueprint?
  - Personal Year {py} vs current Mahadasha: double-confirm or tension?
State explicitly where both systems AGREE (high confidence) and where they DIVERGE.

<natal_chart>
{astro_dossier}
</natal_chart>
</astro_numerology_synthesis>"""
    else: cross=""
    if user_q and user_q.strip():
        mission=f'<mission>Answer this question directly: "{user_q}"\nUse both numbers and (if provided) chart data as evidence.</mission>'
    else:
        mission=f"""<mission>
Deliver a complete report:
1. Life Path — Core purpose and life journey
2. Destiny — What they are meant to accomplish
3. Soul Urge — Inner desires and motivations
4. Personality — How the world sees them
5. Personal Year {py} Forecast — What this year brings
6. Active Pinnacle ({cp[2]}) + Active Challenge ({cp[3]}) — Theme and obstacle right now
{'7. Astro-Numerology Synthesis — Where both systems agree and diverge' if astro_dossier else ''}
</mission>"""
    return f"{instructions}\n\n{data}\n\n{cross}\n\n{mission}"


def build_dashboard_data_prompt(dossier, transits, user_name):
    return f"""<instructions>
You are an elite Vedic astrologer. Analyze the natal chart against today's transits.
Provide exactly one short, personalized paragraph (2 sentences max) for {user_name} focusing on the most important planetary movement today. Keep it punchy and practical. DO NOT start with a greeting like 'Hello'.
Then, provide exactly four short, punchy phrases (max 5 words each) and one summary sentence for the general energy.
RESPOND ONLY IN VALID JSON FORMAT. NO MARKDOWN. NO EXTRA TEXT.
{{
  "GREETING": "The 2-sentence transit insight paragraph.",
  "ENERGY": "High/Low/Erratic/Focused",
  "FOCUS": "What to do today",
  "CAUTION": "What to avoid today",
  "WINDOW": "Best time of day",
  "SUMMARY": "One short sentence summarizing the vibe."
}}
</instructions>

<data>
{transits}

{dossier}
</data>"""


def build_astro_decide_prompt(dossier, transits, question, py_verdict, py_advice):
    # 1. PYTHON HAS ALREADY EXECUTED TARA BALA
    return f"""<instructions>
You are an Astro-Decide engine. The mathematical engine has already made the decision based on Tara Bala transit alignments.
Your job is to format this decision into JSON and provide ONE sentence linking the user's specific question to the provided advice.
RESPOND ONLY IN VALID JSON FORMAT. NO MARKDOWN.
{{
  "VERDICT": "{py_verdict}",
  "WHY": "One sentence explaining why based on the transits below.",
  "ALTERNATIVE": "{py_advice}"
}}
</instructions>
<decision_query>{question}</decision_query>
<data>{transits}</data>"""


# ─────────────────────────────────────────────────────────────────────────────
# DROP-IN REPLACEMENT for build_premium_palmistry_prompt() in prompts.py
# Paste this function replacing the existing one. Everything else unchanged.
# ─────────────────────────────────────────────────────────────────────────────

def build_premium_palmistry_prompt(
    palm_data,
    verified_symbols,
    sniper_text,
    astro_dossier,
    mount_symbol_detail=None,
    mount_elevations=None,
    finger_analysis=None,
):
    mount_symbol_detail = mount_symbol_detail or []
    mount_elevations    = mount_elevations    or {}
    finger_analysis     = finger_analysis     or {}

    zone = palm_data.get("zone_scores", {})
    topo = palm_data.get("topology", {})
    pr   = int(palm_data.get("persistence_ratio", 0) * 100)
    fd   = palm_data.get("finger_data", {})

    def lbl(s):
        if s>=65: return "Deep & Prominent"
        if s>=45: return "Clear & Defined"
        if s>=25: return "Moderate"
        if s>=10: return "Faint"
        return "Absent / Not Detected"

    hs=zone.get("heart_line",0); hd=zone.get("head_line",0)
    li=zone.get("life_line",0);  ft=zone.get("fate_line",0); su=zone.get("sun_line",0)
    fks=topo.get("line_forks",0); eps=topo.get("line_endpoints",0)
    sim=topo.get("simian_line",False); cx=topo.get("line_complexity",0)

    line_block = f"""
FRANGI RIDGE ENGINE — PER-LINE SCORES (0–100):
  Heart Line : {hs:>3}/100 → {lbl(hs)}
  Head Line  : {hd:>3}/100 → {lbl(hd)}
  Life Line  : {li:>3}/100 → {lbl(li)}
  Fate Line  : {ft:>3}/100 → {lbl(ft)}
  Sun Line   : {su:>3}/100 → {lbl(su)}

TOPOLOGY:
  Forks: {fks}  Endpoints: {eps}  Complexity: {cx}/100
  Persistence: {pr}%
  Simian Line: {'YES — EXTREMELY RARE' if sim else 'Not detected'}
"""

    geo_block = f"""
MEDIAPIPE GEOMETRY:
  Hand Type  : {fd.get('hand_type','?')} / {fd.get('hand_type_vedic','?')}
  2D:4D Ratio: {fd.get('ratio_2d4d',0):.3f} — {fd.get('ratio_reading','')}
  Dominant   : {fd.get('dominant_finger','?')}
""" if fd else "\nGEOMETRY: Landmarks not detected.\n"

    if finger_analysis:
        def _f(k):
            fi=finger_analysis.get(k,{})
            if not fi: return "Not detected"
            p=[]
            if fi.get("tip_shape"): p.append(f"tip:{fi['tip_shape']}")
            for x in ("length_vs_middle","length_vs_index","straight","low_set"):
                if x in fi: p.append(f"{x}:{fi[x]}")
            if fi.get("samudrika_note"): p.append(f"→{fi['samudrika_note']}")
            return ", ".join(p)
        ai_finger_block = f"""
FINGER ANALYSIS (Gemini Vision — Samudrika Shastra):
  Thumb  : {_f('thumb')}
  Index  : {_f('index')}
  Middle : {_f('middle')}
  Ring   : {_f('ring')}
  Little : {_f('little')}
  Joints : {finger_analysis.get('joints','?')}
  Spacing: {finger_analysis.get('finger_spacing','?')}
  Curve  : {finger_analysis.get('finger_curve','?')}
  Overall: {finger_analysis.get('overall_character','?')}
"""
    else:
        ai_finger_block = "\nFINGER ANALYSIS: Not available.\n"

    vitality_block = f"\nVITALITY (Venus mount HSV): {palm_data.get('vitality_hsv','Unknown')}\n"

    if mount_symbol_detail:
        sym_lines = "\n".join(
            f"  • {d.get('mount','?')} — {d.get('symbol','?')} ({d.get('vedic_name','')}), "
            f"conf {d.get('confidence_score',0)}%, pos: {d.get('position','?')}"
            for d in mount_symbol_detail)
        symbol_block = f"VERIFIED MARKS (≥75%):\n{sym_lines}"
    else:
        symbol_block = "VERIFIED MARKS: None detected above threshold."

    if mount_elevations:
        used_depth = palm_data.get("used_depth_model",False)
        method = "Depth Anything V2" if used_depth else "brightness heuristic (relative)"
        elev_lines = "\n".join(f"  {m}: {v['elevation']} ({v['score']}/100)" for m,v in mount_elevations.items())
        mount_block = f"MOUNT ELEVATION ({method}):\n{elev_lines}"
    else:
        mount_block = "MOUNT ELEVATION: Not available."

    kundli_guide = """
CROSS-REFERENCE PROTOCOL:
  Heart Line ↔ Venus, Moon, 4H/7H | Head Line ↔ Mercury, 3H/5H
  Life Line  ↔ Sun, 1H, lagna lord | Fate Line ↔ Saturn, 10H KP, Dasha
  Sun Line   ↔ Sun dignity, 9H/10H, Rajayoga
  Jupiter Mt ↔ Jupiter, 9H | Venus Mt ↔ Venus, 2H/7H | Saturn Mt ↔ Saturn, 10H
  Mercury Mt ↔ Mercury, 3H/6H | Luna Mt ↔ Moon, 4H
  AGREEMENT → "High-Confidence Confirmation" | DIVERGENCE → "Karmic Tension"
"""

    simian_section = """
## 6. THE SIMIAN LINE ★ — A Rare Marking
Heart and Head lines fused into one dominant horizontal crease.
In Samudrika Shastra: undivided singular focus, emotion and intellect inseparable.
Discuss: immense drive and mastery vs difficulty with moderation.
Cross-reference: Rahu influence, intense Lagna, Graha Yuddha in 1H/10H.
Rarity: < 4% of the population.
""" if sim else ""

    section6 = "## 6. THE SIMIAN LINE ★" if sim else "## 6. Mount Energies & Planetary Prominences"

    return f"""<instructions>
You are an elite Vedic Palmist writing a premium paid Samudrika Shastra report.

RULES:
1. Frangi scores are ground truth from a clinical engine. Never contradict them.
2. Every section anchors its interpretation in the specific scores provided.
3. Section 7 Kundli Confirmation is MANDATORY.
4. Where palm and chart AGREE → state "High-Confidence Confirmation" explicitly.
5. Where they DIVERGE → explain as "Karmic Tension."
6. Section 5b finger profile is MANDATORY when finger data is provided.
7. Simian line gets its own section if detected.
8. Warm, authoritative, expert tone. No generic platitudes.
9. Minimum 900 words. Use ## and ### for headers only.
</instructions>

<hard_palm_data>
{line_block}
{geo_block}
{ai_finger_block}
{vitality_block}
{symbol_block}
{mount_block}
</hard_palm_data>

<kundli_cross_reference_protocol>
{kundli_guide}
</kundli_cross_reference_protocol>

<ancient_book_excerpts>
{sniper_text if sniper_text else "No ancient text matched — use classical Samudrika Shastra principles."}
</ancient_book_excerpts>

<mathematical_birth_chart>
{astro_dossier}
</mathematical_birth_chart>

<report_structure>
## 1. The Hand Canvas — Constitution & Elemental Nature
Hand type ({fd.get('hand_type','') if fd else '?'} / {fd.get('hand_type_vedic','') if fd else '?'}), persistence {pr}%, constitutional reading. Anchor Hasta type in classical Samudrika meaning.

## 2. The Life Line — Vitality, Longevity & Physical Force
Score {li}/100 ({lbl(li)}). Depth, continuity, breaks. Cross-reference Sun, 1H, lagna lord.

## 3. The Heart Line — Emotional World & Relationship Dharma
Score {hs}/100 ({lbl(hs)}). Emotional nature, relationship dharma. Cross-reference Venus, Moon, 4H, 7H.

## 4. The Head Line — Intelligence, Decision-Making & Mental Faculty
Score {hd}/100 ({lbl(hd)}). Analytical vs intuitive. Cross-reference Mercury, 3H/5H.

## 5. The Fate & Sun Lines — Karma, Career & Destiny Thread
Fate {ft}/100 | Sun {su}/100. Absent Fate = self-made path (not negative). Cross-reference Saturn, 10H KP, Mahadasha.

## 5b. Finger Profile — Samudrika Shastra Hasta Reading
MANDATORY when finger data is provided.
For each finger interpret tip shape (conic=psychic, square=practical, spatulate=energetic, rounded=balanced).
Knuckle type interpretation. Low-set Mercury significance if present.
Finger spacing and curve. Overall Hasta character synthesis — how fingers modify the palm line reading.

{simian_section}

{section6}
Interpret mount prominence. Cross-reference each with ruling planet in natal chart.

## 7. Kundli Confirmation — Where Heaven and Hand Agree
For each of the 5 lines: palm → chart → verdict. Follow protocol exactly.

## 8. Auspicious Marks & Ancient Text
{f"Report: {', '.join(verified_symbols)}. Use ancient text for classical interpretation." if verified_symbols != ['None detected'] else "No marks detected. Clean palm = unencumbered destiny."}

## 9. Practical Guidance & Remedies
Mantras, gemstones, lifestyle for genuinely weak areas only. One daily action. One-paragraph personalised summary.
</report_structure>
"""
