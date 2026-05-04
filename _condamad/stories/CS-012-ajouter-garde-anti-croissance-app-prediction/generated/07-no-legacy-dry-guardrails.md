# No Legacy / DRY Guardrails - CS-012

## Forbidden patterns

- Compatibility wrapper, alias, re-export or fallback to preserve an old prediction path.
- Wildcard allowlist entry.
- Folder-wide exception under `backend/app/prediction`.
- New Python file under `backend/app/prediction` absent from the persisted allowlist.
- `from app.api` or `import app.api` under `backend/app/prediction`.
- `fastapi` under `backend/app/prediction`.
- `from app.core.config` or `settings` under `backend/app/prediction`.
- `from app.infra` or SQLAlchemy imports under `backend/app/prediction`.
- `AIEngineAdapter` or `LLMNarrator` under `backend/app/prediction`.

## Canonical owners

| Responsibility | Canonical owner |
|---|---|
| Architecture guard | `backend/app/tests/unit/test_daily_prediction_guardrails.py` |
| Prediction allowlist and import exception register | `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/prediction-namespace-allowlist.md` |
| LLM narrator deprecation guard | `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py` |

## Required negative evidence

- `pytest -q app/tests/unit/test_daily_prediction_guardrails.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py`
- `rg -n "from app\\.api|import app\\.api|fastapi|AIEngineAdapter|from sqlalchemy|import sqlalchemy|LLMNarrator" app/prediction -g "*.py"`

## Exceptions

Aucune exception active. Une future exception doit etre une ligne exacte dans
`prediction-namespace-allowlist.md` avec condition de sortie et guard pytest passant.

## Review checklist

- L'allowlist ne contient aucun wildcard.
- Les nouveaux fichiers prediction ne peuvent pas passer sans modification explicite.
- Les imports interdits sont controles par AST.
- Les hits legacy restants sont historiques ou hors scope de cette story.
