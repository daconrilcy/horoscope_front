# Final Evidence CS-177

## Story status

done

## Preflight

- AGENTS.md lu.
- Regression guardrails lus.
- Local mappings targeted before/after captured.

## Capsule validation

- Capsule générée avec `condamad_prepare.py`.
- Validation finale exécutée avec `condamad_validate.py`.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Resolver covers signs, planets, aspects and houses | resolver tests passed | PASS |
| AC2 | `PLANET_NAMES_FR` and `ASPECT_NAMES_FR` removed | targeted scans passed | PASS |
| AC3 | astro context keeps exact owner | `test_astro_context_builder.py` passed | PASS |
| AC4 | PDF `SIGN_LABELS` removed | localization guard passed | PASS |
| AC5 | domain astrology has no translation imports | scan returned no hits | PASS |

## Files changed

- `backend/app/services/reference_data/astrology_translation_resolver.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/services/llm_generation/shared/natal_context.py`
- `backend/app/services/llm_generation/natal/prompt_context.py`
- `backend/app/services/natal/pdf_export_service.py`
- `backend/app/tests/unit/test_astrology_translation_resolver.py`
- `backend/app/tests/unit/test_astrology_localization_guardrails.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_natal_interpretation_service.py`

## Files deleted

None.

## Tests added or updated

- Updated resolver tests for planets/aspects/houses.
- Updated localization guardrails.
- Updated chart/natal tests to reflect canonical-code fallback without resolver.

## Commands run

- `ruff format .` - PASS
- `ruff check .` - PASS
- `pytest -q` - PASS, 2588 passed, 1 skipped, 1175 deselected
- `pytest -q app/tests/unit/test_astrology_translation_resolver.py app/tests/unit/test_astrology_localization_guardrails.py app/tests/unit/test_natal_pdf_export_service.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_natal_interpretation_service.py` - PASS, 63 passed
- Backend startup `/docs` on `127.0.0.1:8015` - PASS, HTTP 200

## Commands skipped or blocked

None.

## Review fixes

- Removed the broad PDF label `except Exception` fallback so PDF labels fail through the canonical resolver instead of silently masking DB/reference issues.
- Updated PDF export tests to provide explicit empty label query results for isolated mocks.

## DRY / No Legacy evidence

- Single resolver under `services/reference_data`.
- Local FR mappings targeted by the story removed.
- Domain astrology remains independent from translation services.

## Diff review

Scope limited to backend localization consumers, tests and evidence.

## Final worktree status

Dirty with intended story/code changes; no commit requested.

## Remaining risks

None identified.

## Suggested reviewer focus

Check PDF technical fallback behavior when DB label resolution is unavailable.
