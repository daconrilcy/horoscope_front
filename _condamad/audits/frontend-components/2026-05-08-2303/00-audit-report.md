<!-- Rapport d'audit CONDAMAD du domaine frontend components. -->

# Audit Report - frontend-components

## Scope

- Domain key: `frontend-components`
- Audit date: `2026-05-08-2303`
- Archetype: `dependency-direction-audit` plus `legacy-surface-audit`, `test-guard-coverage-audit`, and mandatory `no-legacy-dry-audit-contract`.
- Mode: read-only for application code; audit artifacts written under `_condamad/audits/**`.
- Audited surface: `frontend/src/components/**`.

## Expected Responsibility

`frontend/src/components` should remain a reusable component layer. Shared primitives and composed components may own rendering, local UI state, accessibility states, and CSS module ownership, but durable API orchestration, page-specific workflow decisions, feature ownership, and TypeScript suppression should be isolated, classified, or guarded.

## Prior History Consulted

- `_condamad/audits/frontend-design-system/2026-05-08-0054`: design-system findings closed; relevant guardrails `RG-044` through `RG-063`.
- `_condamad/audits/frontend-react-pages/2026-05-08-1323`: page architecture findings closed; relevant guardrails `RG-064` through `RG-067`.
- `_condamad/audits/frontend-layouts/2026-05-08-2227`: layout findings closed; relevant guardrail `RG-068`.
- `_condamad/stories/regression-guardrails.md`: consulted before findings. Applicable invariants: `RG-047`, `RG-048`, `RG-049`, `RG-050`, `RG-056`, `RG-057`, `RG-064`, `RG-067`, `RG-068`.

## Closure Ledger

| Prior finding | Classification | Current evidence | Guardrail |
|---|---|---|---|
| frontend-design-system 2026-05-08-0054 F-001 | `still-closed` | E-006, E-007 | RG-044 to RG-063 |
| frontend-design-system 2026-05-08-0054 F-002 | `still-closed` | E-006, E-007 | RG-047, RG-048, RG-049, RG-050 |
| frontend-design-system 2026-05-08-0054 F-003 | `still-closed` | E-006, E-007 | RG-061, RG-062, RG-063 |
| frontend-react-pages 2026-05-08-1323 F-001 | `non-domain` | E-002, E-004 | RG-064 to RG-067 cover pages only, not components |
| frontend-layouts 2026-05-08-2227 active findings | `still-closed` | E-002, E-007 | RG-068 |

## Executive Finding Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 2 |
| Medium | 2 |
| Low | 0 |
| Info | 1 |

## Main Conclusion

Domain closure status: `phased-with-map`.

The styling guardrails for `frontend/src/components` are active and passing, so no new CSS fallback, inline-style, or legacy vocabulary finding is emitted. The active risks are architectural: several components still act as API/feature containers, four component files keep `@ts-nocheck` outside the page guardrails, and the component inventory has files with no runtime consumer outside tests or only a barrel export. `NatalInterpretation.tsx` is the largest concrete closure slice and combines API orchestration, feature composition, entitlement decisions, formatting, modal state, and rendering in one component file.

## Active Implementation Findings

See `02-finding-register.md` for details.

Top risks:

1. `F-001`: shared components own API and feature orchestration, making the component layer a second feature/page owner.
2. `F-002`: `@ts-nocheck` remains active in component files without a component-domain guard.
3. `F-003`: `NatalInterpretation.tsx` and its CSS are oversized and concentrate multiple responsibilities.
4. `F-005`: multiple component files have no runtime reference outside tests, or are only barrel-exported without a direct runtime consumer. The supporting inventory is static and must be rechecked symbol/import-aware before deletion.

## Exhaustive Active Surface

Application files with pending implementation work are listed in `03-story-candidates.md`.

Governance/test files with pending implementation work:

- `frontend/src/tests/component-architecture-allowlist.ts` or equivalent new exact allowlist.
- `frontend/src/tests/component-architecture-guards.test.ts` or equivalent guard added to the existing architecture suite.

Deferred non-domain context:

- Page route ownership remains covered by `frontend-react-pages`.
- Layout hierarchy remains covered by `frontend-layouts`.
- Broader CSS token governance remains covered by `frontend-design-system`.

## Validation

Executed successfully:

- `npm run test -- components design-system inline-style legacy-style`
- `npm run lint`
- `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py _condamad/audits/frontend-components/2026-05-08-2303 --explain-audit`
- `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py _condamad/audits/frontend-components/2026-05-08-2303`
