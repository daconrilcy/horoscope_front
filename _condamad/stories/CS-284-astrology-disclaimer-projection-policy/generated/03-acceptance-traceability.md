# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Existing disclaimers are inventoried. | Policy/evidence only; no app source change. | CS-284 inventory covers backend, frontend, docs and briefs. | PASS |
| AC2 | Usage classes are explicit. | Policy/evidence only; no runtime schema change. | Policy and inventory name natal, prediction, AI, degraded mode and missing birth time. | PASS |
| AC3 | B2C plan attachment is explicit. | Policy/evidence only; no projection builder change. | Policy maps both B2C projections by free, basic and premium plans. | PASS |
| AC4 | LLM disclaimer authorship is forbidden. | Policy/evidence only; no prompt rewrite. | Policy states application ownership and blocks LLM create, rewrite and mutation. | PASS |
| AC5 | Degraded states are covered. | Policy/evidence only; no payload change. | Policy covers `no_time`, degraded hints and `BGS_DEGRADED_NO_TIME`. | PASS |
| AC6 | Text deltas are justified. | No text delta. | Final evidence records no disclaimer text creation or mutation. | PASS |
| AC7 | Public API surface stays unchanged. | No route or OpenAPI change. | Loaded app OpenAPI and route neutrality checks PASS. | PASS |
| AC8 | Application source surfaces remain unchanged. | No `backend/app`, `frontend/src` or migration change. | Scoped git status evidence PASS. | PASS |
| AC9 | Regression tests stay green. | Existing tests only. | Architecture test and full backend pytest evidence PASS. | PASS |
| AC10 | Evidence artifacts are persisted. | CS-284 evidence and generated artifacts only. | Evidence folder and final evidence path checks PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
