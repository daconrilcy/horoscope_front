# Target Files - CS-202

## Must read

- `AGENTS.md`
- `_condamad/stories/CS-202-natal-expert-panel/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/package.json`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/i18n/natalChart.ts`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/natalChartApi.test.tsx`

## Must search

```powershell
rg -n "NatalExpert|expert|dignities|advanced_conditions|dominant_planets|interpretation_adapter" frontend/src
rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|SECT_PLANETS|DAY_SECT_PLANETS|NIGHT_SECT_PLANETS" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES|JOY_HOUSES|PLANETARY_JOYS|HAYZ_RULES" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code|planet_sect_code|planet_sect_legacy|sect_score_legacy|legacy_planet_sect" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "sun\.house|sun_house|planet\.house|house_number\s*[<>=]|planet_code\s+in" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "includes\(planet_code\)|isHayz|hayz\s*=|chart_sect ===|chartSect ===" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "sun_above_horizon\s*&&|is_in_sect\s*&&" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "OpenAI|AIEngineAdapter|prompt_hint|personalized|conseil" frontend/src
```

## Likely modified files

- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx`
- `frontend/src/features/natal-chart/NatalExpertPanel.css`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/tests/NatalExpertPanel.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- Evidence files under `_condamad/stories/CS-202-natal-expert-panel/evidence/`

## Forbidden unless blocker is documented

- `backend/app/domain/astrology/**`
- `backend/app/services/chart/json_builder.py`
- `backend/app/api/**`
- `backend/app/infra/**`
- `migrations/**`
- `docs/db_seeder/**`
