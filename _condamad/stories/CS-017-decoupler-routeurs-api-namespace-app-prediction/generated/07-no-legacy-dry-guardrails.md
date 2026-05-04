# No Legacy / DRY Guardrails

## Canonical owners

- HTTP adaptation: `backend/app/api/v1/routers/public/predictions.py` and `backend/app/api/v1/routers/internal/llm/qa.py`.
- Prediction DTO/projection: `backend/app/domain/prediction`.
- Daily prediction services and narration enrichment: `backend/app/services/prediction`.
- API response contracts: `backend/app/services/api_contracts`.

## Forbidden patterns

- `from app.prediction` or `import app.prediction` under `backend/app/api`.
- Recreating `backend/app/prediction`.
- Compatibility wrapper, re-export, alias, or silent fallback preserving `app.prediction`.
- Moving public projection or narration ownership into an API router.

## Required negative evidence

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
rg -n "app\.prediction" app/api -g "*.py"
pytest -q app/tests/unit/test_daily_prediction_guardrails.py
```

## Hit classification

| Pattern | Classification | Action | Status |
|---|---|---|---|
| `rg -n "app\.prediction" app/api -g "*.py"` | zero active hits | none | PASS |
| `legacy|compat|shim|fallback|deprecated|alias` in touched API/guard files | expected guard/test or unrelated existing fallback wording | no API legacy wrapper introduced | PASS |

## Regression guardrails

- `RG-006`: API remains a strict HTTP adapter.
- `RG-029`: public projection remains deterministic.
- `RG-033`: correlation IDs flow from API/service path.
- `RG-037`: API prediction routers do not import `app.prediction`.

## Reviewer checklist

- Confirm route handlers still delegate to services/domain contracts.
- Confirm no API router imports `app.prediction`.
- Confirm OpenAPI snapshots have no unintended diff.
