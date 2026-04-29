# No Legacy / DRY Guardrails

## Canonical source

- `backend/pyproject.toml` is the single pytest discovery configuration for the backend standard command.
- Runtime collection via `pytest --collect-only -q --ignore=.tmp-pytest` is the source of truth for collected files.

## Forbidden patterns

- Keeping `app/ai_engine/tests` in `testpaths` while the directory is absent.
- Creating a second pytest configuration file.
- Adding a helper script that becomes an alternate standard collection path.
- Excluding retained test roots silently.
- Adding wildcard opt-in exceptions without explicit file-level justification.

## Required negative evidence

- `rg -n "app/ai_engine/tests" backend/pyproject.toml`
- Static inventory of `test_*.py` and `*_test.py` under `backend/`.
- Runtime collected file inventory from pytest.
- `uncollected-tests-after.md` with zero uncollected retained files or exact approved exceptions.

## Regression guardrails

All active registry invariants `RG-001` through `RG-009` apply because this story controls whether their backend guard tests are collected by the standard command.

## Review checklist

- One source of pytest discovery configuration remains.
- Every configured `testpaths` entry exists.
- Every retained backend test file is collected or explicitly listed as opt-in.
- The only approved opt-in exception is `app/domain/llm/prompting/tests/test_qualified_context.py` unless reviewer approval changes this story.
- No compatibility shim, alias, fallback, or duplicate collection command was introduced.
