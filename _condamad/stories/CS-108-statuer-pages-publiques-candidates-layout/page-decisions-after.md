# CS-108 - Decisions pages apres

Source executable apres implementation: `frontend/src/tests/page-architecture-allowlist.ts`.

## Decision summary

Decision utilisateur du 2026-05-08 appliquee apres l'audit de continuite:
privacy est routee publiquement, les callbacks Stripe sont routes car la config
checkout pointe vers ces URLs, l'ancienne home est supprimee, et testimonials est
rattachee a la landing.

| Item | Type | Current classification | Decision | Owner | Expiry / next artifact | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `pages/PrivacyPolicyPage.tsx` | UI page | `routed-page` | `route` | LandingLayout sous RootLayout | Permanent tant que la page privacy publique est requise. | Route `/privacy`; allowlist classee `routed-page`; test App public. | Contenu legal a maintenir par owner legal/produit. |
| `pages/billing/BillingSuccessPage.tsx` | UI page | `routed-page` | `route` | AppLayout sous RootLayout | Permanent tant que `STRIPE_CHECKOUT_SUCCESS_URL` pointe vers `/billing/success`. | Config backend par defaut; route `/billing/success`; tests BillingSuccessPage. | Callback dependant de la session utilisateur et de la reconciliation webhook. |
| `pages/billing/BillingCancelPage.tsx` | UI page | `routed-page` | `route` | AppLayout sous RootLayout | Permanent tant que `STRIPE_CHECKOUT_CANCEL_URL` pointe vers `/billing/cancel`. | Config backend par defaut; route `/billing/cancel`; test BillingCancelPage. | Callback dependant du flow Stripe checkout. |
| `pages/HomePage.tsx` | UI page | removed | `delete` | LandingPage remplace l'ancienne home | Fichier supprime, sans shim ni re-export. | `rg --files frontend/src/pages -g "*.tsx"` ne liste plus `HomePage.tsx`; allowlist sans entree HomePage. | Risque faible: la landing est la route `/`. |
| `pages/landing/sections/TestimonialsSection.tsx` | UI component | `page-adjacent-component` | `reattach` | LandingPage | Permanent tant que LandingPage compose cette section. | Import et rendu dans `LandingPage`; allowlist owner `LandingPage`. | Controle par feature flag `VITE_SHOW_TESTIMONIALS`. |

## Removal contract audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `PrivacyPolicyPage.tsx` | UI page | `canonical-active` | route tree `/privacy` | `LandingLayout` | `keep` | route and App test | legal copy maintenance |
| `BillingSuccessPage.tsx` | UI page | `canonical-active` | Stripe checkout success URL | `AppLayout` | `keep` | config default plus route and tests | callback/session risk |
| `BillingCancelPage.tsx` | UI page | `canonical-active` | Stripe checkout cancel URL | `AppLayout` | `keep` | config default plus route and tests | callback/session risk |
| `HomePage.tsx` | UI page | `dead` | none | `LandingPage` | `delete` | file removed; no barrel export | none identified |
| `TestimonialsSection.tsx` | UI component | `canonical-active` | `LandingPage` import | `LandingPage` | `keep` | runtime import and feature flag | controlled by env flag |

## Route evidence after

- `frontend/src/app/routes.tsx` contient `PrivacyPolicyPage`, `BillingSuccessPage` et `BillingCancelPage` comme routes canoniques.
- `frontend/src/pages/HomePage.tsx` est supprime sans shim, alias ni re-export.
- `frontend/src/pages/landing/LandingPage.tsx` importe et rend `TestimonialsSection`.
- `frontend/src/tests/page-architecture-guards.test.ts` continue de bloquer les entrees non classees, bloquees ou mortes si elles reapparaissent.
- Aucune route de compatibilite, redirect legacy, alias, fallback ou wildcard n'est ajoute.
