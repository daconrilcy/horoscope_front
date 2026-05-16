# CONDAMAD Code Review CS-177

## Review target

`_condamad/stories/CS-177-finaliser-i18n-astrologique-backend/00-story.md`

## Inputs reviewed

- Story, final evidence, regression guardrails and current repository diff.
- Resolver, chart/natal consumers, PDF export service and localization tests.

## Findings

None remaining.

## Findings fixed

### CR-1 High - PDF labels masked resolver failures

- Bucket: patch
- Location: `backend/app/services/natal/pdf_export_service.py`
- Source layer: no-legacy / edge
- Evidence: `_resolve_pdf_labels` caught `Exception` and returned `AstrologyLabels.technical_fallback()`, which could silently hide DB/reference failures in the PDF consumer.
- Impact: CS-177 requires one durable resolver and no per-consumer language fallback; the broad catch created a second failure behavior.
- Fix: removed the broad fallback and updated PDF tests to provide explicit empty resolver query results.

## Acceptance audit

- AC1: resolver covers signs, planets, aspects and houses.
- AC2/AC4: targeted local mappings are absent.
- AC3: astro context ownership remains unchanged.
- AC5: `app/domain/astrology` has no translation resolver/model dependency.

## Validation audit

- `pytest -q app/tests/unit/test_astrology_translation_resolver.py app/tests/unit/test_astrology_localization_guardrails.py app/tests/unit/test_natal_pdf_export_service.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_natal_interpretation_service.py` - PASS, 63 passed.
- `rg -n "PLANET_NAMES_FR|ASPECT_NAMES_FR|SIGN_LABELS|SIGN_NAMES_FR|\bSIGNS\s*=\s*\[" app/services app/domain/astrology -g "*.py"` - PASS, no hits.
- `rg -n "AstrologyTranslationResolver|translation_reference|LanguageModel" app/domain/astrology -g "*.py"` - PASS, no hits.
- `ruff format .` - PASS.
- `ruff check .` - PASS.
- `pytest -q` - PASS, 2588 passed, 1 skipped, 1175 deselected.
- `python -B .agents/skills/condamad-dev-story/scripts/condamad_validate.py _condamad/stories/CS-177-finaliser-i18n-astrologique-backend` - PASS.
- `git diff --check` - PASS.
- Backend `/docs` startup on `127.0.0.1:8015` - PASS, HTTP 200.

## Verdict

CLEAN

Iterations: 2 review/fix iterations in this review-fix loop.
