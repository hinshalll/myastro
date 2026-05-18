"""
pdf_engine/generate_theme_assets.py — one-shot AI image generator.

Generates the 12 deity images (6 themes × cover + watermark) and saves
them to pdf_engine/static/themes/<theme>/cover.png and watermark.png.

Run ONCE (or whenever you want to refresh the art). The premium kundli
PDF will automatically pick the PNGs up — no template changes needed.
Falls back gracefully to SVG art if any image fails to generate.

Usage
-----
    python -m pdf_engine.generate_theme_assets [--theme NAME] [--force]
    python -m pdf_engine.generate_theme_assets --theme ganesha
    python -m pdf_engine.generate_theme_assets --force  # regenerate all

Reads GEMINI_API_KEY from .streamlit/secrets.toml.

Models tried in order (free → cheapest paid):
    1. gemini-2.5-flash-image          (free tier)
    2. gemini-3.1-flash-image-preview  (free tier, newer)
    3. imagen-4.0-fast-generate-001    (paid)

If all return 429 (quota), the script reports per-theme and exits without
clobbering existing PNGs.
"""

from __future__ import annotations

import argparse
import base64
import sys
import time
import tomllib
from pathlib import Path


PKG_ROOT  = Path(__file__).parent
ASSETS_DIR = PKG_ROOT / "static" / "themes"
SECRETS    = PKG_ROOT.parent / ".streamlit" / "secrets.toml"


# ─── Carefully-crafted prompts per theme ──────────────────────────────────
# Each theme has two prompts: a "cover" art (centerpiece) and a "watermark"
# variant (lighter, more transparent, simplified for behind-text use).
#
# Constraints baked into every prompt:
#   - cute & pretty but NOT cartoonish
#   - aesthetic and premium, traditional miniature painting style
#   - NOT bold or in-your-face — subtle and elegant
#   - transparent / soft-background friendly for layering on parchment
#   - square 1:1 aspect ratio
# ───────────────────────────────────────────────────────────────────────────

PROMPTS: dict[str, dict[str, str]] = {
    "classic_vedic": {
        "cover": (
            "An elegant decorative mandala in traditional Indian Vedic style. "
            "Centered Om (ॐ) symbol in deep saffron-brown calligraphy, "
            "surrounded by a 16-petal lotus mandala in soft gold leaf, "
            "outer ring with 24 small sun-ray ornaments. Cream parchment "
            "background with very subtle aged texture. Color palette: "
            "saffron, deep maroon, antique gold, ivory. Style: traditional "
            "Indian miniature painting with hand-painted detail, soft pastels, "
            "delicate gold-leaf accents. Very elegant, premium, refined — "
            "NOT busy. Subtle aura/glow around the central Om. Square 1:1."
        ),
        "watermark": (
            "Same Om-and-lotus mandala as the cover but VERY faded, "
            "ghostly, at about 12% opacity, on a fully transparent background. "
            "Single soft gold/saffron tone only, no shadows. Designed to sit "
            "behind page text as a delicate watermark — should be barely "
            "visible but unmistakable on close inspection. Square 1:1."
        ),
    },
    "ganesha": {
        "cover": (
            "A cute, gentle baby Ganesha (Bal Ganesha) sitting cross-legged "
            "on a fully-open lotus throne. Round elephant head, small curled "
            "trunk pointing left holding a sweet (modak), large gentle ears, "
            "tiny gold crown with one feather, third-eye tilak. Plump small "
            "body wrapped in a soft yellow dhoti, simple gold bangles and "
            "necklace. Eyes closed in meditation. Soft halo glow behind the "
            "head. Traditional Indian miniature painting style — hand-drawn "
            "linework with delicate watercolor washes. Color palette: warm "
            "yellows, soft pinks, mint green, antique gold, cream background. "
            "Style: PRETTY and CUTE but NOT cartoonish; refined and serene. "
            "Subtle decorative flourishes around — small floating flowers. "
            "Square 1:1, transparent off-white background."
        ),
        "watermark": (
            "Same baby Ganesha figure as cover but reduced to a delicate "
            "outline / silhouette, about 12% opacity, gold-saffron monochrome, "
            "on a fully transparent background. Soft and ghostly, sized to sit "
            "behind page text without competing with it. Square 1:1."
        ),
    },
    "krishna": {
        "cover": (
            "A cute baby Krishna (Bal Krishna / Laddu Gopal) sitting cross-"
            "legged playing a small bamboo flute. Soft blue skin, curly hair "
            "with one prominent peacock feather, small gold crown, gentle "
            "closed-eye smile. Wearing a yellow silk dhoti with gold trim, "
            "small jewelry. Decorative peacock feathers fanning out behind "
            "him. Soft starry sky in midnight blue and indigo with delicate "
            "gold star accents around. Traditional Indian miniature style, "
            "watercolor washes with linework. Color palette: midnight blue, "
            "soft sky blue, antique gold, ivory. PRETTY and CUTE but elegant "
            "and refined, not cartoonish. Subtle halo behind. Square 1:1."
        ),
        "watermark": (
            "A single delicate peacock feather + small flute crossed, "
            "single-tone gold-blue, about 12% opacity, transparent background, "
            "soft brush-stroke style. Hand-drawn miniature line art. Square 1:1."
        ),
    },
    "shiva": {
        "cover": (
            "A serene meditative Shiva symbol composition (NOT a face): a tall "
            "ornate trishul (trident) at center with a small damaru (hourglass "
            "drum) at its midpoint, a delicate cobra coiled at the base of the "
            "shaft, a fine crescent moon at the top, small rudraksha-bead "
            "rosary hanging from the crossbar, distant Himalayan mountain "
            "silhouette in the background. Color palette: indigo, deep "
            "midnight blue, silver, soft white-grey with hints of saffron. "
            "Traditional Indian miniature style, hand-painted with refined "
            "linework. Very elegant, calm, premium, NOT bold or aggressive. "
            "Subtle aura of light around the trishul. Square 1:1."
        ),
        "watermark": (
            "Same trishul + crescent + damaru composition as cover but "
            "ghostly faint at 12% opacity, single-tone indigo-silver, on a "
            "transparent background, hand-drawn line-art quality. Square 1:1."
        ),
    },
    "durga": {
        "cover": (
            "A decorative composition of an ornate trishul at center rising "
            "from an 8-petal lotus, framed by 8 smaller trishuls radiating "
            "outward, a small lion paw print at the base. NO face, NO figure "
            "— pure decorative geometric mandala. Color palette: deep crimson "
            "red, royal saffron orange, antique gold, ivory. Traditional "
            "Indian miniature style with hand-painted watercolor washes, "
            "delicate gold-leaf details. Strong but refined, premium, elegant. "
            "Subtle aura/glow at the center. Square 1:1."
        ),
        "watermark": (
            "Same trishul-and-lotus mandala but ghostly at 12% opacity, "
            "single tone of soft crimson/gold, transparent background, "
            "delicate line art only. Square 1:1."
        ),
    },
    "lakshmi": {
        "cover": (
            "An open many-layered pink lotus in full bloom, with golden coins "
            "softly cascading down each side, two small stylized elephants "
            "(silhouettes, no faces) at the base flanking a tiny golden kalash "
            "(sacred water pot) overflowing. Subtle sun-ray halo behind the "
            "lotus. Color palette: rose-pink, antique gold, ivory, soft "
            "champagne. Traditional Indian miniature painting style — gentle "
            "watercolor washes, very refined gold-leaf detail. Beautiful, "
            "abundant feeling but NOT busy. Premium and serene. Square 1:1."
        ),
        "watermark": (
            "The same open lotus simplified to delicate gold-only outline, "
            "12% opacity, transparent background, very pretty and minimal, "
            "no coins, just the central lotus. Square 1:1."
        ),
    },
}


def _load_api_key() -> str | None:
    if not SECRETS.exists():
        return None
    with open(SECRETS, "rb") as f:
        s = tomllib.load(f)
    return s.get("GEMINI_API_KEY")


def _save_image_bytes(data: bytes, theme_slug: str, kind: str) -> Path:
    out_dir = ASSETS_DIR / theme_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{kind}.png"
    out_path.write_bytes(data)
    return out_path


# Image source chain — tries free options first, falls back to paid Gemini.
# Per Google's own advice (AI Studio chat):
#   - Pollinations.ai: free, no key, public wrapper for Flux/SDXL
#   - Hugging Face Serverless: free token, FLUX.1-schnell
#   - Gemini free-tier image models: quota-limited but often available
#   - Imagen 4: requires paid tier
MODEL_CHAIN = [
    "pollinations:flux",                # FREE, no key needed — primary
    "gemini-3.1-flash-image-preview",
    "gemini-2.5-flash-image",
    "imagen-4.0-fast-generate-001",     # paid fallback
    "imagen-4.0-generate-001",
]


def _fetch_pollinations(prompt: str, model: str = "flux") -> bytes | None:
    """Pollinations.ai — completely free, no API key. Returns PNG bytes."""
    import urllib.parse
    import urllib.request
    encoded = urllib.parse.quote(prompt, safe="")
    # Pollinations URL format: https://image.pollinations.ai/prompt/<prompt>?width=1024&height=1024&model=flux&nologo=true
    url = (f"https://image.pollinations.ai/prompt/{encoded}"
           f"?width=1024&height=1024&model={model}&nologo=true&enhance=true")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            return resp.read()
    except Exception:
        return None


def _generate_one(client, prompt: str) -> tuple[bytes | None, str]:
    """Try each provider in chain until one returns an image."""
    from google.genai import types as gtypes

    last_err = "no providers attempted"
    for model_name in MODEL_CHAIN:
        try:
            # ── Pollinations.ai — free, no key ───────────────────────────
            if model_name.startswith("pollinations:"):
                sub_model = model_name.split(":", 1)[1]
                data = _fetch_pollinations(prompt, model=sub_model)
                if data and len(data) > 1000:  # sanity check (not error html)
                    return data, model_name
                last_err = f"{model_name}: no image returned (or too small)"
                continue

            # ── Imagen (paid) ─────────────────────────────────────────────
            if model_name.startswith("imagen-"):
                resp = client.models.generate_images(
                    model=model_name,
                    prompt=prompt,
                    config=gtypes.GenerateImagesConfig(
                        number_of_images=1, aspect_ratio="1:1",
                    ),
                )
                img = resp.generated_images[0]
                return img.image.image_bytes, model_name

            # ── Gemini multimodal image models ────────────────────────────
            resp = client.models.generate_content(
                model=model_name, contents=prompt,
            )
            for cand in resp.candidates:
                for part in cand.content.parts:
                    if (getattr(part, "inline_data", None)
                            and part.inline_data.data):
                        data = part.inline_data.data
                        if isinstance(data, str):
                            data = base64.b64decode(data)
                        return data, model_name
            last_err = f"{model_name}: no inline_data in response"
        except Exception as e:
            err = str(e)[:200]
            last_err = f"{model_name}: {type(e).__name__}: {err}"
            continue
    return None, last_err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", help="Generate just one theme (e.g. ganesha)")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite existing PNG files")
    ap.add_argument("--kind", choices=("cover", "watermark", "both"),
                    default="both", help="Which image(s) to (re)generate")
    args = ap.parse_args()

    api_key = _load_api_key()
    if not api_key:
        print(f"ERROR: no GEMINI_API_KEY found in {SECRETS}", file=sys.stderr)
        sys.exit(2)

    try:
        from google import genai
    except ImportError:
        print("ERROR: install the new SDK:  pip install google-genai",
              file=sys.stderr)
        sys.exit(2)

    client = genai.Client(api_key=api_key)
    themes_to_do = [args.theme] if args.theme else list(PROMPTS.keys())
    kinds = ["cover", "watermark"] if args.kind == "both" else [args.kind]

    total, ok, skipped, failed = 0, 0, 0, 0
    for slug in themes_to_do:
        if slug not in PROMPTS:
            print(f"  unknown theme: {slug}  (known: {list(PROMPTS)})")
            continue
        for kind in kinds:
            total += 1
            target = ASSETS_DIR / slug / f"{kind}.png"
            if target.exists() and not args.force:
                print(f"  skip  {slug}/{kind}.png  (exists; use --force)")
                skipped += 1
                continue
            print(f"  gen   {slug}/{kind}.png  ...", end=" ", flush=True)
            prompt = PROMPTS[slug][kind]
            data, info = _generate_one(client, prompt)
            if not data:
                print(f"FAIL — {info}")
                failed += 1
                # Small pause so we don't hammer rate-limited endpoints
                time.sleep(2)
                continue
            out = _save_image_bytes(data, slug, kind)
            print(f"ok ({len(data):,} bytes, via {info})  → {out.name}")
            ok += 1
            time.sleep(1)  # gentle pacing

    print()
    print(f"Total: {total}  generated={ok}  skipped={skipped}  failed={failed}")
    if failed:
        print("Hint: if everything failed with 429, your daily image-gen quota "
              "is exhausted. Retry tomorrow, or upgrade to the paid tier for "
              "Imagen 4 / higher rate limits.")


if __name__ == "__main__":
    main()
