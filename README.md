# Pickla API V1

[![codecov](https://codecov.io/gh/vunontay/pickla-api-v1/graph/badge.svg?token=D8ZZIV3Z2H)](https://codecov.io/gh/vunontay/pickla-api-v1)

Backend service for **Pickla** — a mobile-first Pickleball matchmaking platform for the Vietnamese community.

Hosts post open match sessions; Joiners browse and join them. A Reputation Score system replaces financial deposits to build community trust.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python `>=3.12` |
| Framework | FastAPI + Uvicorn |
| Database | PostgreSQL 16 (SQLAlchemy async + asyncpg) |
| Cache | Redis 7 |
| Migrations | Alembic |
| Config | Pydantic Settings |
| Package Manager | Poetry |
| Containerization | Docker + Docker Compose |
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
│   │   ├── auth/              # Registration, login, JWT
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
├── docker/
├── alembic/
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
└── .env.example
```

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + [Docker Compose](https://docs.docker.com/compose/)
- Python `>=3.12` + [Poetry](https://python-poetry.org/docs/#installation) (for local development without Docker)

---

## Quick Start (Docker)

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd pickla-api-v1

# 2. Copy environment file
cp .env.example .env

# 3. Start all services (API + PostgreSQL + Redis)
docker compose up -d

# 4. Check services are running
docker compose ps
```

| Service | URL |
|---------|-----|
| API | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v
```

---

## Local Development (without Docker)

1. Install dependencies:

```bash
poetry install
```

2. Copy the environment file and fill in your values:

```bash
cp .env.example .env
```

3. Run the server:

```bash
poetry run uvicorn src.main:app --reload
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://pickla:pickla@postgres:5432/pickla` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379` |
| `SECRET_KEY` | JWT signing secret | `your-secret-key` |
| `DEBUG` | Enable debug mode | `True` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token TTL | `60` |

> When running locally (without Docker), use `localhost` instead of the service names `postgres` / `redis`.

---

## Database Migrations

```bash
# Create a new migration
poetry run alembic revision --autogenerate -m "description"

# Apply all pending migrations
poetry run alembic upgrade head

# Rollback one step
poetry run alembic downgrade -1
```

---

## API Overview

| Group | Prefix | Description |
|-------|--------|-------------|
| Auth | `/api/v1/auth/` | Register, login, token refresh, logout |
| Users | `/api/v1/users/` | Profile CRUD, reputation history |
| Matches | `/api/v1/matches/` | Match feed, create/edit/cancel, join/leave |
| Reports | `/api/v1/reports/` | Submit and review misconduct reports |
| Ratings | `/api/v1/ratings/` | Post-match ratings (1–5 stars) |
| Admin | `/api/v1/admin/` | User moderation, reputation adjustment |

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
poetry run pytest -q

# Run with coverage
poetry run pytest --cov=src --cov-report=term-missing -q
```

> See `tests/AGENTS.md` for full conventions, patterns, and examples.

---

## Notes

- See `AGENTS.md` at the project root for architecture rules and agent guidance.
- See `docs/PRD.md` for full product requirements and data model definitions.
