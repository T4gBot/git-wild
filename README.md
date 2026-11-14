# git-wild

Nature Exploration by Radio and Data Streams Unlimited (NERDS uc)

*Dropping out of TU Wien to track wildlife in real time.*

---

## Overview

`git-wild` is the web application behind the **NERDS uc Wild Cam Observation Logger**: a small Flask app where operators log animal sightings and see the full history on one page.

Each observation consists of:

* **Animal**: free-text species name (e.g. `Wolf`, `Deer`, `Owl`)
* **Stream**: free-text stream/camera name (e.g. `Cam-Alpha-01`)
* **Timestamp**: set automatically on the server (UTC)

Observations are stored in PostgreSQL and listed newest first. The app does not embed or play the live streams itself; the stream is just a label you type in.

---

## Tech Stack

* **App:** Python, Flask, Flask-SQLAlchemy, a single Jinja2 template with inline HTML/CSS (no JavaScript)
* **Database:** PostgreSQL (via `psycopg2-binary`)
* **Server:** Gunicorn (2 workers) inside Docker
* **Runtime:** Docker & Docker Compose
* **Tooling:** Ruff (lint/format) and mypy, configured in `pyproject.toml`

---

## Project Structure

```text
.
├── app.py              # Flask app, Observation model, single "/" route
├── templates/
│   └── index.html      # Form + observation table
├── Dockerfile          # python:3.11-slim image, runs gunicorn on :8080
├── docker-compose.yml  # Single "web" service (no database included)
├── requirements.txt
└── pyproject.toml      # Ruff & mypy config
```

---

## Configuration

The app reads one environment variable, `DATABASE_URL`, and **will not start without it**. It can be set in the environment or in a `.env` file in the project root (loaded with `python-dotenv`; `.env` is git-ignored).

```env
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME
```

The database must already exist and be reachable. On startup the app creates the `observation` table automatically if it is missing.

> **Note:** `docker-compose.yml` does not start a PostgreSQL container. You need to provide your own database (another container, a VM, a managed instance).

---

## Setup & Deployment

### Run with Docker Compose

```bash
git clone https://github.com/T4gBot/git-wild.git
cd git-wild

# Provide the database connection
echo 'DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME' > .env

docker compose up -d --build
```

The app is available at `http://localhost:8080` (or the host's IP).

Stop it with:

```bash
docker compose down
```

The `.env` file is copied into the image by `COPY . .` (there is no `.dockerignore`). Avoid pushing the built image to a public registry, or add a `.dockerignore` and pass `DATABASE_URL` through Compose's `environment:` / `env_file:` instead.

### Run locally without Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME
python app.py          # Flask dev server with debug=True on port 8080
```

`python app.py` runs with `debug=True` and is meant for development only. The Docker image uses Gunicorn.

---

## Intended Infrastructure

The app is deployed as a container on three Ubuntu Server VMs running on Proxmox VE, with a Traefik VM acting as load balancer in front of them:

```text
               [ Client Traffic ]
                       │
                       ▼
            ┌────────────────────┐
            │   Traefik VM       │  (Load Balancer)
            └──────────┬─────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
  ┌───────────┐  ┌───────────┐  ┌───────────┐
  │ Worker 01 │  │ Worker 02 │  │ Worker 03 │  (Ubuntu VMs on Proxmox)
  │ [Docker]  │  │ [Docker]  │  │ [Docker]  │
  └───────────┘  └───────────┘  └───────────┘
```

The Traefik, Proxmox and PostgreSQL setup is **not part of this repository**; only the application container is. All workers must point `DATABASE_URL` at the same database so they share one observation log.

---

## Known Limitations

* No authentication: anyone who can reach the app can add entries.
* No edit/delete, pagination or filtering; the whole log is rendered on every page load.
* Dependencies in `requirements.txt` are unpinned, and the file is saved as UTF-16 (pip handles it, but many tools expect UTF-8).
* The Docker image uses Python 3.11, while the Ruff/mypy config targets 3.13.
* No tests.

---

## License

MIT License

