<!-- Plan de validation CONDAMAD pour CS-205. -->

# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- All Python commands run after `.\.venv\Scripts\Activate.ps1`.
- No frontend command is required because CS-205 must not touch frontend code.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Dedicated triplicity golden cases | `pytest -q backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py` | repo root | yes | all tests pass |
| Scoring service integration | `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` | repo root | yes | all tests pass |
| Traditional golden stability | `pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | repo root | yes | all tests pass |
| Dignity contract stability | `pytest -q backend/tests/unit/domain/astrology/test_dignity_contracts.py` | repo root | yes | all tests pass |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Sect contract stability | `pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py` | repo root | yes | all tests pass |
| Natal result contract stability | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | yes | all tests pass |
| Public JSON unchanged | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` | repo root | yes | all tests pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Production triplicity constants | `rg -n "TRIPLICITY_RULERS|DAY_TRIPLICITY_RULERS|NIGHT_TRIPLICITY_RULERS|PARTICIPATING_TRIPLICITY_RULERS|FIRE_TRIPLICITY|EARTH_TRIPLICITY|AIR_TRIPLICITY|WATER_TRIPLICITY" backend/app -g "*.py"` | repo root | yes | no hits |
| Local doctrine patterns | `rg -n "if .*chart_sect.*day|if .*chart_sect.*night|planet_code\\s+in|element\\s*==\\s*['\\\"]fire|element\\s*==\\s*['\\\"]earth|element\\s*==\\s*['\\\"]air|element\\s*==\\s*['\\\"]water" backend/app/domain/astrology/dignities -g "*.py"` | repo root | yes | only classified allowed hits |
| Forbidden imports | `rg -n "Session|select\\(|from app\\.infra|from app\\.services|from app\\.api|from app\\.domain\\.prediction|OpenAI|AIEngineAdapter|prompt" backend/app/domain/astrology/dignities -g "*.py"` | repo root | yes | no forbidden hits |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | repo root | yes | no formatting errors |
| Lint | `ruff check .` | repo root | yes | no lint errors |

## Evidence checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Before JSON validity | `python -m json.tool _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-before.json` | repo root | yes | valid JSON |
| After JSON validity | `python -m json.tool _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-after.json` | repo root | yes | valid JSON |
| Evidence content | `rg -n "triplicity|day|night|participating|runtime|no score change|no public payload change" _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence` | repo root | yes | expected evidence hits |
| Forbidden path diff | `git diff -- backend/app/api backend/app/infra backend/app/domain/prediction backend/migrations docs/db_seeder frontend` | repo root | yes | empty diff |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff whitespace | `git diff --check` | repo root | yes | no whitespace or conflict-marker errors |
| Diff summary | `git diff --stat` | repo root | yes | only CS-205 files and targeted tests changed |
| Worktree status | `git status --short` | repo root | yes | expected files only |

