# Story CS-245 canonical-astrology-runtime-transition: Canonical Astrology Runtime Transition Architecture
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-245-archi-canonical-astrology-runtime-transition.md`.
- Problem statement: transform CS-237 to CS-244 audit findings into a decision-ready product architecture plan.
- Source-alignment evidence: PASS; the story preserves the required folder, six files, four matrices, story remapping, and no-app-change rule.

## Objective

Create one timestamped CONDAMAD architecture folder under `_condamad/architecture/astro-canonical-runtime-transition/`.

The architecture must decide how `ChartObjectRuntimeData` and `CalculationGraph` can become canonical internal primitives across astrology product families.

## Target State

- A latest architecture folder exists under `_condamad/architecture/astro-canonical-runtime-transition/`.
- `00-architecture-plan.md` contains the transverse synthesis, decision matrices, and product architecture plan.
- `01-evidence-log.md` cites reproducible proof from CS-237 to CS-244 audits and source stories.
- `02-gap-register.md` records blockers preventing canonical runtime adoption across product families.
- `03-story-candidates.md` remaps prioritized candidate stories to available future IDs without reusing allocated labels.
- `04-risk-matrix.md` covers architecture, product, exposure, doctrine, cache, trace, replay, and narration risks.
- `05-executive-summary.md` gives a decision-ready summary for product and engineering arbitration.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-245-archi-canonical-astrology-runtime-transition.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-245`.
- Evidence 3: `_condamad/audits/astro-feature-coverage/2026-05-23-1905/05-executive-summary.md` - coverage baseline consulted.
- Evidence 4: `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919/05-executive-summary.md` - exposure baseline consulted.
- Evidence 5: `_condamad/audits/astro-chart-object-capability-payload/2026-05-23-1928/05-executive-summary.md` - object capability baseline consulted.
- Evidence 6: `_condamad/audits/astro-reference-governance/2026-05-23-1939/05-executive-summary.md` - reference governance baseline consulted.
- Evidence 7: `_condamad/audits/astro-astronomical-accuracy/2026-05-23-1950/05-executive-summary.md` - astronomy baseline consulted.
- Evidence 8: `_condamad/audits/astro-calculation-graph-readiness/2026-05-23-2000/05-executive-summary.md` - graph baseline consulted.
- Evidence 9: `_condamad/audits/astro-calculation-interpretation-boundary/2026-05-23-2013/05-executive-summary.md` - boundary baseline consulted.
- Evidence 10: `_condamad/audits/astro-product-data-needs/2026-05-23-2024/05-executive-summary.md` - product data baseline consulted.
- Evidence 11: `_condamad/stories/regression-guardrails.md` - registry consulted through the guardrail resolver for this architecture scope.
- Source-alignment review result: PASS; all mandatory questions, matrices, candidate stories, and forbidden application deltas are preserved.

## Domain Boundary

- Domain: architecture-documentation
- In scope:
  - Architecture-only synthesis of audits CS-237 to CS-244 and their source stories.
  - Product architecture decision plan for `ChartObjectRuntimeData`, `CalculationGraph`, graph families, object taxonomy, and public projections.
  - Roadmap ordering for platform prerequisites, product surfaces, temporal techniques, doctrine governance, exposure guards, astronomy proof, and narration.
  - Remapping candidate stories toward future available IDs after `CS-245`.
- Out of scope:
  - Backend app changes, backend tests, frontend UI, API routes, DB migrations, seed data, serializers, cache implementation, auth, i18n, styling, and build tooling.
  - Adding a graph family, endpoint, serializer, public payload, application cache, or calculation behavior.
- Explicit non-goals:
  - No application code change.
  - No raw exposure of `ChartObjectRuntimeData` or `chart_objects`.
  - No product, doctrine, security, or commercial decision made without a `needs-user-decision` marker.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this architecture documentation contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Produce documentation artifacts only under the scoped architecture folder.
  - Do not change runtime behavior, public payloads, database schema, API routes, tests, seed data, migrations, or frontend behavior.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the architecture cannot classify a product, doctrine, security, or exposure question from evidence.
- Additional validation rules:
  - The architecture plan must cite all eight audits CS-237 to CS-244.
  - The architecture plan must include all four mandatory matrices with every required row family, surface, object, and roadmap category.
  - The evidence log must cite concrete proof from audit files, source stories, code scans, tests, or documented absence scans.
  - Candidate stories must be remapped to future IDs without reusing CS-237 to CS-245.
  - No application files may be changed.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Runtime architecture claims must cite audits, stories, code, tests, docs, and bounded scans. |
| Baseline Snapshot | yes | The architecture folder is a persisted before/after decision baseline. |
| Ownership Routing | yes | Architecture artifacts have canonical CONDAMAD locations and must not be mixed into app code. |
| Allowlist Exception | no | No allowlist handling is authorized for this architecture-only story. |
| Contract Shape | yes | The six files, four matrices, required statuses, and candidate fields are mandatory. |
| Batch Migration | no | No migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | The story must guard against app changes while producing architecture artifacts. |
| Persistent Evidence | yes | The architecture folder and validation outputs must remain available for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The timestamped architecture folder exists. | Evidence profile: baseline_before_after_diff; `python` checks `_condamad/architecture/astro-canonical-runtime-transition`. |
| AC2 | All six architecture files exist. | Evidence profile: baseline_before_after_diff; `python` checks required filenames in the latest folder. |
| AC3 | All eight audits are cited. | Evidence profile: baseline_before_after_diff; `rg` checks `CS-237` to `CS-244` in architecture artifacts. |
| AC4 | Mandatory runtime families are covered. | Evidence profile: json_contract_shape; `AST guard`; `rg` checks graph family codes in `00-architecture-plan.md`. |
| AC5 | Canonical primitives are evaluated. | Evidence profile: baseline_before_after_diff; `AST guard`; `rg` checks `ChartObjectRuntimeData` and `CalculationGraph`. |
| AC6 | Exposure surfaces are separated. | Evidence profile: json_contract_shape; `rg` checks `Public API`, `Admin/debug`, `LLM`, `Frontend`, and `Projection`. |
| AC7 | Astrology objects are classified. | Evidence profile: json_contract_shape; `rg` checks required object groups in `00-architecture-plan.md`. |
| AC8 | The roadmap separates work categories. | Evidence profile: baseline_before_after_diff; `rg` checks platform, product, doctrine, exposure, astronomy, and narration terms. |
| AC9 | Candidate stories are remapped. | Evidence profile: baseline_before_after_diff; `rg` checks `03-story-candidates.md` for priority, stop condition, and future IDs. |
| AC10 | No application files are changed. | Evidence profile: no_legacy_contract; `python` or `git status --short` verifies only architecture artifacts changed. |

## Implementation Tasks

- [ ] Task 1: Create the latest architecture folder under `_condamad/architecture/astro-canonical-runtime-transition/`. (AC: AC1)
- [ ] Task 2: Create the six required architecture files with coherent cross-references. (AC: AC2)
- [ ] Task 3: Read and cite the eight audit folders plus CS-237 to CS-244 source stories. (AC: AC3)
- [ ] Task 4: Build the runtime family matrix with all mandatory families and allowed status values. (AC: AC4)
- [ ] Task 5: Evaluate `ChartObjectRuntimeData` and `CalculationGraph` as internal primitives, not public payloads. (AC: AC5, AC6)
- [ ] Task 6: Build the surface exposure matrix for public, internal, admin/debug, LLM, frontend, and projection concerns. (AC: AC6)
- [ ] Task 7: Build the astrology object taxonomy matrix with capabilities and decision markers. (AC: AC7)
- [ ] Task 8: Build the product architecture roadmap with separated categories and ranked story candidates. (AC: AC8, AC9)
- [ ] Task 9: Produce the gap register, risk matrix, evidence log, and executive summary from source findings. (AC: AC2, AC3, AC8)
- [ ] Task 10: Run documentary validation and verify that no application surface changed. (AC: AC1, AC2, AC10)

## Files to Inspect First

- `_story_briefs/cs-245-archi-canonical-astrology-runtime-transition.md` - source contract.
- `_condamad/audits/astro-feature-coverage/2026-05-23-1905/` - CS-237 audit evidence.
- `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919/` - CS-238 audit evidence.
- `_condamad/audits/astro-chart-object-capability-payload/2026-05-23-1928/` - CS-239 audit evidence.
- `_condamad/audits/astro-reference-governance/2026-05-23-1939/` - CS-240 audit evidence.
- `_condamad/audits/astro-astronomical-accuracy/2026-05-23-1950/` - CS-241 audit evidence.
- `_condamad/audits/astro-calculation-graph-readiness/2026-05-23-2000/` - CS-242 audit evidence.
- `_condamad/audits/astro-calculation-interpretation-boundary/2026-05-23-2013/` - CS-243 audit evidence.
- `_condamad/audits/astro-product-data-needs/2026-05-23-2024/` - CS-244 audit evidence.
- `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md` - source story.
- `_condamad/stories/CS-238-audit-runtime-surface-exposure/00-story.md` - source story.
- `_condamad/stories/CS-239-audit-chart-object-capability-payload/00-story.md` - source story.
- `_condamad/stories/CS-240-audit-reference-governance/00-story.md` - source story.
- `_condamad/stories/CS-241-audit-astronomical-accuracy/00-story.md` - source story.
- `_condamad/stories/CS-242-audit-calculation-graph-readiness/00-story.md` - source story.
- `_condamad/stories/CS-243-audit-calculation-interpretation-boundary/00-story.md` - source story.
- `_condamad/stories/CS-244-audit-product-data-needs/00-story.md` - source story.
- `backend/app/domain/astrology/**` - bounded runtime evidence source, read-only.
- `backend/tests/**/astrology/**` - bounded deterministic evidence source, read-only.

## Runtime Source of Truth

- Primary source of truth:
  - `AST guard`, generated architecture evidence, CS-237 to CS-244 audits, source stories, backend astrology code, and deterministic tests.
- Secondary evidence:
  - Targeted `rg` scans for family codes, surface names, object groups, source findings, and documented absence.
- Static scans alone are not sufficient for implemented claims because:
  - Each implemented or partially-ready statement must cite audit evidence, code, tests, generated evidence, or documented absence scans.

## Contract Shape

- Contract type:
  - CONDAMAD architecture folder.
- Fields:
  - `source_audit`: CS-237 to CS-244 audit identifier or source story identifier.
  - `decision_subject`: runtime family, surface, object group, roadmap item, gap, risk, or candidate story.
  - `current_status`: allowed family status, current owner, current exposure state, or documented absence.
  - `target_state`: canonical internal owner, projection state, decision marker, or future story route.
  - `evidence`: concrete source path, test path, code path, generated artifact, or bounded scan.
  - `blocker`: product, doctrine, security, architecture, cache, trace, replay, narration, or none.
  - `story_recommandee`: remapped future candidate ID or `none`.
- Required fields:
  - `source_audit`
  - `decision_subject`
  - `current_status`
  - `target_state`
  - `evidence`
  - `blocker`
  - `story_recommandee`
- Optional fields:
  - none
- Status codes:
  - none; this is not an API route.
- Serialization names:
  - Markdown matrix columns keep the exact French labels required by the source brief.
- Required files:
  - `00-architecture-plan.md`
  - `01-evidence-log.md`
  - `02-gap-register.md`
  - `03-story-candidates.md`
  - `04-risk-matrix.md`
  - `05-executive-summary.md`
- Matrix 1 required columns:
  - Famille, Statut actuel, Runtime canonique cible, Inputs requis, Graph requis, Objets requis, Surfaces publiques, Surfaces internes.
  - Trace/replay requis, Cache/invalidation, Blockers, Story recommandée.
- Matrix 1 required rows:
  - `natal_chart_v1`, `transit_chart_v1`, `synastry_chart_v1`, `solar_return_v1`, `lunar_return_v1`, `progressed_chart_v1`.
  - `composite_chart_v1`, `profection_v1`, `forecasting_v1`, `ai_scoring_v1`, `narrative_generation_v1`.
- Matrix 2 required columns:
  - Surface, Owner actuel, Statut cible, Public API, Admin/debug, LLM/input, Frontend, Risque d'exposition brute, Projection requise, Guard requis.
- Matrix 2 required rows:
  - `ChartObjectRuntimeData`, `chart_objects`, `CalculationGraphDefinition`, `CalculationGraphRunner`, `CalculationGraphExecutionResult`.
  - provenance, trace d'exécution, replay snapshot, graph manifest, node IO schema, fixed-star contacts, advanced planetary conditions.
  - dignities, dominance, aspects structural data, interpretation input, chart facts projection, beginner summary projection, expert technical projection.
- Matrix 3 required rows:
  - Soleil, Lune, planètes classiques, planètes modernes, ASC/MC/angles, noeuds lunaires, Lilith, apsides, parts arabes/lots.
  - astéroïdes, Chiron, midpoints, étoiles fixes.
- Matrix 4 required categories:
  - Platform prerequisites, product surfaces, temporal techniques, doctrine governance, raw exposure guards, astronomy proof, narration/AI.
- Allowed family statuses:
  - `implemented`
  - `partially-ready`
  - `reference-only`
  - `missing`
  - `blocked-by-product-decision`
  - `blocked-by-doctrine-decision`
  - `out-of-scope`
- Candidate story fields:
  - source findings, priority, primary domain, likely files to modify, files explicitly out of scope, expected validation, stop condition, user decisions.
- Minimum candidate stories to qualify:
  - Define canonical astrology graph family registry.
  - Add graph manifest and node IO schema contract for canonical runtime.
  - Add calculation graph execution trace contract.
  - Define chart object capability and object taxonomy matrix.
  - Define official product primitives and public projection roadmap.
  - Select first temporal technique implementation path.
  - Define astrology doctrine and school governance model.
  - Define AI scoring and narrative input contract from canonical runtime.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-245-archi-canonical-astrology-runtime-transition.md`
  - `_condamad/audits/astro-feature-coverage/2026-05-23-1905/`
  - `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919/`
  - `_condamad/audits/astro-chart-object-capability-payload/2026-05-23-1928/`
  - `_condamad/audits/astro-reference-governance/2026-05-23-1939/`
  - `_condamad/audits/astro-astronomical-accuracy/2026-05-23-1950/`
  - `_condamad/audits/astro-calculation-graph-readiness/2026-05-23-2000/`
  - `_condamad/audits/astro-calculation-interpretation-boundary/2026-05-23-2013/`
  - `_condamad/audits/astro-product-data-needs/2026-05-23-2024/`
- Comparison after implementation:
  - Latest child folder under `_condamad/architecture/astro-canonical-runtime-transition/`.
- Expected invariant:
  - The only intended repository delta is the new architecture folder and its six CONDAMAD architecture files.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Architecture plan | `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/00-architecture-plan.md` | `backend/app/**` |
| Evidence log | `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/01-evidence-log.md` | `backend/tests/**` |
| Gap register | `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/02-gap-register.md` | `frontend/src/**` |
| Candidate stories | `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/03-story-candidates.md` | `_condamad/stories/story-status.md` |
| Risk matrix | `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/04-risk-matrix.md` | `backend/migrations/**` |
| Executive summary | `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/05-executive-summary.md` | `docs/db_seeder/**` |

## Mandatory Reuse / DRY Constraints

- Reuse the source audit findings instead of restating the same gap with different names.
- Consolidate duplicate findings into one canonical gap with source references.
- Do not create multiple candidate stories for the same unresolved architecture decision.
- Use the same status vocabulary across the family matrix, gap register, and executive summary.
- Preserve audit IDs, story IDs, and source paths exactly for traceability.

## No Legacy / Forbidden Paths

- No legacy route path, serializer path, graph path, or public payload may be added.
- No compatibility layer may be added around `ChartObjectRuntimeData`, `chart_objects`, or `CalculationGraph`.
- No fallback public projection may be introduced for raw runtime surfaces.
- Forbidden application surfaces:
  - `backend/app/**`
  - `backend/tests/**`
  - `backend/app/tests/**`
  - `backend/migrations/**`
  - `frontend/src/**`
  - `docs/db_seeder/**`

## Reintroduction Guard

- Guard scope:
  - Application files must remain unchanged while the architecture artifacts are produced.
  - Raw runtime surfaces must remain classified as internal unless a future story carries a product/security decision.
- Deterministic guard:
  - `git status --short -- frontend/src backend/app backend/tests backend/app/tests backend/migrations docs/db_seeder`
  - `rg -n "ChartObjectRuntimeData|chart_objects|CalculationGraph" "$($archiFolder.FullName)\00-architecture-plan.md"`
- Forbidden alternate route:
  - Do not satisfy this story by implementing backend, frontend, database, serializer, cache, seed, or endpoint changes.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| Registry gap | No exact architecture-folder guardrail exists for this documentary scope. | Resolver output; targeted `rg` registry check. |
| RG-047 | Non-applicable; frontend TSX styling is out of scope. | No `frontend/src/**` delta. |
| RG-052 | Non-applicable; frontend CSS namespace migration is out of scope. | No `frontend/src/**` delta. |
| RG-041 | Non-applicable; entitlement documentation is not touched. | No `backend/docs/**` delta. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Architecture plan | `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/00-architecture-plan.md` | Keep product architecture decisions. |
| Evidence log | `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/01-evidence-log.md` | Keep reproducible source proof. |
| Gap register | `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/02-gap-register.md` | Keep blockers and unresolved decisions. |
| Story candidates | `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/03-story-candidates.md` | Keep remapped future work. |
| Risk matrix | `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/04-risk-matrix.md` | Keep risk classification. |
| Executive summary | `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/05-executive-summary.md` | Keep decision handoff. |
| Validation output | `_condamad/stories/CS-245-canonical-astrology-runtime-transition/evidence/validation.txt` | Keep story implementation validation notes. |
| Review output | `_condamad/stories/CS-245-canonical-astrology-runtime-transition/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this architecture-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/00-architecture-plan.md` - architecture plan.
- `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/01-evidence-log.md` - source proof log.
- `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/02-gap-register.md` - blockers and decision gaps.
- `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/03-story-candidates.md` - future story candidates.
- `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/04-risk-matrix.md` - architecture risk matrix.
- `_condamad/architecture/astro-canonical-runtime-transition/YYYY-MM-DD-HHMM/05-executive-summary.md` - executive summary.

Likely tests:

- Assumption risk: no new test file is expected; validation is documentary and git-scope based.
- `_condamad/stories/CS-245-canonical-astrology-runtime-transition/evidence/validation.txt` - expected validation transcript path.

Files not expected to change:

- `backend/app/**` - out of scope; no backend implementation is touched.
- `backend/tests/**` - out of scope; no test implementation is touched.
- `backend/app/tests/**` - out of scope; no app test implementation is touched.
- `backend/migrations/**` - out of scope; no migration is touched.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `docs/db_seeder/**` - out of scope; no seed or reference data artifact is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `$archiFolder = Get-ChildItem -Directory .\_condamad\architecture\astro-canonical-runtime-transition | Sort-Object Name -Descending | Select-Object -First 1`
- VC2: `rg -n "CS-237|CS-238|CS-239|CS-240|CS-241|CS-242|CS-243|CS-244" "$($archiFolder.FullName)"`
- VC3: `rg -n "ChartObjectRuntimeData|CalculationGraph|natal_chart_v1|transit_chart_v1|synastry_chart_v1|progressed_chart_v1" "$($archiFolder.FullName)\00-architecture-plan.md"`
- VC4: `rg -n "solar_return_v1|profection|forecasting|scoring|narrative" "$($archiFolder.FullName)\00-architecture-plan.md"`
- VC5: `rg -n "blocked-by-product-decision|blocked-by-doctrine-decision|partially-ready|reference-only|missing|implemented" "$($archiFolder.FullName)\00-architecture-plan.md"`
- VC6: `rg -n "Public API|Admin/debug|LLM|Frontend|Projection|Guard" "$($archiFolder.FullName)\00-architecture-plan.md"`
- VC7: `Test-Path "$($archiFolder.FullName)\00-architecture-plan.md"`
- VC8: `Test-Path "$($archiFolder.FullName)\01-evidence-log.md"`
- VC9: `Test-Path "$($archiFolder.FullName)\02-gap-register.md"`
- VC10: `Test-Path "$($archiFolder.FullName)\03-story-candidates.md"`
- VC11: `Test-Path "$($archiFolder.FullName)\04-risk-matrix.md"`
- VC12: `Test-Path "$($archiFolder.FullName)\05-executive-summary.md"`
- VC13: `git status --short -- frontend/src backend/app backend/tests backend/app/tests backend/migrations docs/db_seeder`

## Regression Risks

- The architecture could silently expose raw runtime surfaces as product APIs instead of requiring controlled projections.
- Candidate stories could reuse already allocated source labels without explicit remapping to future IDs.
- Product, doctrine, security, or commercial decisions could be treated as engineering defaults instead of `needs-user-decision`.
- The plan could blur platform prerequisites with user-facing features, making implementation order unsafe.
- A documentation-only story could drift into backend, frontend, DB, seed, serializer, cache, or test changes.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep generated architecture artifacts under the latest timestamped architecture folder only.
- Record source findings from CS-237 to CS-244 before writing conclusions.
- Use `needs-user-decision` for doctrine, product, security, exposure, and commercial questions not proven by source evidence.
- Keep line lengths readable in markdown matrices by splitting long explanations into evidence notes.

## References

- `_story_briefs/cs-245-archi-canonical-astrology-runtime-transition.md`
- `_condamad/audits/astro-feature-coverage/2026-05-23-1905/`
- `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919/`
- `_condamad/audits/astro-chart-object-capability-payload/2026-05-23-1928/`
- `_condamad/audits/astro-reference-governance/2026-05-23-1939/`
- `_condamad/audits/astro-astronomical-accuracy/2026-05-23-1950/`
- `_condamad/audits/astro-calculation-graph-readiness/2026-05-23-2000/`
- `_condamad/audits/astro-calculation-interpretation-boundary/2026-05-23-2013/`
- `_condamad/audits/astro-product-data-needs/2026-05-23-2024/`
- `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md`
- `_condamad/stories/CS-238-audit-runtime-surface-exposure/00-story.md`
- `_condamad/stories/CS-239-audit-chart-object-capability-payload/00-story.md`
- `_condamad/stories/CS-240-audit-reference-governance/00-story.md`
- `_condamad/stories/CS-241-audit-astronomical-accuracy/00-story.md`
- `_condamad/stories/CS-242-audit-calculation-graph-readiness/00-story.md`
- `_condamad/stories/CS-243-audit-calculation-interpretation-boundary/00-story.md`
- `_condamad/stories/CS-244-audit-product-data-needs/00-story.md`
