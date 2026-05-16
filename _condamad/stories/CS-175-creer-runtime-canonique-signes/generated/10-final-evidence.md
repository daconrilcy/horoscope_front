# Final Evidence CS-175

## Story status

done

## Preflight

- AGENTS.md lu.
- `_condamad/stories/regression-guardrails.md` lu.
- Dirty files initiaux: `story-status.md`, capsules CS-175..178 non suivies, `story-writing-review-2026-05-16.md`.

## Capsule validation

- Capsule générée avec `condamad_prepare.py`.
- Validation finale exécutée avec `condamad_validate.py`.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | `sign_runtime_data.py` | `test_sign_runtime_data.py` | PASS |
| AC2 | `sign_runtime_builder.py` | `test_sign_runtime_builder.py` | PASS |
| AC3 | Dignities from `DignityReferenceSet` | scan no-hit `SIGN_DIGNIT|DIGNITIES_BY_SIGN` | PASS |
| AC4 | `NatalResult.signs_runtime` | chart/natal tests passed | PASS |
| AC5 | astrology boundary unchanged | `test_astrology_prediction_boundary.py` passed | PASS |

## Files changed

- `backend/app/domain/astrology/runtime/sign_runtime_data.py`
- `backend/app/domain/astrology/builders/sign_runtime_builder.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/runtime/__init__.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_data.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_builder.py`

## Files deleted

None.

## Tests added or updated

- Added `test_sign_runtime_data.py`.
- Added `test_sign_runtime_builder.py`.

## Commands run

- `ruff format .` - PASS
- `ruff check .` - PASS
- `pytest -q` - PASS, 2588 passed, 1 skipped, 1175 deselected
- Backend startup `/docs` on `127.0.0.1:8015` - PASS, HTTP 200

## Commands skipped or blocked

None.

## DRY / No Legacy evidence

- No local sign list.
- No local dignity mapping.
- No astrology -> prediction import.

## Diff review

Scope limited to astrology runtime, tests and story evidence.

## Final worktree status

Dirty with intended story/code changes; no commit requested.

## Remaining risks

None identified.

## Suggested reviewer focus

Check normalized sign weight policy and additive `NatalResult.signs_runtime`.
