# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | La note historique cible `docs/architecture/`. | Move markdown file and update doc path in parity test. | `pytest -q app/tests/unit/test_entitlement_docs_runtime_parity.py`. | PASS |
| AC2 | Aucun ancien fichier entitlement canonique ne reste sous `backend/docs/`. | Delete old file path and assert absence. | ownership + entitlement tests. | PASS |
| AC3 | `backend/docs/ownership-index.md` couvre les fichiers `backend/docs/**`. | Remove stale ownership row. | `pytest -q app/tests/unit/test_backend_docs_ownership.py`. | PASS |
| AC4 | Les controles entitlement runtime restent actifs. | Preserve OpenAPI/table assertions in parity test. | `pytest -q app/tests/unit/test_entitlement_docs_runtime_parity.py`. | PASS |
| AC5 | Supprimer le contenu conserve exige une decision utilisateur. | Retain content under `docs/architecture/`; delete old path only. | `entitlement-doc-path-after.md`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
