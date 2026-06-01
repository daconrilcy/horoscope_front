# Dev Log

## Preflight

- Initial `git status --short`:
- `_condamad/run-state.json` was already modified before this implementation.
- Current branch:
- not recorded; no branch was created.
- Existing dirty files:
- `_condamad/run-state.json`

## Search evidence

- Story/status alignment checked for `CS-431`.
- Capsule generated files were missing and repaired with `condamad_prepare.py --repair-generated-only`.
- Scoped guardrails resolved from story IDs: RG-018, RG-021, RG-149, RG-150, RG-152, RG-155, RG-166, RG-171.
- Targeted code inspection covered `backend/app/domain/llm/runtime`, natal runtime/validator services, run models, and integration/orchestration tests.

## Implementation notes

- Added generic snapshot-bound runtime contracts in `contracts.py`.
- Added contract-bound gateway execution, provider call, strict validation, single form repair, and injected validator handling in `gateway.py`.
- Adapted Basic full-reading fake-provider validation to use the gateway contract evaluator and persist contract metadata on runs.
- Added orchestration, rejection workflow, and integration tests.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `condamad_prepare.py --repair-generated-only ...` | PASS | Generated required capsule files. |
| `condamad_validate.py ...` | PASS | Capsule structure valid. |
| `ruff format <changed files>` | PASS | Scoped format only. |
| `ruff check <changed files>` | PASS | Targeted lint. |
| `cd backend; ruff check .` | PASS | Full backend lint. |
| `pytest ...test_contract_bound_llm_gateway.py ...test_contract_bound_rejection_workflow.py` | PASS | 11 passed. |
| `pytest ...test_contract_bound_llm_gateway_rejections.py --long` | PASS | 3 passed. |
| `pytest ...test_theme_natal_basic_full_reading_runtime.py --long` | PASS | 13 passed. |
| `pytest backend/tests/llm_orchestration backend/tests/integration -k "gateway or rejection or generation_contract or theme_natal" --long` | PASS | 82 passed. |
| `pytest ...legacy_extinction.py ...prompt_governance_registry.py ...assembly_resolution.py -k ...` | PASS | 31 passed. |
| `pytest ...test_natal_interpretation_rejected_public_boundary.py --long` | PASS | 8 passed. |
| `python -B -c "from app.main import app; print(len(app.routes))"` | PASS | 230 routes imported. |
| `git diff --check -- <story paths>` | PASS | CRLF warnings only. |

## Issues encountered

- Generated capsule files were absent; repaired per workflow.
- Integration tests are deselected without `--long` by `backend/conftest.py`; rerun with `--long` passed.
- VC10 scan still reports pre-existing `AstroResponse_v3` / `fallback_default` references outside this story's deletion scope.

## Decisions made

- Stored full snapshot version/hash metadata under `llm_generation_runs.raw_provider_response["contract_metadata"]` to avoid an unauthorized schema migration.
- Kept policy validators outside the gateway and injected them through `ResolvedGenerationContractSnapshot.validators`.
- Used service-level public-boundary tests rather than adding a public endpoint cutover, matching story non-goals.

## Final `git status --short`

- `_condamad/run-state.json` remains pre-existing dirty context.
- Story/code/evidence files for CS-431 are modified or untracked as expected.
