# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Les 9 imports croises actuels sont remplaces. | Imports consommateurs mis a jour vers des modules helpers non executables; baseline avant/apres persiste. | `rg -n "from app\.tests\.(integration|unit|regression)\.test_|from tests\.integration\.test_" app/tests tests -g test_*.py` retourne zero hit depuis `backend/`. | PASS |
| AC2 | Les helpers extraits ont un proprietaire non executable. | Nouveaux helpers sous `app/tests/**/helpers*.py` ou helpers existants enrichis; aucun re-export depuis `test_*.py`. | Inventaire `rg --files app/tests tests -g '*helpers*.py' -g conftest.py` et revue des imports. | PASS |
| AC3 | Les tests consommateurs continuent de passer. | Assertions inchangees; imports et sources helpers seulement modifies. | Tests cibles billing, ops alerts, engine persistence et entitlement alert handling. | PASS |
| AC4 | Une garde bloque de nouveaux imports depuis `test_*.py`. | Nouveau test d'architecture AST sous `app/tests/unit`. | `pytest -q app/tests/unit/test_backend_test_helper_imports.py` passe et echouerait sur import depuis `test_*.py`. | PASS |
