# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Runtime des maisons sans constante `house_axes.py` | `house_runtime_builder.py` recoit un mapping d'axes et n'importe plus la constante; `house_axes.py` supprime | `pytest tests/unit/domain/astrology/test_house_runtime_builder.py -q` + scan zero-hit anciens symboles | PASS |
| AC2 | Axes charges depuis DB dans les donnees de reference | `ReferenceRepository._get_house_axes` lit `astral_house_axis_members` + `astral_house_axis_definitions`; les definitions d'axes sont structurelles et non versionnees | `pytest app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py -q` + migration ciblee | PASS |
| AC3 | Echec explicite si axes absents/incomplets ou types invalides | `_extract_house_axes` valide les 12 maisons et rejette les coercitions silencieuses | `test_reference_house_axes_extraction_rejects_incomplete_payload` + `test_reference_house_axes_extraction_rejects_coerced_numbers` | PASS |
| AC4 | Tests cibles uniquement | Tests adaptes/ajoutes sur repository, seed, migrations et runtime | Pytest cible, Ruff cible, format check cible | PASS |
| AC5 | Pas de legacy actif | Ancien fichier constant supprime et doc mise a jour | `rg -n "resolve_house_axis|HOUSE_AXES|constants/house_axes\.py|constants\\house_axes\.py" backend docs` zero hit | PASS |
