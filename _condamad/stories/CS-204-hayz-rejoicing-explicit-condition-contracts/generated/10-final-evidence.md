<!-- Evidence finale CONDAMAD pour CS-204. -->

# CS-204 Final Evidence

Status: done
Date: 2026-05-20

## Implementation

- Added explicit domain contracts for `HayzCondition`, `RejoicingCondition`,
  `TraditionalPlanetCondition` and `TraditionalConditionsResult`.
- Added `TraditionalConditionNormalizer` as the canonical owner for the
  `traditional_conditions` payload.
- Added `AdvancedPlanetaryCondition.calculation_facts` so hayz exposes
  sect/hemisphere/sign-gender facts from `HayzCalculator`.
- Sourced `rejoicing_house` from runtime accidental dignity rules even when the
  planet is not currently rejoicing, and kept `traditional_conditions: null` in
  no-time JSON projection.
- Kept hayz component facts internal to the domain and removed
  `calculation_facts` from public `advanced_conditions` JSON/frontend types.
- Added false-case hayz evidence so in-sect non-hayz planets expose explicit
  component booleans instead of silent `null`.
- Attached `traditional_conditions` to `NatalResult` and serialized it from
  `json_builder.py` without recalculating doctrine in the projection layer.
- Updated frontend manual API types and `NatalExpertPanel` to render
  `Contrats traditionnels` from explicit backend fields only.
- Added G13/G14 golden cases to lock sect-aware triplicity day/night rulers for
  the same fire element.

## Validation

- `.\.venv\Scripts\Activate.ps1; ruff check .`: PASS.
- `.\.venv\Scripts\Activate.ps1; ruff format --check .`: PASS, 1480 files
  already formatted.
- `.\.venv\Scripts\Activate.ps1; pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/tests/unit/domain/astrology/test_hayz_calculator.py backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py`:
  PASS, 44 passed after adding runtime `rejoicing_house`, no-time, all-hayz-rule
  iteration, and in-sect non-hayz component guards.
- `npm --prefix frontend run test -- NatalExpertPanel`: PASS, 4 passed.
- `npm --prefix frontend run lint`: PASS.
- `npm --prefix frontend run build`: PASS.
- `npm --prefix frontend run dev -- --host 127.0.0.1 --port 5199 --strictPort`:
  PASS via `Start-Process npm.cmd` and HTTP probe `200`; process stopped after
  check.
- `.\.venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --host 127.0.0.1 --port 8011`
  from `backend/`: PASS via HTTP probe `200` on `/docs`; process stopped after
  check.
- `git diff --check`: PASS, whitespace clean; Git reported line-ending
  normalization warnings only.
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/00-story.md`:
  PASS.
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/00-story.md`:
  PASS.

Guard scans are recorded in `evidence/hayz-rejoicing-validation.md`.

## Residual Risk

- No route, migration, seed or persistence behavior was changed.
- `traditional_conditions` is additive and display-only.
- Remaining risk is limited to manual frontend contract maintenance if the API
  shape changes without regenerating/updating `frontend/src/api/natal-chart`.
- The current runtime fixture exposes `planetary_joy` house data for Moon; other
  planets keep `rejoicing_house: null` until the runtime reference provides a
  canonical joy-house rule for them.
