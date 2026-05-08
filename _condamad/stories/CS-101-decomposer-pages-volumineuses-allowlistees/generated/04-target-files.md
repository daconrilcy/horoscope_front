<!-- Carte des fichiers cible CS-101. -->

# CS-101 Target Files

## Read first

- `_condamad/audits/frontend-react-pages/2026-05-08-1142/00-audit-report.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/01-evidence-log.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/02-finding-register.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/03-story-candidates.md`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- target page files and existing target tests

## Modified

- `frontend/src/pages/AstrologerProfilePage.tsx`
- `frontend/src/pages/BirthProfilePage.tsx`
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/features/astrologers/components/AstrologerProfileSections.tsx`
- `frontend/src/features/birth-profile/components/BirthProfileNatalGenerationSection.tsx`
- `frontend/src/components/settings/SubscriptionPlanGrid.tsx`
- `frontend/src/features/admin-prompts/AdminSamplePayloadsAdmin.tsx`
- `frontend/src/features/admin-prompts/AdminSamplePayloadsParts.tsx`
- CS-101 evidence files

## Inspected unchanged

- Former `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx` path, removed by the completed CS-100 prerequisite and represented by `frontend/src/features/admin-prompts/AdminSamplePayloadsAdmin.tsx`.

## Forbidden unless explicitly justified

- `backend/**`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- CSS files
- package/dependency files
