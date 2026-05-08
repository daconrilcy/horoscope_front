<!-- Journal de preuves de l'audit de cloture frontend-react-pages. -->

# Evidence Log - frontend-react-pages

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | prior-history | `Get-Content -Raw` on prior audit reports and story status | `_condamad/audits/frontend-react-pages/**`, `_condamad/stories/story-status.md` | PASS | CS-100, CS-101, and CS-102 are marked `done`; prior residual findings identified. |
| E-002 | persistent-evidence | `Get-Content -Raw _condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/admin-prompts-after.md` | `_condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/admin-prompts-after.md` | PASS | Artifact states `AdminPromptsPage.tsx` is 81 lines, active sections are extracted, and residual status is none. |
| E-003 | architecture-guard-inventory | `Get-Content -Raw frontend/src/tests/page-architecture-allowlist.ts` and `Get-Content -Raw frontend/src/tests/page-architecture-guards.test.ts` | `frontend/src/tests` | PASS | `TS_NOCHECK_PAGE_EXCEPTIONS`, `DIRECT_API_PAGE_EXCEPTIONS`, and `PAGE_SIZE_EXCEPTIONS` are empty; guards enforce exact absence/stale checks. |
| E-004 | targeted-forbidden-symbol-scan | `rg -n "@ts-nocheck" frontend/src/pages -g "*.tsx"`; `rg -n "apiFetch\\(" frontend/src/pages -g "*.tsx"`; route/barrel forbidden scan | `frontend/src/pages`, `frontend/src/app` | PASS | Zero hits for `@ts-nocheck`, page direct `apiFetch`, forbidden public route aliases, and forbidden admin barrel exports. |
| E-005 | targeted-forbidden-symbol-scan | `rg -n "new Date\\([^\\n]+\\)\\.toLocale(DateString\|String)\|Intl\\.DateTimeFormat\|\\.toLocaleString\\(" frontend/src/pages -g "*.tsx"` | `frontend/src/pages` | PASS | Remaining hits are numeric-only formatting already classified by CS-102. |
| E-006 | frontend-validation | `npm run lint` | `frontend/` | PASS | TypeScript lint command completed successfully. |
| E-007 | frontend-validation | `npm run test -- page-architecture formatDate AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow AstrologerProfile BirthProfile SubscriptionSettings AdminSamplePayloads` | `frontend/` | PASS | Vitest: 9 files passed, 121 tests passed, 8 skipped. Output includes non-blocking jsdom navigation notice. |
| E-008 | structural-inventory | PowerShell line-count inventory for `frontend/src/pages/**/*.tsx` and target files | `frontend/src/pages`, `frontend/src/features/admin-prompts` | PASS | No page exceeds 700 lines; key counts: AdminPrompts 81, AstrologerProfile 697, BirthProfile 688, SubscriptionSettings 699, AdminSamplePayloads feature 683. |
| E-009 | canonical-owner-inventory | `rg -n "formatDate\|formatDateTime\|formatDateWithOptions\|formatLocal" frontend/src/pages frontend/src/utils/formatDate.ts frontend/src/tests/formatDate.test.ts` | `frontend/src/pages`, `frontend/src/utils/formatDate.ts`, `frontend/src/tests/formatDate.test.ts` | PASS | Date/time UI formatting routes through canonical helpers; helper behavior is covered by tests. |
| E-010 | git-status | `git status --short` | repository root | PASS | Only pre-existing untracked `release-test-output.txt` was observed before audit artifacts were written. |

## Limitations

- This audit did not run a browser or backend runtime because the audited residuals are page architecture, static ownership, and focused frontend tests.
- Numeric formatting was intentionally not migrated into date helpers; it is documented as non-domain for the CS-102 date/time finding.
