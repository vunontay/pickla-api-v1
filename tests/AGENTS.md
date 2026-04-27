# AGENTS.md — tests/

> Full testing guide: [`docs/testing.md`](../docs/testing.md)

---

## Quick Reference

```bash
poetry run pytest -q
poetry run pytest --cov=src --cov-report=term-missing
```

- Mirror `src/` layout when adding test files.
- Use `db_session` and `client` fixtures from `conftest.py`.
- No mocks for core business logic — use real DB and real app.
- One behavior per test function. Arrange / Act / Assert.
