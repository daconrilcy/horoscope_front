# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Inspected path | Result | Notes / Limitations |
|---|---|---|---|---|---|
| E-001 | story-inventory | `Get-ChildItem _condamad/stories -Directory \| Where-Object { $_.Name -match '^CS-0(26\|27\|28\|29\|30\|31\|32)' }` | `_condamad/stories` | PASS | All seven expected follow-up story folders exist. |
| E-002 | guardrail-registry | Read `_condamad/stories/regression-guardrails.md` | `_condamad/stories/regression-guardrails.md` | PASS | Frontend invariants `RG-044` through `RG-050` now protect design-system surfaces. |
| E-003 | artifact-inventory | `rg --files frontend/src \| rg "(token-namespace-registry\|hardcoded-values\|typography-roles\|css-fallback-allowlist\|legacy-style-surface-registry\|design-system-allowlist\|tests)"` | `frontend/src` | PASS | Registries and static guard files are present. |
| E-004 | source-inspection | Read `design-system-guards.test.ts`, `inline-style-policy.test.ts`, `css-fallback-policy.test.ts`, `legacy-style-policy.test.ts` | `frontend/src/tests` | PASS | Guards connect registries to real CSS/TSX inventory and assert zero unclassified exceptions. |
| E-005 | targeted-test | `npm run test -- design-system inline-style css-fallback legacy-style theme-tokens` | `frontend` | PASS | 5 test files, 108 tests passed. |
| E-006 | lint | `npm run lint` | `frontend` | PASS | TypeScript lint command passed. |
| E-007 | build | `npm run build` | `frontend` | PASS | Production build passed; Vite warned that the main chunk is larger than 500 kB. |
| E-008 | static-scan | `rg -n "#[0-9A-Fa-f]{3,8}\|rgba?\(\|hsla?\(\|\b(?:white\|black\|transparent)\b" frontend/src --glob '*.css' --glob '!styles/design-tokens.css' --glob '!styles/theme.css' --glob '!styles/premium-theme.css' --glob '!styles/utilities.css'` | `frontend/src/**/*.css` | PASS | 1890 color-like occurrences remain outside core token and utility files. Static scan includes legitimate CSS keywords and may overcount. |
| E-009 | static-scan | `rg --pcre2 -n "border-radius:\s*(?!var\()\|gap:\s*(?!var\()\|padding:\s*(?!var\()\|margin:\s*(?!var\()\|box-shadow:\s*(?!var\()" frontend/src --glob '*.css'` | `frontend/src/**/*.css` | PASS | 2627 non-tokenized spacing/radius/shadow declaration hits remain. Static scan includes migration-only and legitimate local layout values. |
| E-010 | static-scan | `rg --pcre2 -n "font-size:\s*(?!var\()\|font-weight:\s*(?!var\()\|line-height:\s*(?!var\()\|letter-spacing:\s*(?!var\()" frontend/src --glob '*.css'` | `frontend/src/**/*.css` | PASS | 1533 non-tokenized typography declaration hits remain. |
| E-011 | static-scan | `rg -n "style=" frontend/src --glob '*.tsx'` | `frontend/src/**/*.tsx` | PASS | 85 inline style attributes remain and are expected to be exactly allowlisted by the guard suite. |
| E-012 | static-scan | `rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," frontend/src --glob '*.css'` | `frontend/src/**/*.css` | PASS | 329 CSS fallback usages remain and are expected to be exactly allowlisted by the guard suite. |
| E-013 | test-limitation | `npm run test`, then `npm run test -- HelpPage` | `frontend` | LIMITATION | Full run failed once in `HelpPage.test.tsx` on missing text `Bug / dysfonctionnement`; isolated HelpPage run passed 4/4 immediately after. |
| E-014 | targeted-static-scan | `rg -n "border-radius:\s*(999px)\|gap:\s*(8px\|12px)" frontend/src/App.css frontend/src/pages/admin/AdminPromptsPage.css frontend/src/pages/HelpPage.css frontend/src/pages/settings/Settings.css frontend/src/pages/AstrologerProfilePage.css` | migrated CSS batch | PASS | No exact `border-radius: 999px;`, `gap: 8px;`, or `gap: 12px;` regression found. One `gap: 8px 10px;` remains in `AstrologerProfilePage.css` and is outside the exact guard pattern. |
| E-015 | targeted-static-scan | `rg -n "style=" frontend/src/layouts/SettingsLayout.tsx frontend/src/features/astrologers/components/AstrologerCard.tsx frontend/src/components/settings/DeleteAccountModal.tsx` | audited inline-style batch | PASS | No inline style attributes remain in the three previously audited files. |

## Evidence Notes

- Static scan counts are used as drift indicators, not exact defect counts.
- The frontend audit did not start a browser dev server because no application code was changed and `npm run build` already proved the compiled app can be produced.
