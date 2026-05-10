# Finding Register - frontend-api - 2026-05-10-1850

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | duplicate-responsibility | frontend-api | E-003,E-004 | Some requests bypass configured timeout and token-expired cleanup. | Converge backend HTTP calls under `apiFetch` or a documented wrapper. | yes |
| F-002 | High | High | duplicate-responsibility | frontend-api | E-005 | Error behavior is inconsistent and hard to guard during endpoint changes. | Add a shared response/error helper and migrate modules by domain. | yes |
| F-003 | Medium | High | missing-canonical-owner | frontend-api | E-002,E-014,E-015 | Refactors and contract changes are high-risk and hard to review. | Split large modules into domain subfolders while preserving public contracts. | yes |
| F-004 | Medium | High | dependency-direction-violation | frontend-api | E-006 | The public facade becomes a dependency of its own implementation and can hide import cycles. | Replace the import with `./client` and add a guard. | yes |
| F-005 | Medium | High | boundary-violation | frontend-api | E-007,E-008 | Ownership is blurred and future cleanup may remove or change the wrong surface. | Move composition to the feature or canonical ops owner; classify the support search endpoint. | yes |
| F-006 | Medium | Medium | needs-user-decision | frontend-api | E-009,E-010,E-014 | Dead-code cleanup and domain reorganization cannot be completed safely without an API facade policy. | Decide whether `@api` remains a global public facade or moves to domain entrypoints. | yes |

## Finding Details

### F-001 - Central transport is bypassed

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-api
- Evidence:
  - id: E-003
  - id: E-004
- Expected rule: backend HTTP calls in `frontend/src/api` use a single central transport owner for timeout, URL resolution, and auth-expiry handling.
- Actual state: Direct `fetch` calls exist outside `client.ts` in multiple backend client modules.
- Impact: Some requests bypass configured timeout and token-expired cleanup.
- Recommended action: Converge backend HTTP calls under `apiFetch` or a documented wrapper.
- Story candidate: yes
- Suggested archetype: frontend-api-transport-convergence

### F-002 - Error handling is duplicated

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-api
- Evidence:
  - id: E-005
- Expected rule: API response envelopes and transport error parsing have a canonical helper.
- Actual state: Local envelope types, parser functions, typed errors, and plain `Error` fallback paths are repeated.
- Impact: Error behavior is inconsistent and hard to guard during endpoint changes.
- Recommended action: Add a shared response/error helper and migrate modules by domain.
- Story candidate: yes
- Suggested archetype: api-error-contract-centralization

### F-003 - Large API modules own too many concerns

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-api
- Evidence:
  - id: E-002
  - id: E-014
  - id: E-015
- Expected rule: API modules separate DTO contracts, request functions, React Query hooks, and browser side effects when a domain grows.
- Actual state: `adminPrompts.ts` and `natalChart.ts` are large multi-concern modules with broad public exports.
- Impact: Refactors and contract changes are high-risk and hard to review.
- Recommended action: Split large modules into domain subfolders while preserving public contracts.
- Story candidate: yes
- Suggested archetype: namespace-convergence

### F-004 - In-domain import through public barrel

- Severity: Medium
- Confidence: High
- Category: dependency-direction-violation
- Domain: frontend-api
- Evidence:
  - id: E-006
- Expected rule: modules under `frontend/src/api` import local API dependencies through relative canonical owners, not the public `@api` facade.
- Actual state: `useDailyPrediction.ts` imports `ApiError` from `@api`.
- Impact: The public facade becomes a dependency of its own implementation and can hide import cycles.
- Recommended action: Replace the import with `./client` and add a guard.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening

### F-005 - Support module mixes support and ops persona ownership

- Severity: Medium
- Confidence: High
- Category: boundary-violation
- Domain: frontend-api
- Evidence:
  - id: E-007
  - id: E-008
- Expected rule: support API client owns support endpoints only; ops persona actions remain under the ops persona owner or feature composition.
- Actual state: `support.ts` re-exports an ops persona hook and contains a placeholder support search endpoint.
- Impact: Ownership is blurred and future cleanup may remove or change the wrong surface.
- Recommended action: Move composition to the feature or canonical ops owner; classify the support search endpoint.
- Story candidate: yes
- Suggested archetype: ownership-routing-refactor

### F-006 - Flat public API hides ownership

- Severity: Medium
- Confidence: Medium
- Category: needs-user-decision
- Domain: frontend-api
- Evidence:
  - id: E-009
  - id: E-010
  - id: E-014
- Expected rule: API files have a clear runtime owner, intentional public export contract, test-only owner, or delete-candidate classification.
- Actual state: the flat folder plus broad `index.ts` barrel makes public intent ambiguous for some B2B/Ops/guidance modules.
- Impact: Dead-code cleanup and domain reorganization cannot be completed safely without an API facade policy.
- Recommended action: Decide whether `@api` remains a global public facade or moves to domain entrypoints.
- Story candidate: yes
- Suggested archetype: namespace-convergence
