<!-- Traceabilite acceptance criteria pour CS-215. -->

# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Fonction publique attendue. | `advanced_condition_modifiers.py::calculate_advanced_condition_modifiers`. | `pytest -q backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py` | PASS |
| AC2 | `AccidentalDignityModifier` immutable avec cinq champs. | `contracts.py::AccidentalDignityModifier`. | `test_modifier_contract_is_immutable_with_required_fields`; `pytest -q backend/tests/unit/domain/astrology/test_dignity_contracts.py` | PASS |
| AC3 | Profils de deltas centralises. | `advanced_condition_modifier_profiles.py`. | `test_profiles_centralize_expected_deltas_and_categories`; `Test-Path` confirme le fichier. | PASS |
| AC4 | Cazimi exclut combustion. | `_solar_condition_modifiers`. | `test_cazimi_has_priority_over_combust_and_sun_has_no_combust_penalty` | PASS |
| AC5 | Combust non solaire vaut `-5`. | Profil `combust_penalty`. | `test_cazimi_has_priority_over_combust_and_sun_has_no_combust_penalty` | PASS |
| AC6 | Under beams vaut `-2`. | Profil `under_beams_penalty`. | `test_under_beams_uses_solar_proximity_without_visibility_double_count` | PASS |
| AC7 | Stationary + retrograde cohabitent. | `_motion_condition_modifiers`. | Tests direction retrograde + flag stationnaire et direction stationnaire + flag retrograde. | PASS |
| AC8 | Vitesses extremes generent leurs deltas. | `_motion_condition_modifiers`. | `test_motion_modifiers_allow_stationary_retrograde_and_speed_extremes` | PASS |
| AC9 | Visibilite V1 limitee sans double comptage. | `_visibility_condition_modifiers`. | `test_visibility_v1_only_scores_invisible_and_emerging`; test under beams. | PASS |
| AC10 | Oriental/occidental seulement planetes superieures. | `_SUPERIOR_PLANETS`, `_solar_phase_condition_modifiers`. | `test_solar_phase_v1_scores_only_superior_planets` | PASS |
| AC11 | Phase lunaire seulement Lune. | `_lunar_condition_modifiers`. | `test_lunar_phase_scores_only_moon_and_tolerates_partial_conditions`; integration Lune. | PASS |
| AC12 | Conditions partielles `None` tolerees. | Tous builders retournent `()`. | `test_lunar_phase_scores_only_moon_and_tolerates_partial_conditions` | PASS |
| AC13 | Score accidentel inclut les modificateurs. | `PlanetDignityScoringService._modifier_score`. | `test_scoring_service_adds_advanced_modifiers_to_score_and_result` | PASS |
| AC14 | Resultat expose les modificateurs. | `PlanetDignityResult.advanced_condition_modifiers` exclu du dump/schema public. | Tests integration scoring, contrats et `TypeAdapter` Pydantic. | PASS |
| AC15 | Soleil sans penalite combust. | Regle `bundle.planet_key != "sun"`. | Tests moteur et integration Soleil. | PASS |
| AC16 | Surfaces interdites absentes. | Nouveaux modules sans imports interdits. | Scans `rg` zero-hit pour deps/surfaces/termes interdits. | PASS |
| AC17 | Surfaces adjacentes sans diff. | Aucun changement adjacent interdit. | `git diff -- $adjacent_diff_paths` vide. | PASS |
| AC18 | Calculateurs CS-209 a CS-214 non dupliques. | Le moteur consomme les contrats. | Scan duplication zero-hit. | PASS |
| AC19 | Validation complete sous venv. | Evidence et statut capsule. | `ruff format backend`, `ruff check backend`, `ruff check .`, `pytest -q`. | PASS |
