# Audit Archetypes

Each archetype audits one bounded domain. Findings must stay within the selected boundary unless they prove an inbound or outbound dependency violation.

## api-adapter-boundary-audit

Use for: `backend/app/api`, `backend/app/api/v1`, FastAPI routers, HTTP adapters.

Audit must verify:

- API remains an HTTP adapter layer.
- API does not own business decisions.
- API does not duplicate service/domain logic.
- API errors are centralized.
- Routes map to runtime OpenAPI.
- Services do not depend on `app.api`.
- Historical facades are identified.
- Router ownership matches HTTP roots.

Required evidence:

- `rg` dependency scans
- runtime OpenAPI or route table when available
- router inclusion inventory
- tests/guards inventory

Forbidden findings:

- findings about unrelated frontend views without API evidence
- broad backend architecture claims without route or import proof

Expected contracts:

- `api-adapter-audit-contract.md`
- `no-legacy-dry-audit-contract.md`

Common story candidates:

- `api-adapter-boundary-convergence`
- `legacy-facade-removal`
- `api-error-contract-centralization`
- `route-architecture-convergence`

## domain-purity-audit

Use for: `backend/app/domain`, business invariants, entities, value objects, policy concepts.

Required evidence: framework import scan, infra dependency scan, rule ownership inventory, test inventory.
Forbidden findings: API route concerns without dependency proof.
Expected contracts: `domain-purity-audit-contract.md`, `no-legacy-dry-audit-contract.md`.
Story candidate archetypes: `domain-purity-convergence`, `duplicate-rule-removal`, `architecture-guard-hardening`.

## service-boundary-audit

Use for: `backend/app/services`, use-case orchestration, application services.

Required evidence: API import scan, HTTP type scan, repository/port usage inventory, duplicated policy scan.
Forbidden findings: domain purity claims without service evidence.
Expected contracts: `service-boundary-audit-contract.md`, `no-legacy-dry-audit-contract.md`.
Story candidate archetypes: `service-boundary-refactor`, `duplicate-rule-removal`, `architecture-guard-hardening`.

## auth-security-audit

Use for: login, token/session flows, password handling, auth guards, auth dependencies.

Required evidence: auth entrypoint inventory, negative authorization tests, secret handling scans, OWASP ASVS control mapping.
Forbidden findings: speculative vulnerability claims without source or test evidence.
Expected contracts: `auth-security-audit-contract.md`.
Story candidate archetypes: `auth-guard-hardening`, `security-test-coverage`, `secret-handling-convergence`.

## entitlement-policy-audit

Use for: entitlements, permissions, policy decisions, review/approval states, policy mutation.

Required evidence: policy owner inventory, bypass scans, mutation lifecycle trace, audit trail evidence, negative tests.
Forbidden findings: product policy changes without explicit user decision.
Expected contracts: `entitlement-policy-audit-contract.md`, `no-legacy-dry-audit-contract.md`.
Story candidate archetypes: `entitlement-policy-convergence`, `policy-bypass-guard`, `mutation-audit-trail-hardening`.

## legacy-surface-audit

Use for: old routes, aliases, shims, fallbacks, wrappers, re-exports, compatibility code.

Required evidence: targeted symbol scans, runtime route inventory if route related, canonical replacement evidence.
Forbidden findings: removal recommendations without canonical owner or blocker classification.
Expected contracts: `no-legacy-dry-audit-contract.md`.
Story candidate archetypes: `legacy-facade-removal`, `namespace-convergence`, `dead-code-removal`.

## dependency-direction-audit

Use for: imports crossing API/domain/service/infra boundaries.

Required evidence: import scans, dependency graph snippets, inspected source paths.
Forbidden findings: style-only import preferences.
Expected contracts: domain-specific boundary contract.
Story candidate archetypes: `architecture-guard-hardening`, `service-boundary-refactor`, `ownership-routing-refactor`.

## contract-shape-audit

Use for: API payloads, DTOs, OpenAPI, generated clients, response/error shape.

Required evidence: runtime OpenAPI, DTO/schema source, client usage inventory, tests.
Forbidden findings: behavior claims without runtime or schema evidence.
Expected contracts: `api-adapter-audit-contract.md`.
Story candidate archetypes: `api-contract-change`, `runtime-contract-preservation`.

## runtime-route-audit

Use for: route table, included routers, deprecated endpoints, OpenAPI route drift.

Required evidence: runtime route table or OpenAPI, router inclusion inventory, route tests.
Forbidden findings: source-only route drift claims when runtime evidence is available but skipped without reason.
Expected contracts: `api-adapter-audit-contract.md`.
Story candidate archetypes: `route-architecture-convergence`, `legacy-facade-removal`.

## test-guard-coverage-audit

Use for: architecture guards, negative tests, regression coverage.

Required evidence: test inventory, guard inventory, missing-path scans.
Forbidden findings: broad quality claims without named risks.
Expected contracts: `report-output-contract.md`.
Story candidate archetypes: `test-guard-hardening`, `architecture-guard-hardening`.

## data-model-boundary-audit

Use for: SQLAlchemy models, migrations, repositories, persistence ownership.

Required evidence: model inventory, migration inventory, repository usage scans, direct DB access scans.
Forbidden findings: DB schema change recommendations without migration evidence.
Expected contracts: service or infra boundary contract.
Story candidate archetypes: `data-model-boundary-convergence`, `repository-ownership-refactor`.

## observability-audit

Use for: logs, metrics, traces, audit events, mutation observability.

Required evidence: signal inventory, error path scan, audit trail checks.
Forbidden findings: generic logging requests without operational risk.
Expected contracts: domain-specific contract.
Story candidate archetypes: `observability-guard-hardening`, `audit-trail-coverage`.
