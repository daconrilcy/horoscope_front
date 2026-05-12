# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Supprimer les references runtime a `AstroCharacteristicModel`. | `reference.py`, `reference_repository.py`, tests/fixtures importeurs mis a jour. | Tests cibles PASS + scan sans hit runtime. | Passed |
| AC2 | Retirer `characteristics` du payload public sans casser les aspects. | `ReferenceRepository.get_reference_data` ne lit plus la table et retourne planetes/signes/maisons/aspects. | Tests reference data PASS + tests d'aspects PASS. | Passed |
| AC3 | Supprimer la table pour les bases existantes. | Migration `20260512_0085_drop_astro_characteristics.py` ajoutee. | `test_reference_data_migrations.py` PASS. | Passed |
| AC4 | Ajouter/adapter les tests de contrat et No Legacy. | Tests reference data et migration adaptes; RG-091 ajoute. | Tests cibles PASS + scans avec seuls hits de garde. | Passed |
| AC5 | Valider localement avec venv active. | Aucun code additionnel attendu. | Ruff PASS, tests cibles PASS, demarrage `/health` PASS; suite complete FAIL sur guard SQL API hors scope. | PASS_WITH_LIMITATIONS |
