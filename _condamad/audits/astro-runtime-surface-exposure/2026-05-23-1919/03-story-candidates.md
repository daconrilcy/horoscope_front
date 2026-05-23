# Story Candidates - Astro Runtime Surface Exposure

## SC-001

- Source finding: F-001
- Suggested story title: CS-237 - Define public chart facts projection contract
- Suggested archetype: `api-contract-change`
- Primary domain: backend astrology public projection
- Required contracts: Runtime Source of Truth, Contract Shape, Ownership Routing, Reintroduction Guard, No Legacy
- Draft objective: define a stable `chart_facts` projection derived from `chart_objects` without exposing `ChartObjectRuntimeData`.
- Closure intent: `phased-with-map`
- Must include: selected object identity, display name, zodiac position, house facts, optional dignity/dominance summaries, optional fixed-star summary link, and explicit omission of raw payload internals.
- Validation hints: run public contract tests, OpenAPI/schema diff, `rg -n "chart_objects|ChartObjectRuntimeData" backend/app/api frontend/src backend/app/services -g "*.py" -g "*.ts" -g "*.tsx"`, and targeted JSON projection tests.
- Blockers: product must approve exact frontend fact set and whether this projection is API-visible now.

### Exhaustive Files To Modify

- Application files: exact selection rule only; public projection owner under `backend/app/services/chart/**` or service API contracts selected by story-writer, not raw domain runtime files.
- Governance/test files: public contract tests and no-raw-runtime guard tests selected by implementation story.
- Before evidence: E-005, E-007, E-008, E-014.
- After evidence required: OpenAPI/API payload excludes `ChartObjectRuntimeData`; new projection tests prove only selected facts are public.
- Reintroduction guard: no wildcard allowlist; explicit zero-hit scans for raw `chart_objects` in API/frontend payload code.
- Stop condition: F-001 public part closes when a reduced projection exists or a product decision rejects public chart facts; admin/debug remains SC-003.

## SC-002

- Source finding: F-002
- Suggested story title: CS-238 - Expose fixed star contacts through stable public projection
- Suggested archetype: `api-contract-change`
- Primary domain: backend astrology public projection
- Required contracts: Runtime Source of Truth, Contract Shape, Ownership Routing, Reintroduction Guard, No Legacy
- Draft objective: expose calculated fixed-star contacts through a stable reduced projection, not through raw `FixedStarConjunctionRuntimePayload`.
- Closure intent: `full-closure`
- Must include: target code/display, fixed-star code/display, orb, rule/source, optional categories, deterministic ordering and empty-state behavior.
- Validation hints: run fixed-star runtime tests, public JSON projection tests, OpenAPI/schema diff, and zero-hit scan for raw fixed-star runtime payload classes in public schemas.
- Blockers: product must decide whether fixed-star contacts are public by default or gated behind a feature/admin flag.

### Exhaustive Files To Modify

- Application files: exact selection rule only; projection/serializer contract selected by story-writer, with no change to `backend/app/domain/astrology/fixed_stars/**` unless a current test proves projection data missing.
- Governance/test files: public contract tests and fixed-star projection tests.
- Before evidence: E-011, E-012, E-014.
- After evidence required: public payload includes reduced contacts and excludes raw runtime payload class names.
- Reintroduction guard: no wildcard allowlist; exact scan for `FixedStarConjunctionRuntimePayload` in public API/schema code.
- Stop condition: F-002 closes when fixed-star contact exposure is either implemented as reduced projection or explicitly rejected by product decision.

## SC-003

- Source finding: F-003
- Suggested story title: CS-239 - Add debug/admin endpoint for internal calculation graph trace
- Suggested archetype: `observability-guard-hardening`
- Primary domain: protected admin/debug backend
- Required contracts: Auth/Admin Protection, Runtime Source of Truth, Contract Shape, Reintroduction Guard, No Legacy
- Draft objective: provide a protected diagnostic view of graph node execution and selected internal payload summaries without creating public runtime exposure.
- Closure intent: `blocked`
- Must include: explicit authz owner, protected route or non-HTTP artifact decision, redaction policy, request trace linkage, and no public OpenAPI exposure unless admin schema is deliberately separated.
- Validation hints: negative unauthorized tests, route/OpenAPI inventory, `rg` scans proving no public route exposes `chart_objects`, and targeted admin authorization tests.
- Blockers: blocked until admin/debug protection model is selected.

### Exhaustive Files To Modify

- Application files: none until user selects admin/debug protection. If selected, story-writer must name exact admin router/service/contract owners.
- Governance/test files: unauthorized/forbidden tests, route inventory tests, and no-public-exposure scans.
- Before evidence: E-006, E-007, E-014.
- After evidence required: protected access tests pass, public unauthenticated access fails, public payload still excludes raw runtime.
- Reintroduction guard: no wildcard route allowlist; exact route inventory for public vs admin roots.
- Stop condition: F-003 closes only when a protected diagnostic owner exists or the user rejects admin/debug exposure.

## Deferred Non-Domain Context

- Frontend rendering, auth/admin architecture, API versioning, and serializer implementation are deferred to their own stories.
- No current candidate should edit `frontend/src/**`, `backend/migrations/**`, or runtime calculators as part of this audit.

## Candidate Priority

1. SC-001 / CS-237: highest because it prevents raw `chart_objects` pressure from becoming API coupling.
2. SC-002 / CS-238: second because fixed-star contacts already have runtime and interpretation evidence.
3. SC-003 / CS-239: third and blocked because admin/debug protection must be decided before implementation.
