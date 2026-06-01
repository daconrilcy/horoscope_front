# Validation Plan

## Executed

| Command | Working directory | Result |
|---|---|---|
| `ruff format app\infra\db\models\theme_natal_reading_slot.py app\infra\db\models\llm_generation_run.py app\infra\db\models\__init__.py app\services\llm_generation\natal\theme_natal_reading_slots.py migrations\versions\20260601_0142_create_theme_natal_reading_slots.py tests\integration\test_theme_natal_reading_slots.py tests\unit\test_natal_chart_long_quota_on_acceptance.py` | `backend` | PASS |
| `ruff check app\infra\db\models\theme_natal_reading_slot.py app\infra\db\models\llm_generation_run.py app\infra\db\models\__init__.py app\services\llm_generation\natal\theme_natal_reading_slots.py migrations\versions\20260601_0142_create_theme_natal_reading_slots.py tests\integration\test_theme_natal_reading_slots.py tests\unit\test_natal_chart_long_quota_on_acceptance.py` | `backend` | PASS |
| `ruff check .` | `backend` | PASS |
| `python -B -m pytest -q --long tests/integration/test_theme_natal_reading_slots.py --tb=short` | `backend` | PASS, 8 passed |
| `python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short` | `backend` | PASS, 5 passed |
| `python -B -m pytest -q app/tests/unit/test_backend_db_test_harness.py --tb=short` | `backend` | PASS, 4 passed |
| `python -B -m pytest -q --long tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short` | `backend` | PASS, 8 passed |
| `python -B -m pytest -q app/tests/unit/test_backend_db_test_harness.py tests/unit/test_narrative_natal_reading_v1.py tests/architecture/test_rejected_narrative_answer_boundary.py tests/architecture/test_narrative_natal_reading_public_boundary.py tests/unit/test_basic_natal_reading_contracts.py tests/architecture/test_basic_natal_reading_contract_boundaries.py --tb=short` | `backend` | PASS, 42 passed |
| Alembic temp SQLite upgrade to `head` and schema inspection | `backend` | PASS, recorded in `evidence/schema-after.txt` |
| `python -B -m alembic heads` | `backend` | PASS, `20260601_0142 (head)` |
| `python -B -c "from app.main import app; ..."` | `backend` | PASS, app imports with 230 routes |
| `git diff --check` | repo root | PASS |
| `ruff check .` | `backend` | PASS |
| `condamad_story_validate.py _condamad\stories\CS-428-public-reading-slots-llm-generation-runs\00-story.md` | repo root | PASS |
| `condamad_story_lint.py --strict _condamad\stories\CS-428-public-reading-slots-llm-generation-runs\00-story.md` | repo root | PASS |

## Scans / guards

- `rg -n "ThemeNatalReadingSlot|LlmGenerationRun|accepted_at|source_generation_run_id" backend/app backend/tests`: expected hits in new model/service/tests.
- `rg -n "client_request_id|idempot" backend/app backend/tests`: expected hits in new service/tests and existing idempotence code.
- `rg -n "UserNatalInterpretationModel\.user_id == user_id,[\s\S]*UserNatalInterpretationModel\.level" backend/app/services/llm_generation/natal`: PASS, no matches.
- `rg -n "_slot_lock_for_key|_publication_lock_for_slot|status != THEME_NATAL_SLOT_STATUS_ACCEPTED" backend/app/services/llm_generation/natal/theme_natal_reading_slots.py`: PASS, lock and atomic acceptance guard present.
- `rg -n "UserNatalInterpretationModel\.user_id == user_id,[\s\S]*UserNatalInterpretationModel\.level" backend/app/services/llm_generation/natal`: PASS, no matches.
- `rg -n "check_and_consume" backend/app/api/v1/routers/public/natal_interpretation.py`: PASS, no matches.
- `rg -n "fallback = response\.sections\[0\]" backend/app/services/llm_generation/natal`: PASS, no matches.
- AST guard for direct `SessionLocal`/`engine` imports from `app.infra.db.session` in new/modified tests: PASS.

## Not executed

- `python -B -m pytest -q --tb=short` full backend suite: not run because this story is backend-persistence scoped and the repository has a large long-test matrix; targeted story, migration and guardrail suites were run instead.
