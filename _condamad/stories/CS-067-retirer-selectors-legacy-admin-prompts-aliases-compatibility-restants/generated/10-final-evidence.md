# Final Evidence — CS-067 retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Final status after review loop: done
- Story key: CS-067-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants
- Capsule path: `_condamad/stories/CS-067-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants`

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | `legacy-removal-audit.md` classe selectors et aliases | `npm run test -- legacy-style` | PASS |
| AC2 | `AdminPromptsPage.tsx/css` utilisent `.admin-prompts-archive*` et `.admin-prompts-modal--rollback` | scan zero-hit old selectors + AdminPrompts tests | PASS |
| AC3 | aliases `--text-*`, `--glass*`, `--primary*` retires du theme global, de `App.css`, de `index.css` et des registres legacy | `legacy-style-after.md` + tests theme/AppBgStyles | PASS |
| AC4 | surfaces residuelles classees sans alias de compatibilite global actif; tokens locaux DailyHoroscope exacts documentes dans le registre namespace | scan cible + audit | PASS |
| AC5 | `legacy-style-surface-registry.md` retire selectors supprimes et aliases supprimes; `token-namespace-registry.md` conserve uniquement les tokens locaux exacts | legacy/theme/design-system tests | PASS |
| AC6 | aucun doublon legacy cree | nouveau guard TSX+CSS dans `legacy-style-policy.test.ts` | PASS |

## Files changed

- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/App.css`
- `frontend/src/index.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/tests/AppBgStyles.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `_condamad/stories/CS-067-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants/legacy-style-before.md`
- `_condamad/stories/CS-067-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants/legacy-style-after.md`
- `_condamad/stories/CS-067-retirer-selectors-legacy-admin-prompts-aliases-compatibility-restants/legacy-removal-audit.md`

## Commands run

| Command | Working directory | Result |
|---|---|---|
| `npm run test -- css-fallback design-system theme-tokens inline-style legacy-style AdminPromptsPage Badge MiniInsightCard ShortcutCard visual-smoke AppBgStyles` | `frontend` | PASS, 12 files, 261 passed, 8 skipped |
| `npm run lint` | `frontend` | PASS |
| `npm run build` | `frontend` | PASS, Vite chunk-size warning only |
| `rg -n "admin-prompts-legacy|admin-prompts-modal--legacy-rollback" src/pages/admin/AdminPromptsPage.tsx src/pages/admin/AdminPromptsPage.css` | `frontend` | PASS, zero hits |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py .../00-story.md` | repo root, venv active | PASS |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict .../00-story.md` | repo root, venv active | PASS |

## Review findings

- Accepted and fixed: added a targeted legacy guard covering TSX and CSS for exact zero-hit old selectors plus presence of canonical selectors.
- Accepted and fixed: retired remaining global compatibility aliases `--text-*`, `--glass*`, and `--primary*` from active theme/App surfaces.
- Re-review verdict: CLEAN.

## Remaining risks

- Aucun ecart AC restant.
- Vite reports an existing chunk-size warning during build; this is not an AC limitation.
