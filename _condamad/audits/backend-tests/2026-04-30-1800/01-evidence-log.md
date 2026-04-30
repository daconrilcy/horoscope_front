# Evidence Log - backend-tests

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | guardrail-registry | `_condamad/stories/regression-guardrails.md` | `_condamad/stories/regression-guardrails.md` | PASS | `RG-010` a `RG-016` couvrent les surfaces backend-tests auditees. |
| E-002 | topology-contract | `backend/pyproject.toml` | `backend/pyproject.toml` | PASS | `testpaths` contient `app/tests`, `tests/evaluation`, `tests/integration`, `tests/llm_orchestration`, `tests/unit`. |
| E-003 | topology-registry | `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md` | `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md` | PASS | Les racines pytest standard et l'exception exacte sont documentees. |
| E-004 | db-allowlist | `_condamad/stories/converge-db-test-fixtures/db-session-allowlist.md` | `_condamad/stories/converge-db-test-fixtures/db-session-allowlist.md` | PASS | Aucune exception active; helpers canoniques documentes. |
| E-005 | ownership-registry | `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md` | `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md` | PASS | 23 tests docs/scripts/secrets/security/ops sont classes avec owner et commande. |
| E-006 | deprecation-decision | `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-deprecation-decision.md` | `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-deprecation-decision.md` | PASS | `LLMNarrator` n'est plus une dependance nominale des tests de prediction. |
| E-007 | seed-decision | `_condamad/stories/replace-seed-validation-facade-test/seed-validation-decision.md` | `_condamad/stories/replace-seed-validation-facade-test/seed-validation-decision.md` | PASS | Le test facade seed a ete remplace par une validation comportementale. |
| E-008 | static-inventory | `rg --files backend -g 'test_*.py'` | `backend/` | PASS | 433 fichiers de tests backend inventories. |
| E-009 | static-negative-scan | `rg --files backend -g 'test_story_*.py'` | `backend/` | PASS | 0 hit; aucun ancien guard `test_story_*.py` actif. |
| E-010 | static-negative-scan | `rg -n "from app\.tests\.(integration\|unit\|regression)\.test_\|from tests\.(integration\|unit\|regression)\.test_" backend\app\tests backend\tests -g "test_*.py"` | `backend/app/tests`, `backend/tests` | PASS | 0 hit; aucun import entre modules executables de tests. |
| E-011 | static-negative-scan | `rg -n "from app\.prediction\.llm_narrator import LLMNarrator\|LLMNarrator\(\|LLMNarrator\.narrate" backend\tests backend\app\tests -g "test_*.py"` | `backend/app/tests`, `backend/tests` | PASS | 0 hit; pas de consommation nominale de la classe depreciee. |
| E-012 | static-negative-scan | `rg -n "from app\.infra\.db\.session import .*\b(SessionLocal\|engine)\b\|app\.infra\.db\.session\.(SessionLocal\|engine)" backend\app\tests backend\tests -g "*.py"` | `backend/app/tests`, `backend/tests` | PASS | 0 hit; pas d'import direct nominal de session DB production. |
| E-013 | static-scan | `rg --files backend -g "test_*.py" \| rg "(docs\|scripts\|ops\|secret\|security)"` | `backend/` | PASS | 23 tests concernes; tous couverts par le registre E-005. |
| E-014 | check-only-lint | `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | `backend/` | PASS | `All checks passed!` |
| E-015 | targeted-tests | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_backend_test_topology.py app/tests/unit/test_backend_pytest_collection.py app/tests/unit/test_backend_db_test_harness.py app/tests/unit/test_backend_test_helper_imports.py app/tests/unit/test_backend_quality_test_ownership.py app/tests/unit/test_backend_noop_tests.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py tests/unit/prediction/test_llm_narrator.py` | `backend/` | PASS | 31 passed in 29.60s. |
| E-016 | collection-runtime | `.\.venv\Scripts\Activate.ps1; cd backend; pytest --collect-only -q --ignore=.tmp-pytest` | `backend/` | PASS | 3497 tests collected. |
| E-017 | explicit limitation | `ruff format` | `backend/` | SKIPPED | Audit read-only: formatter non execute pour respecter le workflow du skill. |

## Notes De Preuve

Les scans statiques sont utilises comme preuves negatives d'absence. Les preuves structurantes sont les guards pytest et registres persistants cites ci-dessus.
