# Final Evidence — replace-deprecated-llm-narrator-tests

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: replace-deprecated-llm-narrator-tests
- Source story: `_condamad/stories/replace-deprecated-llm-narrator-tests/00-story.md`
- Capsule path: `_condamad/stories/replace-deprecated-llm-narrator-tests`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/replace-deprecated-llm-narrator-tests/00-story.md`
- Initial `git status --short`: `_condamad/stories/replace-deprecated-llm-narrator-tests/00-story.md` was already modified.
- Pre-existing dirty files: `_condamad/stories/replace-deprecated-llm-narrator-tests/00-story.md`
- AGENTS.md files considered: `AGENTS.md`
- Regression guardrails considered: `_condamad/stories/regression-guardrails.md` (`RG-006`, `RG-014`)
- Capsule generated: yes; helper initially generated a title-derived duplicate, then generated files were moved into this story directory and the duplicate was removed.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Story validator and strict lint passed. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Story-specific objective and boundaries recorded. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC5 mapped and completed. |
| `generated/04-target-files.md` | yes | yes | PASS | Target files and searches recorded. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Required validation commands recorded. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Legacy class usage and allowed DTOs classified. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed by implementation. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Added `llm-narrator-warnings-before.md` and `llm-narrator-warnings-after.md`. | Before: `pytest -q tests/unit/prediction/test_llm_narrator.py` passed; after: `pytest -q -W error::DeprecationWarning tests/unit/prediction` passed. | PASS | Before artifact shows current targeted suite was already warning-clean because warnings were locally expected; after artifact proves policy mode. |
| AC2 | Replaced nominal class tests in `backend/tests/unit/prediction/test_llm_narrator.py` with canonical adapter/gateway tests. | `pytest -q tests/unit/prediction/test_llm_narrator.py` passed. | PASS | Coverage includes success mapping, gateway failures, invalid output, retry thresholds, summary-only plan, and assembler flag behavior. |
| AC3 | Removed deprecated class import/instantiation from prediction unit tests and related integration coverage. | `pytest -q -W error::DeprecationWarning tests/unit/prediction` passed with 53 tests. | PASS | No global warning ignore was added. |
| AC4 | Added AST guard `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py`; removed `LLMNarrator.narrate` patch from app integration test. | Guard test passed; exact forbidden `rg` scan returned no hits. | PASS | Broad `rg -n "LLMNarrator" tests app/tests -g "test_*.py"` also returned no hits. |
| AC5 | Added `llm-narrator-deprecation-decision.md`; governance test now exercises `FallbackType.NARRATOR_LEGACY` directly. | Decision `rg` command returned expected `LLMNarrator`, `decision`, and `expiry` hits. | PASS | DTO/config references remain allowed and classified by the decision artifact. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/stories/replace-deprecated-llm-narrator-tests/00-story.md` | modified | Story was tightened before implementation and revalidated. | AC4, AC5 |
| `_condamad/stories/replace-deprecated-llm-narrator-tests/generated/01-execution-brief.md` | generated | Execution capsule brief. | all |
| `_condamad/stories/replace-deprecated-llm-narrator-tests/generated/03-acceptance-traceability.md` | generated | AC traceability and final statuses. | all |
| `_condamad/stories/replace-deprecated-llm-narrator-tests/generated/04-target-files.md` | generated | Target file/search map. | all |
| `_condamad/stories/replace-deprecated-llm-narrator-tests/generated/06-validation-plan.md` | generated | Validation command contract. | all |
| `_condamad/stories/replace-deprecated-llm-narrator-tests/generated/07-no-legacy-dry-guardrails.md` | generated | Story-specific legacy guardrails. | AC4, AC5 |
| `_condamad/stories/replace-deprecated-llm-narrator-tests/generated/10-final-evidence.md` | generated | Final implementation evidence. | all |
| `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-deprecation-decision.md` | added | Persist migration decision and expiry rule. | AC5 |
| `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-warnings-before.md` | added | Persist before snapshot. | AC1 |
| `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-warnings-after.md` | added | Persist after warning-policy evidence. | AC1, AC3 |
| `_condamad/stories/regression-guardrails.md` | modified | Add `RG-016` invariant for deprecated narrator class usage in backend tests. | AC4 |
| `backend/tests/unit/prediction/test_llm_narrator.py` | modified | Migrate nominal coverage to `AIEngineAdapter.generate_horoscope_narration`. | AC2, AC3 |
| `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | added | Guard forbidden class usage in backend tests. | AC4 |
| `backend/tests/integration/test_llm_governance_registry.py` | modified | Test narrator legacy fallback governance without class instantiation. | AC3, AC4 |
| `backend/app/tests/integration/test_horoscope_daily_variant_narration.py` | modified | Remove legacy method patch from nominal adapter integration coverage. | AC4 |

## Files deleted

- None.

## Tests added or updated

- Updated `backend/tests/unit/prediction/test_llm_narrator.py`.
- Added `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py`.
- Updated `backend/tests/integration/test_llm_governance_registry.py`.
- Updated `backend/app/tests/integration/test_horoscope_daily_variant_narration.py`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | Initial dirty story file noted; status emitted permission warnings for pytest artifact directories. |
| `python -B .agents/skills/condamad-dev-story/scripts/condamad_prepare.py _condamad/stories/replace-deprecated-llm-narrator-tests/00-story.md` | repo root | PASS | 0 | Generated capsule, then generated files were moved into the intended story directory. |
| `pytest -q tests/unit/prediction/test_llm_narrator.py` | `backend/` | PASS | 0 | Baseline before snapshot: 8 passed. |
| `pytest -q tests/unit/prediction/test_llm_narrator.py` | `backend/` | PASS | 0 | Migrated canonical adapter tests: 8 passed. |
| `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend/` | PASS | 0 | Guard test: 1 passed. |
| `pytest -q -W error::DeprecationWarning tests/unit/prediction` | `backend/` | PASS | 0 | 53 passed; no unclassified deprecation warnings. |
| `rg -n "from app\.prediction\.llm_narrator import LLMNarrator|LLMNarrator\(|LLMNarrator\.narrate" tests app/tests -g "test_*.py"` | `backend/` | PASS | 1 normalized to zero-hit success | No forbidden class usage in tests. |
| `rg -n "LLMNarrator" tests app/tests -g "test_*.py"` | `backend/` | PASS | 1 normalized to zero-hit success | No class-name hits in backend test files. |
| `rg -n "LLMNarrator|decision|expiry" _condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-deprecation-decision.md` | repo root | PASS | 0 | Decision artifact contains expected terms. |
| `pytest -q tests/integration/test_llm_governance_registry.py` | `backend/` | PASS | 0 | 9 passed. |
| `pytest -q tests/llm_orchestration/test_narrator_migration.py` | `backend/` | PASS | 0 | 10 passed. |
| `pytest -q app/tests/integration/test_horoscope_daily_variant_narration.py` | `backend/` | PASS | 0 | 2 passed. |
| `pytest -q app/tests/unit/test_backend_noop_tests.py` | `backend/` | PASS | 0 | 3 passed; RG-014 remains green. |
| `ruff format .; ruff check .` | `backend/` | FAIL then fixed | 1 | Format changed one file; lint requested import organization in the new guard. |
| `ruff check tests/unit/prediction/test_llm_narrator_deprecation_guard.py --fix; ruff format .; ruff check .` | `backend/` | PASS | 0 | Import order fixed; all Ruff checks passed. |
| `pytest -q tests/unit/prediction/test_llm_narrator.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend/` | PASS | 0 | 9 passed after Ruff fix. |
| `pytest -q -W error::DeprecationWarning tests/unit/prediction` | `backend/` | PASS | 0 | 53 passed after Ruff fix; captured in after artifact. |
| `pytest -q` | `backend/` | PASS | 0 | User-confirmed final full suite: 3485 passed, 12 skipped in 824.22s (0:13:44). |
| `python -c "from app.main import app; print(len(app.routes))"` | `backend/` | PASS | 0 | App imports and exposes 220 routes. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/replace-deprecated-llm-narrator-tests/00-story.md` | repo root | PASS | 0 | Story validation passed. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/replace-deprecated-llm-narrator-tests/00-story.md` | repo root | PASS | 0 | Strict story lint passed. |
| `python -B .agents/skills/condamad-dev-story/scripts/condamad_validate.py _condamad/stories/replace-deprecated-llm-narrator-tests` | repo root | PASS | 0 | Capsule validation passed. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict errors; Git reported CRLF conversion warnings for existing text settings. |

## Commands skipped or blocked

- No required command was skipped.

## DRY / No Legacy evidence

- Canonical path is `AIEngineAdapter.generate_horoscope_narration`.
- No new dependencies, wrappers, aliases, or fallback paths were added.
- `LLMNarrator` class import, instantiation, and method patch are absent from `backend/tests` and `backend/app/tests`.
- Remaining `app.prediction.llm_narrator` imports in production/tests are DTO/config-related and classified as allowed by `llm-narrator-deprecation-decision.md`.
- `_condamad/stories/regression-guardrails.md` now records `RG-016` for this invariant.

## Diff review

- `git diff --stat`: reviewed; tracked code diff limited to story, prediction/unit tests, governance integration test, and horoscope daily variant integration test. Untracked generated evidence files are expected for this story.
- `git diff --check`: PASS, with CRLF conversion warnings only.

## Final worktree status

- Expected modified files:
  - `_condamad/stories/replace-deprecated-llm-narrator-tests/00-story.md`
  - `_condamad/stories/regression-guardrails.md`
  - `backend/app/tests/integration/test_horoscope_daily_variant_narration.py`
  - `backend/tests/integration/test_llm_governance_registry.py`
  - `backend/tests/unit/prediction/test_llm_narrator.py`
- Expected untracked files:
  - `_condamad/stories/replace-deprecated-llm-narrator-tests/generated/`
  - `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-deprecation-decision.md`
  - `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-warnings-after.md`
  - `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-warnings-before.md`
  - `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py`
- `git status --short` reports permission warnings for pytest artifact directories; they are unrelated to this story.

## Remaining risks

- The legacy module still hosts `NarratorResult` / `NarratorAdvice`; this is explicitly out of scope and documented as an allowed DTO reference.
- The before snapshot does not show raw warnings because the previous test file locally expected the deprecation warnings; the after snapshot and `-W error` command prove the target warning policy.

## Suggested reviewer focus

- Review that canonical adapter tests preserve the meaningful old assertions without preserving direct OpenAI or `LLMNarrator` behavior.
- Review the AST guard scope for future test roots.
- Review the decision artifact boundary between forbidden class usage and allowed DTO/config references.
