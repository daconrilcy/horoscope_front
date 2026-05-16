# Target Files

## Must Read

- `backend/app/infra/db/models/__init__.py`
- `backend/app/infra/db/models/flagged_content.py`
- `backend/app/infra/db/models/llm/__init__.py`
- `backend/app/infra/db/base.py`
- `backend/app/core/scheduler.py`
- `backend/app/api/v1/routers/admin/support.py`
- `backend/app/tests/integration/test_admin_support_api.py`
- `_condamad/stories/regression-guardrails.md`

## Must Search

- `rg -n "__tablename__\\s*=" backend/app/infra/db/models -g "*.py"`
- `rg -n "flagged_contents|FlaggedContentModel|llm_prompt_version_fallback_archives|SQLAlchemyJobStore|_alembic_tmp_astrologer_profiles|astrologer_prompt_profiles" backend/app backend/tests _condamad/stories/CS-180-aligner-registre-modeles-db-infra -g "*.py" -g "*.md"`
- `rg -n "drop_table\\(|DROP TABLE|_alembic_tmp_astrologer_profiles" app migrations ../_condamad/stories/CS-180-aligner-registre-modeles-db-infra`

## Likely Modified

- `backend/app/infra/db/models/__init__.py`
- `backend/app/infra/db/base.py`
- `backend/app/tests/unit/test_db_model_registry_guard.py`
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-before.md`
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-after.md`
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-table-exception-register.md`
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/generated/**`
- `_condamad/stories/story-status.md`

## Forbidden Unless Justified

- `backend/migrations/**`
- `backend/horoscope.db`
- `backend/app/api/v1/routers/admin/support.py`
- `backend/app/core/scheduler.py`
- `requirements.txt`
