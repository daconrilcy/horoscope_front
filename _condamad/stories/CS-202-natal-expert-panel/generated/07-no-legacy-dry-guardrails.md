# No Legacy / DRY Guardrails - CS-202

## Canonical ownership

- Retrieval owner: `frontend/src/api/natal-chart/index.ts`.
- UI owner: `frontend/src/features/natal-chart/NatalExpertPanel.tsx`.
- Styling owner: CSS file, no inline styles.
- Astrology calculation owners: backend public JSON fields only.

## Forbidden frontend patterns

- Doctrinal constants: `DIURNAL_PLANETS`, `NOCTURNAL_PLANETS`,
  `SECT_PLANETS`, `DAY_SECT_PLANETS`, `NIGHT_SECT_PLANETS`,
  `ABOVE_HORIZON_HOUSES`, `BELOW_HORIZON_HOUSES`, `JOY_HOUSES`,
  `PLANETARY_JOYS`, `HAYZ_RULES`.
- Legacy aliases: `sect_legacy`, `legacy_sect`, `sect_code`,
  `chart_sect_code`, `planet_sect_code`, `planet_sect_legacy`,
  `sect_score_legacy`, `legacy_planet_sect`.
- Derivation patterns: `sun.house`, `sun_house`, `planet.house`,
  `house_number >=`, `house_number <=`, `planet_code in`,
  `includes(planet_code)`, `isHayz`, `hayz =`, `chart_sect ===`,
  `chartSect ===`, `sun_above_horizon &&`, `is_in_sect &&`.
- LLM or narrative generation in the panel: `OpenAI`, `AIEngineAdapter`,
  generated advice or personalized copy from `interpretation_adapter`.

## DRY checks

- Reuse existing natal API hook and page integration.
- Extend existing frontend API types instead of creating a parallel payload
  contract.
- Keep grouping helpers display-only and scoped to the panel.
- Do not create a duplicate fetch layer, route, store or backend adapter.

## Required evidence

- Tests prove grouping uses explicit payload booleans/codes.
- Scans prove forbidden symbols are absent or exactly classified.
- Backend no-change diff is empty for forbidden backend paths.
- Evidence files document before/after state and validation results.
