# PLAN.md — CRM Build Plan

Default scope confirmed by user (2026-07-10). Each task is sized for ONE
delegate call (one endpoint / one component / one test file). Responsible agent
in brackets. Work top to bottom; a task may only start when its dependencies are
merged. Follow the loop in `harness/WORKFLOW.md` for every task.

## Phase A — Foundation

- **T001** [architect] Monorepo scaffold: `backend/`, `frontend/` directories,
  root README, per-package .gitignore entries. (No delegation — pure file layout.)
- **T002** [architect] Docker Compose: Postgres 16 + Redis 7 with healthchecks,
  volumes, `.env`-driven credentials.
- **T003** [backend] FastAPI skeleton: `app/main.py` app factory, settings via
  pydantic-settings, CORS middleware. Paths: `backend/app/main.py`,
  `backend/app/core/config.py`.
- **T004** [backend] Health endpoint GET `/healthz` returning `{"status":"ok"}`
  + DB/Redis ping variants at `/healthz/deep`. Path: `backend/app/api/v1/health.py`.
- **T005** [backend] Async SQLAlchemy session/engine setup + base model class.
  Paths: `backend/app/db/session.py`, `backend/app/db/base.py`.
- **T006** [qa-db] Alembic init config + first empty migration. Paths:
  `backend/alembic.ini`, `backend/alembic/env.py` (async), initial revision.
- **T007** [frontend] Vite React TS skeleton: `main.tsx`, `App.tsx`, Router with
  a single Home page, Tailwind configured.
- **T008** [frontend] Typed API client base: `src/api/client.ts` (fetch wrapper,
  base URL from env, error normalization).
- **T009** [qa-db] Test bootstrap: pytest fixtures (async test DB via SQLite),
  `backend/tests/conftest.py`, smoke test for `/healthz`.
- **T010** [architect] CI: GitHub Actions workflow — pytest on backend + npm
  build on frontend, on every PR. Path: `.github/workflows/ci.yml`.

## Phase B — Auth & Users

- **T011** [backend] User model + Alembic migration (email unique, hashed
  password, role enum: admin/agent/viewer, timestamps).
- **T012** [backend] Auth schemas: register/login/token pairs (Pydantic v2).
  Path: `backend/app/schemas/auth.py`.
- **T013** [backend] Security service: password hashing (argon2/bcrypt), JWT
  create/verify (access + refresh, distinct secrets/expiries). Path:
  `backend/app/services/security.py`.
- **T014** [backend] POST `/api/v1/auth/register` endpoint.
- **T015** [backend] POST `/api/v1/auth/login` + POST `/api/v1/auth/refresh`.
- **T016** [backend] Auth dependencies: `get_current_user`, `require_role(...)`.
  Path: `backend/app/api/deps.py`.
- **T017** [qa-db] Auth test suite: register/login/refresh happy + failure paths,
  role enforcement.
- **T018** [frontend] Auth API hooks: `src/api/auth.ts` + TanStack Query
  mutations, token storage/refresh handling.
- **T019** [frontend] Login page + registration page (react-hook-form + zod).
- **T020** [frontend] Route guard component + role-aware layout shell (sidebar,
  header, logout).

## Phase C — Core CRM

- **T021** [backend] Company model + migration + schemas.
- **T022** [backend] Companies CRUD endpoints (list/paginate, get, create,
  update, delete; role-guarded).
- **T023** [qa-db] Companies test suite.
- **T024** [frontend] Companies list page + create/edit form + delete confirm.
- **T025** [backend] Contact model (FK company) + migration + schemas.
- **T026** [backend] Contacts CRUD endpoints.
- **T027** [qa-db] Contacts test suite.
- **T028** [frontend] Contacts list page + form.
- **T029** [backend] Deal model + pipeline stage enum + migration + schemas.
- **T030** [backend] Deals CRUD + PATCH stage-transition endpoint.
- **T031** [qa-db] Deals test suite incl. stage transition rules.
- **T032** [frontend] Deals kanban board (columns = stages, drag/drop, TanStack
  Query optimistic update).
- **T033** [backend] Activity/Note model (polymorphic target: contact/company/
  deal) + migration + schemas.
- **T034** [backend] Activities endpoints: create + timeline list per target.
- **T035** [qa-db] Activities test suite.
- **T036** [frontend] Activity timeline component + note composer.

## Phase D — Polish

- **T037** [backend] Search endpoint: contacts/companies/deals by name/email,
  paginated.
- **T038** [backend] List filters: query params (stage, owner, date ranges) on
  deals + contacts lists.
- **T039** [frontend] Search bar + filter controls wired to list pages.
- **T040** [backend] Dashboard metrics endpoint: deal counts by stage, win rate,
  recent activities.
- **T041** [frontend] Dashboard page with metric cards + simple charts.
- **T042** [backend] CSV export endpoints (contacts, companies, deals).
- **T043** [backend] CSV import endpoint (contacts) with validation report.
- **T044** [frontend] Import/export UI (upload, progress, validation errors).
- **T045** [qa-db] Search/dashboard/CSV test suites.
- **T046** [qa-db] Seed data script: demo users, companies, contacts, deals.

## Standing rules

- One delegate call per task; briefs in `tasks/`, reports in `reports/`.
- Backend endpoint tasks: qa-db coverage lands in the same phase before the
  phase is considered done.
- Any scope change gets a new T-number; never widen an existing brief.
