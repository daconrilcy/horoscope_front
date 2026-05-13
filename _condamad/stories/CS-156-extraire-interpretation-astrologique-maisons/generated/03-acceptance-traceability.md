# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `HouseStrengthEvaluator` produit les raisons astrologiques. | New `interpretation/house_strength.py`. | `pytest -q tests/unit/domain/astrology/test_house_strength.py` | PASS |
| AC2 | Builder runtime appelle l'interpretation sans dupliquer. | `house_runtime_builder.py` delegates to evaluator; old calculator removed. | `pytest -q tests/unit/domain/astrology/test_house_runtime_builder.py` | PASS |
| AC3 | Interpretation ne depend pas de prediction. | No imports/product symbols. | zero-hit scan | PASS |
