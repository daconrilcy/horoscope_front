# Final Evidence - formalize-consultation-guidance-prompt-ownership

## Story status

- Validation outcome: PASS
- Ready for review: completed
- Story key: `formalize-consultation-guidance-prompt-ownership`
- Source story: `_condamad/stories/formalize-consultation-guidance-prompt-ownership/00-story.md`
- Capsule path: `_condamad/stories/formalize-consultation-guidance-prompt-ownership/`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: untracked `_condamad/audits/prompt-generation/` and `_condamad/stories/formalize-consultation-guidance-prompt-ownership/`; warnings on inaccessible pytest temp directories.
- Pre-existing dirty files: `_condamad/audits/prompt-generation/` was already untracked and left untouched.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes, missing `generated/` files created.
- Regression guardrails considered: `RG-004`, `RG-006`, `RG-020`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story completed. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Story-specific. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC4 mapped. |
| `generated/04-target-files.md` | yes | yes | PASS | Target files and searches recorded. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands and expected evidence recorded. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Consultation ownership guardrails recorded. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `docs/llm-prompt-generation-by-feature.md` documents consultation as `guidance_contextual`; `consultation-routing-before.md` and `consultation-routing-after.md` persisted. | `rg -n "guidance_contextual" docs\llm-prompt-generation-by-feature.md` found doc ownership lines. | PASS | No runtime code change required. |
| AC2 | `backend/app/tests/unit/test_guidance_service.py::test_request_contextual_guidance_uses_consultation_placeholder_contract` added. | Targeted pytest passed; full backend pytest passed. | PASS | Verifies `situation`, `objective`, `time_horizon`, `natal_chart_summary`, and `guidance_contextual`. |
| AC3 | `backend/app/tests/unit/test_consultation_generation_service.py::test_precheck_refusal_returns_without_guidance_call` added. | Targeted pytest passed; full backend pytest passed. | PASS | Uses mock precheck and asserts guidance async method is not called. |
| AC4 | `backend/tests/llm_orchestration/test_prompt_governance_registry.py::test_consultation_specifics_remain_guidance_subcase` added. | Targeted pytest passed; forbidden symbol scan classified. | PASS | Blocks `consultation` family and rejects `consultation_contextual` placeholder family. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `docs/llm-prompt-generation-by-feature.md` | modified | Document ownership and non-owner status of `prompt_content`. | AC1 |
| `backend/app/tests/unit/test_guidance_service.py` | modified | Add contextual placeholder contract test. | AC2 |
| `backend/app/tests/unit/test_consultation_generation_service.py` | added | Add precheck refusal/no guidance call test and `prompt_content` guard. | AC3 |
| `backend/scripts/seed_consultation_templates.py` | modified | Convert canonical consultation `prompt_content` seeds to short product objectives. | AC1 |
| `backend/migrations/versions/20260502_0084_normalize_consultation_template_objectives.py` | added | Normalize existing DB rows that still contain prompt-like consultation text. | AC1 |
| `backend/app/tests/integration/test_migration_20260502_0084_consultation_template_objectives.py` | added | Prove migration correction of existing consultation template rows. | AC1 |
| `backend/app/tests/helpers/db_session.py` | modified | Centralize temporary SQLite engine creation for migration tests. | AC1 |
| `backend/tests/llm_orchestration/test_prompt_governance_registry.py` | modified | Add consultation anti-drift governance guard. | AC4 |
| `_condamad/stories/formalize-consultation-guidance-prompt-ownership/consultation-routing-before.md` | added | Baseline routing artifact. | AC1 |
| `_condamad/stories/formalize-consultation-guidance-prompt-ownership/consultation-routing-after.md` | added | Final routing artifact. | AC1 |
| `_condamad/stories/formalize-consultation-guidance-prompt-ownership/generated/*` | generated/modified | CONDAMAD execution and evidence capsule. | AC1-AC4 |

## Files deleted

- None.

## Tests added or updated

- Added `backend/app/tests/unit/test_consultation_generation_service.py`.
- Added `backend/app/tests/integration/test_migration_20260502_0084_consultation_template_objectives.py`.
- Updated `backend/app/tests/unit/test_guidance_service.py`.
- Updated `backend/tests/llm_orchestration/test_prompt_governance_registry.py`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py _condamad\stories\formalize-consultation-guidance-prompt-ownership\00-story.md --root . --story-key formalize-consultation-guidance-prompt-ownership --with-optional` | repo root | PASS | 0 | Capsule generated. |
| `pytest -q app/tests/unit/test_guidance_service.py app/tests/unit/test_consultation_generation_service.py tests/llm_orchestration/test_prompt_governance_registry.py` | `backend/` | FAIL | 1 | First run: 45 passed, 1 failed due test assumption about unknown placeholder family return. |
| `pytest -q app/tests/unit/test_guidance_service.py app/tests/unit/test_consultation_generation_service.py tests/llm_orchestration/test_prompt_governance_registry.py` | `backend/` | PASS | 0 | Rerun after test correction: 46 passed. |
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\formalize-consultation-guidance-prompt-ownership\00-story.md` | `backend/` | PASS | 0 | CONDAMAD story validation passed. |
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\formalize-consultation-guidance-prompt-ownership\00-story.md` | `backend/` | PASS | 0 | CONDAMAD story lint passed. |
| `rg -n "guidance_contextual" docs\llm-prompt-generation-by-feature.md` | repo root | PASS | 0 | Documentation contains ownership references. |
| `rg -n '"consultation"\|consultation_contextual\|developer_prompt.*prompt_content\|PROMPT_FALLBACK_CONFIGS' backend\app\domain backend\app\services backend\tests` | repo root | PASS | 0 | Hits classified as existing fallback governance or expected guard tests; no `developer_prompt.*prompt_content` hit. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `ruff format --check .` | `backend/` | FAIL | 1 | One modified file needed formatting. |
| `ruff format app\tests\unit\test_guidance_service.py` | `backend/` | PASS | 0 | One file reformatted. |
| `ruff format --check .` | `backend/` | PASS | 0 | 1244 files already formatted. |
| `pytest -q` | `backend/` | PASS | 0 | 3501 passed, 12 skipped. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict errors; CRLF warnings only. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\formalize-consultation-guidance-prompt-ownership` | repo root | PASS | 0 | CONDAMAD capsule validation passed. |
| `pytest -q app/tests/integration/test_migration_20260502_0084_consultation_template_objectives.py app/tests/unit/test_consultation_generation_service.py app/tests/unit/test_guidance_service.py tests/llm_orchestration/test_prompt_governance_registry.py` | `backend/` | PASS | 0 | 48 passed after residual-risk migration. |
| `pytest -q app/tests/unit/test_backend_db_test_harness.py app/tests/integration/test_migration_20260502_0084_consultation_template_objectives.py` | `backend/` | PASS | 0 | 5 passed; migration test uses canonical DB helper instead of local SQLite factory. |
| `pytest -q app/tests/integration/test_migration_20260502_0084_consultation_template_objectives.py app/tests/unit/test_backend_db_test_harness.py app/tests/unit/test_consultation_generation_service.py app/tests/unit/test_guidance_service.py tests/llm_orchestration/test_prompt_governance_registry.py` | `backend/` | PASS | 0 | 52 passed after helper refactor. |
| `pytest -q` | `backend/` | PASS | 0 | 3503 passed, 12 skipped after helper refactor. |
| `alembic heads` | `backend/` | PASS | 0 | New head is `20260502_0084`. |
| `git restore -- backend/horoscope.db` | repo root | PASS | 0 | Local SQLite snapshot reverted; migration remains the source of truth for DB changes. |

## Commands skipped or blocked

- None.

## DRY / No Legacy evidence

| Pattern | Hit classification | Evidence |
|---|---|---|
| `consultation_contextual` | `test_guard_expected_hit` | Only appears in governance test as rejected unknown family. |
| `"consultation"` | `test_guard_expected_hit` | Governance test asserts absence from canonical families. |
| `developer_prompt.*prompt_content` | `negative_evidence` | No hits in scan. |
| `PROMPT_FALLBACK_CONFIGS` | `allowed_historical_reference` | Existing fallback governance and tests; no consultation fallback added. |

## Diff review

- `git diff --stat`: tracked diff limited to story files, guidance/consultation/governance tests, DB helper, seed data, migration, and prompt doc; untracked story capsule and new tests are expected story files.
- `git diff --check`: PASS with CRLF warnings only.
- No frontend, API router, dependency, or runtime service logic changed.

## Final worktree status

- Story status: completed.
- Expected modified files: `backend/app/tests/helpers/db_session.py`, `backend/app/tests/unit/test_guidance_service.py`, `backend/scripts/seed_consultation_templates.py`, `backend/tests/llm_orchestration/test_prompt_governance_registry.py`, `docs/llm-prompt-generation-by-feature.md`.
- Residual-risk fix files: `backend/scripts/seed_consultation_templates.py`, `backend/migrations/versions/20260502_0084_normalize_consultation_template_objectives.py`, `backend/app/tests/integration/test_migration_20260502_0084_consultation_template_objectives.py`.
- Final `git status --short`: modified expected source/test/doc files; untracked `_condamad/audits/prompt-generation/`, `_condamad/stories/formalize-consultation-guidance-prompt-ownership/`, migration test, consultation generation unit test, and migration revision.
- Expected untracked files: `_condamad/stories/formalize-consultation-guidance-prompt-ownership/`, `backend/app/tests/integration/test_migration_20260502_0084_consultation_template_objectives.py`, `backend/app/tests/unit/test_consultation_generation_service.py`, `backend/migrations/versions/20260502_0084_normalize_consultation_template_objectives.py`.
- Pre-existing untracked files left untouched: `_condamad/audits/prompt-generation/`.
- `backend/horoscope.db` was restored and is not part of the commit scope.
- `git status --short` still warns on inaccessible pytest temp directories.

## Remaining risks

- None for runtime behavior. Existing canonical consultation template rows are corrected by migration `20260502_0084`.

## Suggested reviewer focus

- Confirm the product decision that consultation-specific prompts remain under `guidance_contextual`.
- Review the classification of `consultation_template.prompt_content` as product objective rather than provider prompt.
