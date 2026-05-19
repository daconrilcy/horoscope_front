# No Legacy / DRY Guardrails

## Canonical Ownership

- DB schema/model: `backend/migrations/**`, `backend/app/infra/db/models/**`.
- SQLAlchemy loading: `backend/app/infra/db/repositories/**`.
- Runtime contracts: `backend/app/domain/astrology/runtime/runtime_reference.py`.
- Pure transformation: `backend/app/domain/astrology/condition/**`.
- Natal result: `backend/app/domain/astrology/natal_calculation.py`.
- Public projection: `backend/app/services/chart/json_builder.py`.

## Forbidden

- DB/API/service/prediction imports in `backend/app/domain/astrology/condition/**`.
- SQLAlchemy `Session`, `select(`, local threshold maps, LLM symbols, narration, `micro_note`.
- Recomputing `planet_condition_signals` in `json_builder.py`.
- New frontend code, prompts, narrative text, dominant planets, or advanced condition rules.

## Required Negative Evidence

- Boundary scans from `generated/06-validation-plan.md`.
- `test_astrology_runtime_reference_guard.py` must protect `RG-120`.
- Builder tests must prove inclusive runtime ranges and deterministic sorting.

