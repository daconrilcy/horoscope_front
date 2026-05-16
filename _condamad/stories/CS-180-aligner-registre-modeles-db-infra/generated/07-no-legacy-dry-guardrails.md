# No Legacy / DRY Guardrails

## Canonical Owners

- Non-LLM model exports: `backend/app/infra/db/models/__init__.py`.
- LLM model exports: `backend/app/infra/db/models/llm/__init__.py`.
- Declarative metadata loading: `backend/app/infra/db/base.py`.
- Exception classification: `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-table-exception-register.md` plus `backend/app/tests/unit/test_db_model_registry_guard.py`.

## Forbidden Patterns

- Import opportuniste de `FlaggedContentModel` uniquement depuis un routeur pour charger metadata.
- Exception wildcard comme `llm_*`, `_alembic_*` ou `*_archives`.
- Suppression, migration ou nettoyage physique de `_alembic_tmp_astrologer_profiles`.
- Modele applicatif cree pour `alembic_version`, `apscheduler_jobs` ou `llm_prompt_version_fallback_archives`.
- Duplication des exports LLM dans le registre racine non-LLM.
- Fallback silencieux si un modele applicatif est absent de `Base.metadata`.

## Required Negative Evidence

- `pytest -q app/tests/unit/test_db_model_registry_guard.py`
- `rg -n "drop_table\\(|DROP TABLE|_alembic_tmp_astrologer_profiles" app migrations ../_condamad/stories/CS-180-aligner-registre-modeles-db-infra`
- Classification des hits de registre dans `generated/10-final-evidence.md`.

## Review Checklist

- `flagged_contents` est charge dans `Base.metadata`.
- Les tables techniques/historiques sans modele sont listees exactement.
- Les modeles LLM restent portes par leur registre separe tout en etant charges dans `Base.metadata`.
- Aucun changement API, migration ou nettoyage DB n'a ete introduit.
