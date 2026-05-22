# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Motion payload type immuable sans dictionnaire libre. | Runtime payload dataclass typed. | Payload tests. | PASS |
| AC2 | Visibility payload type avec `is_visible` prudent. | Runtime visibility payload typed. | Payload tests. | PASS |
| AC3 | Motion mapping reuses `PlanetaryMotionCondition` or existing speeds. | Pure builder from canonical conditions only; no builder fallback from raw position facts. | Payload tests and scans. | PASS |
| AC4 | Visibility mapping reuses solar contracts. | Pure builder from `PlanetaryConditionsBundle`. | Payload tests and scans. | PASS |
| AC5 | `supports_motion=True` requires motion payload. | Runtime validator. | Validator tests. | PASS |
| AC6 | `supports_visibility=True` requires visibility payload. | Runtime validator. | Validator tests. | PASS |
| AC7 | Payload with false capability is invalid. | Runtime validator rejects extra payloads. | Validator tests. | PASS |
| AC8 | Applicable planets/luminaries expose payloads. | Natal builder passes advanced conditions into chart objects. | Natal chart object tests. | PASS |
| AC9 | Objects without reliable source stay without payloads. | Builder leaves astral points, angles, houses without motion/visibility. | Natal chart object tests. | PASS |
| AC10 | Historical outputs stay stable. | No removal of existing result fields. | Integration tests. | PASS |
| AC11 | Public schema stays stable. | `chart_objects` remains excluded. | OpenAPI/schema test. | PASS |
| AC12 | No consumer drives motion/visibility by `object_type`. | Architecture AST guard. | Architecture test. | PASS |
| AC13 | No local magic thresholds introduced. | No threshold literals in runtime/builder mapping. | `rg` scans. | PASS |
| AC14 | `RG-146` registered. | Registry row remains present. | `rg -n "RG-146" ...`. | PASS |
