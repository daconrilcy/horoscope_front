# No Legacy / DRY Guardrails

## Canonical Owners

- Chart sect: `backend/app/domain/astrology/dignities/sect_calculator.py`
- Planet sect condition: `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py`
- Essential dignity: `backend/app/domain/astrology/dignities/essential_dignity_calculator.py`
- Accidental dignity and rejoicing: `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py`
- Hayz and out-of-sect: `backend/app/domain/astrology/advanced_conditions/**`
- Profiles and signals: `backend/app/domain/astrology/condition/**`
- Dominance: `backend/app/domain/astrology/dominance/**`
- Interpretation adapter: `backend/app/domain/astrology/interpretation_adapters/**`
- Public serialization: `backend/app/services/chart/json_builder.py`

## Forbidden Additions

- Compatibility wrappers, aliases, shims, silent fallbacks, duplicate doctrine engines.
- Production constants named `DIURNAL_PLANETS`, `NOCTURNAL_PLANETS`, `SECT_PLANETS`, `DAY_SECT_PLANETS`, `NIGHT_SECT_PLANETS`, `ABOVE_HORIZON_HOUSES`, `BELOW_HORIZON_HOUSES`, `JOY_HOUSES`, `PLANETARY_JOYS`.
- Downstream imports of `SectCalculator` or `PlanetSectConditionCalculator`.
- Hidden local recalculation of sect, hayz, out-of-sect, rejoicing or dominance.

## Test Helper Rules

- Helpers may contain explicit per-case fixture facts.
- Helpers must call canonical runtime services for calculations.
- Helpers must not encode reusable doctrine tables or alternate calculators.
- Snapshot normalization must only curate and round observed outputs.

## Required Evidence

- Targeted pytest for G1-G12.
- Existing regression tests for sect, dignity, advanced conditions, profiles, dominance, adapter and JSON projection.
- `rg` scans for forbidden symbols, calculator imports, horizon tuples and forbidden dependencies.
- Classified scan hits in `golden-cases-validation.md`.
