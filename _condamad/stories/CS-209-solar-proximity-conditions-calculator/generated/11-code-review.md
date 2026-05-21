# CONDAMAD Code Review - CS-209

## Review target

- Story: `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
- Implementation surface:
  - `backend/app/domain/astrology/planetary_conditions/contracts.py`
  - `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
  - `backend/app/domain/astrology/planetary_conditions/__init__.py`
  - `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`

## Inputs reviewed

- `AGENTS.md`
- CS-209 story and generated capsule files
- `_condamad/stories/regression-guardrails.md`
- `git diff`, `git diff --stat`, `git status --short`
- Fresh validation evidence from the review/fix closure loop run on 2026-05-21
- Independent read-only review layers:
  - Story conformance: CLEAN
  - Technical risk: CLEAN
  - Source closure: one accepted medium finding, one accepted low evidence finding

## Diff summary

- Added immutable threshold contract.
- Added pure solar proximity calculator.
- Added package exports.
- Added and updated unit tests.
- Added CONDAMAD validation/review evidence.
- No adjacent API, infra, migration, frontend, `NatalResult`, JSON builder, advanced conditions, dignities, condition, dominance, or interpretation adapter diff.

## Findings

None remaining.

## Findings fixed in iteration 1

### CR-1 Medium - Implicit `planet_key` alias

- Bucket: patch
- Location: `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
- Source layer: source closure / no-legacy
- Evidence: initial implementation used `planet_key.strip().lower()`, silently accepting aliases such as `Sun` or surrounding spaces.
- Impact: violated CS-209 No Legacy/no-alias stance.
- Fix: preserve the exact caller key and special-case only exact `planet_key == "sun"`.
- Validation: `test_planet_key_is_not_normalized_as_alias`; targeted tests PASS; full pytest PASS.

### CR-2 Low - Missing review artifact referenced by final evidence

- Bucket: patch
- Location: `_condamad/stories/CS-209-solar-proximity-conditions-calculator/generated/10-final-evidence.md`
- Source layer: evidence
- Evidence: final evidence referenced `generated/11-code-review.md` before it existed.
- Impact: reviewer could not verify persisted review closure.
- Fix: added this review artifact and kept final evidence aligned.

## Acceptance audit

- AC1-AC13: PASS.
- `SolarProximityThresholds` is immutable, slotted, ordered, and tested.
- `calculate_solar_proximity_condition` returns exactly one condition by priority.
- Wrap-around, normalization, inclusive thresholds, Sun handling, custom thresholds, and batch calculation are tested.

## Validation audit

- `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`: PASS, `19 passed in 0.37s` after review fix.
- `ruff format --check .`: PASS, `1489 files already formatted`.
- `ruff check .`: PASS.
- `pytest -q`: PASS, `2835 passed, 1 skipped, 1177 deselected in 265.18s` in the fresh closure review.
- Story validate/lint commands: PASS.
- Backend local startup: PASS, `GET /openapi.json` returned HTTP 200 on `127.0.0.1:8020` with `541782` bytes; server stopped after check.
- Startup command note: first local startup attempt was blocked by an invalid PowerShell redirection shape, then corrected with separate stdout/stderr logs.

## DRY / No Legacy audit

- No alias, shim, fallback, compatibility wrapper, duplicate calculator, or adjacent integration remains.
- `RG-135`: satisfied for contract purity.
- `RG-136`: satisfied for calculator purity.
- Forbidden scans for imports, dependencies, scoring and narrative/LLM terms are zero-hit.

## Commands run by reviewer/main loop

- `git diff -- <adjacent forbidden surfaces>`: empty.
- Required `rg` scans: PASS / zero-hit where expected.
- Validation commands listed above: PASS.
- `git diff --check`: PASS.
- Final `git status --short`: tracked CS-209 files modified; new CS-209 calculator, tests, and evidence files untracked.
- Fresh review iteration: CLEAN, no additional finding.

## Residual risks

None identified.

## Verdict

CLEAN.
