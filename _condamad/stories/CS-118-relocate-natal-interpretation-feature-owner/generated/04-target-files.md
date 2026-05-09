# Target Files

## Must Inspect Before Implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/audits/frontend-components/2026-05-09-0031/02-finding-register.md`
- `_condamad/audits/frontend-components/2026-05-09-0031/03-story-candidates.md`
- `_condamad/stories/CS-115-decomposer-natal-interpretation-owner/00-story.md`
- `frontend/package.json`
- `frontend/src/components/NatalInterpretation.tsx`
- `frontend/src/components/NatalInterpretation.css`
- `frontend/src/components/natal-interpretation/NatalInterpretationPersonaSelector.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationEvidence.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationMenus.tsx`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/component-architecture-guards.test.ts`
- `frontend/src/tests/component-architecture-allowlist.ts`

## Required Searches

```powershell
rg -n "NatalInterpretation|NatalInterpretationPersonaSelector|components/NatalInterpretation|natal-interpretation/NatalInterpretationPersonaSelector" frontend/src _condamad/stories/story-status.md -g "*.ts" -g "*.tsx" -g "*.md"
rg -n "components/NatalInterpretation|components/natal-interpretation/NatalInterpretationPersonaSelector" frontend/src -g "*.ts" -g "*.tsx"
rg -n "NatalInterpretation|NatalInterpretationPersonaSelector" frontend/src/tests/component-architecture-allowlist.ts
```

## Likely Modified Files

- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.css`
- `frontend/src/features/natal-chart/NatalInterpretationPersonaSelector.tsx`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/component-architecture-guards.test.ts`
- `frontend/src/tests/component-architecture-allowlist.ts`

## Likely Deleted Files

- `frontend/src/components/NatalInterpretation.tsx`
- `frontend/src/components/NatalInterpretation.css`
- `frontend/src/components/natal-interpretation/NatalInterpretationPersonaSelector.tsx`

## Evidence Files

- `_condamad/stories/CS-118-relocate-natal-interpretation-feature-owner/natal-feature-owner-before.md`
- `_condamad/stories/CS-118-relocate-natal-interpretation-feature-owner/natal-feature-owner-after.md`
- `_condamad/stories/CS-118-relocate-natal-interpretation-feature-owner/natal-feature-owner-no-shim.md`

## Forbidden Unless Directly Justified

- `backend/**`
- API contracts in `frontend/src/api/natalChart.ts`
- New dependencies or lockfile changes
- Compatibility exports under `frontend/src/components/**`
