# CONDAMAD Code Review

## Review target

- Story: `CS-180-aligner-registre-modeles-db-infra`
- Capsule: `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/`
- Verdict: `CLEAN`
- Review/fix iterations in this closure run: 1
- Review date: 2026-05-16

## Inputs reviewed

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/00-story.md`
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/generated/06-validation-plan.md`
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/generated/07-no-legacy-dry-guardrails.md`
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/generated/10-final-evidence.md`
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-before.md`
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-after.md`
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-table-exception-register.md`
- `backend/app/infra/db/base.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/infra/db/models/flagged_content.py`
- `backend/app/tests/unit/test_db_model_registry_guard.py`
- `backend/app/api/v1/routers/admin/support.py`
- `backend/app/core/scheduler.py`
- `git diff`, `git diff --check`, `git status --short`

## Diff summary

- `FlaggedContentModel` is imported and exported by the root non-LLM model registry.
- `Base.metadata` loads both the root non-LLM registry and the separated LLM registry.
- The CS-180 unit guard checks model declarations, loaded metadata, exact table exceptions, and destructive-scan constraints.
- Story evidence persists the before/after DB-model registry audit and exact exception register.
- `_condamad/stories/regression-guardrails.md` now records `RG-111` for the DB model registry invariant.

## Review layers

| Layer | Result | Notes |
|---|---|---|
| Diff integrity | CLEAN | Changed and untracked files are scoped to CS-180 implementation/evidence/status. |
| Acceptance audit | CLEAN | AC1-AC5 are mapped to code and passing validation evidence. |
| Validation audit | CLEAN | Ruff, targeted tests, integration test, full pytest, `git diff --check`, and negative scan were rerun. |
| DRY / No Legacy audit | CLEAN | No duplicate registry, route opportunism, wildcard exception, shim, alias, or destructive cleanup introduced. |
| Edge/security/data audit | CLEAN | DB access in the guard is read-only; no runtime HTTP/API contract change or secret/config change detected. |
| Regression guardrails | CLEAN | `RG-005`, `RG-008`, `RG-011`, and new `RG-111` are covered by evidence. |

## Findings

No actionable findings in this fresh review iteration.

Previously recorded issue `CR-1 High - Guard depended on ignored local DB` remains resolved in the current code: `_sqlite_table_names()` reads `backend/horoscope.db` when present and otherwise falls back to tracked model declarations plus the exact exception register, while the guard still independently verifies every declared model table is loaded in `Base.metadata`.

## Acceptance audit

| AC | Status | Evidence |
|---|---|---|
| AC1 | PASS | `flagged_contents` is declared by `FlaggedContentModel`, exported by `models/__init__.py`, and present in `Base.metadata.tables`; `pytest -q app/tests/unit/test_db_model_registry_guard.py` passed. |
| AC2 | PASS | `db-table-exception-register.md` lists four exact exceptions; the unit guard rejects forbidden wildcard patterns and passed. |
| AC3 | PASS | `db-model-registry-after.md` reports no model table missing from `Base.metadata` and no SQLite modeled table missing from metadata; full guard passed. |
| AC4 | PASS | `pytest -q --long app/tests/integration/test_admin_support_api.py` passed, preserving `FlaggedContentModel` support usage. |
| AC5 | PASS | Modified implementation/evidence files have zero `drop_table(` or `DROP TABLE` hits; no migration or DB file changed. |

## Validation audit

All Python commands below were run after `.\.venv\Scripts\Activate.ps1`.

| Command | Result |
|---|---|
| `ruff format .` from `backend/` | PASS - 1389 files left unchanged. |
| `ruff check .` from `backend/` | PASS - all checks passed. |
| `pytest -q app/tests/unit/test_db_model_registry_guard.py` from `backend/` | PASS - 4 passed. |
| `pytest -q --long app/tests/integration/test_admin_support_api.py` from `backend/` | PASS - 1 passed. |
| `pytest -q` from `backend/` | PASS - 2595 passed, 1 skipped, 1175 deselected. |
| `git diff --check` from repo root | PASS - no whitespace/conflict errors; Git emitted line-ending warnings only. |
| `rg -n "drop_table\\(|DROP TABLE" ...modified CS-180 files...` from repo root | PASS - exit 1, zero matches. |

## DRY / No Legacy audit

- No second active SQLAlchemy registry was introduced.
- LLM models remain owned and exported by `app.infra.db.models.llm`; `base.py` imports that registry only for metadata loading side effects.
- The root non-LLM registry exports `FlaggedContentModel` exactly once.
- The table exception register uses exact names only and contains no wildcard family such as `llm_*`, `_alembic_*`, or `*_archives`.
- No compatibility wrapper, fallback, alias, re-export legacy, or destructive DB cleanup was added.

## Commands run by reviewer

- `git status --short`
- `git diff --stat`
- `git diff -- backend/app/infra/db/base.py backend/app/infra/db/models/__init__.py backend/app/tests/unit/test_db_model_registry_guard.py`
- `git diff --check`
- `git ls-files --others --exclude-standard`
- `rg -n "drop_table\\(|DROP TABLE" backend/app/infra/db/base.py backend/app/infra/db/models/__init__.py backend/app/tests/unit/test_db_model_registry_guard.py _condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-table-exception-register.md _condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-after.md`
- `rg -n "flagged_contents|FlaggedContentModel|llm_prompt_version_fallback_archives|SQLAlchemyJobStore|astrologer_prompt_profiles" backend/app backend/tests _condamad/stories/CS-180-aligner-registre-modeles-db-infra -g "*.py" -g "*.md"`

## Residual risks

None identified.

## Verdict

`CLEAN`
