"""features.consultation.service — RAG-book routing map + helpers.

Per-intent book selection. Timing questions pull from Brihat Parashara (dasha
rules), KP books (cusp/sub-lord timing precision), and the general Hindu
astrology textbooks. Other intents pull narrower sets.
"""

INTENT_RAG_BOOKS = {
    "TIMING":        ("bphs1.md", "bphs2.md", "kp3.md", "kp4.md", "htrh2.md"),
    "MARRIAGE":      ("kp4.md", "bphs2.md", "htrh1.md", "htrh2.md"),
    "CAREER_WEALTH": ("bphs1.md", "bphs2.md", "kp3.md", "htrh1.md"),
    "HEALTH":        ("bphs2.md", "htrh2.md", "kp6.md"),
    "CHILDREN":      ("bphs1.md", "htrh1.md", "kp4.md"),
    "SPIRITUAL":     ("bphs2.md", "htrh2.md"),
    "EDUCATION":     ("bphs1.md", "htrh1.md"),
    "FOREIGN":       ("bphs2.md", "htrh2.md", "kp3.md"),
    "GOCHARA":       ("htrh1.md", "htrh2.md", "bphs2.md"),
    "GENERAL":       ("htrh1.md", "htrh2.md"),
}
