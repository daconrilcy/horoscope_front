# Public GET/list accepted-only proof

Status: PASS

Preuve runtime:

- Test: `python -B -m pytest -q backend\tests\integration\test_theme_natal_public_reads.py --tb=short`
- Resultat observe pendant validation ciblee: inclus dans `8 passed, 5 deselected`.
- TestClient est utilise contre `app`.

Scenario API:

- Une ligne `UserNatalInterpretationModel` acceptee est creee.
- Une ligne rejetee du meme `chart_id` est creee.
- `GET /v1/natal/interpretations?chart_id=chart-cs-435-public-read` retourne `total=1` et seulement l'id accepte.
- `GET /v1/natal/interpretations/{accepted_id}` retourne `200`.
- `GET /v1/natal/interpretations/{rejected_id}` retourne `404`.

Preuve route/OpenAPI:

- `python -B -c "from backend.app.main import app; assert app.routes"`: PASS
- `python -B -c "from backend.app.main import app; assert app.openapi().get('paths')"`: PASS
- Snapshots: `evidence/openapi-before.json`, `evidence/openapi-after.json`.

AC couverts: AC10, AC11, AC12.
