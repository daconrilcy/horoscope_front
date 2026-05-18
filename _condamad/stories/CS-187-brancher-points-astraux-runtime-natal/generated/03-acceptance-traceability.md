# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Modèles points/profils dans `Base.metadata` avec contraintes/FK attendues. | Modèles existants vérifiés via seed et metadata. | `pytest -q app/tests/unit/test_astral_point_seed_integrity.py` | PASS |
| AC2 | Seed des points via unité dédiée ou équivalente séparée. | Seed `seed_astral_point_defaults()` et sous-fonctions dédiées conservés/testés. | `pytest -q app/tests/unit/test_prediction_reference_repository.py` | PASS |
| AC3 | Runtime points typed immutable. | `AstralPointRuntime`, variants, aliases et `reference.astral_points`. | `pytest -q app/tests/unit/test_astral_point_repository.py` | PASS |
| AC4 | Seed rejette références de variantes invalides. | Tests alias/variant FK et seed integrity. | `pytest -q app/tests/unit/test_astral_point_seed_integrity.py` | PASS |
| AC5 | Resolver retourne instruction typée. | `AstralPointCalculationResolver` ajouté. | `pytest -q tests/unit/domain/astrology/test_astral_point_calculation_resolver.py` | PASS |
| AC6 | `calculate_astral_points()` produit positions normalisées. | Calcul points + `NatalResult.points`. | `pytest -q tests/unit/domain/astrology/test_natal_result_contains_configured_points.py` | PASS |
| AC7 | `NatalResult.points` est une liste sans champs plats. | Modèle Pydantic ajouté sans `true_node`, `mean_node`, `lilith`. | `pytest -q app/tests/unit/test_natal_calculation_service.py` + scan négatif | PASS |
| AC8 | Option `include_points_in_aspects`. | Option service et build natal, pool aspectable conditionnel. | `pytest -q tests/unit/domain/astrology/test_natal_aspects_include_points.py` | PASS |
| AC9 | Calcul natal sans keywords/profils. | Aucun import éditorial dans `natal_calculation.py`/calculateurs. | `pytest -q app/tests/unit/test_astrology_runtime_reference_guard.py` + scan négatif | PASS |
| AC10 | Documentation du contrat runtime. | `docs/tables-astral-points.md` ajouté. | `pytest -q app/tests/unit/test_backend_docs_ownership.py` | PASS |
| AC11 | Preuves avant/après depuis chargement runtime. | Evidence JSON et tests repository/natal. | `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py` + génération runtime/service des artefacts before/after | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.

AC11 evidence: les artefacts `before` sont des sorties runtime réelles générées depuis un worktree détaché au commit `989acc7a` avant CS-187 (`AstrologyRuntimeReferenceRepository(db).load("1.0.0")` et `NatalCalculationService.calculate(...).model_dump(mode="json")`). Les artefacts `after` sont des sorties runtime réelles de l'implémentation courante.
