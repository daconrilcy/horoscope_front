# Dev Log

## Preflight

- Initial `git status --short`: untracked story folders under `_condamad/stories/reclassify-story-regression-guards/`, `_condamad/stories/remove-cross-test-module-imports/`, `_condamad/stories/replace-seed-validation-facade-test/`; permission warnings from existing pytest temp/artifact directories.
- Current branch: not required for implementation.
- Existing dirty files: pre-existing untracked story folders preserved.

## Search evidence

- `rg --files backend -g 'test_story_*.py'` found 44 files before migration, 41 files after the first migration lot, then zero after completing the catalogue.
- `rg -n "^def test_" backend -g 'test_story_*.py'` was used to sample protected surfaces and test naming.
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" backend/app/tests backend/tests backend/app/domain -g 'test_*.py'` identifies expected guard-heavy terminology; hits are treated as guard evidence, not nominal legacy support.

## Implementation notes

- Generated the missing CONDAMAD capsule files with `condamad_prepare.py`.
- Renamed the services LLM, entitlement, and services structure guard files to durable names.
- Added a pytest catalogue guard that parses `story-guard-mapping.md`.
- Added RG-012 to the shared guardrail registry for the story-numbered guard catalogue.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py _condamad\stories\reclassify-story-regression-guards\00-story.md --root . --story-key reclassify-story-regression-guards --with-optional` | PASS | Capsule generated. |

## Issues encountered

- Recursive `Get-ChildItem -Recurse` hits permission denied on existing pytest temp/artifact directories; later scans were scoped to relevant paths.
- A broad `rg` attempt with unexpanded Windows glob path arguments failed; replaced with `rg --files ... -g` patterns.

## Decisions made

- First migration batch limited to three closely related services structure guards.
- No backend story-numbered file remains allowed; old names are historical source rows in the mapping only.

## Final `git status --short`

- Modified: `_condamad/stories/regression-guardrails.md`.
- Deleted old story-numbered names for all 44 baseline files.
- Untracked: current story capsule and durable backend test files.
- Pre-existing unrelated untracked story folders remain untouched.
