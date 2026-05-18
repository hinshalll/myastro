# DEPLOY_WEB.md — Deploy the test frontend to Cloudflare Pages

The `web/` folder is the minimal test frontend. This guide deploys it to
**Cloudflare Pages** — free, fast, no build step, no credit card required.

By the end of this you'll have a URL like `myastro-web.pages.dev` that anyone
can open to use every Myastro feature.

---

## Why Cloudflare Pages (vs Vercel / Netlify)

- **Free forever** with no fine-print limits relevant at your scale
- **Fastest CDN** — sub-100ms anywhere in the world
- **Auto-deploy from GitHub** — push to main, site updates
- **Custom domains free** — point `myastro.app` here later, free SSL

---

## Step 1 — Sign up for Cloudflare

1. Open https://dash.cloudflare.com/sign-up
2. Sign up with the email you want to manage this from
3. Verify email if asked
4. Skip any "Add a domain" prompts — we don't need a domain yet

---

## Step 2 — Connect your GitHub repo

1. In the Cloudflare dashboard, look at the **left sidebar**:
   - Click **Compute (Workers)** → **Workers & Pages**
   - (Or directly: https://dash.cloudflare.com/?to=/:account/workers-and-pages)
2. Click the **Create application** button (top right)
3. Pick the **Pages** tab (next to "Workers")
4. Click **Connect to Git**
5. Click **Connect GitHub**
6. Authorise Cloudflare to access your GitHub:
   - Pick "Only select repositories"
   - Tick `hinshalll/myastro`
   - Click **Install & Authorize**
7. Back in Cloudflare, your `myastro` repo should now be listed → click it
8. Click **Begin setup**

---

## Step 3 — Configure the build

Fill in the form:

| Field | Value |
|---|---|
| Project name | `myastro-web` (becomes your URL: `myastro-web.pages.dev`) |
| Production branch | `main` |
| Framework preset | **None** (it's a static site, no build needed) |
| Build command | **leave blank** |
| Build output directory | `web` |
| Root directory | leave blank |

⚠ The key field is **Build output directory: `web`** — that tells Cloudflare
to serve files from the `web/` subfolder of your repo (not the whole repo).

Click **Save and Deploy**.

---

## Step 4 — Wait ~30 seconds

Cloudflare builds in seconds (no compilation needed). You'll see:

✅ Initialising build environment
✅ Deploying to Cloudflare
✅ Success! Your site is live at https://myastro-web.pages.dev

---

## Step 5 — Test it

Open your new URL. You should see the Myastro dashboard with all the feature
cards.

Click around:
1. **Profiles** → Add a profile (use the geocode button to auto-fill lat/lon/tz)
2. **Kundli** → Pick your profile → click Generate free kundli
3. **Chat with Astrologer** → Ask a question
4. Try other features

Everything should work because the frontend just calls your Render backend.

---

## Step 6 — Auto-deploy on every push

Already configured. Every `git push` you make to GitHub will trigger:
1. Render rebuilds the backend (~10 min)
2. Cloudflare rebuilds the frontend (~30 seconds)

You never manually deploy anything again. Edit code → push → both update.

---

## Step 7 — Custom domain (later, when you buy one)

When you own `myastro.app` (or whatever):

1. Cloudflare Pages → your project → **Custom domains** tab
2. Click **Set up a custom domain**
3. Enter your domain → follow the DNS instructions
4. SSL is automatic and free

The Cloudflare-generated `.pages.dev` URL keeps working — you just add the
prettier domain on top.

---

## Updating the API URL

If you ever change the backend URL (e.g., move to a VPS), edit ONE line in
`web/shared/config.js`:

```js
export const API_BASE = "https://your-new-backend.example.com";
```

Push to GitHub → Cloudflare auto-redeploys → frontend now talks to the new
backend. Backend doesn't need to know about the frontend change.

---

## Troubleshooting

**"CORS error" in browser console**
→ Backend's CORS middleware needs to allow your Cloudflare URL. Currently
   set to `["*"]` so this shouldn't happen. If it does, edit
   `api/main.py:CORSMiddleware` and add your domain.

**"Build output directory not found"**
→ Make sure you typed `web` (lowercase, no slash) in the Build output
   directory field.

**"404 on page reload of sub-pages"**
→ Static HTML sites don't have this issue. If you see it, the file probably
   has a typo in its path.

**"Backend says 503 / takes 60s on first request"**
→ Render's free tier was sleeping. UptimeRobot should be keeping it awake;
   verify your monitor is green at uptimerobot.com.

---

## Cost

₹0/month forever, at any traffic level you'll have pre-launch.

After ~100k page views/month, Cloudflare Pages still stays free. The Render
backend is the bottleneck at that scale (free tier limits, not Cloudflare).
