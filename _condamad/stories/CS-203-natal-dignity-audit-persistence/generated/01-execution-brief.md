<!-- Brief d'execution CONDAMAD genere pour CS-203. -->

# Execution Brief

## Objective

Activer la persistance interne des resultats de dignites planetaires natales
deja calcules dans `astral_chart_planet_dignity_results`, une ligne par
planete et par `chart_results.id`, sans modifier le calcul astrologique ni le
payload public.

## Boundaries

- Story key: `CS-203-natal-dignity-audit-persistence`
- Primary owner: `backend/app/services/chart`
- Repository owner: `backend/app/infra/db/repositories/dignity_reference_repository.py`
- Public projection owner unchanged: `backend/app/services/chart/json_builder.py`
- Out of scope: `frontend/**`, `backend/app/api/**`, `backend/migrations/**`,
  `docs/db_seeder/**`, dignity/sect/condition/dominance/interpretation engines.

## Done Conditions

- `ChartResultService.persist_trace` writes audit rows from `NatalResult.dignities`.
- Audit rows match precomputed scores, breakdowns, chart sect and planet sect condition.
- Re-running the audit upsert for the same chart result is idempotent.
- Public payload tests remain stable.
- Persistent evidence files exist under `evidence/`.
- Required tests, scans, lint and story validation are recorded in final evidence.

## Halt Conditions

- The existing schema cannot link audit rows to `chart_results.id`.
- A migration or seed change becomes necessary.
- Audit persistence would require recalculating dignities or sect.
- Required validation fails repeatedly without a scoped fix.
