# Final Evidence

Status: ready-to-review

## Résultat

- Les erreurs `Missing aspect orb rule` avec `context='natal'` sont corrigées sans fallback magique: la résolution utilise les règles d'orbes ciblées puis l'orbe canonique de la définition d'aspect.
- Les projections publiques quotidiennes/QA utilisent le `reference_version_id` du snapshot
  persisté pour charger les profils d'aspects cohérents avec le run.
- Les tests unitaires qui fabriquent des aspects natals injectent maintenant explicitement leur `orb_max`, comme le moteur le fait en runtime.
- Les fixtures de régression ont été régénérées avec le runtime corrigé.

## Validation

- `ruff format .` OK.
- `ruff check .` OK.
- `pytest app/tests/integration/test_daily_prediction_api.py -q --long` OK.
- `pytest app/tests/regression/test_engine_non_regression.py -q --long` OK.
- `pytest app/tests/integration/test_daily_prediction_qa.py -q --long` OK.
- `pytest app/tests/integration/test_horoscope_daily_variant_narration.py app/tests/integration/test_intraday_refinement_integration.py app/tests/unit/test_calibration_versioning.py::test_engine_output_has_calibration_metadata app/tests/integration/test_llm_qa_router.py -q --long` OK.
- `pytest -q --long` OK: `3778 passed, 12 skipped in 957.19s`.

## Notes

- `.discord/bot.py` était déjà modifié avant l'intervention et n'a pas été touché.
- Une première tentative de validation a utilisé un chemin de venv erroné depuis
  `backend`; toutes les validations probantes ci-dessus ont été relancées après
  activation correcte de `.\.venv\Scripts\Activate.ps1` depuis la racine.
