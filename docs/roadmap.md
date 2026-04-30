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

### Phase 1 — Backend rewrite  `feat/backend-rewrite`
**Goal:** Clean, tested, authenticated API with correct models.
**Single large branch; merged when all tests pass.**

#### Models (what changes)

**Inventory** — add:
- `vat_rate: float` (7.0 or 19.0 — required, no default)
- `is_deposit: bool = False` (replaces hardcoded `"Pfand"` string check)
- `requires_deposit: bool = False` (replaces hardcoded `"Drinks"` category check)
- `active: bool = True` (soft-disable instead of delete)

**History (Order)** — add:
- `transaction_id: UUID` (auto-generated, immutable)
- `staff_id: Optional[PydanticObjectId]` (who processed the sale)
- `vat_breakdown: list[VatLine]` (per-rate totals for GoBD compliance)
- No DELETE endpoint. Cancellation flag only. Already present — keep it.

**Reservation** — add:
- `retention_until: datetime` (set to `movie.datetime + 30 days` at creation)
- `scan_timestamp: Optional[datetime]`
- Remove duplicate email → keep for now (no user accounts in scope)

**Movie** — add:
- `active: bool = True` (soft-disable — no hard DELETE)
- Remove `stripe_payment` field (not in scope per product.md)

#### Config fixes
- ~~`SECRET_KEY` must load from env, not `secrets.token_urlsafe()` at import time~~ ✅ done
- ~~`DEBUG` default → `False`~~ ✅ done
- ~~Pydantic v2 `model_config = ConfigDict(env_file=".env")` pattern~~ ✅ done
- `FIRST_SUPERUSER_PASSWORD` default → raise error if not set in production

#### Authentication
- JWT bearer tokens on all write endpoints
- Read endpoints (GET /movies, GET /inventory) remain public — cashier loads products without login
- Auth endpoints: `POST /api/v1/auth/token`, `POST /api/v1/auth/refresh`

#### Business logic fixes
- Replace all hardcoded product name strings with model flags (`is_deposit`, `requires_deposit`)
- Report endpoint: add `start_date` / `end_date` query params for cross-movie date-range aggregation
- Inventory sold endpoint: guard against `amount < 0`
- Movies: replace DELETE with `active = False`

#### Tests (pytest + pytest-asyncio + httpx)
- One test file per endpoint group
- Cover: happy path, auth failures, validation errors, Pfand flag logic, report date ranges
- Target: all critical business rules from `docs/domain.md` are tested

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
