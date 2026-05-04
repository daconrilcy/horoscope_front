# API Import Audit

## Scope

- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/api/v1/routers/internal/llm/qa.py`
- Guard scope: all Python files under `backend/app/api`.

## Canonical imports observed

| File | Canonical prediction imports | Classification |
|---|---|---|
| `backend/app/api/v1/routers/public/predictions.py` | `app.domain.prediction.persisted_snapshot`, `app.domain.prediction.public_projection`, `app.services.prediction.public_predictions` | canonical owner usage |
| `backend/app/api/v1/routers/internal/llm/qa.py` | `app.domain.prediction.persisted_snapshot`, `app.domain.prediction.public_projection`, `app.services.prediction.public_predictions` | canonical owner usage |

## Negative scan

Command, run from `backend/` after venv activation:

```powershell
rg -n "app\.prediction" app/api -g "*.py"
```

Result: zero hits.

## Guard evidence

`backend/app/tests/unit/test_daily_prediction_guardrails.py` now includes
`test_api_prediction_routers_do_not_import_legacy_prediction_namespace`, an AST
guard over `backend/app/api/**/*.py`.
