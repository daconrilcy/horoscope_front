# Final Evidence — CS-065 reduire-exceptions-styles-inline-restantes

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Final status after review loop: done
- Story key: CS-065-reduire-exceptions-styles-inline-restantes
- Capsule path: `_condamad/stories/CS-065-reduire-exceptions-styles-inline-restantes`

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | `inline-styles-before.md` classe chaque style inline initial | scan `style={` | PASS |
| AC2 | `Badge` migre `background` vers classes CSS tokenisees | tests Badge/MiniInsightCard/ShortcutCard | PASS |
| AC3 | `Skeleton.style` et `--skeleton-gap` restent preserves | allowlist inline + guard | PASS |
| AC4 | `inline-style-allowlist.ts` et `design-system-allowlist.ts` retirent l'exception Badge seulement | `npm run test -- inline-style design-system` | PASS |
| AC5 | Aucun nouveau style inline statique non classe | scan `style={` + guard | PASS |

## Files changed

- `frontend/src/components/ui/Badge/Badge.tsx`
- `frontend/src/components/ui/Badge/Badge.css`
- `frontend/src/components/ui/Badge/Badge.test.tsx`
- `frontend/src/components/MiniInsightCard.tsx`
- `frontend/src/components/ShortcutCard.tsx`
- `frontend/src/hooks/useDailyInsights.ts`
- `frontend/src/tests/MiniInsightCard.test.tsx`
- `frontend/src/tests/ShortcutCard.test.tsx`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/inline-style-allowlist.ts`
- `_condamad/stories/CS-065-reduire-exceptions-styles-inline-restantes/inline-styles-before.md`
- `_condamad/stories/CS-065-reduire-exceptions-styles-inline-restantes/inline-styles-after.md`

## Commands run

| Command | Working directory | Result |
|---|---|---|
| `npm run test -- css-fallback design-system theme-tokens inline-style legacy-style AdminPromptsPage Badge MiniInsightCard ShortcutCard visual-smoke AppBgStyles` | `frontend` | PASS, 12 files, 261 passed, 8 skipped |
| `npm run lint` | `frontend` | PASS |
| `npm run build` | `frontend` | PASS, Vite chunk-size warning only |
| `rg -n "style=\{" src -g "*.tsx"` | `frontend` | PASS, only classified runtime/Skeleton exceptions remain |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py .../00-story.md` | repo root, venv active | PASS |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict .../00-story.md` | repo root, venv active | PASS |

## Review findings

- Accepted and fixed: `Badge.color` no longer remains a broad `string`; supported color values are typed by `BadgeColorValue`.
- Re-review verdict: CLEAN.

## Remaining risks

- Aucun ecart AC restant.
- Vite reports an existing chunk-size warning during build; this is not an AC limitation.
