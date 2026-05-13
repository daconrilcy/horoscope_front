# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | AST test blocks prediction imports from astrology. | `test_astrology_prediction_boundary.py`. | pytest guard | PASS |
| AC2 | Guard blocks product symbols. | AST symbol test + scan. | pytest + rg zero-hit | PASS |
| AC3 | Registry contains durable invariant. | `RG-095` row present. | `rg -n "RG-095.*Frontiere domain astrology vers prediction"` | PASS |
