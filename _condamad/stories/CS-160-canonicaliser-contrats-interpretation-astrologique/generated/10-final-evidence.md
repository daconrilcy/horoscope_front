# Final Evidence CS-160

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-160-canonicaliser-contrats-interpretation-astrologique`
- Source story: `_condamad/stories/CS-160-canonicaliser-contrats-interpretation-astrologique/00-story.md`
- Capsule path: `_condamad/stories/CS-160-canonicaliser-contrats-interpretation-astrologique`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial `git status --short`:
  - `?? _condamad/stories/CS-160-canonicaliser-contrats-interpretation-astrologique/`
  - `?? "docs/recherches astro/next step/story_deprecation_house_rulers.md"`
- Pre-existing dirty files: the CS-160 capsule directory and the untracked docs research file above.
- AGENTS.md files considered: user-provided repository instructions for `c:\dev\horoscope_front`.
- Capsule generated: yes, missing generated files created.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status synchronized to `done`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC4 passed. |
| `generated/04-target-files.md` | yes | yes | PASS | Created. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Created. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Created. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |
| `generated/11-code-review.md` | no | yes | PASS | Final clean review persisted. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `HouseStrengthReason` added and used by `HouseStrengthRuntimeData` and `HouseStrengthEvaluator`. | `pytest -q tests/unit/domain/astrology/test_house_strength.py` PASS; raw reason scans PASS. | PASS | Public serializer converts enum values back to stable strings. |
| AC2 | `HouseStrengthLevel` added, derived from normalized score, and serialized as `strength.level`. | `pytest -q tests/unit/domain/astrology/test_house_strength.py` PASS; `pytest -q app/tests/unit/test_chart_json_builder.py` PASS. | PASS | Existing `dominant` boolean remains. |
| AC3 | Runtime score field is `normalized_score`; `score` property documents public JSON compatibility. | `rg -n "normalized_score|score.*normalisee" app/domain/astrology ../docs -g "*.py" -g "*.md"` PASS with expected implementation hits. | PASS | `strength.score` remains JSON name. |
| AC4 | Evaluator appends enum members only; AST test rejects raw string append values. | `rg -n "reasons\\.append\\(\"" app/domain/astrology -g "*.py"` PASS zero hit. | PASS | `house-strength-reason-scan.md` records scan evidence. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/domain/astrology/interpretation/house_strength_contracts.py` | added | Defines `HouseStrengthReason`, `HouseStrengthLevel`, modifiers and normalized score level resolver. | AC1, AC2, AC3 |
| `backend/app/domain/astrology/runtime/house_runtime_data.py` | modified | Replaces free-string strength data with frozen typed runtime contract, strict serialized rehydration and public `score` property. | AC1, AC2, AC3 |
| `backend/app/domain/astrology/interpretation/house_strength.py` | modified | Produces enum reasons, typed modifiers and normalized score contract. | AC1, AC4 |
| `backend/app/domain/astrology/interpretation/__init__.py` | modified | Removes package-level evaluator re-export and leaves modules canonical. | AC1 |
| `backend/app/domain/astrology/builders/house_runtime_builder.py` | modified | Imports evaluator from its canonical module. | AC1 |
| `backend/app/services/chart/json_builder.py` | modified | Keeps public `score` and string reasons stable, adds `level`. | AC2 |
| `backend/app/services/prediction/engine_orchestrator.py` | modified | Rehydrates serialized strength through strict runtime validation without defaults. | AC1 |
| `backend/tests/unit/domain/astrology/test_house_strength.py` | modified | Asserts enum reasons, normalized score, level, strict rehydration and AST raw reason guard. | AC1, AC2, AC3, AC4 |
| `backend/tests/unit/domain/astrology/test_house_runtime_builder.py` | modified | Asserts runtime builder emits typed reasons and levels. | AC1, AC2 |
| `backend/app/tests/unit/test_chart_json_builder.py` | modified | Asserts JSON compatibility and added public level field. | AC2 |
| `_condamad/stories/CS-160-canonicaliser-contrats-interpretation-astrologique/generated/*` | generated | Capsule, before/after, scan, final evidence and code review evidence. | AC1-AC4 |
| `_condamad/stories/story-status.md` | modified | Synchronizes CS-160 status to `done`. | Workflow |

## Files deleted

None.

## Tests added or updated

- Updated `backend/tests/unit/domain/astrology/test_house_strength.py`.
- Updated `backend/tests/unit/domain/astrology/test_house_runtime_builder.py`.
- Updated `backend/app/tests/unit/test_chart_json_builder.py`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q tests/unit/domain/astrology/test_house_strength.py tests/unit/domain/astrology/test_house_runtime_builder.py app/tests/unit/test_chart_json_builder.py` | `backend/` | PASS | 0 | 20 tests passed before review fixes. |
| `pytest -q app/tests/unit/test_astrology_prediction_boundary.py` | `backend/` | PASS | 0 | 2 tests passed, RG-095 boundary intact. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `pytest -q tests/unit/domain/astrology/test_house_strength.py tests/unit/domain/astrology/test_house_runtime_builder.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_astrology_prediction_boundary.py` | `backend/` | PASS | 0 | 23 tests passed after review fixes. |
| `ruff format --check app/domain/astrology/interpretation/house_strength_contracts.py app/domain/astrology/runtime/house_runtime_data.py app/domain/astrology/interpretation/house_strength.py app/domain/astrology/interpretation/__init__.py app/domain/astrology/builders/house_runtime_builder.py app/services/chart/json_builder.py app/services/prediction/engine_orchestrator.py tests/unit/domain/astrology/test_house_strength.py tests/unit/domain/astrology/test_house_runtime_builder.py app/tests/unit/test_chart_json_builder.py` | `backend/` | PASS | 0 | 10 touched Python files already formatted. |
| `pytest -q` | `backend/` | PASS | 0 | 3653 passed, 12 skipped, 102 warnings in 656.82s. |
| `rg -n "from app\\.domain\\.astrology\\.interpretation import|__getattr__\\(" app tests -g "*.py"` | `backend/` | PASS | 0 | No package import hit; unrelated `__getattr__` hits are outside astrology interpretation. |
| `rg -n "reasons\\.append\\(\"" app/domain/astrology -g "*.py"` | `backend/` | PASS | 1 | Zero hit. |
| `rg -n "reasons\\s*=\\s*\\[|HouseStrengthRuntimeData\\(" app/domain/astrology -g "*.py"` | `backend/` | PASS | 1 | Zero hit. |
| `rg -n "strength\\.score\\s*[<>]=?" app/domain/prediction -g "*.py"` | `backend/` | PASS | 1 | Zero hit. |
| `rg -n "app\\.domain\\.prediction|app\\.services\\.prediction|prediction_categories|house_category_weights|visibility_weight|base_priority|routing_role|DomainRouter|PublicAstroFoundationProjector" app/domain/astrology -g "*.py"` | `backend/` | PASS | 1 | Zero hit. |
| `rg -n "normalized_score|score.*normalisee" app/domain/astrology ../docs -g "*.py" -g "*.md"` | `backend/` | PASS | 0 | Expected implementation/documentation hits found. |
| `python -c "from app.main import app; print(app.title)"` | `backend/` | PASS | 0 | Backend app imports; title `horoscope-backend`. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; Git reported CRLF conversion warnings only. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `ruff format --check .` | no | Full repo format check reports out-of-scope line-ending changes in `app/tests/unit/test_domain_router.py`. | Whole-repo format status includes a pre-existing unrelated issue. | All story-touched Python files pass targeted `ruff format --check`; `ruff check .` passes. |

## DRY / No Legacy evidence

- No raw string reason append remains under `app/domain/astrology`.
- No direct `HouseStrengthRuntimeData(...)` construction remains under `app/domain/astrology`.
- No package-level `HouseStrengthEvaluator` re-export remains.
- Serialized strength rehydration is strict: `score`, `level`, and list `reasons` are required and level must match the derived normalized score.
- No `strength.score` threshold comparison exists under `app/domain/prediction`.
- No astrology -> prediction forbidden import or product symbol hit exists.
- No compatibility shim, alias, fallback or duplicate strength contract was introduced.

## Diff review

- `git diff --stat` reviewed: changes are limited to CS-160 backend contract, tests, story registry and capsule evidence.
- Unrelated untracked file `docs/recherches astro/next step/story_deprecation_house_rulers.md` left untouched.
- `git diff --check` passed with CRLF warnings only.

## Final worktree status

```text
 M _condamad/stories/story-status.md
 M backend/app/domain/astrology/builders/house_runtime_builder.py
 M backend/app/domain/astrology/interpretation/__init__.py
 M backend/app/domain/astrology/interpretation/house_strength.py
 M backend/app/domain/astrology/runtime/house_runtime_data.py
 M backend/app/services/chart/json_builder.py
 M backend/app/services/prediction/engine_orchestrator.py
 M backend/app/tests/unit/test_chart_json_builder.py
 M backend/tests/unit/domain/astrology/test_house_runtime_builder.py
 M backend/tests/unit/domain/astrology/test_house_strength.py
?? _condamad/stories/CS-160-canonicaliser-contrats-interpretation-astrologique/
?? backend/app/domain/astrology/interpretation/house_strength_contracts.py
?? "docs/recherches astro/next step/story_deprecation_house_rulers.md"
```

## Remaining risks

- Aucun risque restant identifie pour CS-160.
- Note hors scope: `ruff format --check .` signale `backend/app/tests/unit/test_domain_router.py`, fichier non modifie par cette story.

## Suggested reviewer focus

- Verify `strength.level` is acceptable as a compatible public addition.
- Verify strict serialized strength rehydration is acceptable for malformed legacy payloads.
- Verify RG-096 guard coverage remains strict enough.
