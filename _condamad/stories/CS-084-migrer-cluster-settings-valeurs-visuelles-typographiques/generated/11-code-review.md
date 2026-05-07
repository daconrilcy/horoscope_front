# CONDAMAD Code Review

## Review target

- Story: `CS-084-migrer-cluster-settings-valeurs-visuelles-typographiques`
- Status at first review: `ready-to-review`
- Scope reviewed: `Settings.css`, `design-system-guards.test.ts`, `visual-smoke.test.tsx`, capsule evidence and story status.

## Inputs reviewed

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `hardcoded-values-before.md`
- `hardcoded-values-after.md`
- `git diff --stat`, focused diffs and validation outputs

## Review layers

- Story Conformance Reviewer: ran read-only through subagent.
- Technical Risk Reviewer: ran read-only through subagent.
- Main CONDAMAD review: findings triaged against repository evidence.

## Findings

### CR-001 High - Settings page background token could be unresolved

- Bucket: patch
- Location: `frontend/src/pages/settings/Settings.css`, `frontend/src/layouts/SettingsLayout.tsx`
- Source layer: technical risk
- Evidence: `--settings-*` owner was initially on `.settings-container`, while `.settings-bg-halo` is a sibling outside that container.
- Impact: `background: var(--settings-page-bg)` could fail at runtime.
- Fix: moved Settings semantic owner to `.is-settings-page`, a common ancestor rendered by `SettingsLayout`.
- Status: RESOLVED.

### CR-002 High - Spacing literals were not fully migrated or guarded

- Bucket: patch
- Location: `frontend/src/pages/settings/Settings.css`, `frontend/src/tests/design-system-guards.test.ts`
- Source layer: story conformance
- Evidence: story scope includes spacing; repeated padding, margin, gap and offset literals remained outside a final owner.
- Impact: AC2, AC3 and AC6 were not fully proven.
- Fix: centralized repeated Settings spacing/layout values under `--settings-*` variables and extended the CS-084 guard to block selector-level spacing literals.
- Status: RESOLVED.

### CR-003 High - Visual-smoke evidence did not cover Settings rendering

- Bucket: patch
- Location: `frontend/src/tests/visual-smoke.test.tsx`, `generated/10-final-evidence.md`
- Source layer: story conformance and technical risk
- Evidence: initial visual-smoke suite did not load/render Settings surfaces.
- Impact: AC5 evidence was incomplete.
- Fix: added a SettingsLayout render smoke test that checks `.settings-bg-halo` is under `.is-settings-page` and the CSS defines the halo token path.
- Status: RESOLVED.

### CR-004 Medium - Before/after evidence was too aggregated

- Bucket: patch
- Location: `hardcoded-values-before.md`, `hardcoded-values-after.md`
- Source layer: story conformance
- Evidence: initial artifacts classified broad families without explicit spacing decisions.
- Impact: AC2 auditability was weak.
- Fix: expanded before/after artifacts with baseline literal families, owner block decisions, spacing classification and functional zero/auto exceptions.
- Status: RESOLVED.

### CR-005 Low - `story-status.md` was missing from changed-file evidence

- Bucket: patch
- Location: `generated/10-final-evidence.md`
- Source layer: story conformance
- Evidence: story status changed but was absent from the file table.
- Impact: scope evidence was incomplete.
- Fix: added `story-status.md` to final evidence.
- Status: RESOLVED.

## Acceptance audit

| AC | Verdict | Evidence |
|---|---|---|
| AC1 | PASS | Diff scope is Settings CSS, guards, visual-smoke, story evidence and status only. |
| AC2 | PASS | Before/after artifacts classify visual, typography, spacing and runtime literals. |
| AC3 | PASS | Repeatable selector values route to tokens or `--settings-*` owner variables. |
| AC4 | PASS | Only `--usage-progress` remains as an exact allowlisted fallback. |
| AC5 | PASS | SettingsLayout visual-smoke and design-system guard cover Settings token inheritance. |
| AC6 | PASS | CS-084 guard blocks selector-level migrated literal reintroduction. |
| AC7 | PASS | No forbidden No Legacy vocabulary in `Settings.css`. |
| AC8 | PASS | No AC uses `PASS_WITH_LIMITATIONS`; required validations passed. |

## Validation audit

- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`: PASS.
- `npm run test`: PASS.
- `npm run lint`: PASS.
- `npm run build`: PASS with known Vite chunk-size warning, explicitly out of scope.
- Story validation and lint after venv activation: PASS.

## DRY / No Legacy audit

- No new dependency, shim, alias, compatibility path or migration-only namespace.
- `--settings-*` remains registered and page-scoped.
- `--usage-progress` remains the only runtime CSS fallback in scope.

## Residual risks

- Existing Vite large chunk warning remains out of scope for CS-084.

## Verdict

CLEAN
