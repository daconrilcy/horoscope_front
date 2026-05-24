# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | All mandatory family codes are registered. | Registry declarations and listing API. | Targeted pytest and full backend pytest PASS. | PASS |
| AC2 | Each family exposes required metadata. | Metadata dataclass plus explicit cache blocker test. | Targeted pytest and full backend pytest PASS. | PASS |
| AC3 | `natal_chart_v1` remains linked to the current graph. | Resolver maps to the existing natal graph builder. | Targeted registry and natal graph pytest PASS. | PASS |
| AC4 | Temporal families are blocked by astronomical proof. | Temporal declarations include `profection_v1` and CS-250 blocker. | Targeted registry pytest PASS. | PASS |
| AC5 | Duplicate family codes are rejected. | Registry construction rejects duplicate codes. | Targeted registry pytest PASS. | PASS |
| AC6 | Unknown family codes are rejected. | Lookup raises explicit registry error without fallback. | Targeted registry pytest PASS. | PASS |
| AC7 | Public API runtime contract is unchanged. | API neutrality test and negative scans show no exposure. | API pytest and OpenAPI route probes PASS. | PASS |
| AC8 | Registry evidence artifacts are persisted. | Validation, route and registry evidence files exist. | Story validation and strict lint PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
