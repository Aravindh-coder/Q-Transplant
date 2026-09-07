# Q-Transplant -- single-container build serving both the FastAPI backend
# and the static frontend (public/) from one process, matching how Render
# runs this (see render.yaml and ARCHITECTURE.md's "Deployment" section).
#
# This is for local parity and portability to any other container
# platform -- Render's own deploy uses its native Python buildpack via
# render.yaml, not this file. Build/run locally with:
#   docker build -t qtransplant .
#   docker run -p 8000:8000 --env-file backend/backend/.env qtransplant
# (copy backend/backend/.env.example to backend/backend/.env and fill in
# real values first -- see that file for what each variable does).

FROM python:3.12-slim

# psycopg2-binary needs libpq at runtime; keeping this to runtime-only
# packages (no -dev/build-essential) keeps the image smaller since the
# binary wheel doesn't need a C compiler to install.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/backend/requirements.txt ./backend/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/backend/requirements.txt

# The app resolves its own repo root at runtime (app/config.py's BASE_DIR)
# to find public/ regardless of working directory, so the full repo layout
# must be preserved here, not just the backend subtree.
COPY . .

# Runs as a non-root user -- standard container hardening, not something
# the app depends on.
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

WORKDIR /app/backend/backend
EXPOSE 8000

# No --reload here (that's run_app.py's local dev launcher, not this).
# $PORT isn't set outside Render, so this hardcodes 8000 -- override with
# `docker run -p HOST_PORT:8000` if you need a different host-side port.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
