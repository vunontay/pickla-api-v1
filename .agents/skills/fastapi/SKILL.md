---
name: fastapi
description: FastAPI best practices and conventions. Use when working with FastAPI APIs and Pydantic models for them. Keeps FastAPI code clean and up to date with the latest features and patterns, updated with new versions. Write new code or refactor and update old code.
---

# FastAPI — Pickla Project Conventions

Official FastAPI skill tailored for `pickla-api-v1`.

**Stack**: Python 3.12 · FastAPI · PostgreSQL · SQLAlchemy 2 (async/asyncpg) · Alembic · Pydantic v2 · pydantic-settings · Poetry · Ruff · mypy · pytest

---

## Running the Server

Development (with reload):

```bash
poetry run fastapi dev src/main.py
```

Production:

```bash
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Set the entrypoint in `pyproject.toml` to avoid repeating the path:

```toml
[tool.fastapi]
entrypoint = "src.main:app"
```

---

## Project Architecture

All feature code lives under `src/modules/{name}/` following a strict 4-file layout:

```
src/modules/{name}/
├── router.py      # FastAPI APIRouter — HTTP endpoints only
├── service.py     # Business logic — calls repository, raises errors
├── repository.py  # SQLAlchemy queries — AsyncSession only
└── schemas.py     # Pydantic request/response models
```

Mount new routers in `src/api/v1.py`:

```python
from fastapi import APIRouter
from src.modules.users.router import router as users_router

router = APIRouter()
router.include_router(users_router)
```

**Layer rules (never cross these):**

| Layer | Owns | Never |
|---|---|---|
| `router.py` | HTTP method, path, DI, call service | Business logic |
| `service.py` | Orchestrate logic, call repository | Query DB directly |
| `repository.py` | SQLAlchemy statements | Business logic |
| `schemas.py` | Pydantic request/response models | DB operations |

---

## Use `Annotated`

Always prefer the `Annotated` style for parameter and dependency declarations.

### Path / Query parameters

```python
from typing import Annotated
from fastapi import FastAPI, Path, Query

app = FastAPI()


@app.get("/matches/{match_id}")
async def get_match(
    match_id: Annotated[int, Path(ge=1, description="Match ID")],
    status: Annotated[str | None, Query(max_length=20)] = None,
):
    ...
```

### Dependencies

Create a type alias for reusable dependencies:

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.shared.database.dependencies import get_db

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/")
async def list_matches(db: DbSession):
    ...
```

Do **not** use the old `= Depends(...)` inline style:

```python
# DO NOT DO THIS
async def list_matches(db: AsyncSession = Depends(get_db)):
    ...
```

---

## Do Not Use Ellipsis for Path Operations or Pydantic Models

```python
from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    title: str
    max_players: int = Field(gt=0, le=20)
    location: str | None = None
```

Do **not** use `...` as default:

```python
# DO NOT DO THIS
class MatchRequest(BaseModel):
    title: str = ...
    max_players: int = Field(..., gt=0)
```

---

## Return Type or Response Model

Always declare a return type to validate, filter, and serialize responses:

```python
from fastapi import APIRouter
from src.modules.matches.schemas import MatchResponse

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/{match_id}")
async def get_match(match_id: Annotated[int, Path(ge=1)]) -> MatchResponse:
    ...
```

Use `response_model` only when the return type genuinely cannot match the serialization model (e.g., the function must return a broad union or a third-party type that cannot be annotated directly). In that case, still avoid `Any` — annotate with the most specific type available:

```python
# Preferred: return type matches the response schema directly
@router.get("/me")
async def get_me(current_user: CurrentUserDep) -> UserPublicResponse:
    return UserPublicResponse.model_validate(current_user)
```

If an ORM model is returned and must be filtered to a public schema, use `model_validate` to convert explicitly rather than relying on `response_model` + `Any`:

```python
@router.get("/{user_id}")
async def get_user(user_id: Annotated[int, Path(ge=1)], db: DbSession) -> UserPublicResponse:
    user = await user_repo.get_by_id(user_id)
    return UserPublicResponse.model_validate(user)
```

**Never expose internal/sensitive fields** — always use a dedicated `{Entity}Response` schema.

---

## Schemas (Pydantic v2)

Use **separate schemas** for request and response. Never reuse the same model for both.

```python
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    reputation_score: int

    model_config = {"from_attributes": True}
```

Naming convention: `{Entity}Request` for input, `{Entity}Response` for output.

---

## Including Routers

Declare `prefix`, `tags`, and shared `dependencies` on the router itself — not in `include_router()`:

```python
from fastapi import APIRouter, Depends
from src.shared.auth.jwt import get_current_user

router = APIRouter(
    prefix="/matches",
    tags=["matches"],
    dependencies=[Depends(get_current_user)],  # applies to all endpoints
)
```

Do **not** pass `prefix`/`tags` at include time:

```python
# DO NOT DO THIS
app.include_router(router, prefix="/matches", tags=["matches"])
```

---

## Database (SQLAlchemy 2 Async)

### Session dependency

Always inject via `get_db` — never instantiate `SessionLocal()` manually in service/router:

```python
# src/shared/database/dependencies.py
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.shared.database.session import SessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
```

### Repository pattern

All DB queries belong in `repository.py`:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.users.models import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
```

### Rules

- All DB operations **must be async** — use `await session.execute(...)`.
- Never call `session.commit()` from a repository — let the service or a middleware handle transactions.
- Use `expire_on_commit=False` on `SessionLocal` (already set in `src/shared/database/session.py`).

---

## Settings (pydantic-settings)

Always use the `settings` singleton — never instantiate `Settings()` more than once:

```python
from src.shared.configs.settings import settings

print(settings.DATABASE_URL)
```

Adding new config values: add to `Settings` class and update `.env.example`.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DEBUG: bool = False
```

---

## Async vs Sync Path Operations

Use `async def` for all path operations in this project — every handler calls async services/repositories.

```python
@router.post("/")
async def create_match(body: MatchRequest, db: DbSession) -> MatchResponse:
    return await match_service.create(db=db, data=body)
```

Avoid `async def` only when calling purely blocking/sync third-party code that has no async alternative. In that case, use a plain `def` so FastAPI runs it in a threadpool.

---

## Error Handling

Raise `HTTPException` in the **router** or **service** layer — not in the repository:

```python
from fastapi import HTTPException, status


async def get_match_or_404(match_id: int, db: DbSession) -> MatchResponse:
    match = await match_repo.get_by_id(match_id)
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match
```

Use custom exception classes in `src/shared/errors/` for domain errors; map them to HTTP responses via exception handlers registered in `src/main.py`.

---

## Performance

Prefer standard Pydantic serialization over `ORJSONResponse` or `UJSONResponse` for consistency. Declaring a return type or `response_model` is sufficient — Pydantic v2 handles serialization on the Rust side and is fast enough for this project.

Only reach for `ORJSONResponse` if profiling confirms a specific serialization bottleneck.

---

## Do Not Use Pydantic RootModels

Use `Annotated` + field validators instead of `RootModel`:

```python
from typing import Annotated
from fastapi import Body


@router.post("/bulk")
async def bulk_create(ids: Annotated[list[int], Body(min_length=1)]):
    ...
```

Validation constraints (`min_length`, `ge`, `le`, `max_length`, etc.) belong in the FastAPI parameter class (`Body`, `Query`, `Path`) — not in a separate `pydantic.Field`. `pydantic.Field` is for Pydantic **model fields** only.

Do **not** mix `Field` with `Body` in path operations:

```python
# DO NOT DO THIS
from pydantic import Field

async def bulk_create(ids: Annotated[list[int], Field(min_length=1), Body()]): ...
```

Do **not** subclass `RootModel`:

```python
# DO NOT DO THIS
class IdList(RootModel[Annotated[list[int], Field(min_length=1)]]):
    pass
```

---

## One HTTP Operation per Function

```python
@router.get("/")
async def list_matches(db: DbSession) -> list[MatchResponse]:
    ...


@router.post("/")
async def create_match(body: MatchRequest, db: DbSession) -> MatchResponse:
    ...
```

Do **not** use `api_route` with multiple methods:

```python
# DO NOT DO THIS
@router.api_route("/", methods=["GET", "POST"])
async def handle_matches(request: Request): ...
```

---

## Tooling

| Tool | Command |
|---|---|
| Lint + format | `poetry run ruff check . && poetry run ruff format .` |
| Type check | `poetry run mypy` |
| Tests | `poetry run pytest -q` |
| Tests with coverage | `poetry run pytest --cov=src --cov-report=term-missing` |
| Migrations (generate) | `poetry run alembic revision --autogenerate -m "description"` |
| Migrations (apply) | `poetry run alembic upgrade head` |

Ruff config lives in `pyproject.toml` (`[tool.ruff]`). mypy is also configured there (`[tool.mypy]`). All checks run in CI via `.github/workflows/ci.yml`.

---

## Common Pitfalls

| ❌ Don't | ✅ Do |
|---|---|
| Write ORM queries in `service.py` | Move to `repository.py` |
| Write business logic in `router.py` | Move to `service.py` |
| Instantiate `Settings()` multiple times | Use `settings` singleton |
| Use `= Depends(...)` inline | Use `Annotated[..., Depends(...)]` alias |
| Share one schema for input and output | Split into `*Request` / `*Response` |
| Create `SessionLocal()` manually in handlers | Inject via `Depends(get_db)` |
| Use sync SQLAlchemy in async handlers | Always `await session.execute(...)` |
| Expose internal model fields in responses | Always use a `*Response` schema |
| Default to `ORJSONResponse` / `UJSONResponse` | Prefer Pydantic serialization via return type; use response classes only if profiling justifies it |
| Commit `.env` to version control | Only commit `.env.example` |
