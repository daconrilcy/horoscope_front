<!-- Evidence finale CS-082. -->

# Final Evidence

Story status: done.

## AC status

- AC1: PASS
- AC2: PASS
- AC3: PASS
- AC4: PASS
- AC5: PASS
- AC6: PASS
- AC7: PASS

## Files changed

- `frontend/src/App.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/tests/BottomNavPremium.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees/hardcoded-values-before.md`
- `_condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees/hardcoded-values-after.md`
- generated evidence files in this capsule
- `_condamad/stories/story-status.md`

## Commands run

- `npm run test -- design-system legacy-style` - PASS after one correction cycle.
- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke AdminPromptsPage` - PASS.
- `npm run test -- BottomNavPremium design-system` - PASS after aligning BottomNav assertions with `--app-*`.
- `npm run test` - PASS, 115 files passed, 1254 tests passed, 8 skipped.
- `npm run lint` - PASS.
- `npm run build` - PASS, with existing Vite chunk-size warning.
- `npm run test -- design-system` - PASS after review fix.
- `rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/App.css` - PASS evidence captured.
- `rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/App.css` - PASS evidence captured.
- `rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/App.css` - PASS evidence captured.
- `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees/00-story.md` - PASS.
- `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees/00-story.md` - PASS.

## DRY / No Legacy evidence

- No dependency added.
- No App React behavior changed.
- No broad exception or wildcard added.
- `--app-*` registered as semantic-extension.
- Guard blocks return of selected migrated App literal values outside the `#root` owner block.
- BottomNav premium tests now verify token consumption plus exact token-owned visual values.

## Reviewer focus

- Verify that the chosen `--app-*` owner is acceptable for App-scoped visual roles.
- Verify kept-one-off-final entries remain outside the bounded migrated subset.
