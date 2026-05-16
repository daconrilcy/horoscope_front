# Acceptance Traceability - CS-174

| AC | Statut | Preuve |
|---|---|---|
| AC1 | PASS | `AstrologyTranslationResolver.resolve_labels` + `pytest -q app/tests/unit/test_astrology_translation_resolver.py` |
| AC2 | PASS | `build_chart_json(..., labels=...)` ajoute `sign_label`, `cusp_sign_label`, `ruler_planet_sign_label` + `pytest -q app/tests/unit/test_chart_json_builder.py` |
| AC3 | PASS | `build_natal_chart_summary`, `build_chat_natal_hint` et `AstroContextBuilder` consomment `AstrologyLabels` + `pytest -q app/tests/unit/test_natal_context_localization.py` |
| AC4 | PASS | `natal_context._longitude_to_sign` réutilise `domain.astrology.zodiac.sign_from_longitude`; scan resolver dans `app/domain/astrology` zero-hit |
| AC5 | PASS | `pytest -q app/tests/unit/test_astrology_localization_guardrails.py` + scan `SIGN_NAMES_FR` zero-hit sur surfaces ciblees |
