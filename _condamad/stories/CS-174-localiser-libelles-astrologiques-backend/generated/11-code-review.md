# CONDAMAD Code Review - CS-174

## Review target

- Story: `CS-174-localiser-libelles-astrologiques-backend`
- Story file: `_condamad/stories/CS-174-localiser-libelles-astrologiques-backend/00-story.md`
- Closure class: `non-domain` for audit closure; the story comes from a user brief, not an audit finding.
- Applicable guardrails reviewed: `RG-095`, `RG-106`, `RG-107`, `RG-108`, `RG-109`.

## Inputs reviewed

- `00-story.md`
- `generated/01-baseline-sign-localization.md`
- `generated/03-acceptance-traceability.md`
- `generated/04-target-files.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
- Current tracked diff and untracked CS-174 files.

## Diff summary

- Adds `AstrologyTranslationResolver` and immutable `AstrologyLabels` under `backend/app/services/reference_data/`.
- Removes service-level `SIGN_NAMES_FR` / `SIGNS` sign-label mappings from chart and LLM natal context surfaces.
- Enriches chart JSON with localized sign labels while preserving historic code fields.
- Propagates resolved labels into natal interpretation, consultation, guidance, chat, chart persistence and lunar phase context.
- Adds targeted resolver, chart JSON, natal context and guardrail tests.
- Marks CS-174 `done` in `_condamad/stories/story-status.md`.

## Review layers

- Diff integrity: no unrelated frontend, dependency, migration or generated cache changes detected. Untracked files are story capsule evidence, resolver and tests for CS-174.
- Acceptance audit: AC1 to AC5 mapped to implementation and executable tests.
- Validation audit: lint, format check, targeted tests, broader impacted tests, `git diff --check`, and required scans were rerun by the reviewer.
- DRY / No Legacy audit: no active `SIGN_NAMES_FR`, targeted `SIGNS = [` or competing `SIGN_LABELS` remains in the CS-174 runtime surfaces; the PDF exception remains explicitly out of scope.
- Edge/security/data audit: no new external calls, secrets, auth changes or API error contract changes.

## Findings

Aucun finding ouvert.

## Acceptance audit

| AC | Verdict | Evidence |
|---|---|---|
| AC1 | PASS | `AstrologyTranslationResolver.resolve_labels()` applies explicit language, user default, system `fr`, then canonical code fallback; covered by `test_astrology_translation_resolver.py`. |
| AC2 | PASS | `build_chart_json()` preserves `sign`, `cusp_sign`, `ruler_planet_sign` and adds `sign_label`, `cusp_sign_label`, `ruler_planet_sign_label`; covered by `test_chart_json_builder.py`. |
| AC3 | PASS | `natal_context.py`, `astro_context_builder.py` and calling LLM services consume `AstrologyLabels`; covered by `test_natal_context_localization.py` and impacted LLM tests. |
| AC4 | PASS | `app/domain/astrology` has no resolver or translation model dependency; covered by `tests/unit/domain/astrology/test_zodiac.py` and zero-hit scan. |
| AC5 | PASS | Guard test blocks sign-label mappings in targeted services and documents the PDF exception. |

## Validation audit

Commands run from `c:\dev\horoscope_front` with `.\.venv\Scripts\Activate.ps1` before Python tooling:

- `cd backend; ruff format --check .` - PASS, 1379 files already formatted.
- `cd backend; ruff check .` - PASS.
- `cd backend; pytest -q app/tests/unit/test_astrology_translation_resolver.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_natal_context_localization.py tests/unit/domain/astrology/test_zodiac.py app/tests/unit/test_astrology_localization_guardrails.py` - PASS, 24 passed.
- `cd backend; pytest -q app/tests/unit/test_astrology_translation_resolver.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_natal_context_localization.py tests/unit/domain/astrology/test_zodiac.py app/tests/unit/test_astrology_localization_guardrails.py app/tests/unit/test_natal_interpretation_service.py app/tests/unit/test_astro_context_builder.py app/tests/unit/test_llm_generation_shared_natal_context.py app/tests/unit/test_guidance_service.py app/tests/unit/test_consultation_generation_service.py app/tests/unit/test_chat_guidance_service.py app/tests/unit/test_chart_result_service.py app/tests/unit/test_backend_test_helper_imports.py` - PASS, 116 passed.
- `cd backend; rg -n "SIGN_NAMES_FR|\bSIGNS\s*=\s*\[|SIGN_LABELS" app/services/chart app/services/natal/astro_context_builder.py app/services/llm_generation/shared/natal_context.py app/services/llm_generation/natal/prompt_context.py app/domain/astrology` - PASS, zero hit.
- `cd backend; rg -n "SIGN_NAMES_FR|\bSIGNS\s*=\s*\[|SIGN_LABELS" app/services -g "*.py"` with exact `app/services/natal/pdf_export_service.py` exception filtered out - PASS, no hit outside the documented PDF exception.
- `cd backend; rg -n "AstrologyTranslationResolver|astrology_translation_resolver|translated_name|LanguageModel" app/domain/astrology` - PASS, zero hit.
- `cd backend; python -c "from app.main import app; print(app.title)"` - PASS, app imports and exposes `horoscope-backend`.
- `git diff --check` - PASS.

## DRY / No Legacy audit

- No duplicate sign-label resolver path was introduced.
- `AstrologyLabels.technical_fallback()` is the single technical code fallback for call sites without a DB session; DB-backed service paths resolve labels through `AstrologyTranslationResolver`.
- `backend/app/services/natal/pdf_export_service.py::SIGN_LABELS` remains the explicitly documented out-of-scope exception.
- No re-export of `SIGN_NAMES_FR` remains in `prompt_context.py`.

## Residual risks

Aucun risque restant identifié.

## Verdict

CLEAN
