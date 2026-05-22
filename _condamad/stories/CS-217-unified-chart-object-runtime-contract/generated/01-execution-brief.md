<!-- Brief d'execution genere pour CS-217. -->

# Execution Brief

- Story key: `CS-217-unified-chart-object-runtime-contract`
- Objective: add the canonical internal runtime contract `ChartObjectRuntimeData`, a pure projection builder, and `NatalResult.chart_objects`.
- Scope: `backend/app/domain/astrology/runtime`, `backend/app/domain/astrology/builders`, `backend/app/domain/astrology/natal_calculation.py`, targeted backend tests, and CONDAMAD evidence.
- Non-goals: no API, DB, migrations, frontend, public JSON projection, scoring, dignity, dominance, interpretation, or advanced condition behavior change.
- Required guardrail: `RG-144` must remain registered and covered by tests/scans.
- No Legacy stance: no shim, alias, fallback, compatibility wrapper, broad allowlist, or duplicate chart-object contract.
- Completion: all AC1-AC18 have code and validation evidence; targeted tests, scans, lint, and regression checks pass or are explicitly blocked.

## Halt Conditions

- `chart_objects` cannot stay internal without public JSON/OpenAPI impact.
- Projection requires API/DB/frontend/service changes.
- A required payload cannot be validated explicitly.
- Validation fails repeatedly without a scoped fix.
