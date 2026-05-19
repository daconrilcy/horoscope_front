<!-- Matrice de tracabilite CONDAMAD pour les criteres CS-194. -->

# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `astral_dominance_factor_types` contient exactement les lignes de `4b.1`. | Migration `20260519_0132`, modele `AstralDominanceFactorTypeModel`, seed JSON/service. | `pytest --long -q backend/app/tests/integration/test_reference_data_migrations.py` -> PASS; `dominance-runtime-reference.md`. | PASS |
| AC2 | Le runtime expose uniquement les facteurs actifs tries par `sort_order`. | `AstrologyRuntimeReference.dominance_factor_types`, loader et mapper. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py` -> PASS. | PASS |
| AC3 | Les contrats de dominance sont immuables. | Dataclasses frozen sous `domain/astrology/dominance`. | `pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py` -> PASS. | PASS |
| AC4 | `PlanetDominanceEngine` classe par score decroissant puis code. | `PlanetDominanceEngine.calculate`. | `pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py` -> PASS. | PASS |
| AC5 | Chaque score contient un breakdown par facteur. | `PlanetDominanceResult.factors`. | `pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py` -> PASS. | PASS |
| AC6 | `chart_ruler` provient des maitrises runtime. | Facteur `chart_ruler` lit `house_rulers`, pas de mapping local. | Test moteur + scan local weight/rulership hits classes. | PASS |
| AC7 | `condition_strength` consomme `PlanetConditionProfile`. | Facteurs `condition_strength` et `visibility` lisent `condition_profiles`. | Test moteur. | PASS |
| AC8 | `aspect_centrality` vient des faits d'aspects natals. | Facteur `aspect_centrality` lit les aspects runtime. | Test moteur. | PASS |
| AC9 | `NatalResult` expose `dominant_planets` sans modifier `chart_balance.dominant_planets`. | Champ `NatalResult.dominant_planets`, calcul apres `chart_balance`. | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` -> PASS. | PASS |
| AC10 | `build_chart_json` expose `dominant_planets` sans recalcul. | `_serialize_dominant_planets` projette `NatalResult.dominant_planets`. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` -> PASS. | PASS |
| AC11 | La garde `RG-121` bloque les poids locaux. | `test_astrology_runtime_reference_guard.py` + registre `RG-121`. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py` -> PASS; scans No Legacy. | PASS |
| AC12 | Le contrat public reste stable hors ajouts autorises. | Snapshots evidence before/after, tests chart JSON/persistence. | `ruff check .`, `ruff format .`, `pytest -q`, snapshots. | PASS |
