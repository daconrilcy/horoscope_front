<!-- Inventaire final du formatage date/heure inline dans les pages React. -->

# CS-102 - After date/time inventory

Commande executee:

```powershell
Push-Location frontend
rg -n "new Date\([^\n]+\)\.toLocale(DateString|String)|Intl\.DateTimeFormat|\.toLocaleString\(" src/pages -g "*.tsx"
Pop-Location
```

## Remaining scan hits

| Hit | Classification | Raison |
|---|---|---|
| `src/pages/admin/AdminDashboardPage.tsx:162` | numeric-only | Montant `mrr_cents` converti en euros. |
| `src/pages/admin/AdminDashboardPage.tsx:172` | numeric-only | Montant `revenue_cents` converti en euros. |
| `src/pages/admin/AdminDashboardPage.tsx:238` | numeric-only | Montant tableau `mrr_cents`. |
| `src/pages/admin/AdminDashboardPage.tsx:239` | numeric-only | Montant tableau `estimated_period_revenue_cents`. |
| `src/pages/admin/AdminDashboardPage.tsx:252` | numeric-only | Total revenu estime. |
| `src/pages/SubscriptionGuidePage.tsx:357` | numeric-only | Quota numerique localise. |
| `src/pages/settings/UsageSettings.tsx:13` | numeric-only | Nombre de tokens formate en `fr-FR`. |

## Canonical-owner changes

| Surface | canonical-owner | Preuve |
|---|---|---|
| Date simple admin support/users | `frontend/src/utils/formatDate.ts::formatLocalDate` | Imports directs depuis l'utilitaire canonique. |
| Date simple politique de confidentialite | `frontend/src/utils/formatDate.ts::formatLocalDate` | `PrivacyPolicyPage.tsx` utilise le helper canonique pour la date de mise a jour. |
| Date/heure admin logs/prompts/support/users | `frontend/src/utils/formatDate.ts::formatLocalDateTime` | Remplace les anciens `new Date(...).toLocaleString()` sans options. |
| Date/heure settings avec options | `frontend/src/utils/formatDate.ts::formatDateWithOptions` | `UsageSettings.tsx` utilise le helper canonique avec `getLocale(lang)`. |
| Date settings abonnement avec options | `frontend/src/utils/formatDate.ts::formatDateWithOptions` | `SubscriptionSettings.tsx` utilise le helper canonique pour `formatDisplayDate`. |

## No-shim proof

- `unowned`: zero.
- `page-specific-retained`: zero.
- `canonical-consumer`: les pages touchees importent directement depuis `frontend/src/utils/formatDate.ts`.
- Allowed differences: none; `formatLocalDate` et `formatLocalDateTime` preservent les anciens appels navigateur sans options, et `formatDateWithOptions` utilise `Intl.DateTimeFormat` avec les memes options.

## Validation

- `npm run test -- formatDate page-architecture`: PASS.
- `npm run lint`: PASS.
- Scan final: seulement `numeric-only`.
