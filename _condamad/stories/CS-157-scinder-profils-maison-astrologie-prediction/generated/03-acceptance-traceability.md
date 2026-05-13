# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Deux profils remplacent le contrat ambigu. | `PredictionContext` split fields; repository returns both profiles. | repository/context tests | PASS |
| AC2 | Champs produit hors `domain/astrology`. | `HouseAstrologyProfile` has no product fields. | zero-hit scan | PASS |
| AC3 | Scores prediction equivalents. | Tests prediction/orchestrator targeted pass. | targeted pytest | PASS |
