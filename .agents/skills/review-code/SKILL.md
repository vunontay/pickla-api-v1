---
name: review-code
description: Review code changes in pickla-api-v1 against project standards: layer architecture, TDD compliance, Pydantic schemas, FastAPI patterns, async DB rules, security, and performance. Use when reviewing a pull request, examining a diff, auditing a module, or when the user asks for a code review.
---

# Code Review — pickla-api-v1

## Workflow

1. Read the changed files (or diff).
2. Run each checklist section below — mark each item ✅ pass / ❌ fail / ⚠️ warning.
3. Output a structured review with severity labels.
4. Suggest concrete fixes for every ❌.

---

## Checklist

### 1. Layer Architecture

- [ ] `router.py` contains **no business logic** — only HTTP binding, DI, and service calls.
- [ ] `service.py` contains **no ORM queries** — delegates all DB access to `repository.py`.
- [ ] `repository.py` contains **no business logic** — only SQLAlchemy statements.
- [ ] New modules follow the 4-file structure: `router.py`, `service.py`, `repository.py`, `schemas.py`.
- [ ] New module router is mounted in `src/api/v1.py`.

### 2. Database & Async

- [ ] All DB calls use `await session.execute(...)` — no sync SQLAlchemy in `async def`.
- [ ] Session is injected via `Depends(get_db)` — `SessionLocal()` is never instantiated manually.
- [ ] `commit()` is called **only in `service.py`** — repositories use `flush()` + `refresh()`.
- [ ] `expire_on_commit=False` is respected (already set globally — do not override).

### 3. Pydantic Schemas

- [ ] Input schema named `{Entity}Request`, output schema named `{Entity}Response`.
- [ ] Response schemas include `model_config = {"from_attributes": True}` when built from ORM models.
- [ ] No sensitive/internal fields (hashed password, raw tokens) exposed in any `*Response`.
- [ ] ORM → response conversion uses `model_validate()`, not manual dict construction.
- [ ] No `RootModel` usage — use `Annotated[list[T], Body(...)]` instead.

### 4. FastAPI Patterns

- [ ] Every endpoint has an explicit return type annotation.
- [ ] Dependencies use `Annotated[T, Depends(...)]` type aliases — not inline `= Depends(...)`.
- [ ] Path/query/body constraints use `Path`, `Query`, `Body` — not `pydantic.Field`.
- [ ] One HTTP method per function — no `api_route(methods=[...])` with multiple verbs.
- [ ] Router declares `prefix` and `tags` on `APIRouter(...)`, not in `include_router()`.
- [ ] All path operations are `async def`.

### 5. TDD Compliance

- [ ] Every new production code path has a corresponding test.
- [ ] Bug fixes include a regression test that fails before the fix.
- [ ] Tests mirror `src/` layout: `src/modules/auth/` → `tests/api/modules/auth/`.
- [ ] No `unittest.mock`, `monkeypatch`, or fake stubs for core business logic.
- [ ] New modules achieve ≥ 90% coverage.
- [ ] Each test covers exactly one behavior (one `assert` per logical outcome).

### 6. Security

- [ ] No `.env` or secrets committed — only `.env.example`.
- [ ] No credentials or API keys hardcoded in source files.
- [ ] Passwords are hashed via `src/shared/auth/hashing.py` — never stored plaintext.
- [ ] JWT operations use `src/shared/auth/jwt.py` — no raw `python-jose` calls in modules.
- [ ] Auth-protected endpoints use the correct dependency for the current user.
- [ ] No raw SQL strings — all queries via SQLAlchemy ORM.

### 7. Performance & Async

- [ ] No blocking I/O (`open()`, `requests.get()`, `time.sleep()`) inside `async def`.
- [ ] N+1 query risk identified and flagged (lazy loading in a loop).
- [ ] Heavy computation is not run synchronously on the event loop.

### 8. Settings

- [ ] Settings accessed via `from src.shared.configs.settings import settings` singleton.
- [ ] New env vars added to both `Settings` class and `.env.example`.

---

## Severity Labels

| Label | Meaning |
|---|---|
| 🔴 **Block** | Must fix before merge — violates non-negotiable rules |
| 🟡 **Warn** | Should fix — degrades quality but not a hard blocker |
| 🟢 **Suggest** | Optional improvement |

---

## Output Format

```
## Review Summary

**Status**: ✅ Approved / ❌ Changes Requested

---

### 🔴 Blocking Issues
1. `service.py:42` — ORM query inside service. Move to `repository.py`.

### 🟡 Warnings
1. `schemas.py:15` — Missing `model_config = {"from_attributes": True}` on `UserResponse`.

### 🟢 Suggestions
1. `router.py:8` — Consider extracting the `Annotated[AsyncSession, Depends(get_db)]` alias to a shared file.

---

### Tests
- Coverage: [estimated / measured]
- Missing test for: [describe scenario]
```

---

## Common Violations (Quick Reference)

| ❌ Violation | ✅ Fix |
|---|---|
| ORM query in `service.py` | Move to `repository.py` |
| Business logic in `router.py` | Move to `service.py` |
| `= Depends(get_db)` inline | Use `Annotated[AsyncSession, Depends(get_db)]` |
| Single schema for input + output | Split into `*Request` / `*Response` |
| `session.commit()` in repository | Move commit to service |
| Missing return type on endpoint | Add `-> {Entity}Response` |
| `Settings()` instantiated directly | Use `settings` singleton |
| Sync DB call in async handler | Add `await` to `session.execute(...)` |
| No test for new code | Write failing test first (TDD Red step) |
