# CLAUDE.md

This file provides guidance to AI agents working with code in this repository.

## Project Overview

Burning Register is a web-based cinema cash register operated by **Burning Cinema – Hochschulkino Deggendorf e.V.** (registered Verein, THD-affiliated) for managing inventory, orders, movies, reservations, and reporting. It is a monorepo with two services:

- `services/frontend` — Vue 3 + Vuetify 3 SPA (served via Node/nginx)
- `services/backend` — Python FastAPI + Beanie (ODM) + MongoDB

## Environment Setup

For local development, create `services/backend/.env` (pydantic-settings reads it from the working directory):

```
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=burningregister

UVICORN_PORT=8080
DEBUG=true

CORS_ORIGINS=["http://localhost:5173"]

# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=dev-only-change-in-production

FIRST_SUPERUSER=admin
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=changeme
```

See `.env.example` at the repo root for the full reference.

## Running the Stack

**Local full-stack test (backend + MongoDB, via Docker):**
```bash
docker-compose -f docker-compose.test.yml up -d
```
Backend: `http://localhost:9090`

**Backend only (no Docker):**
```bash
cd services/backend
poetry install
poetry run python -m burningbackend   # uvicorn on :8080, reload=DEBUG
poetry run pytest                     # run tests
```

**Frontend only:**
```bash
cd services/frontend
bun install          # bun.lockb present — use bun, not npm
bun run serve        # dev server on :5173
bun run build        # production build
bun run lint         # ESLint
```

**Production:**
- Backend: Railway project `exemplary-exploration` — auto-deploys on merge to `master`
- Frontend: Cloudflare Pages `burning-register` — auto-deploys on merge to `master`
- Database: Railway MongoDB service in the same project as the backend

## Docs

The `docs/` directory is the ground truth for this project. Read these before making any significant change:

- `docs/product.md` — scope, users, what is explicitly out of scope
- `docs/domain.md` — domain model, German/English term mapping, core business rules
- `docs/regulations.md` — German legal requirements (KassenSichV, DSGVO, GoBD, VAT)
- `docs/design-foundation.md` — design principles and existing visual tokens
- `docs/roadmap.md` — full rewrite plan, audit findings, phase breakdown

## Git Conventions

**Authorship**: All commits are authored by `arudaev <hlexhelftd@gmail.com>`. No co-author trailers, no tool attribution, no session IDs — in commits, PR descriptions, or any document other than this file.

**Branches**: All work happens on feature branches. Never commit directly to `master`.

- `feature/<short-description>` — new functionality
- `fix/<short-description>` — bug fixes
- `docs/<short-description>` — documentation only
- `chore/<short-description>` — tooling, config, deps

**Pull requests**: Open a PR into `master` only when work is fully done — clean commits, no leftover TODOs, no debug code. PR titles and descriptions follow the same plain-language, attribution-free standard as commit messages.

**Commit messages**: Describe the change in plain terms. Conventional prefix (`feat:`, `fix:`, `docs:`, `chore:`) followed by a short imperative summary.

## Architecture

### Backend

- Entry point: `src/burningbackend/app/main.py` — FastAPI app with lifespan (DB init on startup), CORS middleware
- Config: `src/burningbackend/app/core/config.py` — `Settings` via `pydantic-settings` v2 (`model_config = ConfigDict(...)`); `SECRET_KEY` and `MONGODB_URI` must be supplied via env — no unsafe defaults
- Database: `src/burningbackend/app/db/init_db.py` — initialises Beanie with Motor (async MongoDB), creates default superuser on first run
- Models: `src/burningbackend/app/models/` — Beanie `Document` subclasses (Movie, Inventory, History, Reservation, User)
- Auth: `core/security.py` (bcrypt + JWT HS256), `core/deps.py` (`get_current_user`, `get_current_superuser` FastAPI dependencies)
- Auth endpoints: `POST /api/v1/auth/token` (OAuth2 password grant), `POST /api/v1/auth/refresh`
- All write endpoints require a bearer token; GET endpoints are public
- API routes: `src/burningbackend/app/api/v1/endpoints/` — one file per resource, all under `/api/v1/<resource>`
  - `auth`, `movies`, `inventory`, `history`, `reservation`, `report`
- Health check: `GET /api/v1/health` → `{"status": "ok"}` (used by Railway)
- OpenAPI docs served at `/api/v1/docs/`
- Beanie serialises document IDs as `"_id"` (not `"id"`) in FastAPI JSON responses

### Frontend

- SPA shell: `src/App.vue` wraps a `NavBar` and `<router-view>`
- Routes (`src/router/index.js`): `/` → `RegisterView`, `/statistics` → `StatisticsView`, `/admin` → `AdminView`
- State: Pinia store at `src/stores/movieStore.js` — persists `selectedMovie` to `localStorage`
- API calls use `axios`; backend URL comes from `VUE_APP_DB_ADDRESS` env var
- Register flow (`RegisterView`): movie selector → `ButtonPanel` (products) or `PayPanel` (checkout) toggled by keypad input from `RegisterKeypad`; cart state managed in `RegisterCart`

### Data flow

Frontend calls `VUE_APP_DB_ADDRESS/api/v1/<resource>` → FastAPI router → Beanie document → MongoDB.
