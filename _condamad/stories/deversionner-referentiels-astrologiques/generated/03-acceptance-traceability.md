# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Structural tables no longer carry `reference_version_id`. | Models and migration remove column/FK/index from `planets`, `signs`, `houses`, `aspects`, `astro_points`. | Targeted model/migration tests and schema scan. | PASS |
| AC2 | Structural unique constraints are stable by code/number. | Unique constraints become `code` or `number` only. | Migration integration test inspects constraints/indexes. | PASS |
| AC3 | Parametric/versioned tables remain version-aware. | Profiles/weights/rulerships/categories keep or gain `reference_version_id` as needed. | Repository tests for two versions returning different profile/weight data. | PASS |
| AC4 | Seed no longer clones structure by version and remains idempotent. | Seed resolves stable structure rows and purges/reseeds versioned rows only. | Seed/unit tests and count checks. | PASS |
| AC5 | Repositories read structural rows globally and versioned rows by version. | Query filters move from structural tables to profile/weight/category/rulership tables. | `test_prediction_reference_repository` updates. | PASS |
| AC6 | Guards prevent reintroduction and duplicate structural rows. | Add/update guard tests and negative scans. | Pytest guard + `rg` evidence. | PASS |
