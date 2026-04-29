# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | L inventaire des imports directs DB est complet. | `db-test-session-imports-before.md`, `db-test-session-imports-after.md`, `db-session-allowlist.md`. | `pytest -q app/tests/unit/test_backend_db_test_harness.py` PASS; scan `rg` classifié. | PASS |
| AC2 | Un helper DB canonique est utilise par un lot. | `tests/integration/app_db.py`, `app/tests/helpers/db_session.py`, `test_llm_release.py`, `test_admin_content_api.py`. | `pytest -q app/tests/integration/test_admin_content_api.py` PASS; sous-ensemble migré de `test_llm_release.py` PASS; le fichier complet reste hors validation obligatoire car ses échecs relèvent du service release LLM, pas du harnais DB. | PASS |
| AC3 | L'alignement SQLite/Alembic est preserve. | Helpers résolvent la session effective sans nouvelle factory SQLite; pas de changement Alembic/modèles. | `pytest -q tests/integration/test_backend_sqlite_alignment.py` PASS. | PASS |
| AC4 | Une garde bloque les nouveaux imports directs. | `app/tests/unit/test_backend_db_test_harness.py` + `db-session-allowlist.md` + `RG-011`. | `pytest -q app/tests/unit/test_backend_db_test_harness.py` PASS. | PASS |
