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

# Install Python deps first (better layer caching on code-only changes)
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# App code (ephe/ Swiss Ephemeris data is included; see .dockerignore)
COPY . .

# Render injects $PORT; default to 8000 for local `docker run`.
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn fastapi_main:app --host 0.0.0.0 --port ${PORT:-8000}"]
