---
name: pull-request-description
description: Generate a pull request description for pickla-api-v1 following the project PR template. Use when opening a PR or when asked to write a PR description.
---

# Pull Request Description Generator

Generate a complete PR description for `pickla-api-v1` following the project's PR template.

## Steps

### 1. Gather context

Run these commands in parallel to understand what is changing:

```bash
# All changed files vs base branch
git diff develop...HEAD --stat

# Full diff for content analysis
git diff develop...HEAD

# Commits on this branch
git log develop...HEAD --oneline

# Current branch name (may hint at ticket or feature)
git branch --show-current
```

If the branch has no upstream or `develop` doesn't exist, fall back to:

```bash
git diff HEAD~1 --stat
git diff HEAD~1
git log --oneline -10
```

### 2. Analyse the diff

Identify:
- **Type of change**: feat / fix / refactor / perf / test / docs / chore
- **Modules touched**: which `src/modules/{name}/` directories changed
- **Layer changes**: router, service, repository, schemas, models, shared, tests
- **New endpoints**: method + path (e.g. `POST /api/v1/matches`)
- **Migration**: are there new files in `alembic/versions/`?
- **New env vars**: any additions to `Settings` or `.env.example`?
- **Breaking changes**: schema renames, endpoint removals, config changes

### 3. Fill the template

Read `.github/PULL_REQUEST_TEMPLATE.md` to get the exact template structure, then fill every section based on your analysis. Use HTML comments for optional empty sections. Do not omit any section.

---

## Filling Rules

### Summary
Write 1–2 sentences: what the PR does and why. Focus on **intent**, not implementation.

> ✅ "Adds the match creation endpoint so hosts can post open sessions for joiners to browse."
> ❌ "Added router.py and service.py and schemas.py for the matches module."

### Type of Change
Check **exactly one** box (replace `[ ]` with `[x]`).

### Changes
- One bullet per meaningful unit of change.
- Be concrete: prefer "Added `POST /api/v1/matches`" over "Added match endpoint".
- Group by layer if many changes: endpoints → service logic → repository → schemas → tests.

### Testing
Give the reviewer actionable steps to verify the feature works.
Always include: what to call, what payload/params to use, what response to expect.

### Deploy Notes
Required if any of these are true:
- New Alembic migration → "Run `poetry run alembic upgrade head` before deploying."
- New env var → list the var name and where it goes in `.env.example`.
- Breaking API change → note what consumers need to update.
- Deploy order dependency → e.g., "Deploy DB migration before API."

### Checklist
Check every box that applies. Leave unchecked only if genuinely not applicable (e.g., no new env vars → leave that box unchecked and add a note).

## Output Format

Output only the filled PR description as a Markdown code block so it can be copy-pasted directly. Do not add commentary before or after unless the user asks for an explanation.
