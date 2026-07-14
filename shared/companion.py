"""shared.companion — the app's companion identity (the Sage).

ONE place for the companion's name + its one-time welcome text, so the chat header,
the push-notification sender, and the first-open intro all agree. The backend system
that powers the companion is still named `moon` (module / table / `/moon/*`) for
legacy reasons; the user only ever sees this name.

No per-user rename in v1 (deliberately simple). If we ever add "rename your
companion", store it per user and fall back to COMPANION_NAME here — nothing else
needs to change.
"""

COMPANION_NAME = "Sage"

# The one-time welcome/intro TEXT lives in features/moon/service.build_welcome()
# (it belongs to the companion's domain and needs the user's first name). This
# module is the single source of just the NAME.
