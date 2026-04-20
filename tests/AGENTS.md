# AGENTS.md — Tests (`tests/`)

Testing guideline for `pickla-api-v1` (FastAPI + pytest).  
Goal: keep tests deterministic, fast, and production-relevant.

## Current Stack

- Test runner: `pytest`
- HTTP testing: `fastapi.testclient` (sync) and `httpx` (async-ready)
- Async support: `pytest-asyncio`
- App entrypoint: `src.main:app`

## Directory Structure

```text
tests/
├── unit/                        # pure business logic tests (no I/O)
├── integration/                 # DB/repository/service integration tests
└── api/                         # endpoint-level behavior tests
```

Notes:
- Mirror `src/` layout when adding new tests (example: `src/modules/auth/...` -> `tests/api/modules/auth/...`).
- Keep shared helpers in `tests/conftest.py` or `tests/helpers/` when the suite grows.

## Naming Conventions

- File names: `test_<feature>.py`
- Test names: `test_<expected_behavior>()`
- One behavior per test function.
- Use Arrange / Act / Assert structure for readability.

## Test Levels (Production Convention)

### 1) Unit tests
- No network, no database, no filesystem.
- Cover validation, transformation, and domain logic.

### 2) Integration tests
- Use real integration boundaries (database session, repository, migration-ready schema).
- Keep data setup explicit and isolated per test.

### 3) API tests
- Verify request/response contract: status code, payload shape, and error behavior.
- Include auth and permission scenarios when auth is added.

## Rules

### Do

- Prefer fixtures over duplicated setup code.
- Keep tests deterministic (no random time/ID without control).
- Assert behavior and contracts, not internal implementation details.
- Add regression tests for every bug fix.
- Keep tests independent; each test must pass when run alone.

### Don't

- Do not depend on execution order.
- Do not call external services in unit tests.
- Do not share mutable global state across tests.
- Do not hide complex setup inside unclear fixtures.

## No Mock / No Stub Policy

For this project, prefer real behavior over simulated behavior:

- Do not use `unittest.mock`, monkeypatching, or fake service stubs for core business logic tests.
- Unit tests should validate pure functions/domain rules with real inputs.
- Integration tests should use a real test database and real repository/service wiring.
- API tests should call the real FastAPI app (`TestClient` or `httpx.AsyncClient`) and assert contract outputs.

Allowed exception:
- Temporary mock/stub is acceptable only for uncontrollable external systems (third-party APIs) and must be documented in the test file.

## Fixture Guidelines

- `tests/conftest.py` should contain only reusable fixtures/bootstrap.
- Scope carefully:
  - `function` scope by default.
  - `session` scope only for expensive immutable resources.
- Prefer explicit fixture injection in test signatures.

## Factory-Based Test Data

Use factories to keep data realistic and reusable.

Recommended layout:

```text
tests/
├── factories/
│   ├── user_factory.py
│   └── auth_factory.py
```

Example factory (`tests/factories/auth_factory.py`):

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterPayload:
    email: str
    password: str
    full_name: str


def build_register_payload(
    email: str = "alice@example.com",
    password: str = "StrongPass123!",
    full_name: str = "Alice Nguyen",
) -> RegisterPayload:
    return RegisterPayload(email=email, password=password, full_name=full_name)
```

Usage in tests:

```python
def test_register_payload_has_required_fields() -> None:
    payload = build_register_payload()

    assert payload.email.endswith("@example.com")
    assert len(payload.password) >= 8
```

## Async and Event Loop

- Use `@pytest.mark.asyncio` for async test functions.
- For async API tests, prefer `httpx.AsyncClient` with ASGI app.
- Avoid mixing sync and async clients in the same test unless necessary.

## Database Testing (When DB tests are added)

- Use a dedicated test database URL.
- Run migrations before integration/api DB test jobs.
- Wrap each test in transaction rollback strategy, or recreate schema per test module.
- Never run tests against production/staging database.

## Required Commands

```bash
poetry run pytest -q
poetry run pytest tests/test_main.py -q
poetry run ruff check .
poetry run mypy
```

## Minimal API Test Pattern

```python
from fastapi.testclient import TestClient

from src.main import app


def test_docs_endpoint_is_available() -> None:
    client = TestClient(app)
    response = client.get("/docs")

    assert response.status_code == 200
```

## Business Logic Test Examples

### 1) Unit example (validation rule)

```python
import pytest


@pytest.mark.parametrize(
    ("password", "expected"),
    [
        ("StrongPass123!", True),
        ("short", False),
        ("alllowercase123", False),
    ],
)
def test_password_policy(password: str, expected: bool) -> None:
    result = is_valid_password(password)  # from your domain/service layer
    assert result is expected
```

### 2) Integration example (real DB, no mock)

```python
async def test_create_user_persists_to_database(db_session: AsyncSession) -> None:
    payload = build_register_payload()

    user = await user_service.create_user(
        db=db_session,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )

    await db_session.flush()
    assert user.id is not None
    assert user.email == payload.email
```

### 3) API example (real app contract)

```python
def test_health_endpoint_returns_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

## Coverage Targets

- Focus first on critical business flows (auth, permission, payment, state transitions).
- Minimum target for CI:
  - New modules: >= 90%
  - Whole repository baseline: increase over time, do not decrease in PRs.
- Every bug fix must include at least one regression test.
- Do not chase coverage numbers by testing framework internals; prioritize business outcomes.

## Checklist — Adding New Tests

- [ ] Test file path mirrors related code in `src/`
- [ ] Happy path covered
- [ ] Error/edge case covered
- [ ] No shared mutable state
- [ ] `pytest -q` passes locally
- [ ] Lint/type checks still pass (`ruff`, `mypy`)
