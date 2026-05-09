<!-- Candidats stories issus de l'audit CONDAMAD frontend components apres CS-120. -->

# Story Candidates - frontend-components

## Candidate Summary

| Candidate | Source finding | Closure intent | Priority |
|---|---|---|---|
| none | none | none | none |

## Findings Without Implementation Candidate

### F-001

Application files: none.

Governance/test files: none.

Rationale: prior API-owning component debt is closed. Current component API/feature scan, old-path scans, component architecture/usage guards, targeted runtime suites, and lint pass.

### F-002

Application files: none.

Governance/test files: none.

Rationale: component architecture guard suite is already active and passing; exception registers are empty and exact.

### F-003

Application files: none.

Governance/test files: none.

Rationale: old component owner paths remain absent; the only config hit points to the canonical feature owner, not to `components/**`.

## Exhaustive Files To Modify

No in-domain implementation finding remains.

Application files: none.

Governance/test files: none.

Deferred non-domain context: none.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-069` - shared components must not own unclassified API/feature orchestration.
  - `RG-070` - component `@ts-nocheck` must not return without exact classification.
  - `RG-071` - `NatalInterpretation` must remain decomposed and guarded.
  - `RG-072` - component usage classification must remain exact.
  - `RG-073` - old natal component paths must not return.
  - `RG-074` - deleted test-only component surfaces must not be recreated.
- Required regression evidence for future component changes:
  - `npm run test -- component-architecture component-usage`
  - targeted old-path scans for any moved/deleted component surface
  - `npm run lint`
- Allowed differences: none for this audit.

## Recommended Next Action

No `condamad-story-writer` story is recommended from this audit. Continue with another bounded domain audit only if the product owner wants to inspect a different frontend layer, such as pages, layouts, features, or design-system CSS.
