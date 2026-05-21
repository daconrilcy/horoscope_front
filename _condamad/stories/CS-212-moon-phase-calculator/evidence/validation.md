# Validation Evidence

## Baseline

- `contracts.py` contenait deja `MoonPhaseCondition`, `MoonPhaseKey` et `WaxingWaningState`.
- `__init__.py` exportait les contrats lunaires mais pas `calculate_moon_phase_condition`.
- `moon_phase_calculator.py`: absent avant implementation.
- `test_moon_phase_calculator.py`: absent avant implementation.
- `RG-139`: present dans le registre comme changement preexistant.

## Implementation

- Added `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`.
- Updated `backend/app/domain/astrology/planetary_conditions/__init__.py`.
- Added `backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py`.

## Validation Commands

All Python commands were run after `.\.venv\Scripts\Activate.ps1`.

| Command | Result | Evidence |
|---|---|---|
| `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | PASS | `51 passed in 0.42s` |
| `ruff format .` | PASS | `1 file reformatted, 1495 files left unchanged` |
| `ruff check .` | PASS | `All checks passed!` |
| `pytest -q` | PASS | `2900 passed, 1 skipped, 1177 deselected in 196.81s` |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-212-moon-phase-calculator/00-story.md` | PASS | `CONDAMAD story validation: PASS` |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-212-moon-phase-calculator/00-story.md` | PASS | Missing required contracts: none |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-212-moon-phase-calculator/00-story.md` | PASS | `CONDAMAD story lint: PASS` |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-212-moon-phase-calculator/00-story.md` | PASS | `CONDAMAD story lint: PASS` |

## Static Guards

| Guard | Result |
|---|---|
| Forbidden app layer imports in `moon_phase_calculator.py` | PASS, zero hits |
| Forbidden external/runtime dependencies in `moon_phase_calculator.py` | PASS, zero hits |
| Forbidden scoring symbols in `moon_phase_calculator.py` | PASS, zero hits |
| Forbidden interpretation/narration/prompt symbols in `moon_phase_calculator.py` | PASS, zero hits |
| Forbidden out-of-scope domains in `moon_phase_calculator.py` | PASS, zero hits |
| Public moon phase symbols in adjacent roots | PASS, zero hits |
| Adjacent production diff | PASS, empty |

## Review Findings Fixed

- Technical review found a floating-point edge case for decimal wrapped longitudes near exact `0.0` and `180.0`.
- Fixed by validating raw finite longitudes, computing `(moon - sun) % 360.0`, snapping major angles with a small tolerance, and adding regression tests for `360.1/0.1` and `540.1/0.1`.
- Second review found that `math.isclose` kept its default relative tolerance around `180.0`, widening the declared snap threshold.
- Fixed by using normalized longitudes explicitly, setting `rel_tol=0.0` for every major-angle snap, and adding a regression test for an angle just outside the absolute tolerance.

## Guardrail Status

- `RG-135`: preserved, contracts unchanged.
- `RG-136`: preserved, solar proximity untouched.
- `RG-137`: preserved, planetary motion untouched.
- `RG-138`: preserved, solar phase relation untouched.
- `RG-139`: satisfied by tests and zero-hit scans for the new moon phase calculator.

## Skipped Commands

None.

## Remaining Risks

None identified.
