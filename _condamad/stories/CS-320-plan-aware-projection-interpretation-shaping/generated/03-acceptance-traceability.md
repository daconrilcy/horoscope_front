# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | A canonical shaping contract uses the B2C plan set. | `docs/architecture/client-interpretation-projection-v1-contract.md` defines the plan shaping table. | `rg` contract scan in `evidence/validation.txt`. | PASS |
| AC2 | The contract defines LLM input selection by plan. | `LLMInputSelection.allowed_fact_groups` is documented for all plans and mirrored in `evidence/*-sample.json`. | `rg` contract scan and JSON parse evidence. | PASS |
| AC3 | The contract defines `EditorialDepthProfile` by plan. | `EditorialDepthProfile` and `precision_level` are documented for all plans and mirrored in samples. | `rg` contract scan and JSON parse evidence. | PASS |
| AC4 | The contract defines frontend visibility by plan. | `FrontendVisibilityRules` and display hints are documented for all plans and mirrored in samples. | `rg` contract scan and frontend Vitest target. | PASS |
| AC5 | The contract preserves full projection for all plans. | Contract states shaping does not change projection availability. | `python -B -m pytest -q tests\api\test_projection_real_conditions.py tests\api\test_projection_endpoint.py --tb=short`: PASS, 12 tests. | PASS |
| AC6 | The contract defines future implementation ownership. | Owner table names backend contract, builder, structured facts/LLM and React render owners. | `rg` owner/contract scan plus OpenAPI route neutrality check. | PASS |
| AC7 | Future validations prevent policy drift. | Contract lists backend, frontend and OpenAPI guard requirements; no React policy added. | `pnpm --dir frontend ... vitest run component-architecture-guards natalInterpretation NatalChartPage natalChartApi`: PASS, 130 tests. | PASS |
| AC8 | Evidence artifacts are persisted. | `evidence/free-sample.json`, `basic-sample.json`, `premium-sample.json`, `source-alignment.md`, `validation.txt`, `runtime-surface-guard.txt`. | JSON parse and path-based evidence recorded in final evidence. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
