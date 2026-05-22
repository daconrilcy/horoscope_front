# Execution Brief - CS-216

## Story

- Story key: `CS-216-advanced-planetary-conditions-interpretation-profiles`
- Source: `_condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md`
- Objective: create a pure pre-narrative symbolic profile layer for advanced planetary conditions.

## Boundaries

- Add contracts, catalog and runtime under `backend/app/domain/astrology/interpretation/advanced_conditions/`.
- Add an internal `NatalResult.interpretation_profiles_by_planet` field and populate it from already computed `AdvancedPlanetaryConditionsResult`.
- Do not modify public JSON, OpenAPI, API, DB, migrations, frontend, scoring, planetary-condition calculators or dignity modifier behavior.

## Validation

- Targeted profile runtime tests.
- NatalResult integration tests.
- Existing CS-214 and CS-215 targeted tests.
- Story scans for scoring, prompt/LLM/API/DB/frontend terms, final-user text and condition recalculation.
- `ruff format backend`, `ruff check backend`, and `pytest -q` under the activated venv.

## Halt Conditions

- Implementation would require public API/schema changes.
- Implementation would require DB, frontend, migration, scoring or calculator changes.
- A required validation fails repeatedly with no scoped fix.
