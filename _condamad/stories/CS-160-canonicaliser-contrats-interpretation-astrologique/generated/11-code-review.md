# CONDAMAD Code Review CS-160

## Review target

- Story: `CS-160-canonicaliser-contrats-interpretation-astrologique`
- Review date: 2026-05-14
- Scope: backend house strength interpretation contract, runtime data,
  chart serialization, prediction rehydration boundary, tests and evidence.

## Inputs reviewed

- `_condamad/stories/CS-160-canonicaliser-contrats-interpretation-astrologique/00-story.md`
- `_condamad/stories/CS-160-canonicaliser-contrats-interpretation-astrologique/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-160-canonicaliser-contrats-interpretation-astrologique/generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md` (`RG-094`, `RG-095`, `RG-096`)
- `git status --short`
- `git diff --stat`
- Relevant hunks for changed backend files and tests
- Current repository searches and targeted validation commands

## Diff summary

- Added `house_strength_contracts.py` with canonical enum reasons, qualitative
  level and modifiers.
- Migrated runtime strength to a frozen typed contract with `normalized_score`.
- Kept public JSON stable for `strength.score` and string `strength.reasons`,
  and added compatible `strength.level`.
- Removed package-level evaluator re-export; consumers import from canonical modules.
- Hardened serialized strength rehydration so incomplete or contradictory
  payloads fail explicitly.
- Added/updated focused tests and CONDAMAD evidence.

## Findings

No open findings.

## Prior findings rechecked

| Finding | Status | Evidence |
|---|---|---|
| Package-level lazy re-export preserved `HouseStrengthEvaluator` old import path. | RESOLVED | `interpretation/__init__.py` no longer exposes lazy `__getattr__`; scan for package imports has no astrology-interpretation package import hit. |
| Serialized strength rehydration accepted missing defaults and silent `None` fallback. | RESOLVED | `engine_orchestrator._extract_runtime_strength` now requires `score`, `level`, and list `reasons`; `HouseStrengthRuntimeData.from_serialized` validates level/score consistency. |
| Evidence/status used limited or stale state. | RESOLVED | `00-story.md`, `story-status.md`, `10-final-evidence.md` now show closure state; validation evidence includes full backend pytest. |

## Acceptance audit

| AC | Verdict | Evidence |
|---|---|---|
| AC1 | PASS | `HouseStrengthReason` is the only reason source in runtime/evaluator; tests assert enum reasons; raw reason scans are zero-hit. |
| AC2 | PASS | `HouseStrengthLevel` is derived and serialized; tests assert runtime level and JSON `strength.level`. |
| AC3 | PASS | `normalized_score` is the runtime field; `score` property preserves stable JSON name and documents normalized scale. |
| AC4 | PASS | Raw reason append and constructor scans under `app/domain/astrology` are zero-hit; AST guard rejects raw string append values. |

## Validation audit

- `pytest -q tests/unit/domain/astrology/test_house_strength.py tests/unit/domain/astrology/test_house_runtime_builder.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_astrology_prediction_boundary.py`: PASS, 23 tests passed.
- `ruff check .`: PASS.
- `pytest -q`: PASS in final evidence, 3653 passed, 12 skipped.
- `git diff --check`: PASS with Git CRLF warnings only.
- `ruff format --check .`: not required for this story; known out-of-scope line-ending issue remains in `backend/app/tests/unit/test_domain_router.py`.

## DRY / No Legacy audit

- No package-level evaluator re-export remains.
- No string reason append remains under `app/domain/astrology`.
- No direct `HouseStrengthRuntimeData(...)` construction remains under `app/domain/astrology`.
- No broad allowlist, fallback, shim, alias or duplicate active strength contract was introduced.
- Serialized rehydration is strict and fails explicitly on incomplete or contradictory strength payloads.
- No `strength.score` threshold comparison exists under `app/domain/prediction`.
- No forbidden astrology -> prediction import or product symbol exists.

## Commands run by reviewer

| Command | Working directory | Result | Notes |
|---|---|---|---|
| `git status --short` | repo root | PASS | Expected CS-160 files plus unrelated untracked docs research file. |
| `git diff --stat` | repo root | PASS | Diff is scoped to CS-160 backend files, story registry and capsule evidence. |
| `git diff --check` | repo root | PASS | CRLF warnings only. |
| `pytest -q tests/unit/domain/astrology/test_house_strength.py tests/unit/domain/astrology/test_house_runtime_builder.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_astrology_prediction_boundary.py` | `backend/` | PASS | 23 tests passed. |
| `ruff check .` | `backend/` | PASS | All checks passed. |
| `rg -n 'reasons\\.append\\(\"|reasons\\s*=\\s*\\[|HouseStrengthRuntimeData\\(' app/domain/astrology -g '*.py'` | `backend/` | PASS | Zero hit; `rg` exit 1 expected for no matches. |
| `rg -n 'strength\\.score\\s*[<>]=?' app/domain/prediction -g '*.py'` | `backend/` | PASS | Zero hit; `rg` exit 1 expected for no matches. |
| `rg -n 'app\\.domain\\.prediction|app\\.services\\.prediction|prediction_categories|house_category_weights|visibility_weight|base_priority|routing_role|DomainRouter|PublicAstroFoundationProjector' app/domain/astrology -g '*.py'` | `backend/` | PASS | Zero hit; `rg` exit 1 expected for no matches. |
| `rg -n 'from app\\.domain\\.astrology\\.interpretation import|__getattr__\\(' app tests -g '*.py'` | `backend/` | PASS | Only unrelated `__getattr__` hits outside astrology interpretation. |
| `rg -n 'normalized_score|score.*normalisee' app/domain/astrology ../docs -g '*.py' -g '*.md'` | `backend/` | PASS | Expected implementation/documentation hits. |

## Reviewer command notes

- Two initial `rg` attempts had quoting/regex errors in PowerShell and were not
  used as evidence. They were rerun with corrected quoting and are listed above.

## Residual risks

- None identified for CS-160.
- Out-of-scope note: whole-repo `ruff format --check .` reports line-ending
  changes in `backend/app/tests/unit/test_domain_router.py`, not touched by this story.

## Verdict

CLEAN
