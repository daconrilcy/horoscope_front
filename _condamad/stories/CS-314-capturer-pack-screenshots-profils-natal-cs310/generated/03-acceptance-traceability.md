# Acceptance Traceability - CS-314

| AC | Requirement | Status | Implementation evidence | Validation evidence |
|---|---|---|---|---|
| AC1 | The CS-314 screenshot directory exists. | PASS | `evidence/screenshots/` contains seven Chromium PNG captures. | `validation-ledger.txt`: screenshot directory exists and every ledger path resolves. |
| AC2 | Every CS-310 profile has browser evidence. | PASS | `evidence/screenshot-ledger.json` covers the five CS-310 profiles from the CS-310 profile set. | `validation-ledger.txt`: five distinct `profile_id` values. |
| AC3 | Missing-time desktop capture exists. | PASS | `cs310-missing-time-paris__desktop.png`. | `validation-ledger.txt`: missing-time desktop entry exists. |
| AC4 | Missing-time mobile capture exists. | PASS | `cs310-missing-time-paris__mobile.png`. | `validation-ledger.txt`: missing-time mobile entry exists. |
| AC5 | Controlled-incomplete desktop capture exists. | PASS | `cs310-controlled-incomplete__desktop.png`. | `validation-ledger.txt`: controlled-incomplete desktop entry exists. |
| AC6 | Controlled-incomplete mobile capture exists. | PASS | `cs310-controlled-incomplete__mobile.png`. | `validation-ledger.txt`: controlled-incomplete mobile entry exists. |
| AC7 | Disclaimers are visible or classified per profile. | PASS | `screenshot-ledger.json` records `disclaimer_result` per profile. | Ledger entries classify success/degraded as `visible` and controlled error as `not_applicable`. |
| AC8 | Sensitive raw payload surfaces are absent. | PASS | Ledger/notes avoid raw payload content; screenshots are generated from synthetic deterministic API routes. | Scoped `rg` on ledger, notes, and anomaly ledger: `PASS: no sensitive markers in ledger/notes`. |
| AC9 | Reproducible anomalies are tracked as briefs. | PASS | `evidence/anomaly-ledger.json` exists with an empty `entries` list; no follow-up brief required. | `validation-anomalies.txt`: `PASS: no reproducible anomalies requiring follow-up brief`. |
| AC10 | Targeted frontend validations pass. | PASS | Frontend validation output persisted under `evidence/validation-frontend-*.txt`. | `pnpm lint`: PASS; targeted Vitest: 123 tests PASS; guardrail Vitest: 145 tests PASS. |
| AC11 | Targeted backend validations pass. | PASS | Backend validation output persisted under `evidence/validation-backend-pytest.txt`. | `python -B -m pytest -q tests\api\test_projection_real_conditions.py tests\api\test_projection_endpoint.py --tb=short`: 12 PASS. |
| AC12 | Final evidence summarizes the browser pass. | PASS | `generated/10-final-evidence.md` summarizes the browser pass and validation status. | `condamad_validate.py`: PASS after evidence update. |
