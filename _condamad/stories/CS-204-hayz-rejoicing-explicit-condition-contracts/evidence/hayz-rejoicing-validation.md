<!-- Validation CS-204 des contrats hayz et rejoicing explicites. -->

# Hayz Rejoicing Validation

Date: 2026-05-20

## Scope

- `traditional_conditions` is normalized in the astrology domain from existing
  dignity, sect, advanced-condition and accidental-breakdown facts.
- Public JSON and frontend remain projection/display surfaces.
- G13/G14 close the sect-aware triplicity golden-case gap identified in the
  base brief review.

## Commands

Initial targeted validation:

```powershell
.\.venv\Scripts\Activate.ps1; pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/tests/unit/domain/astrology/test_hayz_calculator.py backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py
npm --prefix frontend run test -- NatalExpertPanel
```

Result:

- Backend: PASS, 39 passed after updating the CS-200 golden snapshot to include
  G13/G14.
- Frontend: PASS, 4 passed after scoping repeated `hayz.is_hayz` assertions.

Final validation:

```powershell
.\.venv\Scripts\Activate.ps1; ruff format backend/app/domain/astrology/advanced_conditions/contracts.py backend/app/domain/astrology/advanced_conditions/__init__.py backend/app/domain/astrology/advanced_conditions/traditional_condition_normalizer.py backend/app/domain/astrology/advanced_conditions/advanced_condition_engine.py backend/app/domain/astrology/advanced_conditions/hayz_calculator.py backend/app/domain/astrology/natal_calculation.py backend/app/services/chart/json_builder.py backend/app/tests/unit/test_chart_json_builder.py backend/tests/unit/domain/astrology/test_hayz_calculator.py backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py
.\.venv\Scripts\Activate.ps1; ruff check .
.\.venv\Scripts\Activate.ps1; pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/tests/unit/domain/astrology/test_hayz_calculator.py backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py
npm --prefix frontend run test -- NatalExpertPanel
npm --prefix frontend run lint
npm --prefix frontend run build
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5199 --strictPort
git diff --check
.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/00-story.md
.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/00-story.md
```

Result:

- Ruff format check: PASS, 1480 files already formatted.
- Ruff check: PASS.
- Backend targeted tests: PASS, 44 passed.
- Frontend `NatalExpertPanel`: PASS, 4 passed.
- Frontend lint/typecheck: PASS.
- Frontend build: PASS.
- Frontend dev server: PASS, Vite ready on `http://127.0.0.1:5199/`; process
  stopped after verification.
- Backend server startup: PASS, `uvicorn app.main:app` returned HTTP `200` on
  `http://127.0.0.1:8011/docs`; process stopped after verification.
- `git diff --check`: PASS; only Git CRLF normalization warnings.
- Story validator: PASS.
- Story lint: PASS.
- Follow-up targeted backend validation after runtime `rejoicing_house` and
  no-time guards: PASS, 42 passed.
- Final targeted backend validation after review fixes for public
  `advanced_conditions`, hayz false-case components and multi-rule hayz
  evaluation: PASS, 44 passed.
- Follow-up `ruff check .`: PASS.
- Follow-up frontend test/lint/build: PASS.
- Follow-up local Vite startup: PASS, HTTP `200` on
  `http://127.0.0.1:5199/`.
- Fresh review-loop validation on 2026-05-20:
  `ruff format --check .`, `ruff check .`, story validate/lint, targeted
  backend tests, `NatalExpertPanel`, frontend lint/build, `git diff --check`,
  scoped forbidden scans, frontend startup and backend startup all PASS.

Guard scans:

```powershell
rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|SECT_PLANETS|DAY_SECT_PLANETS|NIGHT_SECT_PLANETS|ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES|JOY_HOUSES|PLANETARY_JOYS|HAYZ_RULES|SIGN_GENDERS" backend/app/domain/astrology/advanced_conditions backend/app/services/chart frontend/src/features/natal-chart frontend/src/api -g "*.py" -g "*.ts" -g "*.tsx"
rg -n "SectCalculator|PlanetSectConditionCalculator|PlanetDignityScoringService|EssentialDignityCalculator|AccidentalDignityCalculator|AdvancedConditionEngine|PlanetConditionProfileService|PlanetConditionSignalBuilder|PlanetDominanceEngine|InterpretationAdapterEngine|SwissEph|swe" backend/app/services/chart -g "*.py"
rg -n "SectCalculator|PlanetSectConditionCalculator|PlanetDignityScoringService|EssentialDignityCalculator|AccidentalDignityCalculator|AdvancedConditionEngine|PlanetConditionProfileService|PlanetConditionSignalBuilder|PlanetDominanceEngine|InterpretationAdapterEngine" frontend -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"
rg -n "sun\\.house|sun_house|planet\\.house|house_number\\s*[<>=]|planet_code\\s+in|includes\\(planet_code\\)|isHayz|hayz\\s*=|sun_above_horizon\\s*&&|is_in_sect\\s*&&|sign_gender\\s*===" frontend -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"
rg -n "style=\\{\\{|\\bany\\b" frontend/src/features/natal-chart/NatalExpertPanel.tsx frontend/src/api/natal-chart/index.ts frontend/src/tests/NatalExpertPanel.test.tsx
git diff -- backend/app/api backend/app/infra backend/app/domain/prediction backend/migrations docs/db_seeder
```

Result:

- Targeted doctrine/constants scans: PASS, no hits.
- Projection/frontend calculator scans: PASS, no hits.
- Frontend anti-derivation scan: PASS, no hits.
- Frontend inline-style/`any` scan on changed files: PASS, no hits.
- Forbidden path diff: PASS, no changes.
- A broader early scan matched `swe` inside unrelated frontend marketing words;
  classified as false positive and replaced by scoped guard scans above.

## Guardrail Classification

- `json_builder.py`: projection only for `traditional_conditions`; no
  calculator import or doctrine constant.
- `NatalExpertPanel`: display only; no hayz, rejoicing, sect or triplicity
  derivation.
- `HayzCalculator`: canonical owner for hayz facts; no public JSON ownership.
- `TraditionalConditionNormalizer`: canonical owner for the explicit public
  contract.
- `EssentialDignityCalculator`: unchanged runtime triplicity behavior, covered
  by new day/night tests.

## No Score Change

- No score profile, runtime weight, dignity seed, migration, route or status
  code changed.
- G13/G14 assert active triplicity score `3` and inactive ruler absence for the
  same element under day/night sect.
