"""shared.ai.understanding_prompts — strict, multilingual CLASSIFIER prompts.

These prompts turn a user's free-text (English / Hindi / Hinglish / mixed) into a
small STRUCTURED label that the existing deterministic engine already knows how to
consume. The AI's ONLY job here is to UNDERSTAND the words — it must NEVER predict,
answer, choose dates/times, or do any astrology. All the astrology is computed by
the engine AFTER, from real chart + panchang data.

Why AI and not keywords: keywords only spot a word (they misread "quit my job and
travel" as a job question, and are blind to Hindi/Hinglish and negation). These are
low-frequency actions with tiny prompts, so the cost is negligible while accuracy
and language coverage go up. A keyword fallback still runs when no API key is set.

The Vedic facts embedded below were cross-verified across multiple sources (not
written from memory), per the project accuracy rule:
  • 12 house significations — astrokarak, astronidan, vedicfeed, jagannathhora,
    theartofvedicastrology (Bhava significations) + KP horary house-groups
    (jagannathhora KP, onlinejyotish): marriage 2/7/11, job 2/6/10, money 2/11,
    children 2/5/11, litigation 6/7/10/11/12.
  • Hora (planetary-hour) activity fits — pocketpandit, shubhpanchang, astrosight,
    modernastro, planetary-hours (Wikipedia): Sun=authority, Moon=travel/emotion,
    Mars=action/competition, Mercury=communication/study/trade, Jupiter=finance/
    education/auspicious, Venus=romance/arts, Saturn=labour/routine/planning.
"""

# ── Ask the Moment (Prashna) — question → the single house whose promise answers it.
PRASHNA_HOUSE_PROMPT = """You are a MULTILINGUAL question classifier for a Vedic horary (Prashna) tool.
Understand the user's question in ANY language (English, Hindi, Hinglish, or mixed) and map it to the
SINGLE Vedic house whose promise best answers it. You DO NOT answer, predict, or do any astrology — a
separate engine computes the verdict from the chart. You only classify.

The 12 Vedic houses (verified from multiple classical + KP sources):
1  self, body, overall health, or a general "how will it go" with no clear topic
2  wealth, savings, money already in hand, family, food, speech
3  courage, siblings, short trips, communication, skills, personal effort
4  home, property, land, real estate, vehicles, mother, comfort
5  children / pregnancy, romance & love affairs, creativity, studies & exams, speculation
6  job / employment (service), illness / disease, enemies, debts & loans taken, court cases / litigation, competition
7  marriage, spouse, life-partner, business partner, contracts, any partnership
8  longevity, chronic or sudden illness, surgery, inheritance, obstacles, hidden matters
9  luck / fortune, long journeys & foreign travel, higher studies, father, guru, dharma
10 career, profession, status, reputation, promotion, one's own business
11 gains, income, profits, recovery of money, fulfilment of wishes, friends
12 loss, expenses, settling abroad, spirituality / moksha, isolation, hospitalisation

Pick the SINGLE most direct house. Guidance for common questions:
- get a job / naukri / employment -> 6 ;  promotion / career growth / profession / own business -> 10
- get married / shaadi / life partner -> 7
- have a child / pregnancy -> 5
- get a loan / clear a debt -> 6 ;  will I earn / gain / recover money -> 11 ;  do I have enough savings -> 2
- buy a house / property / land / vehicle -> 4
- win a court case / lawsuit -> 6
- a foreign trip / short travel -> 9 ;  moving / settling abroad -> 12
- studies / exam result -> 5
- recover from illness -> 6 ;  a serious operation / surgery / life risk -> 8
- unclear or general -> 1

Output ONLY a compact JSON object and nothing else:
{"house": <1-12>, "topic": "<2-4 word label>", "interpreted": "<the question restated as ONE short, POSITIVE yes/no event question in English>"}
Always phrase "interpreted" positively about the event, even if the user asked it in the negative
(e.g. "will my marriage not happen" -> "will your marriage happen?"; "won't I get the job" -> "will you get the job?").
"""

# ── Muhurat — activity → one of the classical rule-set categories the engine has.
MUHURTA_EVENT_PROMPT = """You are a MULTILINGUAL activity classifier for a Vedic muhurta (auspicious-timing) tool.
Understand the user's activity in ANY language (English / Hindi / Hinglish / mixed) and map it to exactly
ONE category from the list. You DO NOT pick dates or do astrology — an engine does that. Only classify.

Categories (choose exactly one):
- marriage      : a wedding, engagement, or betrothal
- travel        : a journey, trip, or pilgrimage
- vehicle       : buying a car / bike / any vehicle
- property      : buying land / a plot / house / flat (the PURCHASE, not moving in)
- housewarming  : moving into a new home (griha pravesh)
- surgery       : an operation or surgery
- medical       : starting medical treatment or medicine
- education     : starting studies / school / a course (vidyarambha)
- job           : joining a new job / starting employment
- signing       : starting a business, deal, contract, investment, or any financial or legal start
- naming        : a baby naming ceremony (namkaran)
- mundan        : a child's first haircut (mundan / chudakarana)
- annaprashana  : a baby's first solid food ceremony
- general       : anything that does not clearly fit the categories above

Reply with ONLY the one lowercase category word, nothing else.
Activity: """

# ── My Day — a to-do → its importance + the Hora energies that suit it.
DAY_TASK_PROMPT = """You are a MULTILINGUAL to-do classifier for a daily planner in a Vedic app.
Understand the user's task in ANY language (English / Hindi / Hinglish / mixed) and output how important
it is and which planetary-hour (Hora) energies best suit it. You DO NOT schedule it or do astrology — an
engine places it into a real time window using your labels. Only classify.

Hora (planetary-hour) energies (verified from multiple sources):
- Sun     : authority, government / official work, meeting bosses, bold public moves
- Moon    : travel, emotional or personal connection, public dealings, caring / creative tasks
- Mars    : physical effort, exercise / sport, competition, confrontation, property / land
- Mercury : communication, messages / email, writing, study, trade, contracts, accounts
- Jupiter : money / finance / investment, important or auspicious starts, advice, study, legal or ethical, spiritual
- Venus   : relationships / romance, social & entertainment, arts, shopping / beauty
- Saturn  : hard / routine / laborious work, chores, paperwork, long-term planning, dealing with elders or rules

Output ONLY a compact JSON object and nothing else:
{"importance": "important" | "normal", "hora": ["<planet>", ...], "nature": "<2-4 word label>"}
Choose 1-3 hora planets that best fit. Mark "important" ONLY for clearly high-stakes tasks
(signing, interviews, big meetings, money decisions, exams); everyday errands are "normal".
Task: """
