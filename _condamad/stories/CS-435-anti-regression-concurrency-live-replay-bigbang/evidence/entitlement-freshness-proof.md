# Entitlement freshness proof

Status: PASS

Preuve runtime:

- Test: `python -B -m pytest -q backend\tests\integration\test_theme_natal_entitlement_freshness.py --tb=short`
- Resultat observe pendant validation ciblee: inclus dans `8 passed, 13 deselected`.

Scenario:

- `execute_theme_natal_reading_product_action` recoit une commande publique `generate_full`.
- Le chart est charge via `UserNatalChartService.get_latest_for_user`.
- `NatalChartLongEntitlementGate.check_access_for_complete_generation` retourne un acces Basic `single_astrologer`.
- Le runtime Basic recoit exactement cet `access_result`.
- La reponse publique expose `output_variant=basic_full_reading`.
- `caplog.text` ne contient pas `plan=free`.

AC couverts: AC6, AC13.
