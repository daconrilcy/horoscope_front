# Dev Log

## Preflight

- Initial `git status --short`: `_condamad/stories/regression-guardrails.md` modified, `_condamad/stories/story-status.md` modified, CS-016/CS-017/CS-018 capsule directories untracked.
- AGENTS.md considered: repository root `AGENTS.md`.
- Regression guardrails considered: RG-027, RG-032, RG-036.
- Capsule generated: yes, because only `00-story.md` was present initially.

## Search evidence

- `backend/app/prediction` absent in current worktree.
- DTO owners present under `backend/app/domain/prediction`.
- Repositories DB already import from `app.domain.prediction`.
- No active import `app.prediction.persisted_*` or `app.prediction.context` found in application/tests.

## Implementation notes

- Added a targeted AST guard for repository imports of legacy persisted DTO modules.
- Added persistent classification and before/after inventory artifacts.
- No runtime repository import needed changing because the current worktree already used the canonical domain owner.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `ruff format app/tests/unit/test_daily_prediction_guardrails.py` | PASS | 1 file reformatted |
| `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` | PASS | 15 passed |
| `pytest -q app/tests/integration/test_v3_persistence.py app/tests/integration/test_relative_scoring_service.py` | PASS | 4 passed |
| `pytest -q app/tests/integration/test_daily_prediction_api.py` | PASS | 25 passed |
| `ruff check app/infra/db/repositories app/tests` | PASS | all checks passed |
| `python -c "from app.main import app; print(app.title)"` | PASS | backend app import smoke returned `horoscope-backend` |

## Final `git status --short`

Recorded in `10-final-evidence.md`.
