# Final Evidence - CS-320-plan-aware-projection-interpretation-shaping

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-320-plan-aware-projection-interpretation-shaping
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/00-story.md`
- Initial `git status --short`: run; worktree was already dirty.
- Pre-existing dirty files: story artifacts, briefs, `docs/architecture/natal-projection-plan-matrix-product-decision.md`, `_condamad/run-state.json`.
- AGENTS.md files considered: user-provided repository instructions in the session.
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | validated | `condamad_validate.py`: PASS |
| `generated/01-execution-brief.md` | yes | yes | validated | `condamad_validate.py`: PASS |
| `generated/03-acceptance-traceability.md` | yes | yes | validated | updated with AC evidence |
| `generated/04-target-files.md` | yes | yes | validated | `condamad_validate.py`: PASS |
| `generated/06-validation-plan.md` | yes | yes | validated | `condamad_validate.py`: PASS |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | validated | `condamad_validate.py`: PASS |
| `generated/10-final-evidence.md` | yes | yes | validated | final evidence completed |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Plan table in `docs/architecture/client-interpretation-projection-v1-contract.md`. | Contract `rg` scan. | PASS | Names `free`, `basic`, `premium`. |
| AC2 | `LLMInputSelection.allowed_fact_groups` per plan plus JSON samples. | Contract scan and JSON parse. | PASS | No provider payload exposed. |
| AC3 | `EditorialDepthProfile` and `precision_level` per plan plus JSON samples. | Contract scan and JSON parse. | PASS | Depth and precision are client-readable. |
| AC4 | `FrontendVisibilityRules` per plan plus JSON samples. | Contract scan and frontend guards. | PASS | React remains renderer only. |
| AC5 | Contract states full projection remains available. | Backend pytest projection tests: 12 passed. | PASS | No access restriction added. |
| AC6 | Owners table added to contract. | Contract scan and OpenAPI route check. | PASS | Backend, LLM and frontend owners explicit. |
| AC7 | Future validation checklist added; active guards pass. | Frontend lint and Vitest target pass. | PASS | Negative React owner scan has no matches. |
| AC8 | Evidence files persisted under CS-320. | JSON parse and final evidence. | PASS | Samples, validation and guard evidence present. |

## Files changed

- `docs/architecture/client-interpretation-projection-v1-contract.md`
- `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/free-sample.json`
- `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/basic-sample.json`
- `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/premium-sample.json`
- `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/source-alignment.md`
- `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/validation.txt`
- `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/evidence/runtime-surface-guard.txt`
- `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/generated/09-dev-log.md`
- `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/generated/10-final-evidence.md`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- none added or modified; existing backend and frontend tests were executed.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `. .\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py ...` | repo root | PASS | 0 | Capsule generated. |
| `. .\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py ...` | repo root | PASS | 0 | Capsule structure valid. |
| `. .\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ...` | repo root | PASS | 0 | Story validation passed. |
| `. .\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ...` | repo root | PASS | 0 | Story lint passed after AC wording was made atomic. |
| `rg -n "free|basic|premium|EditorialDepthProfile|LLMInputSelection|FrontendVisibilityRules|precision_level|calculs|interpretations" ...` | repo root | PASS | 0 | Contract vocabulary found. |
| `. .\.venv\Scripts\Activate.ps1; python -B -c "...json..."` | repo root | PASS | 0 | Evidence samples parse as JSON. |
| `. .\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests\api\test_projection_real_conditions.py tests\api\test_projection_endpoint.py --tb=short` | backend | PASS | 0 | 12 tests passed. |
| `. .\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | backend | PASS | 0 | All checks passed. |
| `pnpm --dir frontend lint` | repo root | PASS | 0 | TypeScript lint checks passed. |
| `pnpm --dir frontend exec node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards natalInterpretation NatalChartPage natalChartApi` | repo root | PASS | 0 | 130 tests passed. |
| `. .\.venv\Scripts\Activate.ps1; python -B -c "...app.openapi()..."` | repo root | PASS | 0 | OpenAPI and `/v1/astrology/projections` route exist. |
| `rg -n "React.*entitlement|entitlement matrix|accepted_matrix|localPlanPolicy" frontend\src\features\natal-chart frontend\src\components\natal-interpretation -g "*.ts" -g "*.tsx"` | repo root | PASS | 1 | No matches; negative scan passed. |
| `git diff --check -- ...` | repo root | PASS | 0 | No whitespace errors; LF/CRLF warnings only. |

## Commands skipped or blocked

- none

## DRY / No Legacy evidence

- No duplicate contract introduced; existing canonical document extended.
- No compatibility shim, alias, fallback, legacy import path, DB migration, Stripe rule, provider integration, React local entitlement policy or plan-specific route introduced.
- Negative React owner scan recorded in `evidence/runtime-surface-guard.txt`.

## Diff review

- `git diff --stat`: run for story surface during final review.
- `git diff --check`: PASS for touched story/docs/status paths.

## Final worktree status

- Final `git status --short`: story files, generated capsule/evidence,
  `story-status.md` and contract doc are changed for CS-320; unrelated dirty
  briefs/docs and `_condamad/run-state.json` were already present or outside
  this implementation scope.

## Remaining risks

- none-recorded

## Suggested reviewer focus

- Review the plan matrix semantics in `docs/architecture/client-interpretation-projection-v1-contract.md`, especially the fact groups and visibility rules.

## Feedback loop routing

- no-propagation: no reusable skill, AGENTS or guardrail correction was identified beyond this story evidence.
