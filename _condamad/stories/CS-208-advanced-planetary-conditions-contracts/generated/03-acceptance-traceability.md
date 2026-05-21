# Acceptance Traceability - CS-208

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le package existe. | Ajouter `planetary_conditions/__init__.py` et `contracts.py`. | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` + `Test-Path`. | PASS |
| AC2 | Les huit dataclasses demandees sont importables. | Definir et exporter les huit dataclasses. | Test d'import et introspection. | PASS |
| AC3 | Les dix enums demandees existent avec valeurs snake_case. | Definir et exporter les dix enums. | Assertions enum dans `test_contracts.py`. | PASS |
| AC4 | Tous les contrats publics sont frozen avec slots. | `@dataclass(frozen=True, slots=True)`. | Tests `dataclasses.is_dataclass`, frozen et absence `__dict__`. | PASS |
| AC5 | Le bundle accepte des conditions partielles. | `PlanetaryConditionsBundle` avec champs optionnels. | Test bundle partiel sans calcul. | PASS |
| AC6 | Le resultat global accepte plusieurs planetes. | `AdvancedPlanetaryConditionsResult.conditions_by_planet`. | Test multi-planetes. | PASS |
| AC7 | Aucune dependance interdite. | Imports standard library uniquement. | Scans `rg` imports/API/infra/services/SQLAlchemy/FastAPI/Pydantic. | PASS |
| AC8 | Aucun calcul. | Aucun calculateur ou scoring. | Scans `calculate_`, `compute_`, `resolve_`, `detect_`, `score_delta`, `interpretation_weight`, `prompt`. | PASS |
| AC9 | Les annotations publiques excluent `Any`. | Types explicites, metadata en `Mapping[str, object]`. | Test introspection + scan `Any`. | PASS |
| AC10 | Pas de listes mutables exposees. | Tuples et mappings. | Tests sur champs aggregate et metadata read-only. | PASS |
| AC11 | Surfaces adjacentes sans integration. | Aucun changement hors package/test/evidence/statut. | `git diff --` sur surfaces adjacentes. | PASS |
| AC12 | Qualite backend dans le venv. | Aucun changement de dependance. | `ruff format .`, `ruff check .`, `pytest -q`. | PASS |
