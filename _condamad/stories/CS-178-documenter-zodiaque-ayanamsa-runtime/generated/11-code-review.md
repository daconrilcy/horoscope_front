# CONDAMAD Code Review CS-178

## Review target

`_condamad/stories/CS-178-documenter-zodiaque-ayanamsa-runtime/00-story.md`

## Inputs reviewed

- Story, final evidence, regression guardrails and current repository diff.
- `backend/docs/astrology-zodiac-runtime-contract.md`, docs ownership index and zodiac/provider tests.

## Findings

None.

## Acceptance audit

- AC1-AC2: documentation states the service/provider/longitude/sign flow and that `sign_from_longitude` does not apply ayanamsa.
- AC3: exact tropical/sidereal/ayanamsa proof commands are listed and tests pass.
- AC4: targeted helper scan shows existing owners only: `zodiac.py::sign_from_longitude`, `pdf_export_service.py::_safe_sign_code`, house assignment and Swiss Ephemeris sidereal setup.

## Validation audit

- `pytest -q tests/unit/domain/astrology/test_zodiac.py app/tests/unit/test_ephemeris_provider.py app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py app/tests/unit/test_natal_calculation_service.py app/tests/unit/test_backend_docs_ownership.py` - PASS, 84 passed.
- `rg -n "def .*sign.*longitude|ZODIAC_SIGNS|ayanamsa.*sign_from_longitude|set_sid_mode" app/domain/astrology app/services/natal -g "*.py"` - PASS, hits classified as expected owners.
- `ruff format .` - PASS.
- `ruff check .` - PASS.
- `pytest -q` - PASS, 2588 passed, 1 skipped, 1175 deselected.
- `python -B .agents/skills/condamad-dev-story/scripts/condamad_validate.py _condamad/stories/CS-178-documenter-zodiaque-ayanamsa-runtime` - PASS.
- `git diff --check` - PASS.
- Backend `/docs` startup on `127.0.0.1:8015` - PASS, HTTP 200.

## Verdict

CLEAN

Iterations: 1 review/fix iteration in this review-fix loop.
