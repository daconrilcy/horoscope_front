# No Legacy / DRY Guardrails

## Forbidden

- Recreate `backend/app/prediction`.
- Add `app.prediction` re-export, alias, facade, wrapper or compatibility package.
- Keep tests importing `app.prediction` as nominal behavior.
- Add fallback imports from `app.domain.prediction` to `app.prediction`.

## Canonical path

- Runtime owner selected for this story: `backend/app/domain/prediction`.
- Active import path: `app.domain.prediction.*`.
- Legacy import path: `app.prediction.*`, forbidden.

## Required negative evidence

- `importlib.util.find_spec("app.prediction") is None`.
- `rg --files app/prediction` from `backend/`: no files.
- `rg -n "from app\.prediction|import app\.prediction" app tests -g "*.py"`: zero-hit.
- `rg -n "from app\.prediction|import app\.prediction" ..\backend\tests -g "*.py"`: zero-hit.

## Guard test

- `backend/app/tests/unit/test_daily_prediction_guardrails.py` now checks:
  - legacy package is not importable;
  - legacy folder has no files;
  - active imports from `app.prediction` are rejected through AST scanning.
