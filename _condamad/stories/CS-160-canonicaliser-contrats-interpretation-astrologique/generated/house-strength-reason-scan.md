# House Strength Reason Scan CS-160

## Commands

| Command | Working directory | Result | Classification |
|---|---|---|---|
| `rg -n "reasons\\.append\\(\"" app/domain/astrology -g "*.py"` | `backend/` | zero hit | PASS: no raw string append in astrology domain. |
| `rg -n "reasons\\s*=\\s*\\[|HouseStrengthRuntimeData\\(" app/domain/astrology -g "*.py"` | `backend/` | zero hit | PASS: no raw list assignment or direct runtime constructor in astrology domain. |
| `rg -n "strength\\.score\\s*[<>]=?" app/domain/prediction -g "*.py"` | `backend/` | zero hit | PASS: no raw threshold consumption in domain prediction. |
| `rg -n "app\\.domain\\.prediction|app\\.services\\.prediction|prediction_categories|house_category_weights|visibility_weight|base_priority|routing_role|DomainRouter|PublicAstroFoundationProjector" app/domain/astrology -g "*.py"` | `backend/` | zero hit | PASS: RG-095 boundary remains clean. |

## Notes

- `HouseStrengthEvaluator` still uses a local mutable list while calculating,
  but every appended value is a `HouseStrengthReason` enum member.
- `tests/unit/domain/astrology/test_house_strength.py` includes an AST guard
  rejecting raw string literals passed to `reasons.append(...)`.
