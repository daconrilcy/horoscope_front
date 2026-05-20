# Target Files

## Inspected before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-197-sect-audit-explicit-contract/00-story.md`
- `backend/app/domain/astrology/dignities/sect_calculator.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- Targeted unit tests listed in the story.

## Modified files

- `backend/app/domain/astrology/dignities/__init__.py`
- `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/dignities/sect_calculator.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- Targeted backend tests under `backend/tests/unit/domain/astrology/` and `backend/app/tests/unit/`.
- Story evidence files under `_condamad/stories/CS-197-sect-audit-explicit-contract/`.

## Forbidden unless explicitly justified

- `frontend/**`
- condition, dominance, interpretation adapter or advanced condition ownership changes.
- public compatibility aliases for sect.
- local horizon house constants in application code.
