# No Legacy / DRY Guardrails - CS-006

## Canonical destinations

- Application orchestration prediction: `backend/app/services/prediction`.
- Pure prediction engine internals: future owner `backend/app/domain/prediction`, not migrated in this story.
- DB/persistence adapters: `backend/app/infra/**` or service-owned adapters, not migrated in this story.

## Forbidden patterns

- `backend/app/prediction/engine_orchestrator.py` after migration.
- `from app.prediction.engine_orchestrator import ...`
- Re-exporting `EngineOrchestrator` or `DailyEngineMode` from `backend/app/prediction/__init__.py`.
- `backend/app/prediction/llm_narrator.py`.
- `from app.prediction.llm_narrator import LLMNarrator`.
- New Python files under `backend/app/prediction` absent from the approved after inventory.

## Required negative evidence

- Scan old orchestrator import path.
- Scan `LLMNarrator`.
- AST guard against namespace growth.
- Diff review confirming no compatibility facade.

## Applicable regression guardrails

- `RG-016`: tests must not consume deprecated `LLMNarrator`.
- `RG-017`: runtime must not reintroduce direct OpenAI via `LLMNarrator`.
- `RG-019`: horoscope daily prompt assembly remains outside `AstrologerPromptBuilder`.
- `RG-026`: `app.prediction` convergence must not be bypassed by shim, alias, fallback or re-export.

## Review checklist

- One canonical active import path for `EngineOrchestrator`.
- No old module left in `app.prediction`.
- No re-export from the old namespace.
- Guard fails on unclassified growth under `app/prediction`.
