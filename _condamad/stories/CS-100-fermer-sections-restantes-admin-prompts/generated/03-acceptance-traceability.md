# Acceptance Traceability - CS-100

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Before inventory identifies residual sections. | `admin-prompts-before.md` capture line-count, exception et sections CS-096. | `rg -n "catalog\|consumption\|release" _condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/admin-prompts-before.md`. | PASS |
| AC2 | Each extracted section has one canonical owner. | `frontend/src/features/admin-prompts/AdminPromptsRoute.tsx` owns catalog, consumption and release active surfaces. | `rg -n "extracted-owner-path" _condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/admin-prompts-after.md`. | PASS |
| AC3 | Page no longer implements extracted sections locally. | `AdminPromptsPage.tsx` is an 81-line route shell/container without catalog/consumption/release section JSX. | `rg -n "duplicate-active: none" _condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/admin-prompts-after.md`. | PASS |
| AC4 | API access remains routed through API owner. | `frontend/src/api/adminPrompts.ts` unchanged; feature route uses existing hooks/contracts. | `npm run test -- page-architecture` included in targeted run; scan `apiFetch(` cible zero hit outside API owner. | PASS |
| AC5 | Page-size governance is closed for AdminPrompts. | AdminPrompts entry removed from `PAGE_SIZE_EXCEPTIONS`. | `npm run test -- page-architecture` included in targeted run; allowlist scan zero hit. | PASS |
| AC6 | AdminPrompts visible behavior is preserved. | Route entry delegates to moved feature owner. | `npm run test -- AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow page-architecture` passed. | PASS |
| AC7 | No page architecture bypass is introduced. | No TS bypass, direct page API call or duplicate local section introduced. | `npm run test -- page-architecture` included in targeted run; forbidden scans zero hit. | PASS |
