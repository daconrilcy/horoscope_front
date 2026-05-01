# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `remove-llm-narrator-legacy-direct-openai`
- Source story: `_condamad/stories/remove-llm-narrator-legacy-direct-openai/00-story.md`
- Capsule path: `_condamad/stories/remove-llm-narrator-legacy-direct-openai`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial `git status --short`: recorded in `generated/09-dev-log.md`
- Pre-existing dirty files: `_condamad/stories/regression-guardrails.md`; untracked audit/story directories.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated for this run. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Covers AC1-AC5. |
| `generated/04-target-files.md` | yes | yes | PASS | Story-specific targets. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Includes required checks. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific No Legacy rules. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Will be completed after validation. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `legacy-narrator-scan-before.md`, `legacy-narrator-scan-after.md`, `removal-audit.md`; `backend/app/prediction/llm_narrator.py` deleted. | `rg -n "LLMNarrator|llm_narrator" app tests ..\docs` run and residual hits classified. | PASS | Residual flag/docs/guard hits are not executable facade usage. |
| AC2 | `NarratorAdvice` and `NarratorResult` now live in `backend/app/domain/llm/prompting/narrator_contract.py`; imports migrated in app/tests. | `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py` PASS; combined targeted tests PASS. | PASS | Canonical adapter path unchanged. |
| AC3 | Direct provider runtime deleted with `backend/app/prediction/llm_narrator.py`. | `rg -n "LLMNarrator\(|from app\.prediction\.llm_narrator import LLMNarrator|chat\.completions\.create|openai\.AsyncOpenAI" app tests` zero hits. | PASS | No direct provider call remains in `backend/app` or `backend/tests`. |
| AC4 | `backend/tests/llm_orchestration/test_narrator_migration.py` updated to canonical contract import. | `pytest -q tests/llm_orchestration/test_narrator_migration.py` PASS; combined targeted tests PASS. | PASS | 10 migration tests pass. |
| AC5 | `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py` now checks legacy module absence, class usage, and direct provider calls. | Guard test PASS; `RG-016` and `RG-017` evidence captured. | PASS | Guard has three tests. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/domain/llm/prompting/narrator_contract.py` | modified | Canonical owner for narration dataclasses. | AC2 |
| `backend/app/domain/llm/runtime/adapter.py` | modified | Import `NarratorResult` from canonical contract. | AC2 |
| `backend/app/services/llm_generation/horoscope_daily/narration_service.py` | modified | Import narrative contract from canonical module. | AC2 |
| `backend/tests/llm_orchestration/test_narrator_migration.py` | modified | Preserve migration tests with canonical contract import. | AC4 |
| `backend/app/tests/integration/test_horoscope_daily_variant_narration.py` | modified | Use canonical `NarratorResult` in integration tests. | AC2 |
| `backend/app/tests/unit/prediction/test_public_projection_evidence.py` | modified | Use canonical `NarratorResult` in projection tests. | AC2 |
| `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | modified | Add runtime and provider direct reintroduction guards. | AC3, AC5 |
| `backend/tests/unit/test_historical_facade_transition_guards.py` | modified | Stop inspecting a deleted legacy module. | AC1 |
| `_condamad/stories/remove-llm-narrator-legacy-direct-openai/00-story.md` | modified | Mark tasks/status complete. | AC1-AC5 |
| `_condamad/stories/remove-llm-narrator-legacy-direct-openai/generated/*` | added/modified | CONDAMAD execution and evidence capsule. | AC1-AC5 |
| `_condamad/stories/remove-llm-narrator-legacy-direct-openai/legacy-narrator-scan-before.md` | added | Baseline inventory. | AC1 |
| `_condamad/stories/remove-llm-narrator-legacy-direct-openai/legacy-narrator-scan-after.md` | added | Final scan classification. | AC1, AC3 |
| `_condamad/stories/remove-llm-narrator-legacy-direct-openai/removal-audit.md` | added/modified | Removal classification. | AC1 |

## Files deleted

| File | Purpose | Related AC |
|---|---|---|
| `backend/app/prediction/llm_narrator.py` | Remove executable legacy facade and direct provider path. | AC1, AC3 |
| `backend/tests/unit/prediction/test_llm_narrator.py` | Remove obsolete nominal tests for deleted facade. | AC1, AC4 |

## Tests added or updated

- Updated `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py`.
- Updated migration/integration/projection tests to import `NarratorResult` from the canonical contract.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\remove-llm-narrator-legacy-direct-openai\00-story.md` | `backend/` | PASS | 0 | CONDAMAD story validation passed. |
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\remove-llm-narrator-legacy-direct-openai\00-story.md` | `backend/` | PASS | 0 | CONDAMAD story lint passed. |
| `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend/` | PASS | 0 | 3 tests passed. |
| `pytest -q tests/llm_orchestration/test_narrator_migration.py` | `backend/` | PASS | 0 | 10 tests passed. |
| `ruff check --fix tests\llm_orchestration\test_narrator_migration.py app\tests\integration\test_horoscope_daily_variant_narration.py` | `backend/` | PASS | 0 | 2 import-order fixes applied. |
| `ruff format app\domain\llm\prompting\narrator_contract.py app\tests\unit\prediction\test_public_projection_evidence.py tests\unit\prediction\test_llm_narrator_deprecation_guard.py` | `backend/` | PASS | 0 | 3 touched files formatted. |
| `ruff format --check .` | `backend/` | PASS | 0 | 1242 files already formatted after targeted formatting. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py tests/llm_orchestration/test_narrator_migration.py` | `backend/` | PASS | 0 | 13 tests passed. |
| `python -B -c "from app.main import app; print(app.title)"` | `backend/` | PASS | 0 | FastAPI app imports; title `horoscope-backend`. |
| `rg -n "LLMNarrator|llm_narrator" app tests ..\docs` | `backend/` | PASS | 0 | Residual hits classified in `legacy-narrator-scan-after.md`. |
| `rg -n "LLMNarrator\(|from app\.prediction\.llm_narrator import LLMNarrator|chat\.completions\.create|openai\.AsyncOpenAI" app tests` | `backend/` | PASS | 1 | Zero forbidden active hits. |
| `rg -n "LLMNarrator|llm_narrator" ..\frontend\src app\api ..\docs` | `backend/` | PASS | 0 | API/docs residual hits classified. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict issues; line-ending warnings only. |
| `git diff --stat` | repo root | PASS | 0 | Diff reviewed for story scope. |
| `git status --short` | repo root | PASS | 0 | Final status recorded below; permission warnings on artifact temp dirs. |
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\remove-llm-narrator-legacy-direct-openai\00-story.md` | `backend/` | FAIL | 1 | Failed after briefly setting story status to `ready-for-review`; validator requires `Status: ready-for-dev`. Status was restored. |
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\remove-llm-narrator-legacy-direct-openai\00-story.md` | `backend/` | FAIL | 1 | Same status constraint as validation; status was restored. |
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\remove-llm-narrator-legacy-direct-openai\00-story.md` | `backend/` | PASS | 0 | PASS after restoring required source-story status. |
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\remove-llm-narrator-legacy-direct-openai\00-story.md` | `backend/` | PASS | 0 | PASS after restoring required source-story status. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `pytest -q` | yes | Initially timed out in the agent environment after about 304 seconds. User then ran the full suite successfully: `3479 passed, 12 skipped in 824.26s (0:13:44)`. | None remaining for full backend regression evidence. | User-provided full-suite result plus story-required targeted tests, guard tests, `ruff`, scans, and app import check passed. |

## DRY / No Legacy evidence

- Deleted the old executable module instead of preserving a wrapper or re-export.
- Canonical dataclasses have one owner: `app.domain.llm.prompting.narrator_contract`.
- Active imports of `app.prediction.llm_narrator` were removed from app/tests.
- Forbidden provider direct scan returned zero hits in `app tests`.
- Residual `llm_narrator_enabled` hits are classified as existing feature flag naming, not active direct provider runtime.

## Diff review

- `git diff --stat` reviewed: changes are limited to backend narrative contract/imports, guard tests, deleted legacy module/test, and CONDAMAD evidence files.
- `_condamad/stories/regression-guardrails.md` was already dirty at preflight and was not modified by this implementation.
- `git diff --check` passed with line-ending warnings only.

## Final worktree status

```text
 M _condamad/stories/regression-guardrails.md
 M backend/app/domain/llm/prompting/narrator_contract.py
 M backend/app/domain/llm/runtime/adapter.py
 D backend/app/prediction/llm_narrator.py
 M backend/app/services/llm_generation/horoscope_daily/narration_service.py
 M backend/app/tests/integration/test_horoscope_daily_variant_narration.py
 M backend/app/tests/unit/prediction/test_public_projection_evidence.py
 M backend/tests/llm_orchestration/test_narrator_migration.py
 D backend/tests/unit/prediction/test_llm_narrator.py
 M backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py
 M backend/tests/unit/test_historical_facade_transition_guards.py
?? _condamad/audits/prompt-generation/
?? _condamad/stories/block-supported-family-prompt-fallbacks/
?? _condamad/stories/converge-horoscope-daily-narration-assembly/
?? _condamad/stories/formalize-consultation-guidance-prompt-ownership/
?? _condamad/stories/remove-llm-narrator-legacy-direct-openai/
```

`git status --short` also emitted permission warnings for `.codex-artifacts/pytest-basetemp/`, `.codex-artifacts/tmp/pytest-of-cyril/`, and `artifacts/pytest-basetemp/`.

## Remaining risks

- Existing `llm_narrator_enabled` flag naming remains for compatibility with current API/projection behavior; this story did not rename configuration.
- `00-story.md` keeps `Status: ready-for-dev` because the repository story validator requires it; readiness is recorded in this final evidence file.

## Suggested reviewer focus

- Confirm deletion of `backend/app/prediction/llm_narrator.py` is acceptable without a compatibility import.
- Review the new guard coverage for `RG-016` and `RG-017`.
- Review residual `llm_narrator_enabled` naming classification as out of scope for this removal.
