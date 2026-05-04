# Final Evidence

## Story status

- Validation outcome: PASS
- Review outcome: CLEAN
- Story closure status: done
- Story key: `CS-015-migrer-moteur-pur-prediction-domain-prediction`
- Source story: `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/00-story.md`
- Capsule path: `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/00-story.md`
- Initial `git status --short`: `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, and CS-015/CS-016/CS-017/CS-018 story directories were dirty or untracked before implementation.
- Pre-existing dirty files: same as initial status; treated as user/pre-existing CONDAMAD changes.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes, missing `generated/` files were created for CS-015.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated for this execution. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Covers AC1-AC5. |
| `generated/04-target-files.md` | yes | yes | PASS | Story-specific targets and scans. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable checks listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific No Legacy guardrails. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed after validation. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/domain/prediction` exists in tracked code with engine modules including `schemas.py`, `aggregator.py`, `astro_calculator.py`, signal builders and public projection modules. | `rg --files app/domain/prediction` from `backend` listed the canonical package files. | PASS | Code was already migrated at preflight; no backend code delta was required in this execution. |
| AC2 | `backend/app/services/prediction/*` imports `app.domain.prediction`; `engine_orchestrator.py` consumes the canonical domain modules. | `rg -n "from app\.prediction" app/services/prediction -g "*.py"` returned zero hits. | PASS | |
| AC3 | Existing AST guard `backend/app/tests/unit/test_daily_prediction_guardrails.py` blocks legacy namespace recreation and forbidden domain dependencies. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` passed; forbidden dependency scan under `app/domain/prediction` returned zero hits. | PASS | |
| AC4 | Existing engine and related public astro tests import canonical domain modules and preserve behavior. | `pytest -q app/tests/unit/test_engine_orchestrator.py app/tests/unit/test_transit_signal_v3.py` passed; `pytest -q tests/unit/prediction/test_public_astro_foundation.py` passed. | PASS | |
| AC5 | Added `domain-prediction-before.md` and `domain-prediction-after.md` with observed before/after evidence for this execution. | Both artifacts are present in the CS-015 capsule and referenced by this evidence. | PASS | The "before" artifact captures preflight state because no historical pre-migration tree was available in the current worktree. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/00-story.md` | modified | Mark CS-015 ready for review and tasks complete. | AC1-AC5 |
| `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/domain-prediction-before.md` | added | Persist preflight inventory. | AC5 |
| `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/domain-prediction-after.md` | added | Persist post-validation inventory. | AC5 |
| `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/generated/01-execution-brief.md` | added | Execution capsule brief. | AC1-AC5 |
| `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/generated/03-acceptance-traceability.md` | added | AC traceability. | AC1-AC5 |
| `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/generated/04-target-files.md` | added | Target file and search map. | AC1-AC5 |
| `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/generated/05-implementation-plan.md` | added | Implementation plan based on current repo state. | AC1-AC5 |
| `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/generated/06-validation-plan.md` | added | Validation commands and skip policy. | AC1-AC5 |
| `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/generated/07-no-legacy-dry-guardrails.md` | added | Story-specific No Legacy guardrails. | AC2-AC3 |
| `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/generated/10-final-evidence.md` | added | Final implementation and validation evidence. | AC1-AC5 |
| `_condamad/stories/story-status.md` | modified | Move CS-015 status to `ready-to-review`. | AC1-AC5 |

## Files deleted

None.

## Tests added or updated

No tests were added or updated in this execution. Existing guard and engine tests already cover the canonical domain owner, legacy namespace absence, forbidden imports, and engine behavior.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | Preflight dirty state captured. |
| `rg --files backend/app/prediction backend/app/services/prediction backend/app/tests/unit backend/tests/unit/prediction` | repo root | PASS | 1 | Expected partial non-zero exit because `backend/app/prediction` is absent; output confirmed services/tests and absence of legacy root. |
| `rg -n "from app\.prediction\|import app\.prediction\|app\.prediction" backend/app backend/tests -g "*.py"` | repo root | PASS | 0 | Hits were only guard-test strings in `test_daily_prediction_guardrails.py`; no active import. |
| `rg -n "fastapi\|sqlalchemy\|Session\|settings\|AIEngineAdapter\|from app\.infra\|from app\.api\|from app\.services" backend/app/domain/prediction -g "*.py"` | repo root | PASS | 1 | Zero forbidden dependency hits. |
| `git ls-tree -r --name-only HEAD backend/app/prediction` | repo root | PASS | 0 | Zero tracked legacy files. |
| `git ls-tree -r --name-only HEAD backend/app/domain/prediction` | repo root | PASS | 0 | Tracked canonical domain files present. |
| `rg -n "from app\.domain\.prediction\|import app\.domain\.prediction\|from app\.prediction\|import app\.prediction" backend/app/services/prediction -g "*.py"` | repo root | PASS | 0 | Services import canonical domain modules; no legacy imports. |
| `pytest -q app/tests/unit/test_engine_orchestrator.py app/tests/unit/test_transit_signal_v3.py` | `backend` after venv activation | PASS | 0 | 29 tests passed. |
| `pytest -q tests/unit/prediction/test_public_astro_foundation.py` | `backend` after venv activation | PASS | 0 | 5 tests passed. |
| `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` | `backend` after venv activation | PASS | 0 | 14 tests passed. |
| `rg --files app/domain/prediction` | `backend` | PASS | 0 | Canonical prediction domain files listed. |
| `rg -n "from app\.prediction" app/services/prediction -g "*.py"` | `backend` | PASS | 1 | Zero legacy service import hits. |
| `rg -n "fastapi\|sqlalchemy\|Session\|settings\|AIEngineAdapter\|from app\.infra\|from app\.api\|from app\.services" app/domain/prediction -g "*.py"` | `backend` | PASS | 1 | Zero forbidden domain dependency hits. |
| `rg -n "from app\.prediction\|import app\.prediction" app tests -g "*.py"` | `backend` | PASS | 1 | Zero active legacy import hits. |
| `rg -n "legacy\|compat\|shim\|fallback\|deprecated\|alias" app/domain/prediction app/services/prediction app/tests/unit/test_daily_prediction_guardrails.py -g "*.py"` | `backend` | PASS | 0 | Hits classified under DRY / No Legacy evidence. |
| `ruff check app/domain/prediction app/services/prediction app/tests/unit/test_daily_prediction_guardrails.py` | `backend` after venv activation | PASS | 0 | All checks passed. |
| `ruff format --check app/domain/prediction app/services/prediction app/tests/unit/test_daily_prediction_guardrails.py` | `backend` after venv activation | PASS | 0 | 54 files already formatted. |
| `git diff --stat` | repo root | PASS | 0 | Tracked diff showed pre-existing `_condamad` registry/status changes; untracked CS-015 capsule files are visible in final status. |
| `git diff --check` | repo root | PASS | 0 | No whitespace or conflict-marker errors; Git reported CRLF conversion warnings for pre-existing tracked `_condamad` files. |
| `git status --short` | repo root | PASS | 0 | Final worktree status recorded. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `pytest -q` | no | Full backend suite is broader than CS-015 and was not required by the story validation plan. | A remote unrelated failure could remain undetected. | Targeted engine, transit, public astro foundation, architecture guardrail, Ruff, and import scans passed. |
| Local app startup | no | CS-015 changes no app startup path, API route, frontend, or runtime configuration in this execution. | Startup-only regressions outside the touched surface would not be detected here. | Engine tests import and execute the orchestrator path; guard tests import app-level modules. |

## DRY / No Legacy evidence

- `backend/app/prediction` is absent in tracked code and in the worktree.
- Service imports use `app.domain.prediction`.
- Forbidden domain dependency scan under `app/domain/prediction` returned zero hits.
- Active legacy import scans returned zero hits.
- Broad `legacy|compat|shim|fallback|deprecated|alias` hits were classified:
  - `test_daily_prediction_guardrails.py`: expected guard strings and fallback behavior tests for service failure handling, not legacy namespace support.
  - `app/services/prediction/fallback_policy.py` and `service.py`: business fallback policy outside CS-015 namespace migration; not a compatibility path for `app.prediction`.
  - `app/domain/prediction/astrologer_prompt_builder.py`, `event_detector.py`, `relative_scoring_calculator.py`, `temporal_kernel.py`, `public_projection.py`, `schemas.py`, `natal_sensitivity.py`, and related comments: existing domain/business compatibility vocabulary or V2/V3 model semantics; no active import from `app.prediction`.
  - No hit creates a facade, alias, shim, or re-export for `app.prediction`.

## Diff review

- `git diff --check` passed.
- Relevant hunks reviewed: CS-015 capsule additions, CS-015 story status update, and CS-015 registry status update.
- No backend application code changed during this execution because the canonical domain migration was already present at preflight.

## Final worktree status

```text
 M _condamad/stories/regression-guardrails.md
 M _condamad/stories/story-status.md
?? _condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/
?? _condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/
?? _condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/
?? _condamad/stories/CS-018-remplacer-garde-anti-croissance-par-garde-extinction-prediction/
```

## Remaining risks

None blocking. The only limitation is historical: the current worktree no longer contains a pre-migration `backend/app/prediction`, so `domain-prediction-before.md` records the observed preflight state rather than a reconstructed old tree.

## Review closure

- Review iterations: 1
- Final review artifact: `_condamad/stories/CS-015-migrer-moteur-pur-prediction-domain-prediction/generated/11-code-review.md`
- Final verdict: CLEAN
- Issues fixed during review/fix loop: none; no actionable finding was identified.
- Final validation repeated on 2026-05-04 after venv activation:
  - `pytest -q app/tests/unit/test_engine_orchestrator.py app/tests/unit/test_transit_signal_v3.py`: 29 passed.
  - `pytest -q tests/unit/prediction/test_public_astro_foundation.py`: 5 passed.
  - `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`: 14 passed.
  - `ruff check app/domain/prediction app/services/prediction app/tests/unit/test_daily_prediction_guardrails.py`: pass.
  - `ruff format --check app/domain/prediction app/services/prediction app/tests/unit/test_daily_prediction_guardrails.py`: pass, 54 files already formatted.
  - Required import scans: zero active legacy/service/domain forbidden hits.
