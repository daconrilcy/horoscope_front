# Acceptance Traceability CS-160

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Les raisons de force maison passent par `HouseStrengthReason`. | `house_strength_contracts.py`, `house_strength.py`, `house_runtime_data.py` migrent les raisons en enum. | `pytest -q tests/unit/domain/astrology/test_house_strength.py` PASS + scan raisons libres zero hit. | PASS |
| AC2 | Le contrat expose un niveau qualitatif stable. | `HouseStrengthLevel` est derive du score et serialise sous `strength.level`. | `pytest -q tests/unit/domain/astrology/test_house_strength.py` PASS + `app/tests/unit/test_chart_json_builder.py` PASS. | PASS |
| AC3 | L'echelle numerique est documentee comme normalisee. | `normalized_score` devient le champ runtime, `score` reste propriete publique stable. | `rg -n "normalized_score|score.*normalisee" app/domain/astrology ../docs -g "*.py" -g "*.md"` PASS avec hits attendus. | PASS |
| AC4 | Aucune raison ad hoc n'est ajoutee dans le calcul. | Le calcul ajoute uniquement des membres `HouseStrengthReason` et un test AST bloque les append strings. | `rg -n "reasons\\.append\\(\"" app/domain/astrology -g "*.py"` zero hit + test AST PASS. | PASS |
