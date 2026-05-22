# CS-213 Validation Evidence

## Baseline

- `contracts.py` already exposed `PlanetVisibilityCondition` and `PlanetVisibilityKey`.
- `PlanetVisibilityThresholds`, `PlanetVisibilityKey.CONJUNCT_SOLAR`, `planetary_visibility_calculator.py` and the targeted calculator test were absent before CS-213.
- `_condamad/stories/regression-guardrails.md` already contained `RG-140` for CS-213.

## Commands

| Command | Result | Evidence |
|---|---|---|
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | PASS | 26 passed in 0.42s. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format .; ruff check .; pytest -q` | PASS | 1497 files unchanged; lint passed; 2913 passed, 1 skipped, 1177 deselected. |
| Review-fix rerun: `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | PASS | 26 passed in 0.41s after `sun_visible` fix. |
| Review-fix rerun: `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format .; ruff check .; pytest -q` | PASS | 1497 files unchanged; lint passed; 2913 passed, 1 skipped, 1177 deselected. |
| Story validate/lint block from `generated/06-validation-plan.md` | PASS | Story validation PASS; contract explanation had no missing contracts; lint PASS; strict lint PASS. |
| Final story/capsule validation after closure status update | PASS | Story validation PASS; strict lint PASS; capsule validation PASS. |
| Forbidden dependency scan | PASS | Zero hits, exit 1 from `rg`. |
| Forbidden scoring scan | PASS | Zero hits, exit 1 from `rg`. |
| Forbidden text generation scan | PASS | Zero hits, exit 1 from `rg`. |
| Forbidden observation/integration scan | PASS | Zero hits, exit 1 from `rg`. |
| Public symbols in allowed package/tests | PASS | Hits limited to `planetary_conditions` contracts/exports/calculator and unit tests. |
| Public symbols in adjacent surfaces | PASS | Zero hits, exit 1 from `rg`. |
| Adjacent diff review | PASS | Empty diff for forbidden adjacent paths. |
| `git diff --check` | PASS | No whitespace errors; line-ending warnings only. |
| Current review rerun: targeted tests | PASS | 26 passed in 0.43s. |
| Current review rerun: forbidden scans and adjacent diff | PASS | Forbidden dependency, scoring, text generation, observation/integration and adjacent public-symbol scans returned zero hits; adjacent diff empty. |
| Current review rerun: `git diff --check` | PASS | No whitespace errors; line-ending warnings only. |
| Final closure quality block: `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format .; ruff check .; pytest -q` | PASS | 1497 files unchanged; lint passed; 2913 passed, 1 skipped, 1177 deselected. |
| Final closure story/capsule validation | PASS | CONDAMAD story validation PASS; strict lint PASS; capsule validation PASS. |
| Final local app import: `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -c "from app.main import app; print(app.title)"` | PASS | Printed `horoscope-backend`. |
| Post-closure targeted review tests | PASS | 26 passed in 0.40s. |
| Post-closure forbidden scans and adjacent diff | PASS | Forbidden dependency, scoring/text/observation, free `Any`, adjacent public-symbol scans returned zero hits; adjacent diff empty. |
| Post-closure quality block: `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format --check .; ruff check .; pytest -q` | PASS | 1497 files already formatted; lint passed; 2913 passed, 1 skipped, 1177 deselected. |
| Post-closure capsule validation | PASS | CONDAMAD validation PASS. |
| Post-closure local app import | PASS | Printed `horoscope-backend`. |

## RG-140 evidence

- `planetary_visibility_calculator.py` imports only `collections.abc.Mapping` and same-package contracts.
- The calculator composes `SolarProximityCondition` and `PlanetarySolarPhaseRelation`; it does not consume longitudes.
- No scoring, interpretation, real observation astronomy, API, DB, service, JSON or frontend integration was added.

## Review findings fixed

- Sun reason contract: fixed by returning `sun_visible` for `planet_key == "sun"` and updating the targeted test.
- Governance status: aligned `00-story.md` and story registry to the lifecycle status.
- Final worktree evidence: refreshed in `generated/10-final-evidence.md` and `generated/11-code-review.md` with `git status --short --untracked-files=all`.
- Review artifact governance: refreshed `generated/11-code-review.md` to remove the incorrect subagent claim and align the closure gate with the required commit/push workflow.
- Post-closure implementation review: no new issue found; evidence refreshed with the latest clean validation pass.
