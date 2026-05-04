# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Les trois notes LLM sont sous `docs/llm/`. | Move three markdown files and delete old paths. | `test_llm_docs_governance.py`; scan target names. | PASS |
| AC2 | `backend/docs/ownership-index.md` classe les fichiers `backend/docs/**`. | Remove moved rows from ownership index. | `pytest -q app/tests/unit/test_backend_docs_ownership.py`. | PASS |
| AC3 | La gouvernance LLM reference les nouveaux chemins non canoniques. | Update LLM docs governance rows. | `pytest -q app/tests/unit/test_llm_docs_governance.py`. | PASS |
| AC4 | Le registre DB LLM pointe vers le nouveau chemin de gouvernance. | Update `governance_doc` and known reader path. | `pytest -q tests/integration/test_llm_db_cleanup_registry.py`. | PASS |
| AC5 | Les artefacts LLM gardes restent sous `backend/docs/`. | Keep generated/executable artifacts in `backend/docs`. | `pytest -q tests/unit/test_llm_canonical_perimeter.py`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
