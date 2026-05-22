# Deploy Guide — Step by Step

This guide is written for someone who has **never deployed an API before**.
Every step has exact text to paste. You'll go from "code on my laptop" to "live
API on the internet" in about 30 minutes.

You'll set up two things:

1. **The backend (FastAPI)** — runs on Render (free tier)
2. **(Later) The web frontend** — Next.js on Vercel/Cloudflare Pages

By the end of step 7 below, your backend will be live at a URL like
`https://your-app.onrender.com/docs` — and you can poke every endpoint from
your phone or any browser. That IS the "mobile-app shape" we've been
building toward.

---

## What you need

- A GitHub account (free)
- A Render account (free — sign up with GitHub at https://render.com)
- Your `GEMINI_API_KEY` (already in `.streamlit/secrets.toml`)
- Your Qdrant Cloud URL + API key (already in `qdrant_utils.py`)

That's it. No credit card needed for the free tier.

---

## Step 1 — Push your code to GitHub

If your code isn't already in a GitHub repo, do this once:

```bash
cd C:\Users\hinsh\Desktop\AIS
git init
git add .
git commit -m "Initial commit before Render deploy"
```

Then on GitHub, create a new private repo (e.g., `astro-suite`) and follow the
"push existing repository" instructions GitHub shows you. They'll look like:

```bash
git remote add origin https://github.com/YOUR-USERNAME/astro-suite.git
git branch -M main
git push -u origin main
```

If you already have it on GitHub: skip this step.

---

## Step 2 — Make sure `requirements.txt` is correct

We already added `fastapi`, `uvicorn`, `python-multipart`, `pydantic`,
`opencv-python-headless`, `mediapipe`, `numpy` to your `requirements.txt`.

Just verify it has all of these:

```
streamlit
pyswisseph
geopy
timezonefinder
streamlit-local-storage
google-generativeai
qdrant-client
sentence-transformers
weasyprint
jinja2
indic-transliteration
Pillow
fastapi
uvicorn[standard]
python-multipart
pydantic
opencv-python-headless
mediapipe
numpy
```

If yours has all these, you're good.

---

## Step 3 — Sign in to Render

1. Go to https://render.com
2. Click **Get Started** → sign in with GitHub
3. When prompted, give Render access to your `astro-suite` repo (or "all
   repos" — easier for one-time setup)

---

## Step 4 — Create the Web Service

On the Render dashboard:

1. Click **New +** (top right) → **Web Service**
2. Find your `astro-suite` repo and click **Connect**
3. Fill in the form:

| Field | Value |
|---|---|
| Name | `astro-suite-api` (or any name you like) |
| Region | Pick the closest one to you (e.g., **Singapore** for India) |
| Branch | `main` |
| Root Directory | leave blank |
| Runtime | **Python 3** |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn fastapi_main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | **Free** |

4. Don't click **Create Web Service** yet — first add env vars below.

---

## Step 5 — Add environment variables (your secret keys)

Scroll down to **Environment Variables**. Click **Add Environment Variable**
and add these. The first three are the same values in `.streamlit/secrets.toml`:

| Key | Value |
|---|---|
| `GEMINI_API_KEY` | (your Gemini API key — same one in `.streamlit/secrets.toml`) |
| `QDRANT_URL` | (your Qdrant Cloud URL — from `.streamlit/secrets.toml`) |
| `QDRANT_API_KEY` | (your Qdrant Cloud API key — from `.streamlit/secrets.toml`) |
| `TAROT_DRAW_SECRET` | any long random string (e.g. mash your keyboard) |
| `PYTHON_VERSION` | `3.11` |
| `WEB_CONCURRENCY` | `1` |

**Why these:**
- `GEMINI_API_KEY` is needed by the AI features. Without it, AI endpoints fail.
- `QDRANT_URL` + `QDRANT_API_KEY` power the knowledge lookup (RAG) behind every
  reading. On your laptop these come from `.streamlit/secrets.toml`, but Render
  has no such file — so they MUST be set here, or readings come back thin/empty.
- `TAROT_DRAW_SECRET` signs the tarot interactive-picker "draw tickets". On a
  hosted backend this MUST be a fixed value: Render runs/restarts multiple
  copies of your app, and they all need the same key to validate a ticket the
  user got from a different copy. Set it once; never change it. (Locally it's
  optional — the app invents a temporary one per run.)
- `PYTHON_VERSION` forces Render to use 3.11 (the version your code is tested on).
- `WEB_CONCURRENCY=1` limits to 1 worker process on the free tier — keeps memory under the 512 MB limit. (You can raise it on paid tiers.)

Now click **Create Web Service**.

---

## Step 6 — Wait for the first build (5-10 min)

Render will:
1. Pull your code from GitHub
2. Install all the packages in `requirements.txt`
3. Start your FastAPI app

You'll see scrolling logs. When it says **"Your service is live"** at the
top, you're done.

You'll get a URL like `https://astro-suite-api.onrender.com`.

---

## Step 7 — Test it (the fun part)

Open these URLs in your browser:

1. **Health check** — `https://astro-suite-api.onrender.com/health`
   - Should return: `{"status":"ok"}`

2. **API docs** — `https://astro-suite-api.onrender.com/docs`
   - This is the interactive Swagger UI. You can hit EVERY endpoint from
     here with forms. It's how you'll test new features as you build them.

3. **Try an endpoint**:
   - Open `/docs` → click `POST /api/v1/profiles/validate` → click "Try it out" →
     paste this in the request body:
     ```json
     {
       "name": "Test",
       "date": "1995-06-15",
       "time": "06:30",
       "place": "Delhi",
       "lat": 28.6,
       "lon": 77.2,
       "tz": "Asia/Kolkata",
       "gender": "M",
       "exact_time": true
     }
     ```
   - Click "Execute". You should see a 200 response.

If you got the 200 response — **your mobile-app backend is live.**

---

## Step 8 — About the "sleep" behaviour (free tier)

Render free apps **sleep after 15 minutes of inactivity**. First request
after sleeping takes ~1 minute (cold start), then it's fast.

For development, this is fine. When you have real users:

- **Option A** — keep the free tier and use a free "uptime monitor" like
  https://uptimerobot.com to ping your `/health` every 14 minutes (keeps
  it warm). Free. Works fine for low traffic.
- **Option B** — upgrade to Render Starter at $7/month (always on, faster CPU)
- **Option C** — move to your own VPS (Hetzner CX22 €4.5/mo). Same code,
  no Docker required, see VPS section at the end.

---

## Step 9 — Updating the code

After the first deploy, **every time you push to GitHub, Render auto-rebuilds**.

Workflow:

```bash
# 1. Edit code (or have Claude Code / Antigravity / Codex edit it)
# 2. Commit + push
git add .
git commit -m "describe what you changed"
git push

# 3. Render auto-detects the push and rebuilds (~5 min)
# 4. Live URL is updated automatically
```

You never have to manually deploy again.

---

## Step 10 — Point Streamlit at the backend (optional)

If you want your existing Streamlit prototype to call the new FastAPI
backend (so it acts like a "web client" instead of running everything
locally), do this:

1. In Streamlit Cloud → your app → **Settings** → **Secrets**
2. Add this line:
   ```
   BACKEND_URL = "https://astro-suite-api.onrender.com"
   ```
3. We'll wire this into the views in the next refactor phase.

For now, just leaving Streamlit running as-is is fine.

---

## When you build the mobile app (React Native / Expo) — the tarot flow

Future-you reading this: here's everything the mobile app needs. The backend is
already built for this — you do NOT touch Python. You just make HTTP calls.

### One-time setup
1. Deploy the backend on Render (Steps 1-7 above). Make sure Step 5's env vars
   are all set — **including `TAROT_DRAW_SECRET`** (any long random string).
   This is the moment that secret actually starts to matter (see Step 5's "why").
2. Your app calls the backend at its Render URL, e.g.
   `https://astro-suite-api.onrender.com`.

### The interactive tarot picker = exactly TWO calls
**Call 1 — shuffle a hidden deck:**
```
POST /tarot/draw-session
body: { "spread": "three", "include_reversed": false }
       # spread is one of: "three" | "yes_no" | "celtic"
returns: {
  "token": "<opaque string>",   # keep this; send it back in call 2
  "pick_count": 3,              # how many cards the user must tap (3 / 1 / 10)
  "deck_size": 78,             # render this many face-down cards
  "card_back_url": "https://.../tarotrear.png",  # the image for every card back
  "expires_in": 1800           # token is valid for 30 minutes
}
```
Now in the app: show `deck_size` face-down cards using `card_back_url`. Let the
user swipe and tap `pick_count` of them. Remember the **positions** they tapped
(0-based), in tap order. The app never needs to know what the cards are.

**Call 2 — reveal the picked cards + get the reading:**
```
POST /tarot/reveal
body: {
  "token": "<the token from call 1>",
  "picks": [4, 17, 40],         # the tapped positions, in tap order
  "question": "What's ahead at work?",
  "mode": "General Guidance"    # only used when spread == "three"
}
returns: {
  "cards":      ["Six of Swords", "Four of Cups", "Queen of Cups"],
  "states":     ["Upright", "Upright", "Reversed"],
  "positions":  ["Situation / Past", "Challenge / Present", "Advice / Future"],
  "image_urls": ["https://.../sixofswords.jpg", ...],  # the card front images
  "reading":    "### Overall Summary ... (the full AI reading, markdown)"
}
```
Now: flip the chosen cards to their `image_urls`, label them with `positions`,
rotate any "Reversed" card 180°, and render the `reading` markdown.

### Things to remember
- **Build the swipe/fan animation natively in React Native.** The Streamlit
  swipe picker (`features/tarot/picker/`) is only the web test-bed — the phone
  gets a proper native gesture UI. The backend contract above stays identical.
- The app only ever sends **tap positions**, never card names. The server is the
  source of truth — this is what keeps it cheat-proof.
- **Birth Card** is separate and unchanged: `POST /tarot/birth-card` with
  `{ "dob": "1995-06-15" }`. No picker, no token — it's deterministic from DOB.
- Explore every endpoint live at `https://your-app.onrender.com/docs` — you can
  try these exact calls from the browser before writing any app code.

---

## When you build the mobile app — the face reading flow

Even simpler than tarot: **one** call, **one** AI call behind it.

```
POST /face_reading/read
body: {
  "image_base64": "<the face photo, base64-encoded>",
  "use_kundli": false,            # true ONLY when reading the user's OWN face
  "profile": null                 # required only if use_kundli is true (the saved chart)
}
returns: {
  "metrics":  { "face_shape": {...}, "zones": {...}, "eyes": {...}, ... },  # measured geometry
  "phase_a":  { ...structured observations the AI confirmed... },
  "phase_b":  "## First Impression ... (the full reading, markdown)",
  "error":    ""
}
```

In the app: let the user pick/take a front-facing photo, base64-encode it, POST
it. Render `phase_b` (markdown). Optionally show the `metrics` as a little
"detected features" card. If `error` is non-empty (e.g. no face detected), show
it and ask for a clearer photo.

### Things to remember
- **`use_kundli` is opt-in.** Default `false` = a pure face reading that works
  for ANYONE's face. Set `true` + pass the saved `profile` only when the user is
  reading their own face and wants the face-vs-chart cross-reference.
- It's **lightweight**: no RAG/Qdrant, one Flash Lite call (~under ₹1). Same
  `GEMINI_API_KEY` (+ `QDRANT_*` for other features) from Step 5 — no new secret.
- Photo guidance for the UI: front-facing, even light, neutral expression, hair
  off the forehead, no glasses, face fills the frame.

---

## Local testing (you can do this anytime)

Run the FastAPI backend on your laptop:

```bash
cd C:\Users\hinsh\Desktop\AIS

# Set the Gemini key first (only first time)
set GEMINI_API_KEY=your_actual_key_here

# Start the backend
uvicorn fastapi_main:app --reload --port 8000
```

Then open `http://localhost:8000/docs` — same Swagger UI as on Render,
but running on your machine. Use this when developing — Render is for
"is it live on the internet" testing.

---

## Future — Supabase (database + auth)

When you're ready to add user accounts + persistent storage:

1. Sign up at https://supabase.com (free)
2. Create a project (free tier: 500 MB database, 1 GB file storage)
3. Add these env vars in Render:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
4. We'll write the database tables (`users`, `profiles`, `saved_kundlis`)
   when you ask for that phase

Don't add Supabase yet — for now, you're testing the backend shape.

---

## Future — VPS migration (when you grow)

When you cross ~1-2k active users and want to leave Render's free tier:

1. Buy a Hetzner CX22 VPS (~€4.50/mo, takes 5 min to set up)
2. Run the exact same FastAPI code on the VPS via `systemd` + `uvicorn`
3. Free Caddy reverse proxy gives you auto-HTTPS
4. (Optional) Self-host Supabase + Qdrant on the same VPS via docker-compose

No code changes needed. Just a different host. Total monthly cost: ~Rs 450
for the VPS, $0 for software.

I can write the VPS migration guide when you're ready — for now, focus
on getting the Render deploy working.

---

## Troubleshooting

**"Build failed: pip install failed"**
→ Open the build log on Render. Usually a typo in `requirements.txt`. Fix
   it, push to GitHub, Render rebuilds.

**"Application failed to start"**
→ Check the runtime log on Render. Often a missing env var. Verify
   `GEMINI_API_KEY` is set in **Environment Variables**, not as a
   build-time variable.

**"500 error on /api/v1/kundli/free"**
→ Open the runtime log on Render — the exact Python traceback is there.
   Copy it to Claude Code with "fix this error" and you'll get the fix.

**"It works on my laptop but not on Render"**
→ Usually a path issue. Most paths in our code are already relative to
   the repo root, so this should be rare. If it happens, the error in
   Render's log will tell you exactly what file is missing.

---

That's it. After step 7, you have a real mobile-app backend running on
free infrastructure. Everything else is iteration.
