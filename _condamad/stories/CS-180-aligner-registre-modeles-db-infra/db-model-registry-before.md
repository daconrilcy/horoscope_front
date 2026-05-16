# DB Model Registry Audit Before

## Command

Executed from `backend/` after activating `.\.venv\Scripts\Activate.ps1`.

## Summary

| Inventory | Count |
|---|---:|
| SQLite tables in `backend/horoscope.db` | 129 |
| SQLAlchemy model tables declared under `app/infra/db/models` | 125 |
| Tables loaded in `Base.metadata` | 111 |

## SQLite Tables Without Model File

| Table | Classification |
|---|---|
| `_alembic_tmp_astrologer_profiles` | Historical local Alembic temporary table; out of destructive cleanup scope. |
| `alembic_version` | Alembic technical table. |
| `apscheduler_jobs` | APScheduler technical table. |
| `llm_prompt_version_fallback_archives` | Empty migration archive table pending separate LLM archive decision. |

## Model Tables Missing From Base.metadata

| Table | Before classification |
|---|---|
| `flagged_contents` | Defect: model exists but root registry does not load it. |
| `llm_active_releases` | LLM model registry is separate and not loaded by current `Base.metadata` import path. |
| `llm_assembly_configs` | LLM model registry is separate and not loaded by current `Base.metadata` import path. |
| `llm_call_log_operational_metadata` | LLM model registry is separate and not loaded by current `Base.metadata` import path. |
| `llm_call_logs` | LLM model registry is separate and not loaded by current `Base.metadata` import path. |
| `llm_canonical_consumption_aggregates` | LLM model registry is separate and not loaded by current `Base.metadata` import path. |
| `llm_execution_profiles` | LLM model registry is separate and not loaded by current `Base.metadata` import path. |
| `llm_output_schemas` | LLM model registry is separate and not loaded by current `Base.metadata` import path. |
| `llm_personas` | LLM model registry is separate and not loaded by current `Base.metadata` import path. |
| `llm_prompt_versions` | LLM model registry is separate and not loaded by current `Base.metadata` import path. |
| `llm_release_snapshots` | LLM model registry is separate and not loaded by current `Base.metadata` import path. |
| `llm_replay_snapshots` | LLM model registry is separate and not loaded by current `Base.metadata` import path. |
| `llm_sample_payloads` | LLM model registry is separate and not loaded by current `Base.metadata` import path. |
| `llm_use_case_configs` | LLM model registry is separate and not loaded by current `Base.metadata` import path. |

## Closure Target

- `flagged_contents` must be loaded by the root non-LLM registry.
- LLM tables must be loaded into `Base.metadata` through the existing LLM registry without duplicating LLM exports in the root non-LLM registry.
- The four SQLite tables without model files must remain exact classified exceptions.
