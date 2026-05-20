# Validation Plan - CS-202

## Frontend targeted tests

```powershell
npm --prefix frontend test -- NatalExpertPanel
```

Expected: component tests cover full payload, missing blocks, empty blocks,
no-time degraded mode and explicit boolean grouping.

## Frontend quality gates

```powershell
npm --prefix frontend run lint
npm --prefix frontend run build
```

Expected: TypeScript and Vite build pass with no new dependencies.

## Frontend anti-calculation scans

```powershell
rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|SECT_PLANETS|DAY_SECT_PLANETS|NIGHT_SECT_PLANETS" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES|JOY_HOUSES|PLANETARY_JOYS|HAYZ_RULES" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code|planet_sect_code|planet_sect_legacy|sect_score_legacy|legacy_planet_sect" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "sun\.house|sun_house|planet\.house|house_number\s*[<>=]|planet_code\s+in" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "includes\(planet_code\)|isHayz|hayz\s*=|chart_sect ===|chartSect ===" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "sun_above_horizon\s*&&|is_in_sect\s*&&" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "OpenAI|AIEngineAdapter|prompt_hint|personalized|conseil" frontend/src
```

Expected: zero unclassified hits. Display-only hits, if any, must be listed in
`evidence/frontend-expert-panel-validation.md`.

## Backend regression checks

All Python commands must run after venv activation:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/app/tests/unit/test_chart_json_builder.py
pytest -q backend/app/tests/unit/test_chart_result_service.py
pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py
```

Expected: CS-201 public JSON projection regressions pass.

## Backend no-change check

```powershell
git diff -- backend/app/domain/astrology backend/app/services/chart/json_builder.py backend/app/api backend/app/infra migrations docs/db_seeder
```

Expected: no diff.

## Story and evidence checks

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-202-natal-expert-panel/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-202-natal-expert-panel/00-story.md
rg -n "dignities|sect_condition|hayz|out_of_sect|advanced_conditions" _condamad/stories/CS-202-natal-expert-panel/evidence
rg -n "dominant_planets|interpretation_adapter|aucun calcul astrologique|no astrology calculation" _condamad/stories/CS-202-natal-expert-panel/evidence
```

Expected: story contract remains valid and evidence is populated.

## Skipped command rule

Skipped commands are not pass. Record exact command, reason, risk and fallback
evidence in `generated/10-final-evidence.md`.
