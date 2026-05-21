# Acceptance Traceability - CS-209

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Fonction principale disponible dans le fichier calculateur. | `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py` expose `calculate_solar_proximity_condition`; export public dans `__init__.py`. | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` PASS (`19 passed` after review fix); `pytest -q` PASS (`2835 passed`). | PASS |
| AC2 | `SolarProximityThresholds` expose les trois seuils par defaut. | `contracts.py` ajoute `SolarProximityThresholds` immuable avec `17.0 / 60.0`, `8.5`, `15.0`. | `test_solar_proximity_thresholds_expose_defaults_and_validate_order` PASS. | PASS |
| AC3 | Priorite `CAZIMI > COMBUST > UNDER_BEAMS > NONE`. | Branches ordonnees dans `calculate_solar_proximity_condition`. | Tests `test_calculator_returns_cazimi_with_highest_priority` et `test_calculator_returns_combust_under_beams_and_none` PASS. | PASS |
| AC4 | Distance minimale autour de zero. | `_angular_distance_deg` normalise et prend `min(direct, 360 - direct)`. | `test_calculator_uses_minimal_distance_across_zero` PASS. | PASS |
| AC5 | Normalisation des longitudes. | `_normalize_longitude_deg` applique modulo `360.0`. | `test_calculator_normalizes_longitudes_before_classification` PASS. | PASS |
| AC6 | Bornes inclusives; `15.0001` retourne `NONE`. | Comparaisons `<=` pour les trois seuils et branche finale inactive. | `test_default_threshold_bounds_are_inclusive` PASS. | PASS |
| AC7 | `planet_key="sun"` retourne `NONE` inactif. | Branche explicite pour `sun` apres normalisation de la cle. | `test_sun_returns_inactive_none_condition` PASS. | PASS |
| AC8 | Mapping severites: cazimi/extreme, combust/major, under_beams/moderate, none/none. | Construction de `SolarProximityCondition` avec `ConditionSeverity` attendue. | Tests du calculateur PASS. | PASS |
| AC9 | Seuils personnalises modifient le classement. | Parametre `thresholds: SolarProximityThresholds | None`; validation contractuelle des seuils. | `test_custom_thresholds_change_classification_without_new_contract` PASS. | PASS |
| AC10 | Fonction de lot pure incluant le Soleil. | `calculate_solar_proximity_conditions` itere sur le mapping fourni. | `test_batch_calculator_returns_mapping_including_sun` PASS. | PASS |
| AC11 | Le calculateur exclut les interdits du brief. | Aucun import API/services/infra/DB; aucun scoring, texte narratif ou LLM dans le calculateur. | Scans interdits RG-136: zero hit pour imports, libs interdites, scoring et texte narratif. | PASS |
| AC12 | Aucune integration adjacente hors package. | Aucun changement dans chart/API/infra/frontend/natal/advanced/dignities. | `git diff -- <surfaces adjacentes>` vide. | PASS |
| AC13 | Qualite backend dans le venv. | Patch formate par Ruff. | `ruff format .` PASS; `ruff check .` PASS; `pytest -q` PASS. | PASS |

## Review status

- Implementation evidence complete: yes.
- Review evidence: completed in `generated/11-code-review.md` after review phase.
