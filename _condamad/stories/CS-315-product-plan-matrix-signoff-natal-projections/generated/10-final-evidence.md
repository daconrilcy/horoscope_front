<!-- Commentaire global: cette preuve finale cloture CS-315 sans modifier le runtime applicatif. -->

# Final Evidence - CS-315 Product Plan Matrix Signoff Natal Projections

## Story status

- Validation outcome: PASS_WITH_LIMITATIONS
- Ready for review: yes
- Story key: CS-315-product-plan-matrix-signoff-natal-projections
- Closure story: `CS-317-cloturer-cs315-final-evidence-validation-runtime`
- Status after closure: `done`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md`
- Closure source: `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/00-story.md`
- AGENTS.md considered: `AGENTS.md`
- Initial status: CS-315 was `ready-to-dev`; report classified it `Implemented but not validated`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | status updated after runtime evidence |
| `generated/01-execution-brief.md` | yes | yes | PASS | repaired by `condamad_prepare.py --repair-generated-only` |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | generated skeleton retained; final AC evidence is below |
| `generated/04-target-files.md` | yes | yes | PASS | repaired |
| `generated/06-validation-plan.md` | yes | yes | PASS | repaired |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | repaired |
| `generated/10-final-evidence.md` | yes | yes | PASS | this file |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `docs/architecture/natal-projection-plan-matrix-product-decision.md` documents the official matrix. | Decision field scan PASS. | PASS | Product owner role and date are present. |
| AC2 | The decision artifact states backend authorization remains implementation source and React is render-only. | Field scan and source alignment PASS. | PASS | No runtime owner moved to React. |
| AC3 | Frontend fixtures remain backend-shaped rendering evidence. | Vite logged Vitest PASS, 123 tests passed. | PASS | JSON report written under `frontend/logs/vite/`. |
| AC4 | Backend authorization remains access source. | Backend authorization and endpoint pytest PASS, 5 tests passed. | PASS | Runtime path is `/v1/astrology/projections`. |
| AC5 | Product/backend divergence is routed separately. | Real-conditions pytest PASS, 9 tests passed; divergence brief created. | PASS_WITH_LIMITATIONS | Backend currently accepts `client_interpretation_projection_v1` for `free`, `basic`, `premium`. |
| AC6 | React does not own plan policy. | Targeted `rg` scans found no CS-315 `accepted_matrix`, `frontend_policy`, `implementation_source` or `natal_projection_plan_matrix` owner in React. | PASS_WITH_LIMITATIONS | Broad plan-code scan has existing type/test false positives, not a local `/natal` matrix. |
| AC7 | Story evidence artifacts are persisted. | Final evidence, review, validation transcript and source alignment are present. | PASS | Capsule validation passes. |

## Commands run

| Command | Working directory | Result |
|---|---|---|
| `. .\.venv\Scripts\Activate.ps1; Set-Location backend; python -B -m pytest -q tests\api\test_projection_authorization.py tests\api\test_projection_endpoint.py --tb=short` | repo root | PASS, 5 passed |
| `. .\.venv\Scripts\Activate.ps1; Set-Location backend; python -B -c "... app.openapi() ..."` | repo root | PASS, 201 OpenAPI paths and 205 routes |
| `pnpm --dir frontend lint` | repo root | PASS |
| `pnpm --dir frontend exec node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi` | repo root | PASS, 123 tests |
| `. .\.venv\Scripts\Activate.ps1; Set-Location backend; python -B -m pytest -q tests\api\test_projection_real_conditions.py --tb=short` | repo root | PASS, 9 passed |
| `rg -n "decision_id|decision_date|owner|accepted_matrix|implementation_source|frontend_policy" docs/architecture/natal-projection-plan-matrix-product-decision.md` | repo root | PASS |

## Commands skipped or blocked

- Full backend `pytest -q`: not run; CS-317 validation plan targets projection runtime suites and no application source changed.
- Root `ruff format .`: not run; no Python files were modified and repository instruction prefers scoped formatting.
- Root `ruff check .`: not run before CS-315 status update; no Python source changed. It is run in CS-317 final validation.

## Files changed

- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/10-final-evidence.md`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/11-code-review.md`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md`
- `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md`
- `_condamad/stories/story-status.md`
- `_condamad/reports/CS-312-CS-316-delivery-report.md`

## Files deleted

- none

## Tests added or updated

- none; existing backend and frontend runtime suites were used as evidence.

## DRY / No Legacy evidence

- No backend or frontend application source changed.
- No React-owned entitlement matrix was introduced.
- No alias, shim, wrapper, fallback path or duplicate product decision document was added.
- The existing CS-315 decision document remains the single product matrix artifact.

## Remaining risks

- Product/backend behavior is not aligned for `client_interpretation_projection_v1`; the divergence is explicit and routed to `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md`.

## Diff review

- Application source files under `backend/app/**`, `frontend/src/**` and migrations were not modified.
- Intended changes are limited to CONDAMAD evidence, story status, delivery report and the divergence brief.

## Final worktree status

- Recorded in CS-317 final evidence after closure validation.

## Suggested reviewer focus

Review the divergence routing and confirm whether CS-315 can remain `done` while the backend follow-up is scheduled separately.
