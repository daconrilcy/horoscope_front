<!-- Audit schema avant activation CS-203. -->

# Dignity Audit Persistence - Before

## Schema

- Table: `astral_chart_planet_dignity_results`
- Model: `AstralChartPlanetDignityResultModel`
- Repository: `DignityReferenceRepository`
- Upsert method: `upsert_chart_planet_dignity_result`
- Functional unique key: `chart_result_id`, `planet_id`, `score_profile_id`, `reference_version_id`
- Link to persisted chart: `chart_result_id -> chart_results.id`

## Persistable Fields

- Score fields: `essential_score`, `accidental_score`, `total_score`,
  `functional_strength_score`, `expression_quality_score`, `intensity_score`.
- JSON fields: `essential_breakdown_json`, `accidental_breakdown_json`,
  `condition_summary_json`, `calculation_context_json`.
- Reference fields resolved by repository: planet code, score profile code,
  astral system name, reference version.

## Before State

- `ChartResultService.persist_trace` created `chart_results` only.
- No audit upsert was called from the canonical chart persistence flow.
- `chart_results.result_payload` was and remains the public restitution source.
- No Alembic migration or seed change is required: the audited table, model,
  foreign keys and unique key already exist.

## Limits

- The audit table has no `user_id` and must not duplicate birth data.
- Missing reference rows should fail explicitly through the existing repository
  resolver, not fallback to inferred values.
