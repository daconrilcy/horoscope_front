# Baseline Sign Localization - CS-174

## Avant implementation

- `backend/app/services/chart/json_builder.py` declare `SIGN_NAMES_FR`.
- `backend/app/services/natal/astro_context_builder.py` importe `SIGN_NAMES_FR`.
- `backend/app/services/llm_generation/shared/natal_context.py` declare `SIGNS` et `SIGN_NAMES_FR`.
- `backend/app/services/llm_generation/natal/prompt_context.py` re-exporte `SIGN_NAMES_FR`.
- `backend/app/services/natal/pdf_export_service.py::SIGN_LABELS` est hors perimetre et reste documente comme exception PDF.

## Apres implementation

- `SIGN_NAMES_FR` est supprime de `json_builder.py`, `natal_context.py` et du re-export `prompt_context.py`.
- `SIGNS = [...]` est supprime de `natal_context.py`; la conversion longitude -> code réutilise `sign_from_longitude`.
- Les consommateurs ciblés reçoivent `AstrologyLabels` ou résolvent les labels via `AstrologyTranslationResolver`.
- `pdf_export_service.py::SIGN_LABELS` reste hors périmètre et son exception est couverte par `test_astrology_localization_guardrails.py`.
