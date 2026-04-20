# Pickla API V1

Backend service for **Pickla** — a mobile-first Pickleball matchmaking platform for the Vietnamese community.

Hosts post open match sessions; Joiners browse and join them. A Reputation Score system replaces financial deposits to build community trust.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python `>=3.12` |
| Framework | FastAPI + Uvicorn |
| Database | PostgreSQL 16 (SQLAlchemy async + asyncpg) |
| Migrations | Alembic |
| Config | Pydantic Settings |
| Package Manager | Poetry |
| Testing | pytest + pytest-asyncio + httpx |
| Linting | ruff + mypy |

---

## Project Structure

```text
pickla-api-v1/
├── src/
│   ├── main.py
│   ├── api/
│   │   └── v1.py              # Aggregates all module routers
│   ├── modules/
│   │   ├── auth/              # Registration, OTP, social login, JWT
│   │   ├── users/             # User profiles, reputation log
│   │   ├── matches/           # Match feed, create/join/leave/confirm
│   │   ├── reports/           # Report no-shows and misconduct
│   │   ├── ratings/           # Post-match ratings
│   │   └── admin/             # Admin dashboard and moderation
│   └── shared/
│       ├── auth/              # JWT + bcrypt hashing utilities
│       ├── configs/
│       │   └── settings.py    # Environment config (pydantic-settings)
│       ├── database/
│       │   ├── session.py     # Async engine + SessionLocal
│       │   └── dependencies.py
│       └── errors/
├── tests/
│   ├── conftest.py
│   └── test_main.py
├── alembic/
├── alembic.ini
├── pyproject.toml
└── .env.example
```

---

## Prerequisites

- Python `>=3.12` (managed via [asdf](https://asdf-vm.com/) or system install)
- [Poetry](https://python-poetry.org/docs/#installation)
- PostgreSQL running locally (or via Docker)

---

## Installation

1. Move into the project directory:

```bash
cd pickla-api-v1
```

2. Install dependencies:

```bash
poetry install
```

3. Copy the environment file:

```bash
cp .env.example .env
```

4. Fill in your values in `.env`:

```env
DATABASE_URL=postgresql+asyncpg://pickla:pickla@localhost/pickla
SECRET_KEY=your-secret-key
DEBUG=True
```

---

## Run the Application

```bash
poetry run uvicorn src.main:app --reload
```

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/api/v1` | API base |
| `http://127.0.0.1:8000/docs` | Swagger UI |
| `http://127.0.0.1:8000/redoc` | ReDoc |

---

## API Overview

| Group | Prefix | Description |
|-------|--------|-------------|
| Auth | `/api/v1/auth/` | Register (phone+OTP), social login (Google/Facebook), token refresh, logout |
| Users | `/api/v1/users/` | Profile CRUD, public profile, reputation history |
| Matches | `/api/v1/matches/` | Match feed (with filters), create/edit/cancel, join/leave, confirm attendance |
| Reports | `/api/v1/reports/` | Submit and review misconduct reports |
| Ratings | `/api/v1/ratings/` | Post-match ratings (1–5 stars) |
| Admin | `/api/v1/admin/` | User moderation, reputation adjustment, platform stats |

---

## Database Migrations

Create a new migration:

```bash
poetry run alembic revision --autogenerate -m "description"
```

Apply all pending migrations:

```bash
poetry run alembic upgrade head
```

Rollback one step:

```bash
poetry run alembic downgrade -1
```

---

## Development Commands

```bash
# Lint
poetry run ruff check .

# Auto-fix lint
poetry run ruff check . --fix

# Format
poetry run ruff format .

# Type check
poetry run mypy
```

---

## Testing

```bash
# Run all tests
poetry run pytest

# Run a specific file
poetry run pytest tests/test_main.py -v

# Run with stdout
poetry run pytest -s
```

> Always run tests via `poetry run pytest` to use the correct Python 3.12 virtualenv.
> See `tests/AGENTS.md` for full conventions, patterns, and examples.

---

## Notes

- See `AGENTS.md` at the project root for architecture rules, domain business logic, and agent guidance.
- See `docs/PRD.md` for full product requirements and data model definitions.
