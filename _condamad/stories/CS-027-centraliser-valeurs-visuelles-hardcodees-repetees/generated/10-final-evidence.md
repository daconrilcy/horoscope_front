<!-- Preuve finale CONDAMAD pour CS-027. -->

# Final Evidence CS-027

Status: done

AC evidence:

- AC1 PASS: `hardcoded-values-before.md` and `hardcoded-values-after.md` persist the batch inventory.
- AC2 PASS: existing `--space-*` and `--radius-*` tokens are reused; no synonym token added.
- AC3 PASS: batch CSS now uses `var(--radius-full)`, `var(--space-2)` and `var(--space-3)`.
- AC4 PASS: approximate values are documented as blocked in `hardcoded-value-migration.md`.
- AC5 PASS: `css-fallback-policy.test.ts` guards the migrated literals in the batch.

Validation:

- `npm run test -- css-fallback` PASS.
- `npm run test -- design-system` PASS.
- `npm run lint` PASS.
- scan `border-radius: 999px;|gap: 8px;|gap: 12px;` on batch files: zero hit.
- venv active: story validate/lint PASS.

Remaining risks: broad color/gradient migration intentionally deferred.
