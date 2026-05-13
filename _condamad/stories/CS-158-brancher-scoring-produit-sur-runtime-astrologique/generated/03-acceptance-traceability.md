# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `DomainRouter` transforms runtime house facts via product weights. | Router accepts runtime house metadata. | `test_domain_router.py` | PASS |
| AC2 | `NatalSensitivityCalculator` reads runtime facts. | Occupants/rulers use `NatalChart.houses`. | `test_natal_sensitivity.py`, `test_natal_structural_v3.py` | PASS |
| AC3 | Prediction scores remain stable. | Targeted engine/scoring tests pass. | targeted pytest | PASS |
| AC4 | Prediction does not recalculate rulerships. | `sign_rulerships` scan zero-hit in `domain/prediction`. | scan zero-hit | PASS |
