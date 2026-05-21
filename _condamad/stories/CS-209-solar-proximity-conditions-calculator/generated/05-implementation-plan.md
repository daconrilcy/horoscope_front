# Implementation Plan - CS-209

## Architecture finding

- CS-208 already owns immutable contracts in `planetary_conditions/contracts.py`.
- No existing canonical solar proximity calculator exists.
- Local angular helpers are acceptable because CS-209 forbids creating a global angle utility and existing helpers live in unrelated owners.

## Selected approach

1. Add `SolarProximityThresholds` to `contracts.py` as a frozen slotted dataclass with ordered-threshold validation.
2. Add `solar_proximity_calculator.py` with pure functions only.
3. Export thresholds and functions from `planetary_conditions/__init__.py`.
4. Extend `test_contracts.py` and add focused calculator tests.
5. Prove RG-135/RG-136 with targeted tests, scans, Ruff and full pytest.

## No Legacy stance

- No shim, alias, fallback, compatibility path or second owner.
- No adjacent integration in `NatalResult`, JSON builder, API, infra, migrations or frontend.
- No scoring, prompt, narration or interpretive text in the calculator.

## Rollback strategy

- Revert only the CS-209 files listed in `04-target-files.md`; no unrelated files are involved.
