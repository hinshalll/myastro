"""features.dashboard.prompts — greeting/tiles + Astro-Decide JSON prompts."""


def build_data_prompt(dossier: str, transits: str, user_name: str) -> str:
    return f"""<instructions>
Be conservative and accurate. NEVER fabricate planet positions, degrees, or dates: anchor every
claim to a specific line in the transits or dossier blocks below. When uncertain, prefer the safer
interpretation.

Write {user_name}'s daily reading in the voice of a sharp, warm friend who actually knows astrology:
self-aware and lightly witty, never cheesy, never mean, never mystical filler. Voice rules:
- Ground the day in the REAL transit and say it in plain, human English (e.g. "Moon's in Capricorn,
  so ...") — the realness is what makes it land and feel accurate.
- Warm with a light, knowing edge. A small wink is good; cruelty, sarcasm at the reader's expense,
  and fear are not.
- HEDGE personal-state claims ("a low mood might drift in", "you may feel pulled toward home"),
  never hard declarations about how they feel — this keeps it both true and kind.
- Humor targets everyday behaviour (overthinking, dodging a text), NEVER religion, deities, caste,
  body, or anything sensitive.
- No em dashes. No Sanskrit/jargon on the surface. No "cosmic / mystic / aura"-type filler words.

Give exactly one short, personalised paragraph (2 sentences max) on today's most important planetary
movement for {user_name}. Do NOT start with "Hello". Then four short punchy phrases (max 5 words
each) and one summary line.
RESPOND ONLY IN VALID JSON FORMAT. NO MARKDOWN. NO EXTRA TEXT.
{{
  "GREETING": "The 2-sentence daily reading, in the voice above.",
  "ENERGY": "High/Low/Erratic/Focused",
  "FOCUS": "What to lean into today",
  "CAUTION": "What to gently watch for today",
  "WINDOW": "Best time of day",
  "SUMMARY": "One short, screenshot-worthy line summing up the vibe."
}}
</instructions>

<data>
{transits}

{dossier}
</data>"""


def build_decide_prompt(dossier: str, transits: str, question: str,
                        py_verdict: str, py_advice: str) -> str:
    """Python has already executed Tara Bala. The AI only formats + links to the question."""
    return f"""<instructions>
Be conservative. Do not invent a verdict — the Python verdict is final. Anchor your
WHY sentence to a specific transit line in the data block.

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
