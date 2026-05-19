"""features.dashboard.prompts — greeting/tiles + Astro-Decide JSON prompts."""


def build_data_prompt(dossier: str, transits: str, user_name: str) -> str:
    return f"""<instructions>
Be conservative. When uncertain, prefer the safer of two interpretations. NEVER fabricate
planet positions, degrees, or dates — anchor every claim to a specific line in the
transits or dossier blocks below.

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
