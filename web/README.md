# web/ — Minimal test frontend for the Myastro backend

> **This is the stopgap UI** built while the real Next.js website is being
> designed. It exists so you can actually USE every backend feature without
> sending raw JSON through Swagger UI. Plain HTML + Tailwind via CDN + Vanilla
> JS, zero build step, deployable to Cloudflare Pages free.

## Structure

```
web/
├── index.html              ← Dashboard (feature grid)
├── profiles.html           ← Add / edit / delete profiles (localStorage)
├── kundli.html             ← Free + premium kundli
├── palm.html               ← Palm reading (photo upload)
├── tarot.html              ← Tarot draw
├── numerology.html         ← Numerology profile
├── horoscope.html          ← Vedic horoscope
├── consultation.html       ← Chat with astrologer
├── oracle/
│   ├── index.html          ← Oracle hub (6 feature cards)
│   ├── deep_analysis.html  ← Full Life Reading
│   ├── matchmaking.html    ← Compatibility Match
│   ├── marriage.html       ← Destiny Marriage Matrix
│   ├── gochara.html        ← Live Transits
│   ├── compare.html        ← Compare Profiles
│   └── prashna.html        ← Horary
└── shared/
    ├── config.js           ← API_BASE URL — edit this if backend URL changes
    ├── api.js              ← Every API endpoint as a JS function
    ├── state.js            ← Profile management via localStorage
    └── components.js       ← Reusable UI (nav, profile picker, markdown render)
```

## How a page works (mental model)

Every feature page does the same 4 things:
1. Import what it needs from `shared/` (api functions, helpers)
2. Render the nav + profile picker
3. On button click → call the backend → set loading → render result
4. Catch errors → render error card

Open any page like `tarot.html` and look at the `<script type="module">` at
the bottom — that's the whole feature in ~30 lines.

## How to add a NEW feature page

1. Add the API call in `shared/api.js` (one function, ~5 lines)
2. Copy an existing page (e.g. `tarot.html`) and adapt the form fields +
   the result formatting
3. Add a card to `index.html`
4. Add the page to the nav links in `shared/components.js` if you want it
   in the top nav

That's it. No build step. Save → reload browser.

## How to point at a different backend

Edit ONE line in `shared/config.js`:

```js
export const API_BASE = "https://your-new-backend.example.com";
```

For local dev (when running `uvicorn api.main:app --reload` on your laptop):

```js
export const API_BASE = "http://localhost:8000";
```

## Running locally

This is a static site — open `index.html` directly in a browser, OR run
any static file server:

```bash
# Python (built into your laptop)
python -m http.server 8080 --directory web

# Then open http://localhost:8080
```

⚠ Modern browsers block `import` from `file://` URLs — you must serve
the files via `http://` (use the Python command above).

## Deploying to Cloudflare Pages

See `../DEPLOY_WEB.md` in the repo root for step-by-step instructions.

## Conventions

- **One file per feature** — easy for AI assistants to navigate
- **No build step** — Tailwind via CDN, marked.js via CDN, ES modules
- **Vanilla JS** — no React, no framework. AI tools edit plain DOM.
- **localStorage for profiles** — until Supabase is wired in
- **All API calls go through `shared/api.js`** — central audit point

## When to throw this away

When the real Next.js website (with Cloud Design / Google Stitch) is
ready, delete the entire `web/` folder. The backend stays untouched —
only the UI swaps.
