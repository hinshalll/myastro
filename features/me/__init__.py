"""features.me — the authenticated user's stateful core (the data-layer foundation).

Profiles, check-ins (Pattern Engine input), the Mirror journal, and streaks —
all keyed off the Supabase-authenticated user, with Postgres RLS enforcing
owner-only access. See README.md.
"""
