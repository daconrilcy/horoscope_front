# Implementation Plan

## Initial repository findings

- `HayzCalculator` was the only implementation point projecting `hayz` and `out_of_sect` from accidental dignity breakdowns.
- `PlanetSectCondition` is already attached to `PlanetDignityResult` by CS-198.
- Condition profiles, dominance, interpretation adapter and JSON builder were already consumer/projection layers and did not need runtime code changes.

## Proposed changes

- Change `HayzCalculator` so `out_of_sect` comes from `PlanetSectCondition.is_out_of_sect`.
- Change `HayzCalculator` so `hayz` requires `PlanetSectCondition.is_in_sect` plus runtime-backed non-sect hayz factors evaluated in `advanced_conditions`.
- Raise an explicit `ValueError` when a dignity result lacks `PlanetSectCondition` for sect-dependent advanced conditions.
- Add tests for canonical source consumption, non-sect hayz factor preservation, missing contract failure and downstream non-recalculation.
- Add persistent evidence snapshots and validation summary.

## Files to modify

- `backend/app/domain/astrology/advanced_conditions/hayz_calculator.py`
- `backend/tests/unit/domain/astrology/advanced_condition_test_helpers.py`
- `backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`
- `backend/tests/unit/domain/astrology/test_hayz_calculator.py`
- `backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py`
- `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py`
- `backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py`
- CS-199 capsule/evidence files.

## Files to delete

- None.

## Tests to add or update

- Advanced condition engine tests for `out_of_sect`, hayz non-sect factors and missing `PlanetSectCondition`.
- Hayz calculator tests for canonical sect facts and false hayz when out of sect.
- Downstream guard tests proving condition profiles, dominance and adapter do not import sect calculators.

## Risk assessment

- Main risk: score deltas if previous breakdown and `PlanetSectCondition` diverge. Mitigation: before/after snapshots and targeted tests.
- Main architecture risk: downstream layers becoming sect owners. Mitigation: tests and scans for calculator imports/constants.

## Rollback strategy

- Revert `HayzCalculator` and the CS-199-specific tests/evidence if validation reveals unintended score drift.
