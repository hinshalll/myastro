"""features.numerology.prompts — full-report + cycles prompts."""

from shared.timeloc import FALLBACK_TZ, user_now
from shared.astro.constants import PERSONAL_YEAR_MEANINGS
from shared.astro.astro_calc import (
    get_personal_year, get_personal_month, get_personal_day, get_pinnacle_cycles,
)


def build_full_report_prompt(
    name: str, dob_str: str, lp: int, dest: int, soul: int, pers: int,
    astro_dossier: str | None = None, user_q: str = "",
    system: str = "Western (Pythagorean)", knowledge_context: str = "",
    tz: str = FALLBACK_TZ,
) -> str:
    # Personal year/month/day are DATE-based, so they belong to the user's own day (bucket D in
    # LOCATION_TIME_AUDIT.md). The engine already accepts a tz; this caller used to drop it and
    # hard-code Asia/Kolkata, which quietly gave every non-Indian user India's personal day —
    # and gave everyone the wrong personal YEAR across the New Year boundary.
    is_vedic = system == "Indian/Vedic (Chaldean)"
    sys_name = "Chaldean (Indian/Vedic)" if is_vedic else "Pythagorean (Western)"
    py = get_personal_year(dob_str, tz)
    pm = get_personal_month(dob_str, tz)
    pd = get_personal_day(dob_str, tz)
    r1, r2, r3, r4 = get_pinnacle_cycles(dob_str)
    y = int(dob_str.split('-')[0])
    cur_age = user_now(tz).year - y

    def which_p():
        for s, e, n, c in [r1, r2, r3, r4]:
            if s - y <= cur_age < e - y:
                return s, e, n, c
        return r4
    cp = which_p()

    knowledge_block = f"""
<KNOWLEDGE_CONTEXT>
{knowledge_context}
</KNOWLEDGE_CONTEXT>
<RULES>
Use only the numerology passages above to explain these specific numbers. Do not use generic knowledge outside these passages.
When you cite a doctrine claim, weave in a natural friendly reference to the source (e.g. 'classical Parashari texts', 'the KP system', 'Samudrika Shastra') — NEVER output literal markers like [BOOK: filename.md] in your reply. Those tags are internal.
If a specific nuance isn't in the passages, say so honestly rather than inventing it.
</RULES>""" if knowledge_context else ""

    instructions = f"""<CONSERVATIVE_VOICE>
Be conservative. When uncertain between two readings, prefer the safer one and say
you're uncertain. NEVER fabricate dates or numerological claims outside the LOCKED
numbers Python has supplied below.
</CONSERVATIVE_VOICE>

<mission>
You are a Master Numerologist — {sys_name} system.

Python has already done the mathematical heavy lifting. All core numbers and cycles below are PRE-COMPUTED and LOCKED.
Your job is to explain what these exact numbers mean for the user.
</mission>
{knowledge_block}"""

    data = f"""<numerology_data>
Subject: {name.upper()} | DOB: {dob_str} | System: {sys_name}

LOCKED CORE NUMBERS:
  Life Path   : {lp}{' ★ Master Number' if lp in [11, 22, 33] else ''} — {PERSONAL_YEAR_MEANINGS.get(lp, '')}
  Destiny     : {dest}{' ★ Master Number' if dest in [11, 22, 33] else ''}
  Soul Urge   : {soul}{' ★ Master Number' if soul in [11, 22, 33] else ''}
  Personality : {pers}{' ★ Master Number' if pers in [11, 22, 33] else ''}

LOCKED TIMING NUMBERS:
  Personal Year  ({user_now(tz).year}): {py} — {PERSONAL_YEAR_MEANINGS.get(py, '')}
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
        cross = f"""<astro_numerology_synthesis>
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
    else:
        cross = ""

    if user_q and user_q.strip():
        mission = f'<mission>Answer this question directly: "{user_q}"\nUse both numbers and (if provided) chart data as evidence.</mission>'
    else:
        mission = f"""<mission>
Deliver a complete report:
1. Life Path — Core purpose and life direction
2. Destiny — What they are meant to accomplish
3. Soul Urge — Inner desires and motivations
4. Personality — How the world sees them
5. Personal Year {py} Forecast — What this year brings
6. Active Pinnacle ({cp[2]}) + Active Challenge ({cp[3]}) — Theme and obstacle right now
{'7. Astro-Numerology Synthesis — Where both systems agree and diverge' if astro_dossier else ''}
</mission>"""

    return f"{instructions}\n\n{data}\n\n{cross}\n\n{mission}"


# ── Cycles tab prompt builder ────────────────────────────────────────────────

def build_cycles_prompt(name: str, dob_iso: str, lp: int,
                        py: int, pm: int, pd: int,
                        pinnacles: list[tuple],
                        system: str = "Western (Pythagorean)") -> str:
    is_vedic = "Vedic" in system or "Chaldean" in system
    r1, r2, r3, r4 = pinnacles
    y = int(dob_iso.split('-')[0])
    return f"""<CONSERVATIVE_VOICE>
Be conservative. When uncertain, prefer the safer of two interpretations and say
you're uncertain. NEVER fabricate dates or numerology claims outside the LOCKED
numbers Python has supplied.
</CONSERVATIVE_VOICE>
<instructions>
You are a Master Numerologist — {'Chaldean (Indian/Vedic)' if is_vedic else 'Pythagorean (Western)'} system.
All numbers below are PRE-COMPUTED and LOCKED. Do NOT recalculate.
</instructions>
<numerology_data>
Subject: {name} | DOB: {dob_iso} | Life Path: {lp}
Personal Year: {py} — {PERSONAL_YEAR_MEANINGS.get(py, '')}
Personal Month: {pm} | Personal Day: {pd}
Pinnacle 1 (Ages {r1[0]-y}–{r1[1]-y}): Number {r1[2]} | Challenge: {r1[3]}
Pinnacle 2 (Ages {r2[0]-y}–{r2[1]-y}): Number {r2[2]} | Challenge: {r2[3]}
Pinnacle 3 (Ages {r3[0]-y}–{r3[1]-y}): Number {r3[2]} | Challenge: {r3[3]}
Pinnacle 4 (Ages {r4[0]-y}+): Number {r4[2]} | Challenge: {r4[3]}
</numerology_data>
<mission>
Explain:
1. Current Personal Year energy and what it means for the next 12 months
2. Personal Month and Day energy — what to focus on right now
3. The currently active Pinnacle Number and its life theme
4. The currently active Challenge Number — what specific obstacle is the universe asking you to master?
5. How the Pinnacle and Challenge work together as a push-pull dynamic
</mission>"""
