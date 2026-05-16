# Final Evidence - CS-174

## Statut

Implementation complete, review/fix applique, final clean review obtenue.

## AC-by-AC

| AC | Résultat | Evidence |
|---|---|---|
| AC1 | PASS | `backend/app/services/reference_data/astrology_translation_resolver.py` résout langue explicite, langue utilisateur, système `fr`, puis code. Tests resolver PASS. |
| AC2 | PASS | `backend/app/services/chart/json_builder.py` conserve les codes et ajoute les champs `sign_label`, `cusp_sign_label`, `ruler_planet_sign_label`. Tests chart JSON PASS. |
| AC3 | PASS | `natal_context.py` et `astro_context_builder.py` consomment `AstrologyLabels` sans `SIGN_NAMES_FR`. Tests localisation natal PASS. |
| AC4 | PASS | `app/domain/astrology` reste sans import resolver/modèles traduction. `tests/unit/domain/astrology/test_zodiac.py` PASS. |
| AC5 | PASS | Guard AST dédié + scans négatifs des symboles interdits PASS. Exception PDF documentée hors périmètre. |

## Fichiers changés

- `backend/app/services/reference_data/astrology_translation_resolver.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/services/chart/result_service.py`
- `backend/app/services/llm_generation/chat/chat_guidance_service.py`
- `backend/app/services/llm_generation/consultation_generation_service.py`
- `backend/app/services/llm_generation/guidance/guidance_service.py`
- `backend/app/services/llm_generation/shared/natal_context.py`
- `backend/app/services/llm_generation/natal/prompt_context.py`
- `backend/app/services/natal/astro_context_builder.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/tests/helpers/natal_result_factory.py`
- `backend/app/tests/unit/test_astrology_translation_resolver.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chat_guidance_service.py`
- `backend/app/tests/unit/test_natal_context_localization.py`
- `backend/app/tests/unit/test_astrology_localization_guardrails.py`
- `backend/app/tests/unit/test_natal_interpretation_service.py`

## Validations exécutées

- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check . --fix; ruff format .; ruff check .` - PASS
- `pytest -q app/tests/unit/test_astrology_translation_resolver.py app/tests/unit/test_chart_json_builder.py` - PASS, 17 passed
- `pytest -q app/tests/unit/test_natal_context_localization.py tests/unit/domain/astrology/test_zodiac.py` - PASS, 4 passed
- `pytest -q app/tests/unit/test_astrology_localization_guardrails.py` - PASS, 3 passed
- `pytest -q app/tests/unit/test_astrology_translation_resolver.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_natal_context_localization.py tests/unit/domain/astrology/test_zodiac.py app/tests/unit/test_astrology_localization_guardrails.py app/tests/unit/test_natal_interpretation_service.py app/tests/unit/test_astro_context_builder.py app/tests/unit/test_llm_generation_shared_natal_context.py app/tests/unit/test_guidance_service.py app/tests/unit/test_consultation_generation_service.py app/tests/unit/test_chat_guidance_service.py app/tests/unit/test_chart_result_service.py app/tests/unit/test_backend_test_helper_imports.py` - PASS, 116 passed
- `ruff format --check .` - PASS, 1379 files already formatted
- `python -c "from app.main import app; print(app.title)"` - PASS, app importable et titre `horoscope-backend`
- `git diff --check` - PASS
- `rg -n "SIGN_NAMES_FR|\bSIGNS\s*=\s*\[|SIGN_LABELS" app/services -g "*.py"` avec filtrage de l'exception exacte `app/services/natal/pdf_export_service.py` - PASS, aucun hit hors exception PDF
- `rg -n "AstrologyTranslationResolver|astrology_translation_resolver|translated_name|LanguageModel" app/domain/astrology` - PASS attendu zero-hit

## Legacy / DRY

- Aucun nouveau mapping local de signes n'est introduit.
- Le fallback technique final est centralisé dans `AstrologyLabels.sign_label` et les chemins disposant d'une session DB résolvent d'abord `AstrologyTranslationResolver`.
- `pdf_export_service.py::SIGN_LABELS` reste l'exception hors périmètre explicitement gardée.

## Risques restants

- Aucun risque restant identifié après corrections de revue acceptées.
