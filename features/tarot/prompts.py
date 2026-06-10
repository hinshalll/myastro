"""features.tarot.prompts — Gemini prompts for every tarot mode.

Each builder returns the full prompt string. The caller is responsible for
wrapping it with knowledge_context retrieved from Qdrant (tguide.md).
"""

from features.tarot.constants import CELTIC_CROSS_POSITIONS


_THREE_CARD_MODES = {
    "General Guidance": {
        "roles": ["Situation / Past", "Challenge / Present", "Advice / Future"],
        "instruction": "General life overview — where they are, what blocks them, best path forward.",
    },
    "Love & Dynamics": {
        "roles": ["Your Energy", "Their Energy", "The Connection / Outcome"],
        "instruction": "Read through the lens of a relationship or emotional dynamic.",
    },
    "Decision / Two Paths": {
        "roles": ["Path A", "Path B", "Hidden Factor / Recommendation"],
        "instruction": "Contrast the two paths. Card 3 is the deciding weight or hidden truth.",
    },
}


def three_card_roles(mode: str = "General Guidance") -> list[str]:
    """The three position labels for a given sub-mode (e.g. 'Path A')."""
    return _THREE_CARD_MODES.get(mode, _THREE_CARD_MODES["General Guidance"])["roles"]


_CONSERVATIVE_PREFIX = (
    "Be conservative. When uncertain between two readings, prefer the safer one "
    "and say you're uncertain. Never fabricate card meanings — if the passages "
    "don't cover a nuance, say so rather than guessing.\n\n"
)


def _knowledge_block(knowledge_context: str, fallback_rules: str) -> str:
    if knowledge_context:
        return (
            f"<KNOWLEDGE_CONTEXT>\n{knowledge_context}\n</KNOWLEDGE_CONTEXT>\n"
            "<RULES>\n"
            "Base your interpretation of each card entirely on the passages above. "
            "Do not invent meanings outside them.\n"
            "If a card is Reversed, interpret its energy as blocked, internalised, or delayed.\n"
            "If a specific nuance you'd like to add isn't in the passages, omit it "
            "rather than guessing — saying 'this isn't covered in the guide I was given' is acceptable.\n"
            "</RULES>"
        )
    return f"<RULES>\n{fallback_rules}\n</RULES>"


# ── Three-Card Spread ────────────────────────────────────────────────────────

def build_three_card_prompt(question: str, cards: list[str], states: list[str],
                             mode: str = "General Guidance",
                             knowledge_context: str = "") -> str:
    cfg = _THREE_CARD_MODES.get(mode, _THREE_CARD_MODES["General Guidance"])
    roles = cfg["roles"]
    cards_str = "\n".join(
        f"  {i+1}. {roles[i]}: {cards[i]} ({states[i]})" for i in range(len(cards))
    )
    kb = _knowledge_block(
        knowledge_context,
        "Base your interpretation on established tarot archetypes. "
        "If a card is Reversed, interpret its energy as blocked or delayed.",
    )
    return f"""{_CONSERVATIVE_PREFIX}<mission>
You are an expert, intuitive Tarot Reader. Python has cryptographically drawn the following spread:
{cards_str}
Question: "{question}" | Spread: {mode} | Focus: {cfg['instruction']}
</mission>

{kb}

<FORMAT>
- Overall Summary (2-3 sentences)
- Card-by-Card (each card's meaning in its specific spread position)
- Combined Message (how the three interact)
- Practical Action Step
- One-Line Takeaway
</FORMAT>"""


# ── Yes / No ─────────────────────────────────────────────────────────────────

def build_yes_no_prompt(question: str, card: str, state: str,
                        knowledge_context: str = "") -> str:
    kb = _knowledge_block(
        knowledge_context,
        "Upright cards generally lean Yes; Reversed lean No — factor in the card's archetype.",
    )
    if knowledge_context:
        kb = kb.replace(
            "Base your interpretation of each card entirely on the passages above. "
            "Do not invent meanings outside them.\n"
            "If a card is Reversed, interpret its energy as blocked, internalised, or delayed.",
            "Read the core energy of this card from the passages above.\n"
            "Upright cards generally lean Yes; Reversed lean No — but factor in the archetype from the passages.",
        )
    return f"""{_CONSERVATIVE_PREFIX}<mission>
You are an expert Tarot Reader — Yes/No Oracle mode.
Question: "{question}" | Card drawn: {card} ({state})
</mission>
{kb}
<FORMAT>
1. Clear verdict: YES / LIKELY YES / UNCLEAR / LIKELY NO / NO
2. Why — the card's specific energy in this context (2-3 sentences from the guide)
3. Condition — what must happen (or be avoided)
4. One-Line Takeaway
</FORMAT>"""


# ── Celtic Cross ─────────────────────────────────────────────────────────────

def build_celtic_cross_prompt(question: str, cards: list[str], states: list[str],
                               knowledge_context: str = "") -> str:
    cards_str = "\n".join(
        f"  {CELTIC_CROSS_POSITIONS[i]}: {cards[i]} ({states[i]})"
        for i in range(10)
    )
    kb = (
        f"<KNOWLEDGE_CONTEXT>\n{knowledge_context}\n</KNOWLEDGE_CONTEXT>\n"
        "<RULES>\n"
        "Synthesize these 10 cards strictly based on the meanings in the passages above. "
        "Look for patterns (suits clustering, Major Arcana count).\n"
        "</RULES>"
    ) if knowledge_context else ""
    return f"""{_CONSERVATIVE_PREFIX}<mission>
You are an expert Tarot Reader — Celtic Cross spread.
Question: "{question}"
Ten-card spread:
{cards_str}
</mission>
{kb}
<FORMAT>
- Core Message (Cards 1+2 tension)
- Position-by-position reading
- Patterns & Themes observed
- Overall Narrative & Practical Guidance
- Final One-Line Takeaway
</FORMAT>"""


# ── Birth Card ───────────────────────────────────────────────────────────────

def build_birth_card_prompt(card: str, dob: str, knowledge_context: str = "") -> str:
    kb = (
        f"<KNOWLEDGE_CONTEXT>\n{knowledge_context}\n</KNOWLEDGE_CONTEXT>\n"
        "<RULES>\n"
        "Interpret this card as a deep, lifelong energy based strictly on the passages above.\n"
        "</RULES>"
    ) if knowledge_context else ""
    return f"""{_CONSERVATIVE_PREFIX}<mission>
You are an expert Tarot Reader — Tarot Birth Card reading.
Date of Birth: {dob} | Tarot Birth Card: {card}
</mission>
{kb}
<FORMAT>
1. Core symbolism of this card (from the guide)
2. How this archetype shows up as a lifelong theme
3. Core strengths & Core challenges
4. Karmic lesson & Personal mantra
</FORMAT>"""


# ── Daily Card (used by Dashboard) ───────────────────────────────────────────

def build_daily_card_prompt(card: str, state: str, knowledge_context: str = "") -> str:
    kb = (
        f"<KNOWLEDGE_CONTEXT>\n{knowledge_context}\n</KNOWLEDGE_CONTEXT>\n"
        "<RULES>\n"
        "Extract the practical daily advice for this exact card and state from the passages above only.\n"
        "</RULES>"
    ) if knowledge_context else ""
    return f"""{_CONSERVATIVE_PREFIX}<mission>
You are an expert Tarot Reader — Daily Guidance reading. Today's card: {card} ({state})
</mission>
{kb}"""
