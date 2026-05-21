# No Legacy / DRY Guardrails

## Forbidden For CS-207

- No compatibility wrapper, transitional alias, shim, re-export, or fallback.
- No local doctrine constants in non-owner layers.
- No public JSON recalculation in `json_builder.py`.
- No frontend derivation from houses, planet codes, sect strings, or local astrology maps.
- No persistence-layer recalculation of dignities, sect, hayz, rejoicing, triplicity, mitigation, profiles, dominance, or interpretation facts.
- No production behavior change to pass the audit.

## Canonical Owners

| Responsibility | Canonical owner | Guard evidence |
|---|---|---|
| Chart sect | `backend/app/domain/astrology/dignities` | `RG-124`, `test_sect_calculator.py`, JSON builder tests |
| Planet sect condition | `backend/app/domain/astrology/dignities` | `RG-125`, dignity scoring and JSON tests |
| Advanced sect scoring and hayz precondition | `backend/app/domain/astrology/advanced_conditions` | `RG-126`, advanced condition tests |
| Golden traditional stability | `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | `RG-127` |
| Public JSON projection | `backend/app/services/chart/json_builder.py` as serialize-only projection | `RG-128`, JSON builder tests |
| Frontend expert panel | `frontend/src/features/natal-chart/NatalExpertPanel.tsx` as display-only consumer | `RG-129`, frontend tests/scans |
| Dignity audit persistence | `backend/app/services/chart/result_service.py` and DB repositories as persist-only path | `RG-130`, chart result service tests |
| Hayz/rejoicing contracts | `backend/app/domain/astrology/advanced_conditions` and dignity/traditional condition owners | `RG-131` |
| Triplicity sect-aware scoring | `backend/app/domain/astrology/dignities` | `RG-132`, triplicity tests |
| Benefic/malefic sect mitigation | `backend/app/domain/astrology/advanced_conditions` | `RG-133`, mitigation tests |

## Required Evidence

- Four story scans with hit classification.
- Targeted backend and frontend tests.
- Quality checks.
- Evidence files and final JSON status.

