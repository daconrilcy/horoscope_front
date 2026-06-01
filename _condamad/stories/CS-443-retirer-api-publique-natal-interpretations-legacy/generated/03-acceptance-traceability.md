# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `POST /v1/natal/interpretation` is absent at runtime. | Removed `natal_interpretation_router` from `backend/app/api/v1/routers/registry.py`; deleted `backend/app/api/v1/routers/public/natal_interpretation.py`. | Runtime `app.routes` assertion PASS; architecture guard PASS; `routes-after.txt` omits the path. | PASS |
| AC2 | No runtime public route remains under `/v1/natal/interpretations`. | Deleted the only public router that owned list/get/delete/pdf historical routes. | Runtime prefix assertion PASS; architecture guard PASS; `routes-after.txt` omits the prefix. | PASS |
| AC3 | Public OpenAPI omits historical natal interpretation paths. | Route registration no longer includes the legacy router. | `app.openapi()` assertions PASS; `openapi-after.json` omits legacy paths and includes `/v1/theme-natal/readings`. | PASS |
| AC4 | Public read responses expose accepted theme-natal slots only. | `theme_natal_readings.py` remains the public owner; `test_theme_natal_public_reads.py` targets `POST /v1/theme-natal/readings`. | Targeted integration tests PASS; rejected response has `data: null`. | PASS |
| AC5 | Public code omits old product mapping conversion. | Bounded public route/contract/frontend production code contains no `natal_long_free` or `natal_interpretation_short`. | Mapping scan in `evidence/forbidden-scan-after.txt`: PASS, no matches. | PASS |
| AC6 | Frontend nominal calls avoid historical natal URLs. | `frontend/src/api/natal-chart/index.ts` no longer fetches historical URLs; `NatalInterpretation.tsx` uses `requestThemeNatalReadingAction` for PDF actions. | URL scan PASS; Vitest `natalChartApi`, `natalInterpretation`, DOM guard, page tests PASS. | PASS |
| AC7 | Visible history actions have a modern disposition. | Delete action is no longer rendered by `VersionSelector` unless explicitly provided; `NatalInterpretationSection` does not provide it. PDF commands use product actions. | `natalInterpretation.test.tsx` PASS, including no visible historical delete; frontend lint PASS. | PASS |
| AC8 | Consumption audit artifact is persisted. | Added `route-consumption-audit.md`. | Final evidence and capsule validation check the artifact. | PASS |
| AC9 | Contract snapshot artifacts are persisted. | Wrote `evidence/routes-before.txt`, `openapi-before.json`, `routes-after.txt`, `openapi-after.json`. | Runtime snapshot commands PASS; files exist. | PASS |
| AC10 | Reintroduction guard fails on historical public URLs. | Added runtime/OpenAPI absence guard in `test_legacy_natal_generation_inventory_guard.py`; production scans persisted. | Architecture guard PASS; URL scan PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
