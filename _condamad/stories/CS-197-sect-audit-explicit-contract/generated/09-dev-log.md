# Dev Log

## Preflight

- Initial `git status --short`: clean.
- Applicable repository instructions: root `AGENTS.md`.
- Capsule generated: yes, missing `generated/` files created during implementation.
- Story sufficiency: pass; finite scope, explicit ACs, snapshots, scans and no vague phase boundary.

## Implementation notes

- Added `ChartSectResult` and made `SectCalculator.calculate()` return the explicit contract.
- Preserved string `PlanetDignityResult.sect` for downstream contracts and added `PlanetDignityResult.chart_sect`.
- Added `NatalResult.dignity_sect` as the chart-level dignity sect contract.
- Updated `json_builder.py` to serialize the precomputed sect contract without importing `SectCalculator`.
- Removed pre-existing local horizon house constants from `AccidentalDignityCalculator` by routing horizon checks through runtime `above_horizon` / `below_horizon` rules.
- Review fix: added strict `ChartSectResult` validation and fail-closed chart JSON projection for missing/malformed precomputed sect contracts.
- Review fix: parametrized the missing horizon runtime rule test for both `above_horizon` and `below_horizon`.

## Validation notes

- First targeted test run exposed an over-strict schema-name check in `SectCalculator`; corrected to require runtime rule and `house_codes` rather than a fixed schema label.
- Full backend suite first timed out at 120 seconds, then was rerun from repo root with venv activation and passed. After review fixes, it was rerun again and passed.
- A second long run from `backend/` used the wrong venv activation path; result was not used as validation evidence. The corrected run is recorded in final evidence.

## Final status

- Implementation complete.
- Ready for independent review.
