# CONDAMAD Code Review - CS-210

## Review target

- Story: `CS-210-planetary-motion-conditions-calculator`
- Capsule: `_condamad/stories/CS-210-planetary-motion-conditions-calculator`
- Review iterations: 3

## Inputs reviewed

- `00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
- `git diff`, `git diff --check`, `git status --short`
- Changed implementation and test files under `planetary_conditions`

## Review layers

- Story Conformance Reviewer: two low evidence findings, both fixed.
- Technical Risk Reviewer: two medium implementation findings and one low evidence finding, all fixed.
- Source Finding Closure Reviewer: CLEAN.
- Review/fix evidence pass: one low preflight evidence contradiction, fixed.
- Main CONDAMAD review: CLEAN after fixes.

## Findings

### CR-1 Medium - Non-finite floats could be misclassified

- Bucket: patch
- Source layer: technical risk
- Evidence: `speed_deg_per_day=nan` could reach `_motion_direction`; non-finite profile values were not rejected.
- Fix: added finite validation for `speed_deg_per_day`, `mean_speed_deg_per_day`, `stationary_threshold_abs` and ratio thresholds.
- Validation: targeted tests PASS; full `pytest -q` PASS.
- Status: resolved

### CR-2 Medium - Profile/planet mismatch was silently accepted

- Bucket: patch
- Source layer: technical risk
- Evidence: `calculate_planetary_motion_condition` accepted a `planet_key` separate from `profile.planet_key`.
- Fix: explicit `ValueError` when `profile.planet_key != planet_key`; batch path covered by the same guard.
- Validation: targeted tests PASS; full `pytest -q` PASS.
- Status: resolved

### CR-3 Low - Zero-hit `rg` evidence needed reproducible exit-status handling

- Bucket: patch
- Source layer: validation
- Evidence: raw `rg` zero-hit returns exit status `1`, while evidence recorded success.
- Fix: evidence updated to show the exact PowerShell wrapper that maps zero-hit `rg` to validation success.
- Status: resolved

### CR-4 Low - Changed-file inventory omitted story status

- Bucket: patch
- Source layer: acceptance
- Evidence: `_condamad/stories/story-status.md` changed but was absent from final evidence file list.
- Fix: final evidence file list updated.
- Status: resolved

### CR-5 Low - Final evidence preflight contradicted current review state

- Bucket: patch
- Source layer: validation
- Evidence: `generated/10-final-evidence.md` claimed a clean initial worktree, while this review/fix cycle began with CS-210 implementation and evidence files already dirty.
- Fix: final evidence now records that the dirty worktree was scoped to CS-210 closure and that no unrelated dirty file was touched.
- Status: resolved

## Acceptance audit

All AC1-AC13 have implementation and validation evidence. Stationary priority, zero speed, speed ratio thresholds, invalid finite mean speed, default catalogue, missing profile, non-finite rejection and profile mismatch are covered by tests.

## Validation audit

- `ruff format .`: PASS
- `ruff check .`: PASS
- targeted pytest: PASS, 28 passed
- `pytest -q`: PASS, 2853 passed, 1 skipped, 1177 deselected
- forbidden scans: PASS with explicit zero-hit wrapper
- adjacent diff: PASS, empty
- `git diff --check`: PASS

## DRY / No Legacy audit

No shim, alias, fallback, compatibility path, adjacent integration, scoring, narrative, API, DB, service, frontend or `NatalResult` integration was introduced.

## Residual risks

None identified.

## Feedback propagation

- Decision: no-propagation
- Reason: all findings were local to CS-210 implementation or evidence and are
  fully covered by existing RG-137 validation.

## Verdict

CLEAN
