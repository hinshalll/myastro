"""
shared.ai/kundli_content.py
===========================

AI-personalised prose for kundli (free + premium tiers).

Architecture — FOCUSED multi-call for hallucination-free accuracy:
    Free    → 1 call  (general life topics, ~90 s)
    Premium → 2 calls (general + per-element-batch, ~4-6 min total)

The per-element batch covers 12 houses + 9 planets + 3 years (current +
next 2) in a single focused call, with STRICT per-class hints in the
prompt so each paragraph is grounded ONLY in its specific chart facts.

Free-tier rate-limit handling:
    Gemini 3.1 Flash Lite Preview free tier ≈ 30 RPM. With
    RESPECT_FREE_TIER_LIMITS=True the tool sleeps FREE_TIER_DELAY_SECONDS=4
    between calls to stay safely under that.

    Flip RESPECT_FREE_TIER_LIMITS=False when you move to a paid API — waits
    skip; premium kundli finishes faster.

Cost (gemini-3.1-flash-lite, $0.10/M in, $0.40/M out):
    Free  : ~0.5K input + 3K output    ≈ ₹0.10 / kundli
    Premium: ~1K input + 12K output    ≈ ₹0.40-0.55 / kundli

Both comfortably within the user-stated budget caps (₹1 free, ₹5 premium).

Mobile-app strategy (per user direction):
    Premium kundli — takes time, user warned at click ("delivered shortly")
    Free kundli — when split into mobile API, replace AI calls with bigger
                  static-personalised content so it generates instantly.

Public API:
    generate_kundli_content(chart, tier='free', language='en') -> dict
    is_available() -> bool
"""

from __future__ import annotations

import json
import re
import time
from typing import Literal

from shared.ai.gemini_client import init_gemini, get_ai_model_for_json
from shared.ai import config


# ═════════════════════════════════════════════════════════════════════════
# TOGGLE — set False once you move to paid API (no rate-limit waits needed)
# ═════════════════════════════════════════════════════════════════════════
RESPECT_FREE_TIER_LIMITS = True
FREE_TIER_DELAY_SECONDS  = 4   # 4s buffer for Gemini 3.1 Flash Lite free tier
# ═════════════════════════════════════════════════════════════════════════


# ─── Topic groups ─────────────────────────────────────────────────────────

FREE_TOPICS = [
    "personality", "career", "health", "wealth",
    "marriage", "education", "family", "spirituality",
]

GENERAL_PREMIUM = FREE_TOPICS + [
    "children", "love_life",
    "manglik_analysis", "sade_sati_narrative", "kaal_sarp_narrative",
    "major_dasha", "next_dasha",
    "lucky_factors", "remedies_narrative",
]

HOUSE_TOPICS  = [f"house_{h}"  for h in range(1, 13)]
PLANET_TOPICS = [f"planet_{p}" for p in (
    "Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu",
)]

WORD_COUNT = {"free": 150, "premium": 200}


# ─── System rules — strict accuracy contract ──────────────────────────────

_SYSTEM_RULES = """\
Be conservative. When uncertain between two readings, prefer the safer one and
say you're uncertain. NEVER fabricate dates, degrees, planet positions,
nakshatras, or divisional placements — every such fact must come from the JSON
below.

You are an experienced Vedic astrologer writing a personalised birth-chart
report. Voice: warm, wise, classical-but-accessible. Each topic is flowing
prose (no bullets, no markdown, no headings inside prose).

ZERO-HALLUCINATION RULES (CRITICAL):
1. Use ONLY the chart facts in the JSON. NEVER invent a planetary position,
   sign, house, nakshatra, dasha, yoga, or dosha. If a fact isn't in the JSON,
   do not state it.
2. When you reference a position, the exact sign/house/nakshatra must match
   the JSON byte-for-byte.
3. For house_N: reference ONLY facts.houses[N] (its sign, lord, lord
   placement, occupants). Build the prose around those exact facts.
4. For planet_X: reference ONLY facts.planets[X] (sign, house, degree,
   nakshatra, dignity). Discuss what X signifies for this native given that.
5. For year_YYYY: reference ONLY facts.year_dashas[YYYY] (active Mahadasha +
   Antardasha lord for that year). Frame the year through those lords.
6. If a topic doesn't apply (no Manglik when not present, no Kaal Sarp),
   say so and explain the favourable absence — don't force a negative tone.

STYLE:
• Speak directly ("you", "your") — never third-person.
• Target word count per topic: ~150 (free) or ~200 (premium). Hard ceiling 280.
• Output STRICTLY valid JSON: {"topic_key": "paragraph", ...}. No backticks,
  no prose outside the JSON.
"""


# ─── Facts extraction (compact + per-topic-class precision) ───────────────

def _extract_facts(chart, years_ahead: int = 3) -> dict:
    from datetime import datetime
    from zoneinfo import ZoneInfo
    p = chart.planets

    def planet_summary(name: str) -> dict:
        if name not in p: return {}
        pp = p[name]
        s = {
            "sign": pp.sign, "house": pp.house, "deg": round(pp.longitude % 30, 1),
            "nakshatra": pp.nakshatra, "pada": pp.pada,
        }
        if pp.dignity:       s["dignity"]    = pp.dignity
        if pp.is_retrograde: s["retrograde"] = True
        if pp.is_combust:    s["combust"]    = True
        return s

    houses_data: dict[int, dict] = {}
    for h in range(1, 13):
        hi = chart.houses.get(h)
        if not hi: continue
        lord_pp = p.get(hi.sign_lord)
        houses_data[h] = {
            "sign":          hi.sign,
            "lord":          hi.sign_lord,
            "lord_in_house": lord_pp.house if lord_pp else None,
            "lord_in_sign":  lord_pp.sign  if lord_pp else None,
            "lord_dignity":  lord_pp.dignity if lord_pp and lord_pp.dignity else None,
            "occupants":     list(hi.occupants),
        }

    active_doshas = [
        {"name": d.name, "severity": d.severity, "cause": d.cause[:200]}
        for d in (chart.doshas or []) if d.present
    ]
    active_yogas = [
        {"name": y.name, "category": y.category, "planets": y.planets_involved}
        for y in (chart.yogas or [])
    ][:10]

    tz = ZoneInfo(chart.birth_data.tz)
    now = datetime.now(tz)
    md_lord = ad_lord = md_end = ad_end = None
    year_dashas: dict[int, dict] = {}
    vim = (chart.dashas or {}).get("Vimshottari")
    if vim and vim.periods:
        for md in vim.periods:
            if md.start <= now <= md.end:
                md_lord, md_end = md.lord, md.end.strftime("%b %Y")
                for ad in md.children:
                    if ad.start <= now <= ad.end:
                        ad_lord, ad_end = ad.lord, ad.end.strftime("%b %Y")
                        break
                break
        for y_off in range(years_ahead):
            y = now.year + y_off
            from datetime import datetime as _dt
            jan1 = _dt(y, 1, 1, tzinfo=tz)
            for md in vim.periods:
                if md.start <= jan1 <= md.end:
                    ad_match = None
                    for ad in md.children:
                        if ad.start <= jan1 <= ad.end:
                            ad_match = ad.lord; break
                    year_dashas[y] = {
                        "mahadasha":  md.lord,
                        "antardasha": ad_match,
                        "md_start":   md.start.strftime("%d %b %Y"),
                        "md_end":     md.end.strftime("%d %b %Y"),
                    }
                    break

    return {
        "name":             chart.birth_data.name,
        "gender":           chart.birth_data.gender,
        "birth_date":       chart.birth_data.date.isoformat(),
        "current_year":     now.year,
        "lagna":            chart.lagna.sign,
        "lagna_lord":       chart.lagna.lord,
        "lagna_nakshatra":  chart.lagna.nakshatra,
        "moon_sign":        p["Moon"].sign,
        "moon_nakshatra":   p["Moon"].nakshatra,
        "sun_sign":         p["Sun"].sign,
        "atmakaraka":       chart.chara_karakas.atmakaraka,
        "planets":          {n: planet_summary(n) for n in
            ("Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu")},
        "houses":           houses_data,
        "functional":       {
            "yogakarakas": chart.functional.yogakarakas,
            "benefics":    chart.functional.benefics,
            "malefics":    chart.functional.malefics,
        },
        "active_yogas":     active_yogas,
        "active_doshas":    active_doshas,
        "current_dasha":    {
            "mahadasha":         md_lord,
            "mahadasha_ends":    md_end,
            "antardasha":        ad_lord,
            "antardasha_ends":   ad_end,
        },
        "year_dashas":      year_dashas,
    }


# ─── Single-call helper ───────────────────────────────────────────────────

def _one_call(facts: dict, topics: list[str], word_count: int,
              focus_hint: str, language: str,
              model_chain: list[str]) -> dict:
    """One focused Gemini call. Returns {topic_key: paragraph}. {} on failure."""
    lang_note = ""
    if language and language != "en":
        lang_map = {"hi":"Hindi","ta":"Tamil","te":"Telugu","mr":"Marathi",
                    "bn":"Bengali","gu":"Gujarati"}
        lang_note = f"\nLanguage: Write the prose in {lang_map.get(language,'English')}."

    facts_json = json.dumps(facts, indent=2, ensure_ascii=False)
    topics_list = "\n".join(f"  - {t}" for t in topics)
    user_prompt = f"""\
Birth chart facts:
{facts_json}
{lang_note}

Focus for this call:
{focus_hint}

Generate personalised paragraphs (~{word_count} words each, hard max 280) for:
{topics_list}

Return ONE JSON object {{"topic_key": "paragraph", ...}} with exactly these keys.
"""

    for mname in model_chain:
        try:
            model = get_ai_model_for_json(
                model_name=mname,
                system_instruction=_SYSTEM_RULES,
                temperature=0.7,
            )
            resp = model.generate_content(user_prompt)
            raw = resp.text or ""
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            payload = m.group(0) if m else raw
            data = json.loads(payload)
            if isinstance(data, dict) and len(data) >= len(topics) // 2:
                return data
        except Exception:
            continue
    return {}


# ─── Free-tier rate-limit guard ───────────────────────────────────────────

def _maybe_wait():
    """Sleep between calls to stay under Gemini free-tier RPM. No-op on paid."""
    if RESPECT_FREE_TIER_LIMITS:
        time.sleep(FREE_TIER_DELAY_SECONDS)


# ─── Public API ───────────────────────────────────────────────────────────

def _read_gemini_key() -> str | None:
    """Read GEMINI_API_KEY from env first (FastAPI / mobile), then
    .streamlit/secrets.toml (Streamlit Cloud / local dev)."""
    import os
    v = os.environ.get("GEMINI_API_KEY")
    if v:
        return v
    try:
        import tomllib
        from pathlib import Path
        # repo root is 2 levels up from features/kundli/content.py
        sp = Path(__file__).resolve().parents[2] / ".streamlit" / "secrets.toml"
        if not sp.exists():
            return None
        with open(sp, "rb") as f:
            data = tomllib.load(f)
        return data.get("GEMINI_API_KEY")
    except Exception:
        return None


def is_available() -> bool:
    return bool(_read_gemini_key())


def _configure_api():
    """Initialise the shared Gemini client. Safe to call repeatedly — only
    the first call actually configures it (subsequent calls re-init with
    the same key, which is a no-op cost-wise)."""
    key = _read_gemini_key()
    if not key:
        raise RuntimeError("GEMINI_API_KEY not found (env var or .streamlit/secrets.toml)")
    init_gemini(key)


def generate_kundli_content(
    chart,
    *,
    tier: Literal["free", "premium"] = "free",
    language: str = "en",
    model_name: str = config.model_for("json"),
) -> dict:
    """Multi-call orchestrator with focused per-class accuracy.

    Free   → 1 call  (general life topics, ~90s)
    Premium → 2 calls (general + per-element-batch, ~4-6 min total)

    Per-element-batch (Call 2) covers 12 houses + 9 planets + 3 years
    in a SINGLE focused call, with strict per-topic-class hints so each
    paragraph remains grounded in its specific chart facts.

    Between calls, sleeps FREE_TIER_DELAY_SECONDS when
    RESPECT_FREE_TIER_LIMITS=True. Flip to False on paid API.
    """
    if not is_available():
        return {}
    try:
        _configure_api()
    except Exception:
        return {}

    facts = _extract_facts(chart, years_ahead=3)
    word_count = WORD_COUNT[tier]
    # Use the configured 'json' ladder (Gemini → DeepSeek), honouring any override.
    model_chain = config.usable_models(
        [model_name] + [m for m in config.ladder_for("json") if m != model_name]
    )
    out: dict = {}

    # ── CALL 1 — General life topics (always runs) ──────────────────────
    out.update(_one_call(
        facts=facts,
        topics=FREE_TOPICS if tier == "free" else GENERAL_PREMIUM,
        word_count=word_count,
        focus_hint=(
            "General life-area topics. For each topic, anchor the reading in "
            "facts.lagna, facts.planets, facts.active_yogas, facts.active_doshas, "
            "and facts.current_dasha. For Manglik / Sade Sati / Kaal Sarp, "
            "check facts.active_doshas first — explain favourable absence if not present."
        ),
        language=language,
        model_chain=model_chain,
    ))

    if tier != "premium":
        return out

    # ── CALL 2 — Per-element batch (houses + planets + years) ───────────
    # Strict per-class hints inside the prompt ensure the model doesn't drift
    # between topic types. One call for cost + speed; tight rules for accuracy.
    _maybe_wait()
    year_keys = [f"year_{y}" for y in sorted(facts.get("year_dashas", {}).keys())]
    per_element_topics = HOUSE_TOPICS + PLANET_TOPICS + year_keys
    out.update(_one_call(
        facts=facts,
        topics=per_element_topics,
        word_count=word_count,
        focus_hint=(
            "PER-ELEMENT batch — three topic classes in this call. Apply the "
            "right rule per topic class:\n"
            "  • house_N (N=1..12) — read ONLY facts.houses[N]. Reference its "
            "    sign, lord, where the lord is placed (lord_in_house, "
            "    lord_in_sign), any occupants, and lord_dignity. Build the "
            "    prose around those exact facts; never reference other houses.\n"
            "  • planet_X — read ONLY facts.planets[X]. Reference its exact "
            "    sign, house, degree, nakshatra, dignity, retrograde/combust. "
            "    Then discuss what X classically signifies given THIS exact "
            "    placement for THIS native; never confuse two planets' positions.\n"
            "  • year_YYYY — read ONLY facts.year_dashas[YYYY] (mahadasha + "
            "    antardasha lord for that year). Frame the year through THOSE "
            "    specific lords' significations; never invent dates or lords."
        ),
        language=language,
        model_chain=model_chain,
    ))

    return out
