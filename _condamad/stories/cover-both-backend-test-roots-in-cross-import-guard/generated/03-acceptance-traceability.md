# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Guard root calculation resolves backend root. | `BACKEND_ROOT` dans `backend/app/tests/unit/test_backend_test_helper_imports.py` pointe vers `backend`; assertion dediee. | `pytest -q app/tests/unit/test_backend_test_helper_imports.py`; baseline avant/apres. | PASS |
| AC2 | Both backend test roots are asserted. | Assertion dediee sur `app/tests` et `tests` dans la garde existante. | `pytest -q app/tests/unit/test_backend_test_helper_imports.py`. | PASS |
| AC3 | Cross-test imports remain absent. | La garde AST existante reste l'unique proprietaire et scanne les deux racines. | `pytest -q app/tests/unit/test_backend_test_helper_imports.py`; `rg` zero-hit sur imports interdits. | PASS |
| AC4 | Guard evidence is persisted. | Artefacts `cross-import-guard-before.md` et `cross-import-guard-after.md` ajoutes. | Presence des artefacts et commandes documentees dans `generated/10-final-evidence.md`. | PASS |
