# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | La table referentielle existe avec contraintes. | `backend/migrations/versions/20260519_0131_create_planet_condition_signal_profiles.py`, `AstralPlanetConditionSignalProfileModel`. | `pytest --long -q backend/app/tests/integration/test_reference_data_migrations.py` -> 5 passed. | PASS |
| AC2 | Le runtime expose les profils de signaux types. | `AstrologyRuntimeReference.condition_signal_profiles`, mapper et repository runtime. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py` -> 22 passed. | PASS |
| AC3 | Le builder ne produit aucune narration. | `PlanetConditionSignalBuilder` cree uniquement codes, axes, niveaux, usages et hints courts. | `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_signal_builder.py backend/tests/unit/domain/astrology/test_natal_result_contract.py` -> 5 passed; scan LLM/narration -> zero hit. | PASS |
| AC4 | Les profils de signaux charges dans le runtime sont disponibles pour le builder. | Builder consomme `runtime_reference.condition_signal_profiles`; repository charge la table versionnee. | Tests repository runtime -> 22 passed. | PASS |
| AC5 | Les plages inclusives runtime selectionnent les signaux sans table locale. | Builder compare `axis_value` aux seules bornes `level_min` / `level_max` du runtime. | Tests builder -> 5 passed; scan seuils locaux -> zero hit. | PASS |
| AC6 | `NatalResult` expose `condition_signals`. | Champ `NatalResult.condition_signals` et calcul apres `condition_profiles`. | Tests contrat natal -> inclus dans 5 passed. | PASS |
| AC7 | `build_chart_json` expose `planet_condition_signals`. | `_serialize_condition_signals` projette strictement `NatalResult.condition_signals`. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` -> 20 passed; scan projection -> integration/projection only. | PASS |
| AC8 | La garde `RG-120` passe. | Guard architecture condition + projection-only. | Tests guard -> inclus dans 22 passed; scans RG-120 -> zero hit pour les interdits. | PASS |
| AC9 | Le contrat public reste stable hors ajouts. | Snapshots avant/apres et diff contractuel: seuls `condition_signals` et `planet_condition_signals` sont ajoutes. | Tests chart JSON -> 20 passed; `ruff check backend/app backend/tests` -> PASS; `ruff check .` -> FAIL hors story sur templates `.agent/.agents/.claude/.gemini` preexistants. | PASS_WITH_LIMITATION |
| AC10 | Le tri des signaux est deterministe. | Tri par `priority_weight`, `axis`, `code`. | Tests builder -> 5 passed. | PASS |

## Accepted review fixes

- `expression_quality` retire des axes runtime autorises car absent de `PlanetConditionProfile`.
- Test ajoute pour rejeter explicitement `condition_axis="expression_quality"`.
- Evidence finale et snapshots enrichis apres les revues read-only.

## Scoped limitation

`ruff check .` echoue sur des fichiers de skills/templates hors story deja presents sous `.agent`, `.agents`, `.claude` et `.gemini`. Le perimetre modifie par CS-193 passe `ruff format --check backend/app backend/tests` et `ruff check backend/app backend/tests`.
