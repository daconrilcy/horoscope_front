# Public JSON Validation

## Contract Summary

- `dignities` remains projected from `NatalResult.dignities` and `NatalResult.dignity_sect`.
- `dignities.sect` remains the CS-197 object.
- `dignities.planets[*].sect_condition` remains the CS-198 object for new computed results.
- `planet_condition_profiles` is a direct map keyed by planet code and serializes as `{}` when source lists are empty.
- `planet_condition_signals` is a direct map keyed by planet code whose values are signal lists; it serializes as `{}` when source lists are empty.
- `advanced_conditions` exposes public field names from the brief: `planet_code`, `condition_type`, `score_effect`, `axis_weights` and `evidence`.
- `advanced_conditions` remains computed-empty as `[]`.
- `dominant_planets` exposes public code fields: `top_planet_code`, `chart_ruler_code`, `most_elevated_planet_code` and `planets[*].planet_code`.
- `dominant_planets` and `interpretation_adapter` remain `null` when missing or unavailable because of chart mode.
- `astral_points`, `houses`, `angles`, `signs_runtime`, `house_rulers` and `chart_balance` are public structural blocks serialized from `NatalResult` facts.
- `astral_points[*].house` and `signs_runtime[*].occupants[*].house` are neutralized to `null` in no-time mode.
- Chart JSON remains dynamically shaped and is not represented by a generated client contract.

## Before / After Comparison

| Block | Difference | Classification |
|---|---|---|
| `astral_points` | Added to public projection from `NatalResult.astral_points`. | Allowed CS-201 structural projection. |
| `signs_runtime` | Added to public projection from `NatalResult.signs_runtime`. | Allowed CS-201 structural projection. |
| `dignities` | No score or sect fact change. | no-change score; no-change astrology. |
| `planet_condition_profiles` | Shape changed from metadata envelope to direct planet map; score/fact values unchanged. | no-change score; no-change astrology. |
| `planet_condition_signals` | Shape changed from metadata envelope to direct planet map of signal lists; signal facts unchanged. | no-change astrology; public shape alignment. |
| `advanced_conditions` | Public field names aligned with the brief; condition values and score effect unchanged. | no-change score; no-change astrology; public shape alignment. |
| `dominant_planets` | Public code/score field names aligned with the brief; dominance values unchanged. | no-change score; no-change astrology; public shape alignment. |
| `interpretation_adapter` | No factual adapter value change. | no-change astrology. |
| `houses`, `angles`, `house_rulers`, `chart_balance` | Existing behavior preserved. | no-change astrology. |

## Missing-Block Convention

- Old persisted payload gaps are not mutated or backfilled in storage.
- Missing list blocks validate to `[]` through `NatalResult` defaults.
- Missing optional object blocks validate to `None` through `NatalResult` defaults.
- Missing `dignities.sect` or per-planet `sect_condition` is not fabricated by `json_builder.py`.

## Commands

All Python commands were executed from repository root in PowerShell after:

```powershell
.\.venv\Scripts\Activate.ps1
```

Detailed command results are recorded in `generated/10-final-evidence.md`.

## Scan Classification

- Projection no-calculation scan: zero hits for forbidden engines in `json_builder.py`.
- Legacy sect alias scan: public compatibility aliases are absent. Hits for `sect_code` and `chart_sect_code` are canonical runtime/reference internals, classified below.
- Evidence pattern scan: this file and snapshots mention `dignities`, `sect_condition`, `planet_condition_profiles`, `planet_condition_signals`, `advanced_conditions`, `dominant_planets`, `interpretation_adapter`, `astral_points`, `houses`, `angles`, `signs_runtime`, `house_rulers`, `chart_balance`, generated contract, no recalculation, no-change score and no-change astrology.

| Pattern | File | Classification | Action | Status |
|---|---|---|---|---|
| `sect_code` | `backend/tests/factories/astrology_runtime_reference_factory.py:1045` | test fixture canonical runtime sect value | keep | PASS |
| `sect_code` | `backend/tests/factories/astrology_runtime_reference_factory.py:1052` | test fixture canonical runtime sect value | keep | PASS |
| `chart_sect_code` | `backend/tests/factories/astrology_runtime_reference_factory.py:1217` | test fixture canonical condition key | keep | PASS |
| `chart_sect_code` / `sect_code` | `backend/tests/factories/astrology_runtime_reference_factory.py:1366-1369` | test fixture builder for canonical runtime rules | keep | PASS |
| `sect_code` | `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py:770` | DB-backed canonical runtime projection column | keep | PASS |
| `sect_code` | `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py:445` | mapper for canonical runtime reference contract | keep | PASS |
| `chart_sect_code` | `backend/app/tests/unit/test_astrology_runtime_reference_repository.py:169` | test assertion for canonical runtime condition key | keep | PASS |
| `sect_code` | `backend/app/domain/astrology/runtime/runtime_reference.py:604` | canonical runtime reference field, not public JSON alias | keep | PASS |
| `sect_code` | `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py:49` | local variable for canonical runtime rule evaluation | keep | PASS |
| `chart_sect_code` | `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py:54-57` | canonical runtime condition key consumed by domain calculator | keep | PASS |
| `sect_code` | `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py:66-70` | local canonical sect rule set, not public JSON alias | keep | PASS |
| `chart_sect_code` | `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py:74-77` | helper reading canonical runtime condition key | keep | PASS |
| `sect_code` | `backend/app/domain/astrology/dignities/essential_dignity_calculator.py:58` | canonical dignity runtime field | keep | PASS |
| `chart_sect_code` | `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py:107-114` | canonical accidental dignity condition key | keep | PASS |

`houses[*].sign` remains an intentionally retained historical public field in the existing chart JSON contract. CS-201 does not remove or rename public fields without a user decision, and it keeps `cusp_sign` as the canonical source field.
