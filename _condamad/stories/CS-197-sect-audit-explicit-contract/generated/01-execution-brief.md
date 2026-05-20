# Execution Brief - CS-197-sect-audit-explicit-contract

## Primary objective

Expose a typed chart-level natal sect contract sourced from runtime horizon
rules and project it as `dignities.sect` without recalculating in the JSON
projection layer.

## Boundaries

- Backend-only story.
- Canonical calculation owner: `backend/app/domain/astrology/dignities/sect_calculator.py`.
- Canonical DTO owner: `backend/app/domain/astrology/dignities/contracts.py`.
- Public projection owner: `backend/app/services/chart/json_builder.py`.
- No frontend change.

## Non-goals

- No per-planet sect condition contract.
- No `sect_legacy`, `legacy_sect`, `sect_code` or `chart_sect_code` public alias.
- No local horizon house constants in dignity calculators or chart projection.
- No `SectCalculator` import or instantiation in `json_builder.py`.

## Done when

- AC1 to AC8 have code and validation evidence.
- Before/after JSON artifacts exist under `evidence/`.
- Targeted tests, full backend tests, Ruff, and story guard scans pass or are classified.
- Final evidence and review evidence are complete.
