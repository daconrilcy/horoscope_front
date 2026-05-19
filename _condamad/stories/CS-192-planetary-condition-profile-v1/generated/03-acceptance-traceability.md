<!-- Matrice AC vers preuves pour CS-192. -->

# CS-192 Acceptance Traceability

| AC | Statut | Preuves code | Preuves validation |
|---|---|---|---|
| AC1 | PASS | Migration `20260519_0130` + modeles SQLAlchemy des poids. | `pytest -q backend/app/tests/integration/test_reference_data_migrations.py` - PASS |
| AC2 | PASS | `DignityScoreWeightReferenceData`, repository et mapper transportent les cinq axes sans fallback silencieux. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py` - PASS |
| AC3 | PASS | `PlanetConditionProfile`, `PlanetConditionBreakdownItem`, `PlanetConditionExplanationFact`. | `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py` - PASS |
| AC4 | PASS | `PlanetConditionProfileService` derive les axes depuis `PlanetDignityResult` et les poids runtime. | `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py` - PASS |
| AC5 | PASS | `NatalResult.condition_profiles` et integration dans `build_natal_result`. | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` - PASS |
| AC6 | PASS | `build_chart_json` projette `planet_condition_profiles` depuis les profils calcules. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` - PASS |
| AC7 | PASS | Garde architecture condition/RG-119. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py` + scans zero-hit - PASS |
| AC8 | PASS | Snapshots avant/apres elargis aux champs chart existants; le breakdown conditionnel est coherent avec les dignites essentielles et accidentelles. | `ruff check <fichiers CS-192>` - PASS; `ruff format --check <fichiers CS-192>` - PASS; `pytest -q` - PASS; `ruff check .` - FAIL hors scope sur templates `.agent/.agents/.claude/.gemini` preexistants |
| AC9 | PASS | Test deterministe du classement conditionnel. | `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py` - PASS |
