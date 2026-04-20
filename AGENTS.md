# AGENTS.md

> AI Agent Guide — Entry point for AI coding agents working in this project.

## Product Context

**Pickla** is a web platform for Pickleball matchmaking in Vietnam.

- **Hosts** post open match sessions (have a court, need more players).
- **Joiners** browse and join available matches.
- A **Reputation Score** system (starts at 100) replaces financial deposits to deter no-shows.

Target users: individual players, court owners, small friend groups in Vietnamese cities.

## Project Overview

| Aspect             | Value                                                                    |
| ------------------ | ------------------------------------------------------------------------ |
| **Stack**          | Python 3.12, FastAPI, PostgreSQL, SQLAlchemy 2 (async), Alembic, asyncpg |
| **Architecture**   | Modular — Router → Service → Repository → Model → Schema                 |
| **Source Root**    | `src/`                                                                   |
| **API Versioning** | `/api/v1/...` via `src/api/v1.py`                                        |
| **Auth**           | JWT (access token + refresh token) + bcrypt password hashing             |
| **Config**         | pydantic-settings — environment variables from `.env`                    |
| **Testing**        | pytest + pytest-asyncio + httpx                                          |
| **Linting**        | ruff (format + lint) + mypy (type checking)                              |
| **Migrations**     | Alembic (async engine, asyncpg driver)                                   |

## Directory Structure

```
pickla-api-v1/
├── alembic/            # Migration scripts
│   └── env.py          # Async migration runner — reads DATABASE_URL from Settings
├── src/
│   ├── main.py         # FastAPI app entry point
│   ├── api/
│   │   └── v1.py       # Aggregates all module routers
│   ├── modules/        # Feature modules (each module = 1 bounded context)
│   │   ├── auth/
│   │   │   ├── router.py      # FastAPI router — HTTP endpoints
│   │   │   ├── service.py     # Business logic
│   │   │   ├── repository.py  # DB queries (SQLAlchemy)
│   │   │   └── schemas.py     # Pydantic request/response schemas
│   │   └── matches/           # (placeholder)
│   └── shared/         # Cross-cutting utilities — no business logic
│       ├── auth/
│       │   ├── hashing.py     # Password hashing
│       │   └── jwt.py         # JWT encode/decode
│       ├── configs/
│       │   └── settings.py    # Settings (pydantic-settings) — singleton `settings`
│       ├── database/
│       │   ├── session.py     # Async engine + SessionLocal
│       │   └── dependencies.py # FastAPI dependency `get_db`
│       └── errors/            # Custom exception classes
├── tests/
│   ├── conftest.py            # Shared pytest fixtures
│   └── test_main.py           # Smoke tests
├── .env                       # Local environment variables (do not commit)
├── .env.example               # Environment variable template
├── alembic.ini
└── pyproject.toml
```

## Request Flow

```
HTTP Request
  → src/api/v1.py               (mounts all module routers)
  → modules/{mod}/router.py     (endpoint handler, injects dependencies)
  → modules/{mod}/service.py    (business logic)
  → modules/{mod}/repository.py (DB queries via AsyncSession)
  → JSON Response               (Pydantic Schema)
```

## Layer Responsibilities

| Layer           | Responsible for                                       | Must NOT               |
| --------------- | ----------------------------------------------------- | ---------------------- |
| `router.py`     | HTTP method, path, dependency injection, call service | Contain business logic |
| `service.py`    | Orchestrate logic, call repository, handle errors     | Query DB directly      |
| `repository.py` | SQLAlchemy statements (select/insert/update/delete)   | Contain business logic |
| `schemas.py`    | Pydantic models for request body and response         | Perform DB operations  |
| `shared/`       | Reusable utilities (auth, db, config, errors)         | Contain feature logic  |

## Naming Conventions

| Component  | File            | Class                                 |
| ---------- | --------------- | ------------------------------------- |
| Router     | `router.py`     | — (use `APIRouter()`)                 |
| Service    | `service.py`    | `{Module}Service`                     |
| Repository | `repository.py` | `{Module}Repository`                  |
| Schema     | `schemas.py`    | `{Entity}Request`, `{Entity}Response` |
| DB Model   | `models.py`     | `{Entity}` extending `Base`           |

## Coding Rules

- **All DB operations must be async** — use `AsyncSession`, `await session.execute(...)`.
- **Inject DB session via `get_db`** — never instantiate sessions manually inside service/repo.
- **Always import settings via the singleton** — `from src.shared.configs.settings import settings`.
- **Separate schemas for request and response** — never reuse the same Pydantic model for both.
- **Adding a new module**: create `src/modules/{name}/` with the 4 standard files (`router`, `service`, `repository`, `schemas`), then mount the router in `src/api/v1.py`.
- **Adding a migration**: `alembic revision --autogenerate -m "description"` — requires `target_metadata` in `alembic/env.py` to point to `Base.metadata`.

## Decision Tree

| Task                                  | Read                                                                                                          |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Add a new API endpoint                | `src/modules/AGENTS.md` → `modules/{mod}/router.py` → `modules/{mod}/service.py` → `modules/{mod}/schemas.py` |
| Add or change business logic          | `src/modules/AGENTS.md` → `modules/{mod}/service.py`                                                          |
| Add or change a DB query              | `src/modules/AGENTS.md` → `modules/{mod}/repository.py`                                                       |
| Add or change request/response format | `src/modules/AGENTS.md` → `modules/{mod}/schemas.py`                                                          |
| Add a new DB model                    | `src/modules/AGENTS.md` → create `modules/{mod}/models.py` extending `Base`, update `alembic/env.py`          |
| Run migrations                        | `alembic/AGENTS.md`                                                                                           |
| Add a new module                      | `src/modules/AGENTS.md` → create `src/modules/{name}/`, mount in `src/api/v1.py`                              |
| Change app config or env vars         | `src/shared/AGENTS.md` → `src/shared/configs/settings.py` + `.env.example`                                    |
| Add a shared utility                  | `src/shared/AGENTS.md`                                                                                        |
| Write or fix tests                    | `tests/AGENTS.md`                                                                                             |
| Auth / JWT / hashing                  | `src/shared/AGENTS.md` → `src/shared/auth/`                                                                   |
| Error handling                        | `src/shared/AGENTS.md` → `src/shared/errors/`                                                                 |
| Reputation score logic                | `src/modules/AGENTS.md` → `modules/users/service.py`                                                          |
| Match join eligibility                | `src/modules/AGENTS.md` → `modules/matches/service.py`                                                        |

## Before Any Task

1. Read this file (you are doing it now).
2. Identify which module(s) your task touches.
3. Read the `AGENTS.md` in each relevant directory if one exists (e.g. `tests/AGENTS.md`, `src/modules/AGENTS.md`).
4. Follow both global rules (this file) AND any directory-level rules.
5. For reputation-sensitive work (score changes, match state transitions), re-read the **Key Business Rules** section above.

## Common Pitfalls

| ❌ Don't                                             | ✅ Do                                                                  |
| ---------------------------------------------------- | ---------------------------------------------------------------------- |
| Write SQL/ORM directly in `service.py`               | Move it to `repository.py`                                             |
| Write business logic in `router.py`                  | Move it to `service.py`                                                |
| Instantiate `Settings()` multiple times              | Use the `settings` singleton                                           |
| Use sync `engine_from_config` in Alembic             | Use `create_async_engine` + `asyncio.run` (already set up in `env.py`) |
| Share the same schema for request and response       | Split into `{Entity}Request` and `{Entity}Response`                    |
| Create `SessionLocal()` manually in a handler        | Inject via `Depends(get_db)`                                           |
| Commit `.env` to version control                     | Only commit `.env.example`                                             |
| Decrement `open_slots` without checking match status | Always validate `status == open` before joining                        |
