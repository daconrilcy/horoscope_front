<!-- Journal de preuves pour l'audit frontend design-system. -->

# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Inspected path | Result | Notes / limitations |
|---|---|---|---|---|---|
| E-001 | test_coverage_inventory | `npm run test -- design-system` | `frontend` | PASS | `src/tests/design-system-guards.test.ts`: 5 tests passed. |
| E-002 | ast_dependency_guard | `npm run test -- inline-style` | `frontend` | PASS | `src/tests/inline-style-policy.test.ts`: 4 tests passed. |
| E-003 | ast_dependency_guard | `npm run test -- css-fallback` | `frontend` | PASS | `src/tests/css-fallback-policy.test.ts`: 3 tests passed. |
| E-004 | architecture_guard_inventory | `npm run test -- legacy-style` | `frontend` | PASS | `src/tests/legacy-style-policy.test.ts`: 3 tests passed. Current guard checks `legacy` selectors and selected removed admin prompts aliases, but not every `alias` selector. |
| E-005 | test_coverage_inventory | `npm run test -- theme-tokens` | `frontend` | PASS | `src/tests/theme-tokens.test.ts`: 96 tests passed. |
| E-006 | test_coverage_inventory | `npm run test -- AdminPromptsPage AdminPromptsRouting legacy-style design-system theme-tokens css-fallback inline-style visual-smoke` | `frontend` | PASS | 9 test files passed, 154 tests passed, 8 skipped. |
| E-007 | check_only_lint | `npm run lint` | `frontend` | PASS | TypeScript lint commands passed. |
| E-008 | build_check | `npm run build` | `frontend` | PASS | Build passed; Vite warned that `assets/index-CRHXF_G_.js` is 1,374.82 kB after minification. |
| E-009 | targeted_forbidden_symbol_scan | `rg -n "var\\(\\s*--[a-zA-Z0-9_-]+\\s*," frontend\\src -g "*.css"` | `frontend/src` | PASS | Exactly two fallback hits: `App.css:3124` and `pages/settings/Settings.css:1052`, both `--usage-progress`. |
| E-010 | architecture_guard_inventory | `Get-Content frontend\\src\\styles\\css-fallback-allowlist.md` and `Get-Content frontend\\src\\tests\\design-system-allowlist.ts` | fallback registry and executable allowlist | PASS | Markdown registry and TS allowlist both classify the two `--usage-progress` fallbacks as dynamic. |
| E-011 | targeted_forbidden_symbol_scan | `rg -n "style=\\{" frontend\\src -g "*.tsx"` | `frontend/src` | PASS | Exactly five inline style hits: `DomainRankingCard.tsx`, `TwoColumnLayout.tsx`, `DayTimelineSectionV4.tsx`, and two in `Skeleton.tsx`. |
| E-012 | architecture_guard_inventory | `Get-Content frontend\\src\\tests\\design-system-allowlist.ts` | `frontend/src/tests/design-system-allowlist.ts` | PASS | `INLINE_STYLE_EXCEPTIONS` lists the same five inline-style exceptions. |
| E-013 | repo_wide_negative_scan | `rg -n "adminPromptsLegacy\|AdminPromptsLegacyStrings\|promptsLegacy\|legacyTab\|admin-prompts-legacy\|admin-prompts-modal--legacy-rollback" frontend\\src\\pages\\admin frontend\\src\\i18n frontend\\src\\tests -g "*.ts" -g "*.tsx" -g "*.css"` | admin prompts runtime/test surface | PASS | Zero active hits. CS-070 migration to archive vocabulary is effective for the targeted surface. |
| E-014 | targeted_forbidden_symbol_scan | `rg --files-with-matches "hash/color/spacing/radius/shadow/type pattern" frontend\\src -g "*.css" -g "*.tsx" -g "!tests/**"` | `frontend/src` excluding tests and global token owner CSS | FAIL | 106 application files still contain hardcoded visual or typography values outside the token-owner CSS files. |
| E-015 | targeted_forbidden_symbol_scan | `rg -n "\\.([a-zA-Z0-9_-]*(legacy\|alias)[a-zA-Z0-9_-]*)\|--default_dropshadow" frontend\\src -g "*.css" -g "*.tsx" -g "*.ts"` | `frontend/src` | FAIL | One active alias-named style surface remains: `frontend/src/App.css:1128` `.astrologer-card-alias`; consumer is `AstrologerCard.tsx`. |
| E-016 | architecture_guard_inventory | `Get-Content frontend\\src\\styles\\legacy-style-surface-registry.md` | `frontend/src/styles/legacy-style-surface-registry.md` | FAIL | Registry table is empty, so `.astrologer-card-alias` is not classified. |
| E-017 | targeted_forbidden_symbol_scan | `rg -n "legacy\|Legacy" frontend\\src\\i18n\\consultations.ts frontend\\src\\i18n\\predictions.ts frontend\\src\\pages\\admin\\AdminPromptsPage.css` | selected remaining legacy vocabulary surfaces | FAIL | User-visible `(Legacy)` consultation labels remain in `consultations.ts`; `AdminPromptsPage.css` has a comment-only legacy hit. |
| E-018 | architecture_guard_inventory | `_condamad/stories/regression-guardrails.md` | guardrail registry | PASS | `RG-044` to `RG-050` consulted before finding classification. |

## E-014 Hardcoded-Value File Inventory

The 106 files listed in `00-audit-report.md` under `F-004` are the exhaustive candidate files returned by the scan after excluding tests and global token-owner CSS files.

## Limitations

- This audit did not run browser screenshots or a bundle visual diff; it relies on the existing `visual-smoke` Vitest suite for frontend smoke evidence.
- The hardcoded-value scan is intentionally broad. Each story must refine true duplicates versus one-off classified literals before editing.
