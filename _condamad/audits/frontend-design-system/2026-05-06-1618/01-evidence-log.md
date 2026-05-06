<!-- Journal des preuves de l'audit frontend design-system apres refactors. -->

# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | repo_status | `git status --short` | repository root | PASS | Worktree clean before audit artifact creation. |
| E-002 | test_coverage_inventory | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke HelpPage AdminPage ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage` | `frontend` | PASS | 12 test files, 194 tests passed. JSDOM emitted existing canvas `getContext` warnings. |
| E-003 | architecture_guard_inventory | `npm run lint` | `frontend` | PASS | TypeScript lint commands completed successfully. |
| E-004 | runtime_contract_check | `npm run build` | `frontend` | PASS | Production build completed; Vite reported the main JS chunk at 1,371.35 kB, above the 500 kB warning threshold. |
| E-005 | dependency_direction_scan | `rg -n -- "--settings-\|--profile-\|--astro-\|--default_dropshadow\|migration-only" src\styles src\pages\HelpPage.css src\pages\settings\Settings.css src\pages\AstrologerProfilePage.css src\App.css` | token registries and page-scoped owners | PASS | No `--settings-*` consumption remains in `HelpPage.css`; no `--default_dropshadow` hit; `--settings-*`, `--profile-*`, and `--astro-*` are now registered as `semantic-extension`. |
| E-006 | targeted_forbidden_symbol_scan | `rg -n --glob "*.tsx" "style=" src` | `frontend/src` | PASS | Exactly five TSX inline-style exceptions remain and match `src/tests/design-system-allowlist.ts`. |
| E-007 | targeted_forbidden_symbol_scan | `rg -n --glob "*.css" --pcre2 "var\(\s*--[A-Za-z0-9_-]+\s*," src` | `frontend/src` | PASS | Exactly two CSS fallback exceptions remain, both `--usage-progress` dynamic bridges listed in `src/styles/css-fallback-allowlist.md`. |
| E-008 | targeted_forbidden_symbol_scan | `rg -n "/admin/(pricing\|monitoring\|personas)" src -g "*.ts" -g "*.tsx" -g "*.css"` | `frontend/src` | PASS | Zero hits; legacy admin redirects are removed. |
| E-009 | targeted_forbidden_symbol_scan | `rg -n "Deprecated:\|backwards compatibility\|backward compatibility\|legacy fallback\|Legacy codes\|aspectLegacy\|compatibility" src\pages src\components src\utils src\i18n -g "*.ts" -g "*.tsx"` | frontend runtime/i18n modules | FAIL | Compatibility vocabulary remains in five runtime/i18n files. |
| E-010 | targeted_forbidden_symbol_scan | `rg --files-with-matches --pcre2 --glob "*.css" --glob "*.tsx" --glob "!src/tests/**" --glob "!**/*.test.ts" --glob "!**/*.test.tsx" --glob "!src/styles/**" "<hardcoded visual regex>" src` | `frontend/src`, excluding tests and `src/styles/**` | FAIL | 101 non-test application files still contain hardcoded visual or typography literals. Full candidate inventory is in `00-audit-report.md`. |

## E-009 Compatibility Hits

- `frontend/src/pages/ChatPage.tsx:82` - deprecated `astrologerId` kept for backwards compatibility.
- `frontend/src/utils/dailySummaryHelper.ts:8` - `summary.overall_summary` documented as legacy fallback.
- `frontend/src/i18n/predictions.ts:142` - `Legacy codes` comment and compatibility mapping.
- `frontend/src/components/DailyInsightsSection.tsx:38` - default export kept for backward compatibility.
- `frontend/src/components/NatalInterpretation.tsx:994` - `aspectLegacy` parser branch for old aspect IDs.

## Limitations

- The hardcoded-value regex is intentionally broad. It is reliable as an exhaustive candidate-file inventory for story scoping, but each story must inspect the selected files before deciding which literals should become tokens.
- This audit is read-only for application code. It validates guards, scans source contracts, and writes only audit artifacts.
