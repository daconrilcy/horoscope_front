# CS-108 - Decisions pages apres

Source executable apres implementation: `frontend/src/tests/page-architecture-allowlist.ts`.

## Decision summary

CS-108 ne route aucune page et ne supprime aucun fichier. Les cinq residus sont conserves uniquement avec decision explicite, owner et sortie auditable.

| Item | Type | Current classification | Decision | Owner | Expiry / next artifact | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `pages/PrivacyPolicyPage.tsx` | UI page | `needs-user-decision` | `needs-user-decision` | Legal/Product decision owner | Expire le `2026-06-30` si aucune decision legal/product nommee ne cree une route publique ou une story de retrait dediee. | Allowlist mise a jour avec `decisionSource.story`, `decisionSource.decidedOn`, `decisionSource.owner`, `decisionSource.evidence` et `expiresOn`; aucun hit dans `routes.tsx`; guard decision sourcee. | Exposition legale bloquee tant qu'une decision legal/product nommee n'existe pas. |
| `pages/billing/BillingSuccessPage.tsx` | UI page | `needs-user-decision` | `needs-user-decision` | Billing/Stripe decision owner | Expire le `2026-06-30` si aucune decision billing/Stripe nommee ne cree une route callback ou une story de retrait dediee. | Allowlist mise a jour avec `decisionSource` et `expiresOn`; aucun hit dans `routes.tsx`; tests `BillingSuccessPage` restent test-only. | Callback externe bloque tant que le contrat billing n'est pas decide. |
| `pages/billing/BillingCancelPage.tsx` | UI page | `needs-user-decision` | `needs-user-decision` | Billing/Stripe decision owner | Expire le `2026-06-30` si aucune decision billing/Stripe nommee ne cree une route callback ou une story de retrait dediee. | Allowlist mise a jour avec `decisionSource` et `expiresOn`; aucun hit dans `routes.tsx`; guard decision sourcee. | Callback externe bloque tant que le contrat billing n'est pas decide. |
| `pages/HomePage.tsx` | UI page | `dead/unmounted-page-candidate` | `keep` | Product removal decision owner | Retenue jusqu'a story de retrait dediee; aucune suppression physique dans CS-108. | Allowlist mise a jour avec `decisionSource` et `removalStory`; aucun hit dans `routes.tsx`; export barrel retire. | Surface morte conservee volontairement jusqu'au retrait dedie. |
| `pages/landing/sections/TestimonialsSection.tsx` | UI component | `dead/unmounted-page-candidate` | `keep` | Product removal decision owner | Retenue jusqu'a story de retrait dediee; aucune suppression physique dans CS-108. | Allowlist mise a jour avec `decisionSource` et `removalStory`; aucun hit dans `routes.tsx`; non rattachee a `LandingPage`. | Section non montee conservee volontairement jusqu'au retrait ou rattachement decide. |

## Removal contract audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `PrivacyPolicyPage.tsx` | UI page | `needs-user-decision` | none in route tree | public route owner or removal story after legal/product decision | `needs-user-decision` | `routes.tsx` scan zero-hit; allowlist owner/expiry exacts | legal exposure if routed early |
| `BillingSuccessPage.tsx` | UI page | `needs-user-decision` | tests only | billing callback owner or removal story after billing/Stripe decision | `needs-user-decision` | `routes.tsx` scan zero-hit; billing tests preserved | callback risk if routed early |
| `BillingCancelPage.tsx` | UI page | `needs-user-decision` | none in route tree | billing callback owner or removal story after billing/Stripe decision | `needs-user-decision` | `routes.tsx` scan zero-hit; allowlist owner/expiry exacts | callback risk if routed early |
| `HomePage.tsx` | UI page | `dead/unmounted-page-candidate` | none after CS-108; prior barrel export removed | none | `keep` pending removal story | no route hit; no barrel hit; allowlist owner/exit exacts | hidden link risk controlled by route and runtime import scan |
| `TestimonialsSection.tsx` | UI component | `dead/unmounted-page-candidate` | none in route tree or `LandingPage` | `LandingPage` only if reattached by product decision | `keep` pending removal story | no route hit; allowlist owner/exit exacts | content risk controlled by no-rattach decision |

## Route evidence after

- `frontend/src/app/routes.tsx` still contains no `PrivacyPolicyPage`, `BillingSuccessPage`, `BillingCancelPage`, `HomePage` or `TestimonialsSection`.
- `frontend/src/tests/page-architecture-guards.test.ts` rejects retained decisions without structured `decisionSource`, `expiresOn` or `removalStory`.
- `frontend/src/tests/page-architecture-guards.test.ts` rejects route-table or runtime imports for `dead/unmounted-page-candidate` entries.
- No page file was deleted.
- No public callback, redirect or compatibility route was added.
