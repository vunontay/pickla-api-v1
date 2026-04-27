# Testing Guide

> Authoritative testing reference for `pickla-api-v1`.
> Goal: deterministic, fast, production-relevant tests.

---

## Stack

| Tool | Role |
|---|---|
| `pytest` | Test runner |
| `pytest-asyncio` (`asyncio_mode = "auto"`) | Async test support |
| `httpx.AsyncClient` + `ASGITransport` | Async API tests |
| `fastapi.testclient.TestClient` | Sync smoke tests |

---

## Directory Layout

```
tests/
├── conftest.py          # Shared fixtures — keep minimal
├── factories/           # Test data builders
│   ├── user_factory.py
│   └── auth_factory.py
├── unit/                # Pure logic — no I/O
├── integration/         # Real DB — repository/service level
└── api/                 # Endpoint contract tests
```

Mirror `src/` layout: `src/modules/auth/` → `tests/api/modules/auth/`.

---

## Test Levels

### Unit
- No network, no database, no filesystem.
- Cover validation, transformation, and pure domain logic.

### Integration
- Use a real test database (`TEST_DATABASE_URL` from `.env`).
- Real repository/service wiring — no mocks.
- Keep data setup explicit and isolated per test.

### API
- Call the real FastAPI app via `httpx.AsyncClient`.
- Assert: status code, response payload shape, error behavior.
- Include auth and permission scenarios.

---

## No Mock / No Stub Policy

Prefer real behavior:

- Do **not** use `unittest.mock`, `monkeypatch`, or fake service stubs for core business logic.
- Unit tests → real inputs, pure functions.
- Integration tests → real DB, real repo/service.
- API tests → real app (`AsyncClient` or `TestClient`).

**Allowed exception**: third-party external APIs that cannot be controlled in CI. Must be documented in the test file.

---

## Naming Conventions

- Files: `test_<feature>.py`
- Functions: `test_<expected_behavior>()`
- One behavior per function.
- Use Arrange / Act / Assert structure.

---

## Fixtures

```python
# tests/conftest.py
@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
```

- Default scope: `function`.
- `session` scope only for expensive immutable resources.
- Keep `conftest.py` minimal — move complex helpers to `tests/helpers/`.

---

## Factory Pattern

Use factories for realistic, reusable test data.

```python
# tests/factories/auth_factory.py
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

---

## Test Examples

### Unit — validation rule

```python
@pytest.mark.parametrize(
    ("password", "expected"),
    [
        ("StrongPass123!", True),
        ("short", False),
        ("alllowercase123", False),
    ],
)
def test_password_policy(password: str, expected: bool) -> None:
    result = is_valid_password(password)
    assert result is expected
```

### Integration — real DB, no mock

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

### API — contract test

```python
async def test_health_endpoint_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

---

## Database Testing Rules

- Use `TEST_DATABASE_URL` — never run tests against production.
- Run `alembic upgrade head` before integration/API DB test jobs.
- Wrap each test in a transaction rollback or recreate the schema per module.

---

## Coverage Targets

- New modules: ≥ 90%.
- Repository baseline: never decrease in PRs.
- Every bug fix → at least one regression test.
- Do not chase coverage by testing framework internals — prioritize business outcomes.

---

## Commands

```bash
poetry run pytest -q
poetry run pytest --cov=src --cov-report=term-missing
poetry run ruff check .
poetry run mypy
```

---

## Checklist — Adding New Tests

- [ ] Test file path mirrors related `src/` path
- [ ] Happy path covered
- [ ] Error / edge case covered
- [ ] No shared mutable state between tests
- [ ] `pytest -q` passes locally
- [ ] Lint and type checks pass (`ruff`, `mypy`)
