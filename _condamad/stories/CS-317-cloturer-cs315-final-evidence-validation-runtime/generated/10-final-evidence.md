<!-- Commentaire global: cette preuve finale documente la cloture CS-317 et les validations runtime executees. -->

# Final Evidence - CS-317 Cloturer CS315 Final Evidence Validation Runtime

## Story status

- Validation outcome: PASS_WITH_LIMITATIONS
- Ready for review: yes
- Story key: CS-317-cloturer-cs315-final-evidence-validation-runtime
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: pre-existing untracked `_condamad/reports/CS-312-CS-316-delivery-report.md` and `_story_briefs/cs-317...`, `cs-318...`, `cs-319...`.
- Story-status row checked before implementation: CS-317 path and source brief matched the requested story.
- Capsule repair: CS-317 generated files were missing and repaired with `condamad_prepare.py --repair-generated-only`.
- Accidental lowercase `cs-317` capsule produced by an initial prepare invocation was removed after path safety check.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | status set to `ready-to-review` |
| `generated/01-execution-brief.md` | yes | yes | PASS | repaired |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC-by-AC evidence recorded |
| `generated/04-target-files.md` | yes | yes | PASS | repaired |
| `generated/06-validation-plan.md` | yes | yes | PASS | repaired |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | repaired |
| `generated/10-final-evidence.md` | yes | yes | PASS | this file |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | CS-315 final evidence created. | CS-315 capsule validation PASS. | PASS | |
| AC2 | CS-315 implementation review replaced editorial review. | Review verdict `CLEAN_WITH_ROUTED_DIVERGENCE`. | PASS | |
| AC3 | Backend projection runtime suite executed. | Authorization/endpoint pytest PASS, 5 tests. | PASS | |
| AC4 | Backend OpenAPI/routes neutral. | Runtime check PASS, 201 OpenAPI paths, 205 routes. | PASS | |
| AC5 | Frontend natal projection validation executed. | `pnpm lint` PASS; Vite logged Vitest PASS, 123 tests. | PASS | |
| AC6 | React has no local matrix policy. | No frontend source changes; targeted scans classify broad matches as existing type/test false positives. | PASS_WITH_LIMITATIONS | |
| AC7 | CS-315 status aligned. | Python status check PASS; story and tracker set `done`. | PASS | |
| AC8 | Capsule validation passes. | CS-315 validation PASS; CS-317 validation run after final evidence update. | PASS | |
| AC9 | Divergence routed separately. | `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md` created. | PASS | Backend currently accepts all B2C plans for `client_interpretation_projection_v1`. |
| AC10 | Delivery report gap removed. | Report updated to `Delivered with routed backend follow-up`. | PASS | |

## Files changed

- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/**`
- `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/**`
- `_condamad/stories/story-status.md`
- `_condamad/reports/CS-312-CS-316-delivery-report.md`
- `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md`

## Files deleted

- none from repository scope; only the accidental generated `_condamad/stories/cs-317` capsule was removed during preflight cleanup.

## Tests added or updated

- none; the story closes evidence using existing backend and frontend validation suites.

## Commands run

| Command | Working directory | Result | Evidence summary |
|---|---|---|---|
| `git status --short` | repo root | PASS | Dirty baseline recorded. |
| `condamad_prepare.py --repair-generated-only ...CS-317...` | repo root with venv | PASS | CS-317 generated files created. |
| `condamad_validate.py ...CS-317...` | repo root with venv | PASS | Capsule structure initially valid after repair. |
| `python -B -m pytest -q tests\api\test_projection_authorization.py tests\api\test_projection_endpoint.py --tb=short` | `backend` with venv | PASS | 5 tests passed. |
| `python -B -c "from app.main import app; ..."` | `backend` with venv | PASS | `/v1/astrology/projections` present. |
| `pnpm --dir frontend lint` | repo root | PASS | TypeScript lint projects passed. |
| `pnpm --dir frontend exec node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi` | repo root | PASS | 123 tests passed. |
| `python -B -m pytest -q tests\api\test_projection_real_conditions.py --tb=short` | `backend` with venv | PASS | 9 tests passed; divergence identified. |
| `condamad_prepare.py --repair-generated-only ...CS-315...` | repo root with venv | PASS | CS-315 generated capsule files repaired. |
| `condamad_validate.py ...CS-315...` | repo root with venv | PASS | CS-315 capsule valid. |
| `ruff check .` | repo root with venv | PASS | All checks passed. |
| `git diff --check` | repo root | PASS | Only line-ending warnings, no whitespace errors. |
| `python -B -m pytest -q --tb=short` | `backend` with venv | PASS | 3432 passed, 1 skipped, 1216 deselected. |
| `condamad_validate.py ...CS-317...` | repo root with venv | PASS | CS-317 capsule valid after final evidence update. |

## Commands skipped or blocked

- `ruff format`: skipped; no Python files were modified.
- Local dev server startup: skipped; no application runtime/source/UI code changed, and story validation is evidence/runtime-test oriented.
- Full frontend Vitest suite: skipped; CS-317 validation plan requires lint plus logged natal targets, which passed.

## DRY / No Legacy evidence

- No backend or frontend application source changed.
- No React entitlement matrix, shim, alias, wrapper, fallback or duplicate product matrix document was introduced.
- Product/backend mismatch is routed to a separate brief instead of hidden in React.

## Diff review

- Scoped diff contains only story evidence/status/report surfaces.
- `git diff --check` PASS with CRLF normalization warnings only.

## Final worktree status

- Modified tracked files: CS-315 story/evidence/review, CS-317 story, `story-status.md`.
- Untracked story-scoped/generated files include CS-315/CS-317 generated capsule files, delivery report, CS-315 divergence brief and pre-existing CS-317/CS-318/CS-319 briefs.

## Remaining risks

- Backend/product divergence remains open for owner decision: backend accepts `client_interpretation_projection_v1` for `free`, `basic` and `premium`; CS-315 product decision expects premium-only visibility.

## Suggested reviewer focus

Confirm that marking CS-315 `done` is acceptable with the divergence explicitly routed to the backend follow-up brief.
