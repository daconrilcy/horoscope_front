# No Legacy / DRY Guardrails

## Canonical owners

- Chart sect: `backend/app/domain/astrology/dignities/sect_calculator.py`
- Planet sect condition: `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py`
- Advanced `out_of_sect` and hayz emission: `backend/app/domain/astrology/advanced_conditions/hayz_calculator.py`, consuming `PlanetSectCondition`.
- Public projection: `backend/app/services/chart/json_builder.py`, projection-only.

## Forbidden unless explicitly required by CS-199

- Compatibility wrappers
- Transitional aliases
- Legacy import paths
- Duplicate active sect implementations
- Re-export modules preserving old imports
- Silent fallback behavior
- Local diurnal/nocturnal/common planet constants
- Local above/below horizon house constants
- Sect calculator imports in `condition`, `advanced_conditions`, `dominance`, `interpretation_adapters` or `json_builder.py`
- Public fields named `sect_legacy`, `legacy_sect`, `sect_code`, `chart_sect_code`, `planet_sect_code`, `planet_sect_legacy`, `sect_score_legacy`, `legacy_planet_sect`

## Applicable guardrails

- `RG-118` dignity calculators remain pure/runtime-backed.
- `RG-119` condition profiles derive from dignity facts and runtime weights.
- `RG-120` condition signals do not encode local sect thresholds.
- `RG-121` dominance remains a consumer of profiles and advanced facts.
- `RG-122` advanced conditions remain runtime-backed and do not recreate local sect doctrine.
- `RG-123` interpretation adapter remains non-narrative and fact-consuming.
- `RG-124` chart-level sect is canonical.
- `RG-125` per-planet sect condition is canonical.
- `RG-126` advanced sect scoring consumes only `ChartSectResult`, `PlanetSectCondition` and runtime weights.

## Required negative evidence

- Zero-hit scans for downstream `SectCalculator` and `PlanetSectConditionCalculator`.
- Zero-hit scans for local sect constants and horizon tuples in changed domains.
- Classification of existing `sect_code`/`chart_sect_code` runtime-reference hits.
- Classification of existing `prompt_hint` runtime signal fields as non-LLM and non-sect.

## Review checklist

- `out_of_sect` is sourced from `PlanetSectCondition.is_out_of_sect`.
- `hayz` is gated by `PlanetSectCondition.is_in_sect` and still requires non-sect hayz factors.
- Missing `PlanetSectCondition` fails explicitly.
- No frontend, API, DB, migration, seed or LLM surface changed.
