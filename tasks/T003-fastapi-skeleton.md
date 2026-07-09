# T003 — FastAPI skeleton (app factory + settings + CORS)

## Goal

Create the FastAPI application skeleton for the CRM backend: a settings module
using pydantic-settings and an app factory wiring CORS. NO endpoints, NO
routers, NO database code — those come in later tasks (T004, T005).

## Files to produce (exactly these, no others)

1. `backend/app/core/__init__.py` — empty package marker.

2. `backend/app/core/config.py` — settings via pydantic-settings:
   - `class Settings(BaseSettings)` with fields:
     - `app_name: str = "CRM API"`
     - `debug: bool = False`
     - `cors_origins: list[str] = ["http://localhost:5173"]`
     - `database_url: str = "postgresql+asyncpg://crm:change-me@localhost:5432/crm"`
     - `redis_url: str = "redis://:change-me@localhost:6379/0"`
   - `model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")`
   - `@lru_cache` -decorated module-level function `get_settings() -> Settings`.

3. `backend/app/main.py` — app factory:
   - `def create_app() -> FastAPI:` — creates the FastAPI instance with
     `title=settings.app_name`, `debug=settings.debug`; adds `CORSMiddleware`
     with `allow_origins=settings.cors_origins`, `allow_credentials=True`,
     `allow_methods=["*"]`, `allow_headers=["*"]`. Returns the app.
   - Module-level `app = create_app()` so `uvicorn app.main:app` works from
     inside `backend/`.

## Interfaces to conform to

- Pydantic v2 + pydantic-settings 2.x (`from pydantic_settings import BaseSettings, SettingsConfigDict`).
- Settings are consumed via `get_settings()` (dependency-injection friendly);
  do not instantiate `Settings()` at import time in `main.py` other than
  through `get_settings()`.

## Acceptance criteria

- `python -c "from app.main import app"` succeeds from `backend/` with only
  fastapi, pydantic, pydantic-settings installed.
- No endpoints defined; OpenAPI schema has zero paths.
- All defaults overridable via environment variables (standard pydantic-settings
  behavior); no secrets hardcoded beyond the documented `change-me` dev defaults
  matching `.env.example`.
