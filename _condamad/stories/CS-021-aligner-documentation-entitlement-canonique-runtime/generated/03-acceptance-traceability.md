# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Statut doc explicite. | Header `Document status: historical-note`. | `rg -n "historical-note"` and parity test. | PASS |
| AC2 | Endpoints verifies depuis OpenAPI. | `test_entitlement_docs_runtime_parity.py`. | `pytest -q app/tests/unit/test_entitlement_docs_runtime_parity.py`. | PASS |
| AC3 | Tables entitlement verifiees depuis metadata. | Same guard imports SQLAlchemy metadata. | Same command PASS. | PASS |
| AC4 | Claims review/alert/security classes. | Header historical + guard. | Same command PASS. | PASS |
| AC5 | Tests runtime entitlement passants. | No runtime code changed. | Integration tests PASS. | PASS |
