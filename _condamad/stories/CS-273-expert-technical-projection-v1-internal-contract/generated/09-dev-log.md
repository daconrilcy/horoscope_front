# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: repository dirty before CS-273, including many unrelated story and backend files.
- Story registry row verified: `CS-273` path and source brief match the requested story and brief.
- Capsule generated files were missing; repaired with `condamad_prepare.py --repair-generated-only` and validated.
- A mistaken helper invocation created `_condamad/stories/cs-273`; it was removed after path verification because it was created by this run and outside scope.

## Search evidence

- Source brief read: `_story_briefs/cs-273-define-expert-technical-projection-v1-admin-astro-expert-only.md`.
- Registry inspected: `docs/architecture/official-product-primitives-public-projections.md`.
- Dependencies inspected with targeted searches: CS-270, CS-271, CS-256, CS-266 and CS-272.
- Scoped guardrails from story: RG-002, RG-022 and story-local OpenAPI/B2C guards.

## Implementation notes

- Created the canonical internal projection contract at `docs/architecture/expert-technical-projection-v1-contract.md`.
- Reclassified only the existing expert projection row and roadmap/mapping wording in `docs/architecture/official-product-primitives-public-projections.md`.
- Added `backend/tests/unit/test_expert_technical_projection_contract.py` for contract shape, registry reclassification and runtime neutrality.
- No route, service, model, migration, serializer, frontend file, generated client, RBAC role or DB object was added.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `.venv` activation + `condamad_prepare.py --repair-generated-only ...` | PASS | Generated missing capsule files. |
| `.venv` activation + `condamad_validate.py ...` | PASS | Capsule structure valid. |
| `.venv` activation + `ruff format backend\tests\unit\test_expert_technical_projection_contract.py` | PASS | One test file formatted. |
| `.venv` activation + `ruff check backend\tests\unit\test_expert_technical_projection_contract.py` | PASS | Targeted lint passed. |
| `.venv` activation + `ruff check backend docs` | PASS | Scoped backend/docs lint passed. |
| `.venv` activation + `python -B -m pytest -q backend\tests\unit\test_expert_technical_projection_contract.py --tb=short` | PASS | 6 tests passed. |
| `.venv` activation + `python -B -m pytest -q backend\tests\unit\test_expert_technical_projection_contract.py backend\tests\architecture\test_api_contract_neutrality.py --tb=short` | PASS | 25 tests passed. |
| `.venv` activation + `python -B -c "from app.main import app; ..."` | PASS | `expert_technical_projection_v1` absent from OpenAPI/routes. |
| `rg` checks over contract and expert registry row | PASS | Required terms present; public expert row wording removed. |
| `git diff --check -- <CS-273 paths>` | PASS | Exit 0; line-ending warning only for existing tracked doc behavior. |

## Issues encountered

- Initial generated capsule files were missing; repaired via the skill helper before reading generated files.
- Initial `condamad_prepare.py --story-key CS-273` inferred a parallel `_condamad/stories/cs-273` capsule; removed immediately after verifying it was created by this run.
- A broad validation `rg` over all docs matched unrelated historical documents and another primitive row; replaced by a scoped expert-row scan.

## Decisions made

- Kept `ASTRO_EXPERT` target-only in documentation and out of active RBAC constants.
- Kept public OpenAPI neutral and did not create any runtime projection implementation.
- Did not update global guardrail registry because the story scoped a story-local guard and explicitly treated registry enrichment as out of scope.

## Final `git status --short`

- CS-273 touched files: `00-story.md`, generated capsule files, `docs/architecture/expert-technical-projection-v1-contract.md`, `docs/architecture/official-product-primitives-public-projections.md`, `backend/tests/unit/test_expert_technical_projection_contract.py`, evidence files and `story-status.md`.
- Pre-existing unrelated dirty files remain in the workspace, especially prior CS-256..CS-272 story artifacts and backend app files.
