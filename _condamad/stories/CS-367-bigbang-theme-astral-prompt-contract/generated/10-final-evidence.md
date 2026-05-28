# Final Evidence — CS-367-bigbang-theme-astral-prompt-contract

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-367-bigbang-theme-astral-prompt-contract`
- Source story: `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/00-story.md`
- Source brief: `_story_briefs/cs-367-bigbang-remplacer-ancien-contrat-prompt-theme-astral-supprimer-legacy.md`
- Capsule path: `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract`
- Source finding closure status: full-closure for active `theme_astral` provider prompt path

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `_condamad/run-state.json` untracked before implementation.
- Story-status row matched `CS-367`, story path, and source brief.
- AGENTS.md considered: repository root `AGENTS.md`; no backend-specific `AGENTS.md` found.
- Capsule generated and validated with venv-activated Python.
- Scoped guardrails: `RG-002`, `RG-022`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story unchanged. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC evidence updated. |
| `generated/04-target-files.md` | yes | yes | PASS | Target files updated. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Validation commands updated. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Legacy stance updated. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Final evidence updated. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | `theme_astral` gateway handoff requires `theme_astral_llm_input_v1`; provider payload builder remains canonical. | CS-367 integration + architecture tests; full backend pytest. | PASS |
| AC2 | `chart_json` cannot replace the canonical theme astral payload. | Integration rejection test + legacy scan evidence. | PASS |
| AC3 | `natal_data` cannot replace the canonical theme astral payload. | Integration rejection test + legacy scan evidence. | PASS |
| AC4 | Active prompt contract id is `theme_astral_prompt_v1`; old theme astral prompt id removed from active owners. | Architecture guard + scans. | PASS |
| AC5 | Commercial plan labels stay backend-only. | Integration test and example shape check assert no `plan` key and no `free/basic/premium` string values. | PASS |
| AC6 | Example provider payloads share stable top-level and `input_data` keys. | Regenerated six JSON examples; shape check PASS. | PASS |
| AC7 | Old tests are replaced by canonical contract tests. | Added CS-367 integration/architecture tests; existing CS-366 tests pass. | PASS |
| AC8 | Reintroduction guard fails old path. | `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py` PASS. | PASS |
| AC9 | Public API routes unchanged by this backend-domain story. | No API files changed; `app.routes` and `app.openapi()` loaded successfully with stable hashes recorded. | PASS |
| AC10 | Evidence persisted. | `generated/*` and `evidence/*` updated; final capsule validation PASS. | PASS |
| AC11 | Local startup command exact. | `python -B -m uvicorn app.main:app --host 127.0.0.1 --port 8000` started successfully and was stopped. | PASS |

## Files changed

- Backend runtime/config: `backend/app/domain/llm/configuration/theme_astral_contracts.py`, `backend/app/domain/llm/runtime/gateway.py`, `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`
- Backend governance: `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`
- Backend tests: `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`, `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py`
- Examples/docs: `_condamad/examples/prompt-generation-cartography/**`, `_condamad/docs/prompt-generation-cartography/**`
- Story evidence: `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/**`
- Story registry: `_condamad/stories/story-status.md`

## Files deleted

- None.

## Tests added or updated

- Added `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`.
- Added `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py`.
- Existing theme astral provider payload, handoff, persistence, migration, and doctrine governance tests remain passing.

## Commands run

| Command | Working directory | Result |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py ... --story-key CS-367-bigbang-theme-astral-prompt-contract` | repo root | PASS |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-367-bigbang-theme-astral-prompt-contract` | repo root | PASS |
| `ruff format <modified python files>` | `backend` | PASS |
| `ruff check .` | `backend` | PASS |
| `python -B -m pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py tests/architecture/test_theme_astral_prompt_contract_guard.py --tb=short` | `backend` | PASS |
| `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py tests/integration/llm/test_theme_astral_provider_payload_handoff.py tests/integration/test_theme_astral_prompt_contract_persistence.py tests/integration/test_theme_astral_prompt_contract_migration.py --tb=short` | `backend` | PASS |
| `python -B -m pytest -q tests --tb=short` | `backend` | PASS: `1233 passed, 232 deselected` |
| `python -B -c <example payload shape check>` | `backend` | PASS |
| `python -B -c <app.routes/app.openapi hash check>` | `backend` | PASS |
| `python -B -m uvicorn app.main:app --host 127.0.0.1 --port 8000` | `backend` | PASS startup proof |
| `git diff --check -- <story paths>` | repo root | PASS |

## Commands skipped or blocked

- Frontend validation skipped: no frontend files changed and story non-goal excludes frontend.
- Real provider LLM call skipped: explicit non-goal.

## DRY / No Legacy evidence

- No shim, alias, compatibility wrapper, re-export, duplicate active builder, or silent fallback added.
- `theme_astral` now raises an explicit `InputValidationError` when the canonical provider payload is absent.
- `evidence/legacy-scan-before.txt` and `evidence/legacy-scan-after.txt` persist the before/after old-token scan.
- Remaining old tokens are classified as natal, admin sample, historical docs/tests, or guard evidence, not active `theme_astral` provider input.

## Diff review

- `git diff --check`: PASS.
- Untracked pre-existing `_condamad/run-state.json` left untouched.
- No API router, frontend, migration, provider client, or source brief changes.

## Final worktree status

- Modified and untracked story files are expected for this implementation.
- `_condamad/run-state.json` remains an unrelated pre-existing untracked file.

## Feedback loop routing

- no-propagation: no reusable skill or AGENTS.md learning required beyond story-local evidence.

## Remaining risks

- CS-366 remains marked `ready-to-dev` in `story-status.md` even though its code/tests exist and were reused; reviewer may want registry alignment separately.

## Suggested reviewer focus

- Confirm the explicit `theme_astral` gateway error is the desired behavior when legacy carriers are supplied without `theme_astral_llm_input_v1`.
