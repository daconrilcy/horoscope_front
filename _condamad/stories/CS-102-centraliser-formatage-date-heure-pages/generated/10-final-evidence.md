<!-- Preuves finales de mise en oeuvre pour CS-102. -->

# CS-102 - Final evidence

## Acceptance status

| AC | Status | Evidence |
|---|---|---|
| AC1 | PASS | `date-time-format-before.md` classe chaque hit du scan initial. |
| AC2 | PASS | `date-time-format-after.md` liste les owners `formatDate.ts` et les imports canoniques. |
| AC3 | PASS | `frontend/src/tests/formatDate.test.ts` couvre `formatLocalDate`, `formatLocalDateTime` et `formatDateWithOptions`. |
| AC4 | PASS | Scan final sans hit `date-time-ui` non migre; hits restants classes `numeric-only`. |
| AC5 | PASS | `npm run lint` termine sans erreur. |
| AC6 | PASS | Helpers locaux preservent `toLocaleDateString()` et `toLocaleString()` sans options; `formatDateWithOptions` preserve `Intl.DateTimeFormat`. |
| AC7 | PASS | `npm run test -- formatDate page-architecture` termine sans erreur. |

## Commands run

```powershell
Push-Location frontend
npm run lint
npm run test -- formatDate page-architecture
rg -n "new Date\([^\n]+\)\.toLocale(DateString|String)|Intl\.DateTimeFormat|\.toLocaleString\(" src/pages -g "*.tsx"
Pop-Location
```

## Result

- Lint: PASS.
- Tests `formatDate page-architecture`: PASS, 2 files / 28 tests.
- Final scan: PASS with only classified `numeric-only` hits.
- Story validators after `.\.venv\Scripts\Activate.ps1`: PASS for validate, explain-contracts, lint and strict lint.

## Review notes

- La review a signale un hit hors regex dans `SubscriptionSettings.tsx::formatDisplayDate`; il a ete migre vers `formatDateWithOptions` et ajoute aux inventaires.
- La review a signale `PrivacyPolicyPage.tsx`; il a ete migre vers `formatLocalDate` et ajoute aux inventaires.
- No page-local wrapper was added.
- No numeric formatting was migrated into date helpers.
- No backend, API contract, route alias, style or package dependency changed.
- Remaining in-domain work: none.
