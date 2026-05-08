# CS-098 after inventory

- canonical-owner: `frontend/src/utils/formatDate.ts`
  - `formatDate`
  - `formatDateTime`
  - `formatDateWithOptions`
- canonical-owner: `frontend/src/utils/formatPrice.ts`
  - `formatCurrencyCents`
- canonical-owner: `frontend/src/config/pricingConfig.ts`
  - `formatPrice`, conserve comme owner produit pricing public existant.
- canonical-import-consumer:
  - `AdminPricingPanel.tsx`
  - `SubscriptionGuidePage.tsx`
  - `SubscriptionSettings.tsx`
  - `AccountSettings.tsx`
  - `AdminContentPage.tsx`
  - `PersonasAdmin.tsx`
  - `AdminSamplePayloadsAdmin.tsx`
- page-specific-retained:
  - `UsageSettings.tsx` garde `getErrorMessage(error: BillingApiError | null, lang: AstrologyLang)` car le helper depend de libelles billing/settings specifiques et du type `BillingApiError`.
- Final helper scan:
  - `formatDate` definitions: owners utilitaires seulement.
  - `formatPrice` definitions: owner produit `pricingConfig.ts` seulement.
  - `getErrorMessage` definitions: retention page-specific ci-dessus.

