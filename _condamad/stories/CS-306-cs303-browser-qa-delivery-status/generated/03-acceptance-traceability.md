# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Local startup state is recorded. | `evidence/startup-log.txt` records the Vite startup command, timestamp, and `result=pass`. | `node _condamad\stories\CS-306-cs303-browser-qa-delivery-status\evidence\cs306-browser-qa.mjs` PASS. | PASS |
| AC2 | `/natal` browser success rendering is proven. | `evidence/browser-desktop.png`, `evidence/browser-mobile.png`, and `evidence/browser-qa-ledger.json` prove `/natal` renders both projection cards in Chromium. | Browser ledger records desktop and mobile `projection_state: success`, required texts, screenshots, and no primary-control overlap. | PASS |
| AC3 | Projection state coverage is documented. | `evidence/browser-qa-ledger.json` documents success browser coverage and maps loading, controlled-error, entitlement, empty, and degraded states to logged Vitest coverage. | `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation` PASS, 33 tests. | PASS |
| AC4 | CS-303 frontend validations pass. | No product code change; CS-303 owners remain canonical. | `pnpm lint` PASS after one Windows EPERM retry; `natalChartApi`, `natalInterpretation`, and component architecture logged Vitest commands PASS. | PASS |
| AC5 | The full frontend suite status is proven. | `evidence/validation.txt` records a fresh full suite run; CS-305 final evidence remains linked as historical closure. | `node .\scripts\run-vite-logged.mjs vitest vitest run` PASS, 116 files, 1271 passed, 8 skipped. | PASS |
| AC6 | Backend projection contract remains intact. | Backend source unchanged; projection route/OpenAPI remains present. | `python -B -m pytest -q tests\api\test_projection_openapi.py tests\api\test_projection_endpoint.py tests\api\test_projection_authorization.py --tb=short` PASS, 8 tests; runtime route/OpenAPI check PASS. | PASS |
| AC7 | Public projection ownership stays central. | Browser script intercepts `POST /v1/astrology/projections` but app source still routes through `frontend/src/api/astrologyProjections.ts`; report update is evidence-only. | `rg` direct projection fetch scan PASS: no matches; forbidden internal field scan PASS: no matches; inline style scan on CS-303 owners PASS: no matches. | PASS |
| AC8 | Delivery report status is correct. | `_condamad/reports/CS-302-CS-304-delivery-report.md` now records `Delivered` and references CS-306 browser evidence plus CS-305 full-suite proof. | `evidence/report-before.md`, `evidence/report-after.md`, and `evidence/report-status.md` show proof-backed promotion to `Delivered`. | PASS |
| AC9 | Story evidence artifacts are persisted. | CS-306 `evidence/` contains baseline, after, screenshots, ledger, validation, startup, status, and browser QA script artifacts. | Artifact existence check PASS; capsule validation PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
