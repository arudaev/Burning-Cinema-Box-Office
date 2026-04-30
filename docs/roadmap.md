# Burning Cinema — Full Rewrite Roadmap

## Context

Complete overhaul of a fragile, junior-quality cinema POS into a clean,
production-ready system for Burning Cinema – Hochschulkino Deggendorf e.V.
The existing codebase has multiple runtime-crashing bugs, zero authentication,
no tests, and a Docker-based deployment that is being replaced entirely.

Stack stays: **Vue 3 + Vuetify 3** (frontend) · **FastAPI + Beanie + MongoDB** (backend)
Deployment moves to: **Cloudflare Pages** · **Railway** · **MongoDB Atlas**

---

## Audit Findings (do not re-investigate these)

### Backend — critical bugs
| # | Issue | Location |
|---|-------|----------|
| 1 | `SECRET_KEY` regenerated on every import — JWT auth is broken | `config.py` |
| 2 | Undefined variable `req` in reservation update — NameError crash | `reservation.py:26` |
| 3 | Duplicate function names in inventory — second silently shadows first | `inventory.py:17,25` |
| 4 | Pydantic v1 `Config` inner class used in Pydantic v2 project | `config.py` |
| 5 | **No authentication on any endpoint** — API fully open | all endpoints |
| 6 | Hard DELETE on movies — orphans all reservations and history | `movies.py` |
| 7 | Hardcoded product names as strings in business logic | `report.py`, `history.py` |
| 8 | No VAT rate field on Inventory | `models/inventory.py` |
| 9 | No date-range filtering on reports — only per-movie | `report.py` |
| 10 | `retention_until` missing on Reservation (DSGVO requirement) | `models/reservation.py` |
| 11 | Negative stock allowed — no guard on `amount -= n` | `inventory.py:39` |
| 12 | Zero tests | `tests/` (empty) |

### Frontend — critical bugs
| # | Issue | Location |
|---|-------|----------|
| 1 | Pfand lookup: `addItem(undefined)` crash if Pfand not in inventory | `RegisterView.vue:156` |
| 2 | Checkout race condition: cart cleared before server responds | `RegisterView.vue:checkout()` |
| 3 | `selectedMovie.name` called without null guard — crash if no movie | `RegisterView.vue:checkout()` |
| 4 | `toggleTeam()` calls `.price_team` on undefined if product not found | `RegisterView.vue:toggleTeam()` |
| 5 | `decreaseProductAmount()` calls `.find()` without null guard — crash | `RegisterView.vue` |
| 6 | 401 interceptor navigates to `/login` which does not exist | `main.js:22` |
| 7 | All `.catch()` blocks log to console — zero user-visible error feedback | everywhere |
| 8 | Cart state lives only in component local state — lost on refresh | `RegisterView.vue` |
| 9 | Hardcoded product names `"Pfand"`, `"Drinks"` in 12+ locations | `RegisterView.vue` |
| 10 | Payment buttons are images with no alt, no aria, no keyboard support | `PayPanel.vue` |
| 11 | `cancellation` compared as string `"true"` instead of boolean | `StatisticsView.vue` |

### Infrastructure — what changes
- Backend Dockerfile has a PATH bug (`/app/.venv` vs `/code/.venv`)
- No SPA fallback routing (nginx default — direct URLs return 404)
- CI/CD: frontend only, manual trigger, deprecated action versions, no backend
- No `.env.example`

---

## Development Phases

### Phase 0 — CI/CD skeleton  `chore/ci-cd-setup` ✅ COMPLETE
**Goal:** Every subsequent PR is automatically tested and deployed.

**What shipped:**
- `.github/workflows/ci.yml` — backend tests + frontend lint on every PR
- `.github/workflows/deploy.yml` — Railway + Cloudflare Pages on merge to master
- `railway.toml` — Dockerfile builder, healthcheck at `/api/v1/health`
- `services/frontend/public/_redirects` — SPA fallback
- `.env.example` — full env var reference
- `services/backend/Dockerfile` — added post-Phase 0 to fix Railway nixpacks issues
- `docker-compose.test.yml` — local full-stack test environment (backend + MongoDB)
- Old Docker Compose files and Dockerfiles deleted

**Platform state (as of end of session 1):**
- Railway project: `exemplary-exploration`
  - Backend service: live, auto-deploys from `master`
  - MongoDB service: Railway-managed, internal hostname `mongodb.railway.internal`
  - Variables set: `MONGODB_URI`, `SECRET_KEY`, `DEBUG`, `CORS_ORIGINS`, `FIRST_SUPERUSER_*`
- Cloudflare Pages: `burning-register`, production branch `master`
  - Variable set: `VUE_APP_DB_ADDRESS=https://burning-cinema-box-office-production.up.railway.app`

**Backend config fixes also landed (partial Phase 1 groundwork):**
- `config.py`: `DEBUG` default `True`→`False`, `SECRET_KEY` required (no default), Pydantic v2 `model_config`
- `main.py`: removed duplicate health route and duplicate CORS import
- Audit items #1 and #4 from the backend bug list are resolved

---

### Phase 1 — Backend rewrite  `feat/backend-rewrite` ✅ COMPLETE
**Goal:** Clean, tested, authenticated API with correct models.
**PR:** [#7](https://github.com/arudaev/Burning-Cinema-Box-Office/pull/7) — 37 tests passing, smoke-tested against Docker stack.

**What shipped:**
- Models: Inventory (vat_rate, is_deposit, requires_deposit, active), History (transaction_id UUID, staff_id, vat_breakdown, is_deposit + vat_rate on Product snapshot), Reservation (retention_until, scan_timestamp), Movie (active, remove stripe_payment)
- Auth: JWT HS256 bearer tokens on all write endpoints; `POST /api/v1/auth/token` (OAuth2 password grant) + `POST /api/v1/auth/refresh`; `core/deps.py` with `get_current_user` / `get_current_superuser`
- Business logic: `is_deposit` flag replaces `name == "Pfand"` in `/history/total`; stock guard (HTTP 422) on `/inventory/sold`; soft-delete movies (`active=False`); `retention_until` computed from `movie.datetime + 30 days`; `scan_timestamp` set on scan
- Report: `movie` now optional; `start_date` / `end_date` params for cross-movie aggregation
- Config: `@model_validator` raises if `FIRST_SUPERUSER_PASSWORD == "changeme"` in production
- Fixed: NameError crash in `PUT /reservation/update` (undefined `req`)
- Tests: 37 tests across `test_auth`, `test_movies`, `test_inventory`, `test_history`, `test_reservation`, `test_report` — mongomock-motor (no real DB in CI)
- New deps: `python-jose[cryptography]`, `bcrypt`, `python-multipart`; dev: `pytest-asyncio`, `httpx`, `mongomock-motor`
- `docker-compose.test.yml`: changed `DEBUG=false` → `DEBUG=true` to bypass production password guard on local stack

**Verification notes:**
- Beanie serialises document ID as `"_id"` (not `"id"`) in FastAPI JSON responses — tests use `["data"]["_id"]`
- `poetry.lock` is committed intentionally — this is an application, not a library; CI and Railway both depend on it
- Local tests run via Docker: `docker run --rm -v ... python:3.11-slim bash -c "pip install poetry==1.8.2 && poetry install --with dev && poetry run pytest"` (poetry not installed on dev machine)

---

### Phase 2 — Design  *(no branch — external tool)*
**Goal:** Visual direction and component inventory before writing any UI code.

Inputs to Claude Design:
- `docs/product.md` — who uses it, what it needs to do
- `docs/design-foundation.md` — existing tokens, principles
- `docs/domain.md` — the 5 screens: Register (POS), Admin, Statistics, (future: Login)

Outputs expected:
- Layout direction for the 3 views
- Component inventory: which components exist, rough visual spec
- Interaction patterns for POS flow (keypad → cart → checkout)

Hand-off: extract design decisions into `docs/design-system.md`
(token set, component list, German copy for all error/empty states)

---

### Phase 3 — Frontend rewrite  `feat/frontend-rewrite`
**Goal:** Correct, keyboard-operable, error-handled UI against the clean API.
**Depends on Phase 1 backend being deployed to Railway.**

#### Store redesign (Pinia)

Replace single `movieStore` with two stores:

`useMovieStore`
- `selectedMovie` (persisted to localStorage — existing behaviour, keep)

`useCartStore`
- `items: CartItem[]`
- `teamMode: boolean`
- `clear()` — only called after server confirms order
- `addItem(product, qty)` — Pfand logic driven by `product.requires_deposit` flag
- `removeItem(id, qty)` — Pfand decremented via same flag
- `toggleTeamMode()` — clean, flag-driven, no string matching

#### Critical fixes
1. Pfand logic: replace `product.name === "Pfand"` with `product.is_deposit === true`
2. Drinks logic: replace `category === "Drinks"` with `product.requires_deposit === true`
3. Checkout: POST order → await response → THEN clear cart → show success
4. All `.catch()`: replace with German-language Vuetify snackbar notifications
5. 401 interceptor: remove `/login` redirect (no login route); show session-expired dialog
6. `selectedMovie` null guard: disable checkout button if no movie selected
7. `toggleTeamMode()`: rewrite without string lookups, driven by store flags

#### Accessibility
- `RegisterKeypad`: add `@keydown` listeners for numpad keys 0–9, Enter, Backspace
- `PayPanel`: replace `<v-img @click>` with `<v-btn>` containing the image; add aria-label
- All interactive elements: visible focus ring (Vuetify default is sufficient if not overridden)

#### Error/empty states (German copy — defined in design-system.md)
- No movie selected → "Bitte eine Vorführung auswählen"
- Products load failed → "Artikel konnten nicht geladen werden. Bitte neu laden."
- Checkout failed → "Bestellung konnte nicht gespeichert werden. Bitte erneut versuchen."
- Empty cart → "Noch keine Artikel hinzugefügt"

#### Statistics view
- Fix `order.cancellation === "true"` → `=== true` (boolean)
- Replace sequential API calls with `Promise.all()`
- Add date-range selector for cross-movie report (matches new backend capability)

---

## Branch and PR sequence

```
master
  └─ chore/ci-cd-setup        → PR 1 (no tests needed — config only)
  └─ feat/backend-rewrite      → PR 2 (must pass CI tests)
  [Phase 2: Claude Design — external, no branch]
  └─ docs/design-system        → PR 3 (design-system.md from Claude Design output)
  └─ feat/frontend-rewrite     → PR 4 (must pass CI lint + e2e smoke)
```

---

## Verification checkpoints

| Phase | How to verify |
|-------|---------------|
| CI/CD | Push to a test branch → GitHub Actions runs → Railway preview deploys |
| Backend | `poetry run pytest` passes; `GET /api/v1/movies/` returns 401 without token on write ops |
| Design | `docs/design-system.md` covers all components and German copy before any frontend code starts |
| Frontend | Manual POS smoke test: add drink → Pfand auto-added; checkout → cart survives until server 200; all errors show German snackbar |

---

## Files not changing

- `docs/` — all four foundation docs (ground truth, update only if domain changes)
- `CLAUDE.md` — update only when conventions change
- `services/backend/src/burningbackend/app/` — rewritten in Phase 1, not patched
- `services/frontend/src/` — rewritten in Phase 3, not patched
