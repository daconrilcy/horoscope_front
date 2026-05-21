<!-- Revue redactionnelle CONDAMAD de la story CS-212. -->

# CS-212 Story Writing Review

## Iteration 1 - Issues Found

Verdict: changes requested.

Findings:

- The story required phase boundary validation against "les bornes du brief",
  but did not list all canonical phase intervals in the contract section. A dev
  agent could infer different ranges from the brief, the tests, or the priority
  notes.

Fixes applied:

- Added `Phase boundary shape` to section 4f with the explicit interval for
  each `MoonPhaseKey`.
- Added a `Phase priority rule` in section 4f so `NEW_MOON`, `FULL_MOON` and
  `BALSAMIC` are resolved from story-local contract text.
- Replaced AC9 through AC12 references to "bornes du brief" with references to
  section 4f.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS after shortening AC11.
- `condamad_story_lint.py --strict`: PASS after shortening AC11.

## Iteration 2 - Issues Found

Verdict: changes requested.

Findings:

- The new phase boundary text mixed English and French in a French story,
  making the contract less consistent than the surrounding sections.
- AC14 still referenced "la formule du brief" even though the illumination
  formula is already stated in section 3.

Fixes applied:

- Reworded the phase boundary and priority rule text in French.
- Replaced the AC14 brief reference with a story-local reference to section 3.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 3 - Clean Review

Verdict: clean.

Checks:

- The story is self-contained for phase boundaries, phase priority,
  illumination formula, `phase_index` mapping and waxing/waning classification.
- Acceptance criteria AC9 through AC14 now reference story-local contract
  sections instead of requiring the dev agent to infer details from the brief.
- Required contracts remain present: runtime source of truth, baseline
  snapshot, ownership routing, allowlist exception, contract shape,
  reintroduction guard and persistent evidence.
- No remaining wording permits scoring, interpretation, API/DB/frontend
  integration, compatibility shims, fallback behavior, duplicate contracts or
  out-of-scope `NatalResult` integration.

Validation:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 4 - Brief Alignment Review

Verdict: changes requested, then clean after correction.

Findings:

- The story encoded the effective `WANING_CRESCENT` interval as
  `292.5 <= angle < 315.0`. That matches the final runtime classification
  after the balsamic override, but the initial brief describes a base
  `WANING_CRESCENT` segment up to `337.5` and then applies `BALSAMIC` as a
  priority override from `315.0` to `337.5`.
- The story covered exact `0.0` and `180.0`, but did not explicitly state the
  brief's `360.0 -> 0.0 -> EXACT` edge case in the target-state/test wording.

Fixes applied:

- Replaced `Phase boundary shape` with `Base phase segmentation`, keeping
  `WANING_CRESCENT` as `292.5 <= angle < 337.5`.
- Added `Effective balsamic override` to preserve the final runtime behavior:
  `315.0 <= angle < 337.5` returns `BALSAMIC`, and `angle >= 337.5` returns
  `NEW_MOON`.
- Added the `360.0 -> 0.0 -> EXACT` expectation to the target state and unit
  test tasks.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

Clean alignment check:

- The story now matches the brief's domain API, CS-208 contract reuse,
  longitude normalization, `(moon - sun) % 360.0` angle calculation,
  waxing/waning/exact states, hybrid phase segmentation, balsamic priority,
  approximate illumination formula, stable `phase_index`, target files,
  targeted tests, quality validation and anti-drift exclusions.
