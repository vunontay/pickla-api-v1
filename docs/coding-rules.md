# Coding Rules

> Authoritative coding standards for `pickla-api-v1`. Apply to every PR.

---

## Database

- **All DB operations must be async** — use `AsyncSession`, `await session.execute(...)`. Never call sync SQLAlchemy inside an `async def`.
- **Inject DB session via `get_db`** — never instantiate `SessionLocal()` manually inside a service, repository, or router.
- **Never call `session.commit()` from a repository** — let the service or a transaction middleware own the commit boundary.
- Use `expire_on_commit=False` on `SessionLocal` (already configured in `src/shared/database/session.py`).

## Settings

- **Always import settings via the singleton** — `from src.shared.configs.settings import settings`.
- Never instantiate `Settings()` more than once.
- New env vars must be added to both `Settings` in `src/shared/configs/settings.py` and `.env.example`.

## Schemas

- **Separate schemas for request and response** — never reuse the same Pydantic model for both.
- Naming: `{Entity}Request` for input, `{Entity}Response` for output.
- Add `model_config = {"from_attributes": True}` to response schemas that are built from ORM models.
- Never expose internal/sensitive fields in a `*Response` schema.

## FastAPI Patterns

- Use `Annotated[T, Depends(...)]` type aliases for all reusable dependencies — not the inline `= Depends(...)` style.
- Validation constraints for path operation parameters belong in `Body`, `Query`, or `Path` — not in `pydantic.Field`.
- Declare a return type on every endpoint. Pydantic v2 uses it for validation and serialization.
- Prefer `model_validate()` to convert ORM objects to response schemas explicitly.
- Use `async def` for all path operations (every handler in this project calls async services/repos).

## Migrations

- Decrement `open_slots` only after validating `match.status == "open"`.
- See `docs/migrations.md` for the full Alembic workflow.

## Version Control

- Never commit `.env` — only `.env.example`.
- Never commit secrets or credentials in any form.

---

## Common Pitfalls


| ❌ Don't                                        | ✅ Do                                                                   |
| ---------------------------------------------- | ---------------------------------------------------------------------- |
| Write ORM queries in `service.py`              | Move to `repository.py`                                                |
| Write business logic in `router.py`            | Move to `service.py`                                                   |
| Instantiate `Settings()` multiple times        | Use `settings` singleton                                               |
| Use `= Depends(...)` inline                    | Use `Annotated[..., Depends(...)]` alias                               |
| Share one Pydantic model for input + output    | Split into `*Request` / `*Response`                                    |
| Create `SessionLocal()` manually in handlers   | Inject via `Depends(get_db)`                                           |
| Use sync SQLAlchemy in async handlers          | Always `await session.execute(...)`                                    |
| Expose internal model fields in responses      | Use a dedicated `*Response` schema                                     |
| Use sync `engine_from_config` in Alembic       | Use `create_async_engine` + `asyncio.run` (already set up in `env.py`) |
| Decrement `open_slots` without checking status | Always validate `status == open` before joining                        |
| Commit `.env` to version control               | Only commit `.env.example`                                             |
| Use `pydantic.Field` for path operation params | Use `Body`, `Query`, `Path` constraints instead                        |
