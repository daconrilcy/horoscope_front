# CONDAMAD Code Review - CS-208

## Review target

- Story: `CS-208-advanced-planetary-conditions-contracts`
- Capsule: `_condamad/stories/CS-208-advanced-planetary-conditions-contracts`
- Implementation surface:
  - `backend/app/domain/astrology/planetary_conditions/__init__.py`
  - `backend/app/domain/astrology/planetary_conditions/contracts.py`
  - `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - `_condamad/stories/regression-guardrails.md`
  - `_condamad/stories/story-status.md`
  - CS-208 generated evidence files

## Inputs reviewed

- `00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `evidence/validation.md`
- `_condamad/stories/regression-guardrails.md`
- Current implementation and tests under `planetary_conditions`

## Iteration 1

Verdict: CHANGES_REQUESTED

### Findings accepted

| ID | Severity | Category | Finding | Resolution |
|---|---|---|---|---|
| CR-1 | High | Validation evidence | AC12 evidence did not explicitly prove venv activation for Python commands. | Accepted. Evidence command rows were updated to include `.\\.venv\\Scripts\\Activate.ps1; ...` for Python/Ruff/Pytest/story validation commands. |
| CR-2 | Medium | Validation evidence | AC11 persisted evidence missed the adjacent `planetary_conditions` zero-hit scan. | Accepted. The scan was run and persisted in validation/final evidence. |
| TR-1 | Low | Evidence consistency | Targeted test count changed from 7 to 8 after defensive mapping hardening. | Accepted. Evidence updated to 8 passed. |
| TR-2 | Low | Lifecycle metadata | `00-story.md` still said `ready-to-dev`. | Accepted. `00-story.md` now says `done`. |

## Iteration 2

Verdict: CLEAN

No remaining code-level or evidence-backed findings after the accepted fixes at
that point.

## Iteration 3

Verdict: CHANGES_REQUESTED

### Findings

#### CR-3 High - Mutable signal collections could escape immutable contracts

- Bucket: patch
- Location: `backend/app/domain/astrology/planetary_conditions/contracts.py:203`
- Source layer: acceptance / edge / no-legacy
- Evidence: `PlanetaryConditionsBundle.signals` and
  `AdvancedPlanetaryConditionsResult.signals` were annotated as tuples and had
  tuple defaults, but caller-provided lists were retained as mutable nested
  collections at runtime.
- Impact: AC10 and `RG-135` require exposed collections to remain immutable.
  A future calculator could pass a list and mutate a supposedly frozen contract
  after construction.
- Suggested fix: normalize both signal collections to tuples in `__post_init__`
  and add a regression test that passes a mutable list.

### Fix applied

- `PlanetaryConditionsBundle.__post_init__` now converts `signals` to `tuple`.
- `AdvancedPlanetaryConditionsResult.__post_init__` now converts `signals` to
  `tuple` while keeping `conditions_by_planet` read-only.
- `test_signal_collections_are_normalized_to_tuples` proves a mutable source
  list does not leak into public contract fields.

## Iteration 4

Verdict: CLEAN

No remaining findings after the CR-3 fix and fresh validation.

## Acceptance audit

- AC1-AC9: PASS, unchanged from prior evidence.
- AC10: PASS after explicit runtime normalization of mutable signal inputs.
- AC11: PASS, adjacent surface diff and integration scan are empty/zero-hit.
- AC12: PASS, targeted tests, Ruff and full pytest passed in the activated
  venv.

## Validation audit

Commands rerun after CR-3:

- `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`: PASS, 9 passed.
- `.\\.venv\\Scripts\\Activate.ps1; ruff format .`: PASS, 1487 files left unchanged.
- `.\\.venv\\Scripts\\Activate.ps1; ruff check .`: PASS, all checks passed.
- `.\\.venv\\Scripts\\Activate.ps1; pytest -q`: PASS, 2825 passed, 1 skipped, 1177 deselected.
- Story validate/lint commands: PASS.
- Required forbidden-symbol scans: zero hits.
- Adjacent surface diff: empty.
- `git diff --check`: PASS, line-ending warnings only on tracked markdown files.

## DRY / No Legacy audit

- No compatibility shim, alias, fallback, duplicate active path or adjacent
  integration was introduced.
- `RG-135` is present and mapped to deterministic test and scan evidence.

## Feedback loop decision

No propagation: the remaining issue was a local contract-hardening gap already
covered by the CS-208 regression test and `RG-135`; it did not require updating
shared process guidance.

## Verdict

CLEAN
