# Final Evidence - CS-079

## Status

Implementation status: ready-to-review after review fixes.

Pre-existing dirty files before implementation:

- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`
- `_condamad/audits/frontend-design-system/2026-05-06-1618/`
- `_condamad/stories/CS-079-migrer-cluster-composants-ui-valeurs-visuelles-hardcodees/`
- `_condamad/stories/CS-080-supprimer-compatibilites-runtime-frontend-restantes/`

## Files changed

- `frontend/src/components/ShortcutsSection.tsx`
- `frontend/src/components/ui/Badge/Badge.css`
- `frontend/src/components/ui/Badge/Badge.tsx`
- `frontend/src/components/ui/Button/Button.css`
- `frontend/src/components/ui/Card/Card.css`
- `frontend/src/components/ui/EmptyState/EmptyState.css`
- `frontend/src/components/ui/ErrorState/ErrorState.css`
- `frontend/src/components/ui/Field/Field.css`
- `frontend/src/components/ui/LockedSection/LockedSection.css`
- `frontend/src/components/ui/Modal/Modal.css`
- `frontend/src/components/ui/Select/Select.css`
- `frontend/src/components/ui/Skeleton/Skeleton.css`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx`
- `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.css`
- `frontend/src/components/ui/UserAvatar/UserAvatar.css`
- `frontend/src/components/ui/UserMenu/UserMenu.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/stories/CS-079-migrer-cluster-composants-ui-valeurs-visuelles-hardcodees/hardcoded-values-before.md`
- `_condamad/stories/CS-079-migrer-cluster-composants-ui-valeurs-visuelles-hardcodees/hardcoded-values-after.md`

## Frontend subagent evidence

`condamad-frontend-dev` subagent used for the frontend slice.

Reported results:

- `npm run test -- design-system theme-tokens css-fallback legacy-style visual-smoke` - PASS, 128 tests.
- `npm run lint` - PASS.
- `git diff --check -- frontend` - PASS.
- Targeted `src/components/ui` scans - PASS for migrated literals and No Legacy terms.
- No registry update required because new tokens use canonical namespaces already registered.

## AC validation

| AC | Status | Evidence |
|---|---|---|
| AC1 | PASS | `hardcoded-values-before.md`, scoped frontend diff. |
| AC2 | PASS | `hardcoded-values-after.md` has final decisions for all touched visual values and no limitation marker. |
| AC3 | PASS | Tokens and roles added under canonical owners. |
| AC4 | PASS | No CSS fallback introduced; `Skeleton.tsx` fallback removed. |
| AC5 | PASS | Design-system guard CS-079 added and tests pass. |
| AC6 | PASS | Exact anti-return scan and guard added. |

## Review findings fixed

- Preserved the public `BadgeColorValue` input for the former primary token string while keeping internal consumers on `--color-primary`.
- Completed before/after artefacts for `LockedSection`, `UserMenu`, and `ErrorState` token migrations.
- Removed the generated template block that contained contradictory placeholder status.
- Added story validation and lint commands to this final evidence file.

## No Legacy / DRY evidence

- No compatibility wrapper, shim, fallback namespace or migration-only namespace introduced.
- Direct consumer `ShortcutsSection` migrated to `var(--color-primary)`.
- Repeated literals moved to canonical token families instead of duplicated local variables.
- Public `Badge` input compatibility is preserved only to satisfy the story constraint that React props remain unchanged; the migrated source no longer emits the old token in first-party consumers.

## Commands run

- `npm run test -- design-system theme-tokens css-fallback legacy-style visual-smoke` - PASS, 128 tests.
- `npm run lint` - PASS.
- `git diff --check -- frontend` - PASS.
- `rg` targeted scans over `frontend/src/components/ui` for colors, typography, radius/shadow/fallback and legacy vocabulary - PASS or token-only hits as documented.
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-079-migrer-cluster-composants-ui-valeurs-visuelles-hardcodees/00-story.md` - PASS.
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-079-migrer-cluster-composants-ui-valeurs-visuelles-hardcodees/00-story.md` - PASS.

## Commands not run

- Full frontend suite and E2E - NOT_RUN; outside validation plan for this style-token migration.
- Local dev server - NOT_RUN; no runtime integration change requiring browser startup.

## Remaining risks

Dimensions structurelles UI (`32px`, `40px`, `48px`, `56px`, widths and icon
sizes) remain one-off layout contracts. No remaining legacy risk identified
for the migrated literals.
