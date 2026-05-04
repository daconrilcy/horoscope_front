# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Les routes prediction conservent leur contrat runtime. | Les routeurs `public/predictions.py` et `internal/llm/qa.py` restent fonctionnellement inchanges; snapshots OpenAPI avant/apres persistants. | `pytest -q app/tests/integration/test_daily_prediction_api.py`, diff nul `openapi-before.json` / `openapi-after.json`, `pytest -q`. | PASS |
| AC2 | Aucun import `app.prediction` ne reste sous API. | Les imports API consomment `app.domain.prediction` et les services prediction; aucune dependance `app.prediction` sous `backend/app/api`. | `rg -n "app\.prediction" app/api -g "*.py"` zero-hit, garde `test_api_prediction_routers_do_not_import_legacy_prediction_namespace`. | PASS |
| AC3 | Les routeurs consomment des owners canoniques. | Les DTO/projection viennent de `app.domain.prediction`; la narration et les erreurs restent dans `app.services.prediction`; aucune logique metier nouvelle dans les routeurs. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`, `ruff check .`, revue de diff. | PASS |
| AC4 | La narration horoscope daily reste compatible. | Le chemin API/service continue d'enrichir la projection via `enrich_public_prediction_with_horoscope_narration`. | `pytest -q app/tests/integration/test_horoscope_daily_variant_narration.py`, `pytest -q`. | PASS |
| AC5 | Les snapshots OpenAPI avant/apres sont persistants. | Ajout de `openapi-before.json` et `openapi-after.json` dans la capsule CS-017. | `Compare-Object` sans difference entre les deux snapshots, `pytest -q app/tests/integration/test_daily_prediction_api.py`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
