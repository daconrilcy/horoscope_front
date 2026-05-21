# Implementation Plan

## Findings

- `MoonPhaseCondition`, `MoonPhaseKey` and `WaxingWaningState` already exist in `contracts.py`.
- Existing calculators in `planetary_conditions` use pure functions, French docstrings and explicit `ValueError` for invalid numeric inputs.
- `RG-139` is already present in the pre-existing dirty diff.

## Steps

1. Add `moon_phase_calculator.py` with pure helpers for normalization, angle, phase key, waxing/waning, illumination and index.
2. Export `calculate_moon_phase_condition` from `planetary_conditions.__init__`.
3. Add unit tests covering importability, boundaries, exact angles, normalization, illumination, index and non-finite inputs.
4. Run targeted tests, scans, lint/format and full pytest after activating the venv.
5. Complete validation evidence, acceptance traceability and story status.

## Rollback Strategy

Remove the new calculator, export, test and CS-212 evidence files. Preserve pre-existing guardrail/status additions unless explicitly asked otherwise.
