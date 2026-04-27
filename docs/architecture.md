# Architecture

> Deep-dive reference for the modular structure of `pickla-api-v1`.

---

## Directory Structure

```
pickla-api-v1/
├── alembic/                    # Migration scripts
│   └── env.py                  # Async runner — reads DATABASE_URL from Settings
├── src/
│   ├── main.py                 # FastAPI app entry point
│   ├── api/
│   │   └── v1.py               # Mounts all module routers under /api/v1
│   ├── modules/                # Feature modules (each = 1 bounded context)
│   │   ├── auth/
│   │   │   ├── router.py       # FastAPI router — HTTP endpoints only
│   │   │   ├── service.py      # Business logic
│   │   │   ├── repository.py   # DB queries (SQLAlchemy)
│   │   │   └── schemas.py      # Pydantic request/response schemas
│   │   └── matches/            # (placeholder)
│   └── shared/                 # Cross-cutting utilities — no business logic
│       ├── auth/
│       │   ├── hashing.py      # bcrypt password hashing
│       │   └── jwt.py          # JWT encode/decode
│       ├── configs/
│       │   └── settings.py     # pydantic-settings singleton `settings`
│       ├── database/
│       │   ├── session.py      # Async engine + SessionLocal
│       │   └── dependencies.py # FastAPI dependency `get_db`
│       └── errors/             # Custom exception classes
├── tests/
│   ├── conftest.py             # Shared pytest fixtures
│   └── test_main.py            # Smoke tests
├── docs/                       # Agent and team knowledge base
├── .env                        # Local env vars (do not commit)
├── .env.example                # Env var template
├── alembic.ini
└── pyproject.toml
```

---

## Request Flow

```
HTTP Request
  → src/api/v1.py                 (mounts all module routers)
  → modules/{mod}/router.py       (endpoint handler, injects dependencies)
  → modules/{mod}/service.py      (business logic)
  → modules/{mod}/repository.py   (DB queries via AsyncSession)
  → JSON Response                 (Pydantic schema)
```

---

## Layer Responsibilities

| Layer | Responsible for | Must NOT |
|---|---|---|
| `router.py` | HTTP method, path, dependency injection, call service | Contain business logic |
| `service.py` | Orchestrate logic, call repository, raise errors | Query DB directly |
| `repository.py` | SQLAlchemy statements (select/insert/update/delete) | Contain business logic |
| `schemas.py` | Pydantic models for request body and response | Perform DB operations |
| `shared/` | Reusable utilities (auth, db, config, errors) | Contain feature logic |

---

## Naming Conventions

| Component | File | Class |
|---|---|---|
| Router | `router.py` | — (use `APIRouter()`) |
| Service | `service.py` | `{Module}Service` |
| Repository | `repository.py` | `{Module}Repository` |
| Schema | `schemas.py` | `{Entity}Request`, `{Entity}Response` |
| DB Model | `models.py` | `{Entity}` extending `Base` |

---

## Adding a New Module

1. Create `src/modules/{name}/` with the 4 standard files: `router.py`, `service.py`, `repository.py`, `schemas.py`.
2. Mount the router in `src/api/v1.py`:

```python
from src.modules.{name}.router import router as {name}_router

router.include_router({name}_router)
```

3. If the module has a DB model, create `models.py` extending `Base` and import it in `alembic/env.py` so Alembic detects it.

---

## Shared Utilities

| Utility | Location | Usage |
|---|---|---|
| DB session | `src/shared/database/session.py` | `SessionLocal` — `async_sessionmaker` |
| DB dependency | `src/shared/database/dependencies.py` | `get_db` — inject via `Depends` |
| Settings | `src/shared/configs/settings.py` | `settings` singleton |
| JWT | `src/shared/auth/jwt.py` | Encode/decode access + refresh tokens |
| Hashing | `src/shared/auth/hashing.py` | bcrypt password hash/verify |
| Errors | `src/shared/errors/` | Custom exception classes |

Always import settings via the singleton: `from src.shared.configs.settings import settings`.
