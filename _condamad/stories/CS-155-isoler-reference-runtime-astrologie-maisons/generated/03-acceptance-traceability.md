# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `HouseRuntimeData` expose les faits astrologiques sans champ produit. | `house_kind` ajoute au runtime; aucun champ produit. | `pytest -q tests/unit/domain/astrology/test_house_runtime_builder.py` | PASS |
| AC2 | `domain/astrology` ne contient aucun symbole produit. | Aucun import/symbole produit ajoute. | scan zero-hit `rg ... app/domain/astrology` | PASS |
| AC3 | `houses[*].ruler` reste serialise depuis `HouseRuntimeData`. | Projection chart preexistante preservee; tests chart cibles conserves. | suite cible incluant tests chart modifies/preexistants | PASS |
