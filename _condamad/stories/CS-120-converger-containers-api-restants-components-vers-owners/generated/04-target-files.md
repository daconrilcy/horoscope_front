<!-- Carte cible des fichiers et recherches pour CS-120. -->

# Target Files - CS-120

## Must Read

- `_condamad/audits/frontend-components/2026-05-09-0932/00-audit-report.md`
- `_condamad/audits/frontend-components/2026-05-09-0932/02-finding-register.md`
- `_condamad/audits/frontend-components/2026-05-09-0932/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/src/tests/component-architecture-allowlist.ts`
- `frontend/src/tests/component-architecture-guards.test.ts`
- `frontend/src/tests/component-usage-guards.test.ts`
- All old component owner files listed in `00-story.md` section 18.

## Must Search

- `rg -n "AdminGuard|B2BReconciliationPanel|EnterpriseCredentialsPanel|SupportOpsPanel|DeleteAccountModal|useDashboardAstroSummary|DashboardHoroscopeSummaryCardContainer|UpgradeHint|BottomNav|Header|Sidebar" frontend/src -g "*.ts" -g "*.tsx"`
- Targeted old-path scans from `00-story.md` section 21.
- `rg -n "apiFetch\\(|fetch\\(|axios|from [\"'](?:@api|@/api|.*\\/api|.*\\/features)" frontend/src/components -g "*.ts" -g "*.tsx"`

## Likely Modified

- `frontend/src/app/routes.tsx`
- `frontend/src/app/guards/**`
- `frontend/src/features/**`
- `frontend/src/pages/**`
- `frontend/src/layouts/**`
- `frontend/src/tests/**`
- `frontend/src/tests/component-architecture-allowlist.ts`
- `frontend/src/tests/component-architecture-guards.test.ts`

## Likely Deleted

- `frontend/src/components/AdminGuard.tsx`
- `frontend/src/components/B2BReconciliationPanel.tsx`
- `frontend/src/components/EnterpriseCredentialsPanel.tsx`
- `frontend/src/components/SupportOpsPanel.tsx`
- `frontend/src/components/dashboard/useDashboardAstroSummary.ts`
- `frontend/src/components/dashboard/DashboardHoroscopeSummaryCardContainer.tsx`
- `frontend/src/components/settings/DeleteAccountModal.tsx`
- Layout component files only if moved rather than made API-free.

## Forbidden Unless Directly Justified

- `backend/**`
- Backend API contracts and generated OpenAPI artifacts.
- `frontend/src/api/**` except type-only neutral extraction if unavoidable.
- Design-token and global style surfaces unrelated to moved files.
