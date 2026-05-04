# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Tous les fichiers `backend/docs/**` sont classes. | `backend/docs/ownership-index.md` et `test_backend_docs_ownership.py`. | `pytest -q app/tests/unit/test_backend_docs_ownership.py`. | PASS |
| AC2 | Chaque ligne declare les champs obligatoires. | Parser strict du tableau Markdown. | `test_backend_docs_ownership_rows_are_actionable`. | PASS |
| AC3 | Type inconnu refuse. | Allowlist `ALLOWED_ARTIFACT_TYPES`. | `test_backend_docs_ownership_rejects_vague_classifications`. | PASS |
| AC4 | Nouveau fichier non classe bloque. | Comparaison filesystem/index. | `test_backend_docs_ownership_index_covers_current_inventory`. | PASS |
| AC5 | Guardrails applicables respectes. | Registre ops quality complete. | `pytest -q app/tests/unit/test_backend_quality_test_ownership.py`. | PASS |
