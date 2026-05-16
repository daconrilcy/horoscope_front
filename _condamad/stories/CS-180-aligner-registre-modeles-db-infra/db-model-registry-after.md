# DB Model Registry Audit After

## Command

Executed from `backend/` after activating `.\.venv\Scripts\Activate.ps1`.

## Summary

| Inventory | Count |
|---|---:|
| SQLite tables in `backend/horoscope.db` | 129 |
| SQLAlchemy model tables declared under `app/infra/db/models` | 125 |
| Tables loaded in `Base.metadata` | 125 |

## SQLite Tables Without Model File

| Table | Classification |
|---|---|
| `_alembic_tmp_astrologer_profiles` | Exact historical local Alembic temporary table; out of destructive cleanup scope. |
| `alembic_version` | Exact Alembic technical table. |
| `apscheduler_jobs` | Exact APScheduler technical table. |
| `llm_prompt_version_fallback_archives` | Exact LLM migration archive table pending separate decision. |

## Model Tables Missing From Base.metadata

None.

## SQLite Tables With Model But Missing From Base.metadata

None.

## Closure Evidence

- `flagged_contents` is declared by `FlaggedContentModel` and loaded in `Base.metadata`.
- LLM model tables remain owned by `app.infra.db.models.llm` and are loaded into `Base.metadata` through the central base module.
- Remaining SQLite tables without models match `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-table-exception-register.md` exactly.
