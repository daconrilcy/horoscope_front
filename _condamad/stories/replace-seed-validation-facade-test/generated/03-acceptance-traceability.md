# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le comportement persona vide est decide. | `validate_use_case_seed_contracts` raises `SeedValidationError` when `persona_strategy="required"` has no non-empty required placeholder; decision persisted in `seed-validation-decision.md`. | `pytest -q app/tests/unit/test_seed_validation.py`; seed/persona rg scan; decision artifact. | PASS |
| AC2 | Le test facade ne contient plus `pass`. | `backend/app/tests/unit/test_seed_validation.py` replaced with executable assertions. | no-op rg scan; `pytest -q app/tests/unit/test_backend_noop_tests.py`. | PASS |
| AC3 | La validation est executable ou la decision est tracee. | Seed validation runs before `seed_use_cases` mutates DB; current canonical contracts and blank placeholder rejection are validated by tests. | `pytest -q app/tests/unit/test_seed_validation.py`; `python -c "from app.main import app; print(app.title)"`. | PASS |
| AC4 | Une garde bloque les tests no-op futurs. | Added AST guard `backend/app/tests/unit/test_backend_noop_tests.py`; converted pricing test from `assert True` to `pytest.raises`. | `pytest -q app/tests/unit/test_backend_noop_tests.py`; full `pytest -q`. | PASS |

All acceptance criteria have implementation evidence and validation evidence.
