<!-- Tracabilite des criteres d'acceptation CONDAMAD pour CS-204. -->

# CS-204 Acceptance Traceability

| AC | Statut | Preuve code | Preuve validation |
|---|---|---|---|
| AC1 | PASS | `HayzCondition` dans `advanced_conditions/contracts.py` et serialisation JSON. | `test_traditional_condition_normalizer.py`, `test_chart_json_builder.py` |
| AC2 | PASS | `RejoicingCondition` garde `current_house` et `rejoicing_house` nullables. | Test runtime `rejoicing_house` sans match + JSON no-time. |
| AC3 | PASS | `NatalResult.traditional_conditions` et integration dans `build_natal_result`. | Golden cases + JSON builder tests. |
| AC4 | PASS | Faits hayz `sect_match`, `hemisphere_match`, `sign_gender_match`. | `test_traditional_condition_normalizer.py` |
| AC5 | PASS | Hayz depend des faits non-sect dans `HayzCalculator`. | `test_traditional_golden_cases.py`, `test_hayz_calculator.py` |
| AC6 | PASS | Maison courante et maison de joie explicites. | `test_traditional_condition_normalizer_exposes_runtime_joy_house_without_match` |
| AC7 | PASS | Hayz normalise depuis `AdvancedPlanetaryCondition`. | Tests normalizer + hayz. |
| AC8 | PASS | Rejoicing normalise depuis `accidental_breakdown` et maison runtime. | Tests normalizer + JSON. |
| AC9 | PASS | `_serialize_traditional_conditions` ne lit aucun calculateur doctrinal. | JSON builder tests + scans. |
| AC10 | PASS | `NatalExpertPanel` affiche le bloc depuis le payload. | `npm --prefix frontend test -- NatalExpertPanel` |
| AC11 | PASS | Scores non modifies; G13/G14 verrouillent la triplicite sect-aware. | Golden cases + essential dignity tests. |
| AC12 | PASS | Evidence before/after/validation presente. | `Test-Path` implicite via revue + story validate/lint. |
