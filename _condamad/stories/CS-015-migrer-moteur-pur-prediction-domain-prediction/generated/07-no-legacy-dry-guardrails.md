# No Legacy / DRY Guardrails

## Canonical owner

- Pure prediction engine: `backend/app/domain/prediction`.
- Prediction use-case orchestration: `backend/app/services/prediction`.

## Forbidden patterns

- Recreating `backend/app/prediction`.
- Importing from `app.prediction` in active application or tests.
- Keeping a compatibility facade, alias, wrapper or re-export under `app.prediction`.
- Importing API, infra, services, settings, SQLAlchemy, `Session`, or LLM runtime from `app.domain.prediction`.
- Duplicating engine schemas or calculators in a second active namespace.

## Required negative evidence

- `rg --files app/prediction` must fail or return no files.
- `rg -n "from app\.prediction|import app\.prediction" app tests -g "*.py"` must have no active import hits.
- `rg -n "fastapi|sqlalchemy|Session|settings|AIEngineAdapter|from app\.infra|from app\.api|from app\.services" app/domain/prediction -g "*.py"` must return no hits.
- `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` must pass.

## Applicable regression guardrails

- `RG-027`: domain prediction must not import infra or SQLAlchemy.
- `RG-030`: `astro_foundation` events must remain resolved.
- `RG-034`: root `app.prediction` must not be recreated.
- `RG-035`: pure prediction engine owner remains `app.domain.prediction`.

## Hit classification rules

| Pattern | Expected classification |
|---|---|
| `app.prediction` strings inside guard tests | `test_guard_expected_hit` |
| `fallback` in service fallback policy | `out_of_scope_with_justification` |
| `legacy` in historical CONDAMAD docs | `allowed_historical_reference` |
| Any active import from `app.prediction` | `active_legacy_remaining_blocker` |

## Review checklist

- One canonical engine namespace exists.
- Services use the canonical namespace directly.
- No legacy import path remains active.
- No domain module imports forbidden outer layers.
- Tests protect the positive engine behavior and negative legacy reintroduction.
