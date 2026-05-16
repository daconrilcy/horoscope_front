# Baseline apres CS-175

- `NatalResult.signs_runtime` expose le runtime signe additif.
- `backend/app/domain/astrology/runtime/sign_runtime_data.py` porte `SignRuntimeData`, `SignOccupantRuntimeData`, `SignDignityRuntimeData` et `SignDominanceReason`.
- `backend/app/domain/astrology/builders/sign_runtime_builder.py` construit les douze signes depuis `AstrologyRuntimeReference.signs`, les placements et `DignityReferenceSet`.
- Les champs chart publics historiques restent couverts par `app/tests/unit/test_chart_json_builder.py` et `app/tests/unit/test_natal_calculation_service.py`.
