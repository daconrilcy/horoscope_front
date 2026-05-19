# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Three advanced condition reference tables exist and are seeded. | Migration, SQLAlchemy models, JSON seed sync, including `description` on advanced condition types. | Runtime repository and migration tests passed. | PASS |
| AC2 | Runtime exposes immutable advanced type/profile/weight contracts. | `runtime_reference.py`, mapper, repository. | `test_astrology_runtime_reference_repository.py` passed. | PASS |
| AC3 | `AdvancedPlanetaryCondition` and axis contracts are explicit. | `advanced_conditions/contracts.py`. | `test_advanced_condition_engine.py` passed. | PASS |
| AC4 | Mutual reception V1 is detected. | `mutual_reception_calculator.py`. | `test_mutual_reception_calculator.py` passed. | PASS |
| AC5 | Sect/hayz V1 is detected. | `hayz_calculator.py`, real accidental dignity source evaluation. | `test_hayz_calculator.py`, `test_accidental_dignity_calculator.py` and natal pipeline test passed. | PASS |
| AC6 | Motion speed/stationary V1 is detected. | `planet_speed_classifier.py`, real accidental dignity source evaluation. | `test_speed_classifier.py`, `test_accidental_dignity_calculator.py` passed. | PASS |
| AC7 | Solar phase/orientation V1 is detected. | `heliacal_condition_calculator.py`, real accidental dignity source evaluation; no local half-circle solar-phase heuristic. | `test_heliacal_conditions.py`, `test_accidental_dignity_calculator.py` and natal pipeline test passed. | PASS |
| AC8 | Aspect conditions V1 are detected. | `aspect_condition_detector.py` detects configured bonification/maltreatment aspects and longitudinal besiegement from runtime planet natures. | `test_besiegement_detector.py` and natal pipeline test passed. | PASS |
| AC9 | Advanced conditions enrich profiles without replacing them. | `advanced_condition_engine.py`, natal orchestration. | `test_advanced_condition_engine.py`, natal contract tests passed. | PASS |
| AC10 | Signals consume enriched profiles without recalculating advanced conditions. | Natal orchestration order only. | Targeted suite and serializer guard passed. | PASS |
| AC11 | Dominance integrates advanced `ranking_weight`. | `PlanetDominanceEngine`. | `test_dominance_integration.py` passed. | PASS |
| AC12 | Public JSON exposes `advanced_conditions` without serializer calculation. | `json_builder.py` projection helper. | `test_chart_json_builder.py` and guard passed. | PASS |
| AC13 | Guards block forbidden advanced-condition dependencies and local maps. | `test_astrology_runtime_reference_guard.py`. | Guard test and `rg` scans passed. | PASS |
| AC14 | Deferred techniques remain absent. | No code for excluded techniques. | Targeted `rg` scan returned zero hits. | PASS |
| AC15 | Existing public contract remains stable except authorized additions. | Tests and before/after payload evidence. | Full `pytest -q`, lint, targeted review/fix tests and snapshots/evidence passed. | PASS |
