# OpenAPI impact

`NatalResult.points` est un champ additif du modèle de résultat natal. Aucun changement frontend n'a été réalisé dans cette story.

Validation liée:

- `pytest -q app/tests/unit/test_natal_calculation_service.py`
- `pytest -q tests/unit/domain/astrology/test_natal_result_contains_configured_points.py`

