# Acceptance Traceability

| AC | Requirement | Code / artifact evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Payload excludes baseline phrases. | `backend/tests/integration/test_basic_natal_v2_pipeline.py`; `evidence/basic-readable-api-after.json`. | Backend pytest PASS; persisted evidence token scan PASS. | PASS |
| AC2 | Public DOM text excludes baseline phrases. | `frontend/src/tests/natalPublicDomGuard.test.tsx`; `evidence/basic-readable-dom-text-after.txt`. | Vitest DOM PASS; Playwright evidence PASS; persisted evidence token scan PASS. | PASS |
| AC3 | Public DOM body excludes raw English astrology labels. | `frontend/src/tests/natalPublicDomGuard.test.tsx`; `frontend/e2e/cs-423-natal-basic-readable.spec.ts`. | Vitest DOM PASS; Playwright reading-body assertions PASS. | PASS |
| AC4 | Public DOM body excludes unaccented public labels. | `frontend/src/tests/natalPublicDomGuard.test.tsx`; `evidence/basic-readable-dom-text-after.txt`. | Vitest DOM PASS; Playwright reading-body assertions PASS. | PASS |
| AC5 | Basic DOM renders at most one source zone. | `frontend/src/tests/natalPublicDomGuard.test.tsx`; Playwright DOM text capture. | Vitest DOM PASS; Playwright source-zone count PASS. | PASS |
| AC6 | Basic DOM renders at most one legal zone. | `frontend/src/tests/natalPublicDomGuard.test.tsx`; Playwright DOM text capture. | Vitest DOM PASS; Playwright legal-zone count PASS. | PASS |
| AC7 | Valid Basic V2 does not show regeneration message. | `frontend/src/tests/NatalChartPage.test.tsx`; `frontend/e2e/cs-423-natal-basic-readable.spec.ts`. | Vitest page PASS; Playwright absence assertion PASS. | PASS |
| AC8 | QA payload remains plan-backed. | `backend/tests/unit/test_basic_natal_narrative_validator.py`; `backend/tests/integration/test_basic_natal_v2_pipeline.py`. | Backend pytest PASS. | PASS |
| AC9 | Live `/natal` desktop screenshot is persisted. | `evidence/basic-readable-desktop-after.png`. | Playwright screenshot PASS; Python existence/size check PASS. | PASS |
| AC10 | Live `/natal` mobile screenshot is persisted. | `evidence/basic-readable-mobile-after.png`. | Playwright screenshot PASS; Python existence/size check PASS. | PASS |
| AC11 | QA report classifies remaining gaps. | `evidence/qa-report.md`. | Python report-content check PASS. | PASS |
| AC12 | QA report states the live reading origin. | `evidence/qa-report.md` states origin `fixture`. | Python report-content check PASS. | PASS |
| AC13 | Historical degraded live content blocks QA closure. | Evidence scan over payload, DOM text, report and validation summary. | `rg` persisted-evidence scan returned exit 1, interpreted as PASS/no matches. | PASS |
| AC14 | Validation output is persisted. | `evidence/validation.txt`. | Python evidence existence check PASS. | PASS |
| AC15 | QA report confirms the final report introduction. | `evidence/qa-report.md`; DOM text artifact. | Python report-content check PASS. | PASS |
| AC16 | QA report confirms at least three explanatory themes. | `evidence/qa-report.md`; DOM text artifact. | Python report-content check PASS. | PASS |
| AC17 | QA report confirms the final report conclusion. | `evidence/qa-report.md`; DOM text artifact. | Python report-content check PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
