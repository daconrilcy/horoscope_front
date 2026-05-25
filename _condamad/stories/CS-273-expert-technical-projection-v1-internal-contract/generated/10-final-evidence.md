# Final Evidence — CS-273-expert-technical-projection-v1-internal-contract

## Story status

- Validation outcome: passed
- Ready for review: yes
- Story key: CS-273-expert-technical-projection-v1-internal-contract
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract`
- Registry status: `done`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/00-story.md`
- Source brief: `_story_briefs/cs-273-define-expert-technical-projection-v1-admin-astro-expert-only.md`
- Story-status row matched requested path and source brief before implementation.
- Initial `git status --short`: dirty before this story; unrelated changes left untouched.
- AGENTS.md considered: repository root `AGENTS.md` from prompt and workspace.
- Capsule generated: yes, repaired because required generated files were initially absent.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status updated to ready-to-review. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Helper-generated. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC evidence completed. |
| `generated/04-target-files.md` | yes | yes | PASS | Helper-generated. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Helper-generated. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Helper-generated. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Final evidence completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Contract doc created. | Path check and targeted pytest. | PASS | |
| AC2 | Internal/non-client classification in contract. | `rg` and pytest. | PASS | |
| AC3 | `ADMIN` and future `ASTRO_EXPERT` target-only consumers. | `rg` and pytest. | PASS | |
| AC4 | B2C denial documented. | Targeted pytest. | PASS | |
| AC5 | Astrology data families documented. | `rg` and pytest. | PASS | |
| AC6 | Structured facts, signals and evidence refs linked. | `rg` and pytest. | PASS | |
| AC7 | Raw technical payload exclusions documented; runtime neutral. | `app.openapi()`, `app.routes`, pytest. | PASS | |
| AC8 | CS-271 permission ownership reused. | Contract pytest. | PASS | |
| AC9 | Access-log fields specified. | `rg` and pytest. | PASS | |
| AC10 | Registry and current-state wording reclassified. | Expert-row/current-state negative scans and pytest. | PASS | |
| AC11 | App roots unchanged by CS-273. | Scoped app status plus CS-273 changed-file set recorded. | PASS | Workspace has unrelated dirty app files, but no CS-273 changed file is under `backend/app`, `frontend/src` or migrations. |
| AC12 | Evidence artifacts persisted. | Path checks and capsule validation. | PASS | |

## Files changed

- `docs/architecture/expert-technical-projection-v1-contract.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `docs/architecture/product-architecture-current-state-2026-05-24.md`
- `backend/tests/unit/test_expert_technical_projection_contract.py`
- `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/00-story.md`
- `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/generated/**`
- `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/**`
- `_condamad/stories/story-status.md`

## Files deleted

- `_condamad/stories/cs-273/**` removed because it was accidentally created by this run and outside the requested capsule.

## Tests added or updated

- Added `backend/tests/unit/test_expert_technical_projection_contract.py`.
- Updated the test to guard stale public-expert wording in the current architecture synthesis.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.venv` activation + `condamad_prepare.py --repair-generated-only ...` | repo root | PASS | 0 | Capsule generated files repaired. |
| `.venv` activation + `condamad_validate.py ...` | repo root | PASS | 0 | Capsule valid. |
| `.venv` activation + `ruff format backend\tests\unit\test_expert_technical_projection_contract.py` | repo root | PASS | 0 | Targeted format. |
| `.venv` activation + `ruff check backend docs` | repo root | PASS | 0 | Scoped lint. |
| `.venv` activation + `python -B -m pytest -q backend\tests\unit\test_expert_technical_projection_contract.py --tb=short` | repo root | PASS | 0 | 6 passed. |
| `.venv` activation + `python -B -m pytest -q backend\tests\unit\test_expert_technical_projection_contract.py backend\tests\architecture\test_api_contract_neutrality.py --tb=short` | repo root | PASS | 0 | 25 passed. |
| `.venv` activation + `python -B -c "from app.main import app; ..."` | repo root | PASS | 0 | OpenAPI/routes neutral. |
| `rg` contract and expert-row scans | repo root | PASS | 0 | Required terms present; expert public wording absent. |
| `git diff --check -- <CS-273 paths>` | repo root | PASS | 0 | Exit 0; line-ending warning only. |
| `.venv` activation + `condamad_validate.py ...` | repo root | PASS | 0 | Final capsule validation. |
| `.venv` activation + targeted Ruff, pytest and OpenAPI/routes neutrality after current-state correction | repo root | PASS | 0 | 26 passed; current-state guard covered. |
| `.venv` activation + current-state stale public wording scan | repo root | PASS | 0 | Stale expert public wording absent. |
| `.venv` activation + `condamad_story_validate.py` and strict lint after current-state correction | repo root | PASS | 0 | Story validation and lint passed. |

## Commands skipped or blocked

- Full repository pytest was not run because this story is documentation/contract scoped and the workspace contains many unrelated dirty backend/story changes from prior work. Targeted unit plus architecture neutrality tests passed.
- Frontend lint/tests were not run because the story forbids frontend changes and no `frontend/src` file was modified by CS-273.

## Review/fix loop validation

- PASS: Story validation and strict story lint rerun after review evidence corrections.
- PASS: Targeted contract and architecture neutrality pytest rerun after review evidence corrections: 25 passed.
- PASS: Targeted contract and architecture neutrality pytest rerun after current-state correction: 26 passed.
- PASS: OpenAPI/routes neutrality command rerun from the loaded FastAPI app.
- PASS: Targeted Ruff format check and Ruff lint for the CS-273 backend unit test.
- PASS: `git diff --check` for CS-273 paths, with line-ending warnings only.

## DRY / No Legacy evidence

- One canonical contract document added for `expert_technical_projection_v1`.
- Existing primitive registry reused; no parallel registry created.
- Existing current-state architecture synthesis reclassified; no parallel architecture summary created.
- CS-270/CS-271/CS-256/CS-266/CS-272 terminology reused.
- No shim, alias, compatibility wrapper, fallback branch, route, serializer, service, DB model, migration, generated client or frontend surface added.
- `ASTRO_EXPERT` remains target-only and absent from active RBAC source.

## Diff review

- `git diff --stat` over tracked CS-273 paths shows only the registry doc as tracked before this run; new contract/test/evidence files are untracked until added by the user.
- `git diff --check` over CS-273 paths returned exit 0.
- Scoped status confirms app roots contain pre-existing unrelated dirty files but no CS-273 app implementation file was edited.

## Final worktree status

- CS-273 files are modified/untracked as expected.
- Existing unrelated dirty files remain untouched.

## Remaining risks

- The workspace remains dirty outside CS-273, but no CS-273 implementation issue remains.

## Suggested reviewer focus

- Confirm the reclassification wording in `docs/architecture/official-product-primitives-public-projections.md` is acceptable for a document historically named around public primitives.

## Feedback loop routing

- `no-propagation`: no reusable process correction is needed beyond the local evidence note about the accidental helper-generated parallel capsule, which was fixed in this run.
