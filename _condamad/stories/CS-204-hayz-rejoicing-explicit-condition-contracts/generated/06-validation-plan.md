<!-- Plan de validation CONDAMAD pour CS-204. -->

# CS-204 Validation Plan

## Backend

```powershell
.\.venv\Scripts\Activate.ps1
ruff check .
pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/tests/unit/domain/astrology/test_hayz_calculator.py backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/00-story.md
```

## Frontend

```powershell
npm --prefix frontend test -- NatalExpertPanel
npm --prefix frontend run lint
npm --prefix frontend run build
```

## Guards

```powershell
rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES|JOY_HOUSES|PLANETARY_JOYS|HAYZ_RULES|SIGN_GENDERS" backend/app frontend -g "*.py" -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"
rg -n "SectCalculator|PlanetSectConditionCalculator|AdvancedConditionEngine|AccidentalDignityCalculator" backend/app/services/chart frontend -g "*.py" -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"
rg -n "is_hayz\s*=|is_rejoicing\s*=|planet\.house|planet_code\s+in|sign_gender\s*===|chart_sect\s*===" frontend -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"
rg -n "calculation_facts" frontend/src backend/app/services/chart/json_builder.py
git diff -- backend/app/api backend/app/infra backend/app/domain/prediction backend/migrations docs/db_seeder
```
