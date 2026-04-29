# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Burning Register is a web-based cinema cash register operated by **Burning Cinema – Hochschulkino Deggendorf e.V.** (registered Verein, THD-affiliated) for managing inventory, orders, movies, reservations, and reporting. It is a monorepo with two services:

- `services/frontend` — Vue 3 + Vuetify 3 SPA (served via Node/nginx)
- `services/backend` — Python FastAPI + Beanie (ODM) + MongoDB

## Environment Setup

Create a `.env` file in the repo root before running anything:

```
MONGODB_URI=mongodb://db:27017/
MONGODB_DB_NAME=burningregister

UVICORN_PORT=9090

CORS_ORIGINS=["http://localhost:8080"]

VUE_APP_DB_ADDRESS=http://localhost:9090

# Optional: override default superuser
FIRST_SUPERUSER=admin
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=changeme
```

## Running the Stack

**Full dev stack (includes local MongoDB):**
```bash
docker-compose -f docker-compose-dev.yml up -d
```
Frontend: `http://localhost:8080` | Backend: `http://localhost:9090`

**Production (requires external MongoDB + Cloudflare tunnel):**
```bash
docker-compose up -d
```

## Frontend Commands

All run from `services/frontend/`:

```bash
bun install          # install deps (bun.lockb present — use bun, not npm)
bun run serve        # dev server on :8080
bun run build        # production build
bun run lint         # ESLint
```

## Backend Commands

All run from `services/backend/`:

```bash
poetry install       # install deps
poetry run python -m burningbackend   # run dev server (uvicorn with reload)
poetry run pytest    # run tests
```

## Docs

The `docs/` directory is the ground truth for this project. Read these before making any significant change:

- `docs/product.md` — scope, users, what is explicitly out of scope
- `docs/domain.md` — domain model, German/English term mapping, core business rules
- `docs/regulations.md` — German legal requirements (KassenSichV, DSGVO, GoBD, VAT)
- `docs/design-foundation.md` — design principles and existing visual tokens

## Git Conventions

Branch names must follow conventional prefixes and describe the work — never reference the tool or agent:

- `feature/<short-description>` — new functionality
- `fix/<short-description>` — bug fixes
- `docs/<short-description>` — documentation only
- `chore/<short-description>` — tooling, config, deps

Commit messages describe the change in plain terms. Do not include tool names, session IDs, or agentic attribution of any kind.

## Architecture

### Backend

- Entry point: `src/burningbackend/app/main.py` — FastAPI app with lifespan (DB init on startup), CORS middleware
- Config: `src/burningbackend/app/core/config.py` — `Settings` class via `pydantic-settings`, reads from `.env`
- Database: `src/burningbackend/app/db/init_db.py` — initialises Beanie with Motor (async MongoDB), creates default superuser on first run
- Models: `src/burningbackend/app/models/` — Beanie `Document` subclasses (Movie, Inventory, History, Reservation, User)
- API routes: `src/burningbackend/app/api/v1/endpoints/` — one file per resource, all under `/api/v1/<resource>`
  - `movies`, `inventory`, `history`, `reservation`, `report`
- OpenAPI docs served at `/api/v1/docs/`

### Frontend

- SPA shell: `src/App.vue` wraps a `NavBar` and `<router-view>`
- Routes (`src/router/index.js`): `/` → `RegisterView`, `/statistics` → `StatisticsView`, `/admin` → `AdminView`
- State: Pinia store at `src/stores/movieStore.js` — persists `selectedMovie` to `localStorage`
- API calls use `axios`; backend URL comes from `VUE_APP_DB_ADDRESS` env var
- Register flow (`RegisterView`): movie selector → `ButtonPanel` (products) or `PayPanel` (checkout) toggled by keypad input from `RegisterKeypad`; cart state managed in `RegisterCart`

### Data flow

Frontend calls `VUE_APP_DB_ADDRESS/api/v1/<resource>` → FastAPI router → Beanie document → MongoDB.
