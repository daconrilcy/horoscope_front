<!-- Revue redactionnelle CONDAMAD de la story CS-218. -->

# CS-218 Story Writing Review

## Iteration 1 - Issues Found

Verdict: changes requested.

Findings:

- Several AC validation commands used bare filenames such as
  `test_aspect_chart_object_inputs.py`, while the validation plan uses full repo
  paths. This could make execution ambiguous from the repo root.
- The story still instructed the dev agent to "add `RG-145`" even though the
  regression guardrail registry already contains `RG-145`.
- Section numbering jumped from `15` to `17`, which made the contract checklist
  harder to scan and left the internal usage search implicit.
- The expected invariant used the feminine plural `equivalentes` for masculine
  plural `aspects`, creating a small but visible wording error in a critical
  non-regression statement.

Fixes applied:

- Replaced all bare pytest filenames in AC evidence with full repo-relative
  paths.
- Changed the `RG-145` task and expected-file note from "add" to "verify/keep
  present" so the story matches the current registry state.
- Added an explicit `## 16. Internal Usage Search` section that names the two
  required scans already expected by the story.
- Corrected `equivalentes` to `equivalents`.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 2 - Clean Review

Verdict: clean.

Checks:

- The story remains scoped to the natal aspect-engine input boundary and does
  not broaden into dignities, dominance, advanced conditions, interpretation,
  API, persistence, migrations or frontend.
- Required contracts are present and active: runtime source of truth, baseline
  snapshot, ownership routing, allowlist exception, reintroduction guard and
  persistent evidence.
- Acceptance criteria are atomic and now point to executable repo-relative
  validation commands.
- Implementation tasks map to ACs and cover baseline, selector, projector,
  natal orchestration, tests, guards and final evidence.
- The `RG-145` references now reflect the existing registry state instead of
  implying an unperformed registry edit.
- No remaining wording permits branch-by-`object_type`, specialized aspect
  builders, silent fallback, legacy compatibility, public API changes or
  replacement of the existing orb/aspect engine.

Validation:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 3 - Initial Brief Alignment

Verdict: changes requested, then clean after correction.

Findings:

- The initial brief explicitly distinguishes `longitude` from `zodiac_position`:
  longitude is mandatory for raw aspect calculation, while `zodiac_position`
  is only mandatory if aspect output consumes sign/degree/minute data. The
  story required longitude but did not make the `zodiac_position` rule explicit.
- The brief names `display_name` and `classifications` as possible projection
  fields if `AspectBodyRuntimeData` evolves. The repository contract currently
  contains only `code`, `body_type` and `longitude`; the story needed to state
  that any extension must copy those fields centrally from `ChartObjectRuntimeData`.

Fixes applied:

- Added an internal projection rule to Contract Shape: `longitude` is mandatory,
  `zodiac_position` is optional unless consumed by aspect output, and
  `display_name` / `classifications` must be copied centrally if the internal
  aspect body contract is extended.
- Added the `zodiac_position` target-state invariant.
- Added a projector subtask covering optional `display_name` / `classifications`
  propagation without requiring a public API change.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.
