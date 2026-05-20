# Dev Log

## Preflight

- Initial worktree was clean.
- `AGENTS.md`, CS-199 story, CS-197/CS-198 context and `_condamad/stories/regression-guardrails.md` were read.
- Story sufficiency gate passed: CS-199 has exact scope, evidence artifacts, deterministic scans and no vague batch boundary.

## Implementation notes

- Main runtime change is confined to `HayzCalculator`.
- `out_of_sect` now comes from `PlanetSectCondition.is_out_of_sect`.
- `hayz` now requires `PlanetSectCondition.is_in_sect` plus runtime-backed horizon/sign-gender factors evaluated in `advanced_conditions`.
- Missing `PlanetSectCondition` raises `ValueError`.
- Condition profile, dominance and interpretation adapter runtime code stayed unchanged; tests now guard against sect calculator imports.

## Validation notes

- Targeted tests passed: 49 tests.
- `ruff format` and `ruff check` passed after import ordering fix.
- Evidence JSON files are valid.
- Full `pytest -q` was rerun with a longer timeout and failed on an isolated seed-count mismatch outside the CS-199 diff.
