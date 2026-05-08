# CS-108 - Decisions pages avant

Source executable avant implementation: `frontend/src/tests/page-architecture-allowlist.ts`.

## Baseline

Les cinq residus ci-dessous proviennent de CS-107 et de l'audit `F-101`.
Aucune de ces surfaces n'est modifiee dans ce baseline.

| Item | Type | Current classification | Owner before | Route before | Reason before | Exit before | Proof |
|---|---|---|---|---|---|---|---|
| `pages/PrivacyPolicyPage.tsx` | UI page | `needs-user-decision` | `A definir` | none | Page publique potentielle non routee; exposition legale requiert decision produit. | Decision explicite avant routage ou retrait. | Allowlist row; no hit in `routes.tsx`. |
| `pages/billing/BillingSuccessPage.tsx` | UI page | `needs-user-decision` | `A definir` | none | Retour billing potentiellement externe non route; exposition publique requiert decision produit. | Decision explicite avant routage ou retrait. | Allowlist row; test-only import in `BillingSuccessPage.test.tsx`; no route hit. |
| `pages/billing/BillingCancelPage.tsx` | UI page | `needs-user-decision` | `A definir` | none | Retour billing potentiellement externe non route; exposition publique requiert decision produit. | Decision explicite avant routage ou retrait. | Allowlist row; no route hit. |
| `pages/HomePage.tsx` | UI page | `dead/unmounted-page-candidate` | Aucun owner runtime actif | none | Ancienne page non routee; export barrel seulement. | Decision de retrait dediee. | Allowlist row; barrel export in `pages/index.ts`; no route hit. |
| `pages/landing/sections/TestimonialsSection.tsx` | UI component | `dead/unmounted-page-candidate` | Aucun owner runtime actif | none | Aucun import runtime detecte dans `LandingPage` ou routes; suppression hors scope. | Decision produit ou story de retrait dediee. | Allowlist row; no route hit. |

## Route evidence before

- `frontend/src/app/routes.tsx` contains no import or lazy route for `PrivacyPolicyPage`, `BillingSuccessPage`, `BillingCancelPage`, `HomePage` or `TestimonialsSection`.
- `frontend/src/tests/page-architecture-guards.test.ts` blocks routed entries whose classification is `needs-user-decision`.

## Baseline conclusion

The baseline is intentionally incomplete for owner and exit on the five residual files. CS-108 must replace those anonymous or vague decisions with explicit owners and expiry/next-artifact decisions.
