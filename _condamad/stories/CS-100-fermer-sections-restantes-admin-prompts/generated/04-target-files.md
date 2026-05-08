# Target Files - CS-100

## Must read

- `_condamad/audits/frontend-react-pages/2026-05-08-1142/00-audit-report.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/01-evidence-log.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/02-finding-register.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/03-story-candidates.md`
- `_condamad/stories/CS-096-decomposer-responsabilites-restantes-admin-prompts/admin-prompts-after.md`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/features/admin-prompts/**`
- `frontend/src/api/adminPrompts.ts`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/AdminPromptsPage.test.tsx`
- `frontend/src/tests/AdminPromptsRouting.test.tsx`
- `frontend/src/tests/AdminPromptsCatalogFlow.test.tsx`

## Likely modified

- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/features/admin-prompts/**`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `_condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/admin-prompts-before.md`
- `_condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/admin-prompts-after.md`
- `_condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/generated/**`

## Forbidden unless explicitly justified

- `backend/**`
- `frontend/src/api/adminPrompts.ts`
- unrelated frontend pages or global styles

## Required searches

- `rg -n "@ts-nocheck|@ts-ignore|apiFetch\\(" frontend/src/pages/admin/AdminPromptsPage.tsx frontend/src/features/admin-prompts -g "*.tsx"`
- `rg -n "pages/admin/AdminPromptsPage.tsx" frontend/src/tests/page-architecture-allowlist.ts`
- `rg -n "remaining-next-slice|duplicate-active" _condamad/stories/CS-100-fermer-sections-restantes-admin-prompts`
