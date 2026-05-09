# No Legacy / DRY Guardrails - CS-118

## Canonical Path

- `frontend/src/features/natal-chart/**` is the only active owner for natal
  interpretation orchestration after this story.
- Presentational, API-free child components may remain under
  `frontend/src/components/natal-interpretation/**`.

## Forbidden Active Surfaces

- `frontend/src/components/NatalInterpretation.tsx`
- `frontend/src/components/NatalInterpretation.css` when used only by the moved
  owner
- `frontend/src/components/natal-interpretation/NatalInterpretationPersonaSelector.tsx`
- `components/NatalInterpretation.tsx` allowlist entry
- `components/natal-interpretation/NatalInterpretationPersonaSelector.tsx`
  allowlist entry
- imports from `../components/NatalInterpretation` or
  `@/components/NatalInterpretation`
- compatibility wrappers, aliases, fallbacks or re-exports preserving the old
  component path

## Required Negative Evidence

```powershell
rg -n "components/NatalInterpretation|components/natal-interpretation/NatalInterpretationPersonaSelector" frontend/src -g "*.ts" -g "*.tsx"
rg -n "NatalInterpretation|NatalInterpretationPersonaSelector" frontend/src/tests/component-architecture-allowlist.ts
if (Test-Path frontend/src/components/natal-interpretation) {
  rg -n "apiFetch\\(|fetch\\(|axios|from [\"'](?:.*api|.*features)" frontend/src/components/natal-interpretation -g "*.ts" -g "*.tsx"
}
```

## DRY Requirements

- Do not duplicate natal API hooks or query logic.
- Reuse `frontend/src/api/natalChart.ts` and `frontend/src/features/astrologers`.
- Keep one `NatalInterpretationSection` implementation.
- Keep CSS in a `.css` file and do not add inline styles.

## Review Checklist

- All active consumers import the canonical feature owner.
- The old component path cannot be imported.
- The allowlist has no natal stale entry and no wildcard replacement.
- `component-architecture` protects the canonical owner and API-free
  presentational children.
- All remaining search hits are historical evidence or canonical feature
  references.
