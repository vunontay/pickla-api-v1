# Migrations (Alembic)

> Reference for running and authoring database migrations in `pickla-api-v1`.

---

## Setup

Alembic uses an **async engine** (`create_async_engine` + `asyncio.run`) — never use the sync `engine_from_config`.

The migration runner reads `DATABASE_URL` from the `settings` singleton:

```python
# alembic/env.py (already configured)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

For Alembic to auto-detect model changes, `target_metadata` must point to `Base.metadata`. Import every model file in `alembic/env.py` before the metadata is read.

---

## Common Commands

```bash
# Apply all pending migrations
poetry run alembic upgrade head

# Roll back one migration
poetry run alembic downgrade -1

# Auto-generate a new migration from model changes
poetry run alembic revision --autogenerate -m "add users table"

# Show current revision
poetry run alembic current

# Show migration history
poetry run alembic history --verbose
```

---

## Workflow: Adding a New Model

1. Create `src/modules/{name}/models.py` with the SQLAlchemy model extending `Base`.
2. Import the model in `alembic/env.py` so the metadata is populated:

```python
# alembic/env.py
import src.modules.users.models  # noqa: F401
import src.modules.matches.models  # noqa: F401

target_metadata = Base.metadata
```

3. Generate the migration:

```bash
poetry run alembic revision --autogenerate -m "add {name} table"
```

4. Review the generated file in `alembic/versions/` — always check auto-generated migrations before applying.
5. Apply:

```bash
poetry run alembic upgrade head
```

---

## Rules

- Always review auto-generated migration scripts — Alembic may miss renames or complex constraints.
- Never edit an already-applied migration. Create a new one instead.
- Run `alembic upgrade head` in CI before integration/API tests (see `.github/workflows/ci.yml`).
- Never run migrations against the production database without a tested rollback plan.
