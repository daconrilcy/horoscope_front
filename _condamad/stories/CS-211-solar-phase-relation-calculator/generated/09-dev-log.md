# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: clean.
- Applicable instructions: root `AGENTS.md`, CS-211 `00-story.md`,
  `regression-guardrails.md`, CONDAMAD dev/review/fix skills.
- Capsule generated: yes. A first helper run produced a lower-case duplicate
  path on Windows; the accidental deletion of `00-story.md` was restored from
  `HEAD` before continuing. No user changes were overwritten.

## Sufficiency gate

- Status: PASS.
- Reason: CS-211 has exact files, no audit closure claim, before/after evidence,
  deterministic tests/scans, explicit non-goals and `RG-138`.

## Implementation notes

- Added immutable `SolarPhaseRelationThresholds`.
- Added pure calculator with exact relative angle convention.
- Added batch helper and package exports.
- Added tests for threshold bounds, normalized longitudes, conjunction window,
  oriental/occidental hemispheres, exact opposition, explicit Sun handling,
  non-finite longitudes and batch behavior.

## Validation notes

- Initial `ruff check .` failed only for import sorting in modified files.
- Import order was fixed, then `ruff check .` passed.
