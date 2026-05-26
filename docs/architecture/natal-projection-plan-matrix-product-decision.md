<!-- Commentaire global: ce rapport formalise la decision produit CS-315 pour la matrice des projections /natal sans ajouter de logique applicative. -->

# CS-315 Natal Projection Plan Matrix Product Decision

decision_id: `natal_projection_plan_matrix_product_decision_v1`
decision_date: `2026-05-26`
owner: `Product Owner B2C Projections`
status: `accepted_with_runtime_boundary`
scope: `/natal`, `free`, `basic`, `premium`, `beginner_summary_v1`, `client_interpretation_projection_v1`

## Executive Architecture Decision Summary

- `observed`: CS-309 prouve que `/natal` rend les projections selon les reponses backend et pas selon une matrice React locale. Sources: Evidence 3, Evidence 4, Evidence 6.
- `decision`: la matrice CS-309 est adoptee comme matrice produit officielle CS-315 pour `/natal`.
- `decision`: `beginner_summary_v1` est visible pour `free`, `basic` et `premium`.
- `decision`: `client_interpretation_projection_v1` est refusee avec upgrade pour `free` et `basic`, puis visible pour `premium`.
- `decision`: l'implementation source reste l'autorisation backend; React rend les succes et les 403 backend sans posseder de politique d'entitlement.
- `decision`: CS-283 reste owner de la politique B2C generale; CS-315 ajoute seulement le sign-off produit `/natal`.
- `decision`: toute divergence produit/backend devient un brief backend separe, pas une correction React locale.
- `observed`: le rapport CS-307-CS-311 recommande un brief de sign-off produit pour la matrice CS-309.
  Source: `_condamad/reports/CS-307-CS-311-delivery-report.md`, section 11.
- `blocker`: aucun finding d'audit formel `F-*` ni story candidate `SC-*` n'est fourni pour CS-315.
  La tracabilite utilise le rapport consolide, les Evidence 1-9 de la story et les artefacts CS-309.
- `open question`: le nom nominatif du product owner n'est pas fourni; le role accountable retenu est `Product Owner B2C Projections`.

Highest-risk implementation dependencies:
- conserver la frontiere backend/frontend;
- ne pas deduire de nouvelle regle Stripe/pricing;
- verifier les tests CS-309 avant tout changement futur.

## Audit Source Map

| Audit | Scope | Closure status | Key architecture inputs | Evidence IDs | Findings used | Blockers | Deferred context | Used for |
|---|---|---|---|---|---|---|---|---|
| CS-307-CS-311 report | `/natal` delivery | `Partially delivered` | CS-309 sign-off brief | section 11 action 4 | product risk | CS-307 gap | deferred QA limits | trigger |
| CS-315 story contract | Product sign-off `/natal` | `ready-to-dev`, review `CLEAN` | Owner/date, runtime source, AC1-AC7, non-goals | Evidence 1-9 | N/A | Aucun ID `F-*` fourni | Product owner name | Output contract |
| CS-309 plan matrix after | QA matrix `/natal` | After state documented | Six rows free/basic/premium by projection | Evidence 3 | N/A | Product sign-off missing before CS-315 | None | accepted_matrix |
| CS-309 ambiguity ledger | Product ambiguity | Limitation documented | UI is QA evidence, not entitlement decision | Evidence 4 | N/A | Commercial boundary was not signed off | None | backend/frontend boundary |
| CS-283 entitlement policy | B2C policy | Canonical policy exists | `b2c_projection_entitlement_policy`, plan vocabulary | Evidence 7 | N/A | CS-315 must not replace CS-283 | Quota decisions separate | registry ownership |
| Public projection registry | Projection primitives | Canonical registry exists | public/internal projection taxonomy | Evidence 8 | N/A | Public transit/fixed-star blocked separately | non-/natal primitives | projection IDs |
| Backend authorization tests | API behavior evidence | Existing test target | 403, `projection.unauthorized`, plan details | Evidence 5 | N/A | Must run for implementation evidence | None | runtime source |
| Frontend natal tests | Rendering parity evidence | Existing test target | backend-shaped success and 403 scenarios | Evidence 6 | N/A | Must not become policy owner | None | frontend surface |

Story label caveats: no audit story candidate IDs are promoted to final IDs.
CS-315 is already allocated in `_condamad/stories/story-status.md`.
Future implementation stories below use `next-available-id` unless the tracker assigns them.

Missing Evidence: no `_condamad/audits/**` bundle is cited by CS-315.
There are no source `F-*`, `SC-*` or `E-*` audit IDs beyond the CS-307-CS-311 report,
story Evidence 1-9 and guardrails `RG-022`, `RG-041`.

## Capability Matrix

| Capability / family | Inputs | Objects required | Canonical contracts required | Surfaces required | Status | Blockers | Sources |
|---|---|---|---|---|---|---|---|
| `/natal` beginner summary access | `plan_code`, chart response | `ProjectionRequest`, `ProjectionResult`, `PlanCode` | `beginner_summary_v1`, `natal_projection_plan_matrix_product_decision_v1` | backend, frontend, docs | `implemented` | None observed | Evidence 3, 5, 6 |
| `/natal` client interpretation access | `plan_code`, chart response, 403 | `ProjectionRequest`, `ProjectionResult`, `ProjectionAccessDecision` | `client_interpretation_projection_v1`, CS-283 policy | backend, frontend, docs | `partial` | Product/backend divergence must be briefed | Evidence 3, 4, 7 |
| Mixed success plus 403 rendering | backend success and forbidden responses | `FrontendProjectionState`, `UpgradeState` | backend-shaped response contract | frontend | `implemented` | No React entitlement table allowed | Evidence 3, 4, 6 |
| Product divergence handling | product vs backend behavior | `DivergenceRecord` | follow-up backend brief | docs, backlog | `implicit` | Brief mismatch | report, Evidence 4, AC5 |
| Entitlement ownership routing | plan vocabulary, projection IDs | `B2CProjectionEntitlementPolicy` | `b2c_projection_entitlement_policy` | docs, backend | `implemented` | CS-315 must not replace CS-283 | Evidence 7, 8 |

accepted_matrix:

| plan_code | beginner_summary_v1 | client_interpretation_projection_v1 | Decision source |
|---|---|---|---|
| `free` | visible from backend response | forbidden with upgrade from backend 403 | Evidence 3 |
| `basic` | visible from backend response | forbidden with upgrade from backend 403 | Evidence 3 |
| `premium` | visible from backend response | visible from backend response | Evidence 3 |

## Surface Matrix

| Surface | Current contract | Expected contract | Capabilities exposed | Consumers | Risks | Blockers | Required changes | Sources |
|---|---|---|---|---|---|---|---|---|
| internal | backend services authorize projection access | backend remains runtime source | access decisions | API handlers, tests | hidden policy drift | None observed | run backend tests | Evidence 5, 7 |
| public_api | existing projection endpoint behavior | no new route or OpenAPI surface from CS-315 | success and 403 responses | frontend | docs changing runtime by implication | None observed | app route neutrality check | Story VC13 |
| admin_debug | no CS-315 debug surface | no new admin/debug owner | none | maintainers | debug payload leakage | None observed | no change | Evidence 8 |
| automation_or_llm | not authoritative for entitlement | may consume docs as context only | none | future agents | treating generated text as policy | PO validation remains owner | cite decision doc | Skill contract |
| frontend | renders backend-shaped success/403 | no local entitlement matrix | mixed projection display | React `/natal` | React-owned access policy | Forbidden by story | run vitest and scans | Evidence 6, RG-022 |
| data_storage | no DB or migration scope | no persisted entitlement change | none | backend | accidental migration | Out of scope | no change | Story non-goals |
| observability | tests/evidence artifacts | validation transcript and source alignment | validation proof | reviewers | unproven sign-off | product owner role only | persist CS-315 evidence | Evidence 1-9 |

## Canonical Registry Decisions

### Product Matrix Registry

Decision: adopt
Owner: `Product Owner B2C Projections`

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
|---|---|---|---|---|---|---|---|
| `natal_projection_plan_matrix_product_decision` | `v1` | plan, projection ID, `/natal` | accepted/forbidden matrix | version on plan or projection semantic change | supersede with `v2`, keep CS-315 linked | decision_id, decision_date, owner, evidence IDs | Evidence 1, 3, 4 |

### Projection Registry

Decision: reuse
Owner: `docs/architecture/official-product-primitives-public-projections.md`

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
|---|---|---|---|---|---|---|---|
| `beginner_summary` | `beginner_summary_v1` | chart projection response | public beginner summary | keep ID stable across surfaces | deprecate through registry update | primitive_id, projection_id | Evidence 8 |
| `client_interpretation_projection` | `client_interpretation_projection_v1` | plan-aware projection response | public client interpretation | version on payload or depth semantics | deprecate through registry update | primitive_id, projection_id, plan_code | Evidence 8 |

### Entitlement Policy Registry

Decision: reuse
Owner: `docs/architecture/b2c-projection-entitlement-policy.md`

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
|---|---|---|---|---|---|---|---|
| `b2c_projection_entitlement_policy` | `v1` | plan, projection_id | B2C entitlement policy | policy changes require owner review | replace via policy doc, not React | policy_id, plan_code, projection_id | Evidence 7, RG-041 |

## Object / Entity Decisions

| Object | Kind | Lifecycle owner | Persistence | Serialization | Versioning | Surfaces | Decision | Sources |
|---|---|---|---|---|---|---|---|---|
| `PlanCode` | value_object | product/backend entitlement | existing runtime only | `free`, `basic`, `premium` | version matrix when semantics change | backend, frontend, docs | reuse | Evidence 3, 7 |
| `ProjectionId` | value_object | projection registry | docs and runtime responses | exact projection ID string | projection contract version suffix | API, frontend, docs | reuse | Evidence 8 |
| `ProductMatrixDecision` | core_entity | Product Owner B2C Projections | documentation artifact | markdown fields in this report | `decision_id` suffix `v1` | docs, evidence | adopt | Evidence 1, story contract |
| `ProjectionAccessDecision` | derived_object | backend authorization | runtime response/tests | success or 403 error | backend contract/version owner | API, frontend | backend owns | Evidence 5 |
| `FrontendProjectionState` | presentation_model | frontend rendering | no policy persistence | backend-shaped fixtures | follows backend/API contract | frontend | render only | Evidence 6 |
| `ValidationEvidence` | debug_artifact | CONDAMAD story evidence | `_condamad/stories/.../evidence/` | text/markdown transcript | append per story run | observability | persist | story AC7 |

## Operational Rules

| Rule area | Rule | Applies to | Invalidated by | Trace requirement | Owner | Sources |
|---|---|---|---|---|---|---|
| Versioning | Matrix changes create `natal_projection_plan_matrix_product_decision_v2`. | Product matrix | plan set, projection IDs, visible/forbidden semantics | decision_id, decision_date, owner | Product Owner B2C Projections | Evidence 1, 3 |
| Trace | Every material access decision cites Evidence 3, 5, 6 or CS-283. | docs, tests, future stories | uncited policy or runtime changes | evidence path and guardrail ID | Architecture owner | Evidence 1-9 |
| Cache | Future cache keys must include projection ID, projection version and plan when output differs by plan. | projection outputs | plan_code, projection_version, entitlement semantics | request_id, plan_code, projection_type | Backend owner | Evidence 3, 7 |
| Replay | Replays must use backend authorization state, not React fixtures. | test replay, QA | backend behavior or fixture shape drift | backend test target and fixture target | QA/backend owners | Evidence 5, 6 |
| Invalidation | Product/backend mismatch invalidates local acceptance and creates backend brief. | roadmap and docs | observed mismatch between matrix and backend tests | divergence brief path | Product and backend owners | story AC5 |
| Migration | No DB, Stripe, pricing, checkout or subscription migration is authorized by CS-315. | implementation scope | any requested runtime policy change | git/app surface status | Architecture owner | story non-goals |
| Observability | Persist CS-315 evidence. | evidence folder | missing trace | evidence files | CONDAMAD reviewer | AC7, RG-022, report |

## Blockers And Decision Owners

| Type | Item | Owner | Blocks | Decision |
|---|---|---|---|---|
| `blocker` | Product owner person is not named. | Product Owner B2C Projections | nominative sign-off only | role-level sign-off accepted for CS-315; name remains open question |
| `blocker` | No audit `F-*` or `SC-*` IDs exist for this brief-direct story. | Architecture owner | strict audit-style trace | use story Evidence 1-9 and source paths; do not invent IDs |
| `decision` | CS-309 matrix accepted as official `/natal` matrix. | Product Owner B2C Projections | implementation handoff | accepted in this report |
| `decision` | Backend authorization remains implementation source. | Backend owner | frontend work | accepted |
| `decision` | React must not own entitlement policy. | Frontend owner | UI changes | accepted |
| `open question` | Should CS-283 be revised to narrow `client_interpretation_projection_v1` minimum plan for `/natal`? | Product + backend owners | backend entitlement alignment | default: create backend brief only if tests prove divergence |

## Ordered Implementation Roadmap

### Story 1: Persist CS-315 Product Decision Evidence

Story ID: `CS-315`
Source label: CS-315 story
Goal: keep the product matrix decision, validation transcript and source alignment evidence.
Source audits: CS-307-CS-311 delivery report, CS-315 story, CS-309 evidence, CS-283 policy.
Source findings: report section 11 action 4, Evidence 1-9, RG-022, RG-041.
Scope: this document, `validation.txt`, `source-alignment.md`.
Out of scope: backend, frontend, DB, Stripe, pricing, checkout, subscription.
Dependencies: none.
Acceptance criteria:
- The decision doc names `free`, `basic`, `premium`, `beginner_summary_v1` and `client_interpretation_projection_v1`.
- The doc states `implementation_source` and `frontend_policy`.
- Evidence artifacts exist under the CS-315 evidence folder.
Validation evidence:
- `rg` checks over this document.
- PowerShell path existence checks for evidence files.
Blockers / decisions:
- product owner role is accepted; nominative owner remains an open question.
Stop condition: report and evidence are present with no runtime code changes.

### Story 2: Validate Runtime Parity Before Any Entitlement Change

Story ID: `next-available-id`
Source label: CS-315 follow-up validation
Goal: prove backend authorization and frontend rendering still match the accepted matrix.
Source audits: CS-309 evidence, backend/frontend test paths.
Source findings: Evidence 3, 5, 6.
Scope: run existing backend pytest and frontend vitest targets.
Out of scope: changing behavior.
Dependencies: Story 1.
Acceptance criteria:
- backend authorization tests pass for projection access behavior.
- frontend natal tests pass for backend-shaped success and 403 scenarios.
Validation evidence:
- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests\api\test_projection_authorization.py tests\api\test_projection_endpoint.py --tb=short`
- `pnpm --dir frontend exec node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi`
Blockers / decisions:
- any mismatch triggers Story 3.
Stop condition: parity is green or divergence brief is opened.

### Story 3: Open Backend Divergence Brief If Runtime Differs

Story ID: `next-available-id`
Source label: `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md`
Goal: route product/backend mismatch to backend ownership.
Source audits: CS-315 story AC5, CS-309 ambiguity ledger.
Source findings: Evidence 4, AC5.
Scope: create backend brief describing exact mismatch and expected owner.
Out of scope: React correction, pricing, Stripe, DB migration.
Dependencies: failed Story 2 parity.
Acceptance criteria:
- Brief names mismatching plan/projection rows.
- Brief cites backend tests and this decision document.
- No frontend policy matrix is introduced.
Validation evidence:
- path existence check for the brief.
- targeted scan confirming no React entitlement matrix.
Blockers / decisions:
- product/backend owner decision required before runtime change.
Stop condition: backend brief exists and CS-315 remains documentation-only.

### Story 4: Add Regression Guard For React-Owned Entitlement Drift

Story ID: `next-available-id`
Source label: Registry gap
Goal: prevent a local `/natal` entitlement matrix from appearing in React.
Source audits: CS-315 story, RG-022, RG-041.
Source findings: Evidence 6, story Reintroduction Guard.
Scope: targeted static guard or existing test extension.
Out of scope: modifying product policy.
Dependencies: Story 1.
Acceptance criteria:
- scan catches `accepted_matrix` or plan entitlement tables in `frontend/src`.
- frontend remains a response renderer.
Validation evidence:
- targeted `rg` or test command documented in story evidence.
Blockers / decisions:
- architecture owner decides whether to promote the registry gap to a global guardrail.
Stop condition: drift guard exists or is explicitly declined.

## Open Questions

| Question | Why it matters | Owner | Blocks | Suggested default | Sources |
|---|---|---|---|---|---|
| Who is the named product owner behind the role? | reviewer accountability | Product Owner B2C Projections | nominative sign-off | keep role until tracker supplies name | CS-315 story, report action 4 |
| Should CS-283 minimum plan text be narrowed for `/natal` client interpretation? | CS-283 currently describes broader plan-aware depth | Product + backend owners | policy harmonization | do not edit CS-283 in CS-315 | Evidence 7 |
| Should the React drift guard become global? | current guard is story-local registry gap | Architecture owner | future regression prevention | create next story only after CS-315 acceptance | RG-022, RG-041 |

## Validation Plan

| Check | Command | Expected |
|---|---|---|
| Decision fields | `rg -n "decision_id|decision_date|owner|accepted_matrix" docs/architecture/natal-projection-plan-matrix-product-decision.md` | required fields found |
| Boundary wording | `rg -n "implementation_source|frontend_policy|backend authorization" docs/architecture/natal-projection-plan-matrix-product-decision.md` | backend/frontend boundary found |
| Matrix vocabulary | `rg -n "beginner_summary_v1|client_interpretation_projection_v1|free|basic|premium" docs/architecture/natal-projection-plan-matrix-product-decision.md` | matrix terms found |
| Evidence artifacts | `Test-Path _condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt` | true |
| Source alignment | `Test-Path _condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/source-alignment.md` | true |
| Backend runtime parity | `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests\api\test_projection_authorization.py tests\api\test_projection_endpoint.py --tb=short` | required before runtime handoff |
| Frontend fixture parity | `pnpm --dir frontend exec node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi` | required before runtime handoff |

implementation_source: backend authorization and projection responses remain the implementation source for access decisions.
frontend_policy: React renders backend success and 403 responses and must not own a separate entitlement matrix.
divergence_policy: any product/backend mismatch creates `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md`.
