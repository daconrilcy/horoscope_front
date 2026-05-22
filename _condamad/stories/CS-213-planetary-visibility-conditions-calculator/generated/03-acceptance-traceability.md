# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Creer un calculateur pur dans `planetary_visibility_calculator.py`. | Nouveau module domaine, imports bornes aux contrats du package. | Tests cibles + scans imports interdits. | PASS |
| AC2 | Ajouter `PlanetVisibilityThresholds`. | `contracts.py` + export public. | `test_contracts.py` seuils, immutabilite, validation. | PASS |
| AC3 | Ajouter `PlanetVisibilityKey.CONJUNCT_SOLAR`. | Enum contractuelle et tests de valeurs stables. | `test_contracts.py`. | PASS |
| AC4 | Exporter les fonctions publiques. | `__init__.py`. | Import indirect via tests du package public. | PASS |
| AC5 | Le Soleil retourne `VISIBLE`. | Branche explicite `planet_key == "sun"`. | `test_sun_returns_nominal_visible_condition`. | PASS |
| AC6 | Cazimi ou distance sous tolerance retourne `CONJUNCT_SOLAR`. | Priorite conjonction avant restrictions. | Tests cazimi et tolerance. | PASS |
| AC7 | `COMBUST` retourne `INVISIBLE`. | Composition depuis `SolarProximityConditionKey.COMBUST`. | `test_combust_returns_invisible`. | PASS |
| AC8 | `UNDER_BEAMS` retourne `UNDER_BEAMS`. | Priorite under beams avant emergence. | `test_under_beams_returns_under_beams_even_with_emerging_distance`. | PASS |
| AC9 | Orientale dans `(15, 18]` retourne `EMERGING`. | Fenetre d'emergence orientale. | `test_oriental_planet_in_emerging_window_returns_emerging`. | PASS |
| AC10 | Occidentale dans la fenetre ne retourne pas `EMERGING`. | Condition stricte `SolarPhaseRelationKey.ORIENTAL`. | `test_occidental_planet_in_emerging_window_returns_visible`. | PASS |
| AC11 | Hors restrictions retourne `VISIBLE`. | Cas par defaut visible. | `test_outside_restrictions_returns_visible`. | PASS |
| AC12 | Priorite stricte respectee. | Ordre Soleil, conjonction, combust, under beams, emerging, visible. | Tests de collisions cazimi / under beams / emergence. | PASS |
| AC13 | Seuils personnalises modifient la classification. | Parametre `thresholds`. | `test_custom_thresholds_change_classification`. | PASS |
| AC14 | Fonction de lot pure. | `calculate_planet_visibility_conditions`. | `test_batch_calculator_returns_visibility_for_each_proximity_key`. | PASS |
| AC15 | Pas de `UNKNOWN` ni placeholders heliacaux en nominal. | Aucun retour vers ces valeurs dans le calculateur. | `test_nominal_cases_do_not_return_unknown_or_heliacal_placeholders`. | PASS |
| AC16 | Exclure dependances interdites. | Imports limites a `collections.abc.Mapping` et contrats package. | `rg` imports interdits zero hit. | PASS |
| AC17 | Exclure scoring. | Aucun symbole de scoring dans le calculateur. | `rg` scoring zero hit. | PASS |
| AC18 | Exclure interpretation/narration/prompt. | Raisons techniques uniquement, pas de texte interpretatif. | `rg` interpretation/narration/prompt zero hit. | PASS |
| AC19 | Exclure astronomie observationnelle. | Pas de latitude, horizon, magnitude, ephemeris, etc. | `rg` observationnel zero hit. | PASS |
| AC20 | Pas d'integration adjacente. | Aucun changement hors package/tests/story. | Scan symboles publics adjacent zero hit + diff adjacent vide. | PASS |
| AC21 | Qualite backend dans le venv. | Format/lint/tests. | `ruff format .`, `ruff check .`, `pytest -q` dans `backend/` apres activation. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
