# Myastro API — full backend image (chart math, PDF, palm/face vision, AI).
# Built for Render's free tier (Docker runtime), but portable to any host
# (Oracle Cloud free VM later — see MOBILE_APP_BLUEPRINT.md §8).
#
# Why Docker: weasyprint (PDF) and mediapipe/opencv (palm & face vision) need
# system libraries that Render's *native* Python runtime can't install. In a
# Docker image we install them ourselves, so every feature runs — no scope cut.

FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# System libraries:
#   weasyprint (PDF)            → pango, cairo, gdk-pixbuf, ffi, mime, fonts
#   mediapipe + opencv (vision) → libGL, glib, OpenMP
#   build-essential            → fallback to compile any pip pkg without a wheel
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 \
        libgdk-pixbuf-2.0-0 libcairo2 libffi8 shared-mime-info \
        libgl1 libglib2.0-0 libgomp1 \
        fonts-dejavu-core fonts-noto-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better layer caching on code-only changes).
# NOTE: requirements.txt is the SE-free runtime set (no pyswisseph). The Swiss
# Ephemeris dev reference lives in requirements-dev.txt and is NOT installed here.
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Bake the JPL kernel (de440s.bsp, ~32 MB, public domain) into the image so the
# free Skyfield engine never has to download it at runtime (the container FS is
# ephemeral on Render's free tier — a runtime download would repeat on every cold
# start). Its own cached layer: not invalidated by app-code changes below.
RUN python -c "from skyfield.api import load; load('de440s.bsp')"

# App code. de440s.bsp is gitignored so it is NOT in the build context — the
# baked copy above survives this COPY.
COPY . .

# Render injects $PORT; default to 8000 for local `docker run`.
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn fastapi_main:app --host 0.0.0.0 --port ${PORT:-8000}"]
