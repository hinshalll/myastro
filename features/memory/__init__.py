"""features.memory — THE MEMORY: the app's per-user brain (the headline moat).

Distils durable facts from journal entries + chat into `memory_facts`, lets the
user own them (view/edit/delete), and assembles a compact recall context for the
companion and the personalized forecast. No vector DB — a single user's facts are
few, so they are loaded and ranked directly (salience + recency).
"""
