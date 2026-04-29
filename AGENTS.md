# AGENTS.md

> Entry point for AI agents. This is a **map**, not a handbook — follow the pointers for details.

---

## Product

**Pickla** — Pickleball matchmaking platform in Vietnam.
Hosts post sessions, Joiners browse and join. A **Reputation Score** (starts at 100) deters no-shows.

---

## Stack


|                 |                                                     |
| --------------- | --------------------------------------------------- |
| Language        | Python 3.12                                         |
| Framework       | FastAPI                                             |
| Database        | PostgreSQL · SQLAlchemy 2 async · asyncpg · Alembic |
| Config          | pydantic-settings (`.env`)                          |
| Auth            | JWT (access + refresh) · bcrypt                     |
| Testing         | pytest · pytest-asyncio · httpx                     |
| Linting         | ruff · mypy                                         |
| Package manager | Poetry                                              |


---

## Knowledge Base


| Topic                                             | Read                                           |
| ------------------------------------------------- | ---------------------------------------------- |
| Directory layout, layers, naming, adding a module | [docs/architecture.md](docs/architecture.md) |
| Coding rules and common pitfalls                  | [docs/coding-rules.md](docs/coding-rules.md) |
| Writing and running tests                         | [docs/testing.md](docs/testing.md)           |
| Running Alembic migrations                        | [docs/migrations.md](docs/migrations.md)     |
| Product requirements                              | [docs/PRD.md](docs/PRD.md)                   |


---

## Decision Tree


| Task                                  | Go to                                                  |
| ------------------------------------- | ------------------------------------------------------ |
| Add or change an endpoint             | `docs/architecture.md` → `modules/{mod}/router.py`     |
| Add or change business logic          | `docs/architecture.md` → `modules/{mod}/service.py`    |
| Add or change a DB query              | `docs/architecture.md` → `modules/{mod}/repository.py` |
| Add or change request/response schema | `docs/architecture.md` → `modules/{mod}/schemas.py`    |
| Add a new module                      | `docs/architecture.md` → "Adding a New Module"         |
| Add a DB model / run a migration      | `docs/migrations.md`                                   |
| Write or fix tests                    | `docs/testing.md`                                      |
| Change config or env vars             | `docs/coding-rules.md` → Settings                      |
| Auth / JWT / hashing                  | `src/shared/auth/`                                     |
| Error handling                        | `src/shared/errors/`                                   |
| Reputation score logic                | `modules/users/service.py`                             |
| Match join eligibility                | `modules/matches/service.py`                           |


---

## Non-Negotiable Rules

These apply everywhere — no exceptions:

1. **Never write ORM queries in `service.py`** — they belong in `repository.py`.
2. **Never write business logic in `router.py`** — it belongs in `service.py`.
3. **All DB operations must be async** — `await session.execute(...)` only.
4. **Never instantiate `SessionLocal()` manually** — use `Depends(get_db)`.
5. **Never reuse the same schema for input and output** — split into `*Request` / `*Response`.
6. **Never commit `.env`** — only `.env.example`.
7. **Always follow TDD** — write failing test first, then implement, then refactor.

---

## Before Any Task

1. Read this file.
2. Identify which module(s) the task touches.
3. Follow the Decision Tree above to the relevant `docs/` file.
4. For reputation-sensitive work (score changes, match state transitions), also read `docs/PRD.md`.
