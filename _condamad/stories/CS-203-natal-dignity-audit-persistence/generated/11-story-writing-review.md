<!-- Revue redactionnelle CONDAMAD de la story CS-203. -->

# CS-203 Story Writing Review

## Iteration 1 - Issues Found

Verdict: changes requested.

Findings:

- The story referenced `migrations/**` in forbidden paths and validation diff
  checks, while the repository Alembic directory is `backend/migrations/`.
  This could let a migration change escape the documented forbidden-path check.
- AC10 used the `json_contract_shape` evidence profile for forbidden-path
  preservation. The requirement is a path-diff and negative-change guard, not a
  JSON shape assertion.

Fixes applied:

- Replaced forbidden-path and validation references to `migrations/**` with
  `backend/migrations/**`, and made the Alembic location explicit in the
  inspection instructions.
- Reclassified AC10 evidence as `targeted_forbidden_symbol_scan` and pointed it
  to the forbidden diff plus the public JSON regression test.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS after shortening AC10.
- `condamad_story_lint.py --strict`: PASS after shortening AC10.

## Iteration 2 - Clean Review

Verdict: clean.

Checks:

- The story remains mono-scope around chart dignity audit persistence and keeps
  calculation, public projection, frontend, API routes, seeds and migrations out
  of scope unless a blocker is documented and approved.
- Required contracts are present and active where needed: runtime source of
  truth, baseline snapshot, ownership routing, contract shape, persistent
  evidence and reintroduction guard.
- Acceptance criteria remain atomic, sequential and mapped to concrete evidence.
- Implementation tasks map to ACs and cover baseline, mapper, persistence,
  tests, no-recalculation scans and persistent evidence.
- Forbidden paths now reference the actual repository migration directory.
- No remaining wording permits recalculation, compatibility shims, broad
  allowlists, silent fallbacks, legacy aliases, duplicate audit repositories, or
  audit-table reads for public payload construction.

Validation:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 3 - Brief Alignment Review

Verdict: changes requested, then clean after correction.

Findings:

- The story used `Source type: brief`, while the initial CS-203 brief frames the
  work as a follow-up story after CS-191 and CS-197 through CS-202.
- The brief named `Idempotent Persistence`, `Transaction Boundary` and public
  API preservation as first-class requirements. The story covered them through
  ACs and tasks, but did not make their brief-level status explicit.
- The brief required inspection of the existing migration surface and explicit
  protection against duplicated birth data. The story mentioned both concepts,
  but the inspection list and persisted-facts contract were not explicit enough.

Fixes applied:

- Changed the source type to `follow-up story`.
- Added a brief-level contract note mapping idempotence, transaction boundary
  and public API preservation to ACs, tasks, evidence and forbidden diffs.
- Added the protected public API surfaces and forbidden sensitive persisted
  facts to the Contract Shape section.
- Added `backend/migrations/` to files that must be inspected before a migration
  decision.
- Restored concrete AC10 validation evidence after the validator rejected the
  first shortened wording.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.
