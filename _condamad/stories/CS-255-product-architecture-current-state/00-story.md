# Story CS-255 product-architecture-current-state: Document Current Product Architecture
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-255-archi-synthese-architecture-produit-en-place.md`.
- Primary delivery source: `_condamad/reports/astro-canonical-runtime-transition-CS237-CS254-delivery-report.md`.
- Architecture sources: `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/05-executive-summary.md`.
- Roadmap source: `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md`.
- Product primitive source: `docs/architecture/official-product-primitives-public-projections.md`.
- Implementation evidence source: CS-246 through CS-254 `generated/10-final-evidence.md` files.
- Problem statement: the delivered CS-237 through CS-254 architecture is proven but dispersed across reports, audits, stories, and evidence files.
- Source-alignment evidence: PASS; the story preserves synthesis, boundary, forbidden raw exposure, open decisions, and no application changes.

## Objective

Create one current-state product architecture synthesis under `docs/architecture/product-architecture-current-state.md`.

The document must explain the delivered architecture after CS-237 through CS-254 without repeating the full delivery report. It must distinguish what is in
place, what is only framed, what remains blocked by product, doctrine, security, or proof decisions, and which next stories are recommended.

## Target State

- `docs/architecture/product-architecture-current-state.md` exists and starts with a French global file comment.
- The synthesis cites the delivery report, CS-245 executive summary, CS-245 story candidates, the public primitives roadmap, and CS-246 to CS-254 evidence.
- Canonical primitives are explained: graph family registry, manifest, execution trace, taxonomy, astronomical proof, doctrine governance, temporal selection,
  and AI narrative input contract.
- Public, internal, admin/debug, and LLM-only surfaces are separated.
- `ChartObjectRuntimeData`, `chart_objects`, raw calculation graph payloads, and execution traces are never described as public API surfaces.
- Calculation, interpretation, narration, and product projections are separated with the allowed direction `calcul -> faits -> signaux -> narration/projection`.
- `natal_chart_v1` and `transit_chart_v1` are distinguished by current runtime status, selected path, and missing public exposure.
- Open decisions are preserved without artificial resolution: `fixed_star_contacts`, `astrologer_debug_data`, temporal public runtime, ephemeris proof, and doctrine governance.
- The recommended next stories are concrete actions tied to remaining decisions.
- No backend application file, frontend file, test file, migration, route, serializer, or OpenAPI contract is modified.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-255-archi-synthese-architecture-produit-en-place.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-255`.
- Evidence 3: `_condamad/reports/astro-canonical-runtime-transition-CS237-CS254-delivery-report.md` - primary delivered-state report read.
- Evidence 4: `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/05-executive-summary.md` - architecture decision source read.
- Evidence 5: `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md` - CS-246 to CS-254 mapping source read.
- Evidence 6: `docs/architecture/official-product-primitives-public-projections.md` - product primitive projection source read.
- Evidence 7: CS-246 through CS-254 `generated/10-final-evidence.md` files - implementation validation evidence read.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver and targeted ID lookup only.
- Evidence 9: `docs/architecture/product-architecture-current-state.md` - target document is currently absent and must be created.

## Domain Boundary

- Domain: documentation-architecture
- In scope:
  - Architecture synthesis document under `docs/architecture`.
  - Source-backed explanation of CS-237 through CS-254 delivered decisions, primitives, validations, limits, and next stories.
  - Documentation-only negative checks proving application surfaces remain unchanged.
- Out of scope:
  - Backend application code, backend tests, frontend source, database schema, auth, i18n, styling, build tooling, migrations, seeds, routes, serializers, and OpenAPI changes.
  - Public exposure of raw runtime surfaces.
  - Product decisions for `fixed_star_contacts`, `astrologer_debug_data`, doctrine policy, or temporal public runtime.
  - Rewriting audits, delivery reports, or final evidence files.
- Explicit non-goals:
  - No endpoint, serializer, route, API client, UI component, migration, seed, or calculator implementation.
  - No change to CS-237 through CS-254 evidence artifacts.
  - No registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a documentation-only product architecture synthesis.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only `docs/architecture/product-architecture-current-state.md` and story evidence artifacts.
  - Keep backend, frontend, tests, migrations, generated API contracts, and product runtime behavior unchanged.
  - Preserve unresolved decisions as unresolved.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the source documents contradict whether a surface is public, internal, admin/debug, or LLM-only.
- Additional validation rules:
  - The document must include the nine headings requested by the brief.
  - The delivery report must be cited as the primary implementation source.
  - CS-246 through CS-254 primitives must each be named with their role.
  - Raw runtime primitives must be described as internal or LLM-only, never public API.
  - `natal_chart_v1` and `transit_chart_v1` must have separate status language.
  - Validation must include `rg` content checks and `git status --short -- frontend/src backend/app backend/tests backend/app/tests backend/migrations`.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Final evidence files and source reports prove delivered runtime state before the synthesis claims it. |
| Baseline Snapshot | yes | Before and after evidence must prove one new document and no application surface change. |
| Ownership Routing | yes | Architecture docs and application code must remain separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this documentation-only story. |
| Contract Shape | yes | The document has required headings, source citations, primitive coverage, exposure levels, limits, and recommendations. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Raw runtime surfaces must not be reframed as public API. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The architecture synthesis document exists. | Evidence profile: baseline_before_after_diff; `python` checks `docs/architecture/product-architecture-current-state.md`. |
| AC2 | The delivery report is cited as primary source. | Evidence profile: repo_wide_negative_scan; `rg -n "CS-237|CS-254|delivery report"` on the document. |
| AC3 | Every CS-246 to CS-254 primitive role is named. | Evidence profile: json_contract_shape; `rg` checks primitive role terms. |
| AC4 | Exposure levels are separated. | Evidence profile: json_contract_shape; `rg` checks public, internal, admin/debug, LLM-only, narration, interpretation, and calcul terms. |
| AC5 | Raw runtime surfaces stay non-public. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`; `rg` checks the doc. |
| AC6 | Calculation dependency direction is explicit. | Evidence profile: ast_architecture_guard; `rg` checks `calcul -> faits -> signaux -> narration/projection`. |
| AC7 | The family status matrix is explicit. | Evidence profile: json_contract_shape; `rg` checks natal, transit, path, and exposure wording. |
| AC8 | Open decisions remain unresolved. | Evidence profile: external_usage_blocker; `rg` checks `fixed_star_contacts`, `astrologer_debug_data`, and `needs-user-decision`. |
| AC9 | Recommended next stories are concrete. | Evidence profile: baseline_before_after_diff; `rg` checks `Prochaines stories recommandées` and decision-bound action terms. |
| AC10 | Application files remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped `git status --short` output for app roots. |

## Implementation Tasks

- [ ] Task 1: Create `docs/architecture/product-architecture-current-state.md` with the required French global file comment. (AC: AC1)
- [ ] Task 2: Cite all mandatory sources and keep the delivery report as the primary source. (AC: AC2)
- [ ] Task 3: Summarize the CS-246 through CS-254 canonical primitives and their roles. (AC: AC3)
- [ ] Task 4: Separate public, internal, admin/debug, and LLM-only surfaces in a readable table or sections. (AC: AC4)
- [ ] Task 5: State that raw runtime surfaces are not public API contracts. (AC: AC5)
- [ ] Task 6: Explain the allowed dependency direction from calculation facts to narration and projection. (AC: AC6)
- [ ] Task 7: Distinguish `natal_chart_v1` runtime status from selected `transit_chart_v1` path and absent public exposure. (AC: AC7)
- [ ] Task 8: Preserve open decisions without resolving them. (AC: AC8)
- [ ] Task 9: Write concrete next story recommendations tied to remaining blockers. (AC: AC9)
- [ ] Task 10: Persist validation evidence and prove application files remain untouched. (AC: AC10)

## Files to Inspect First

- `_story_briefs/cs-255-archi-synthese-architecture-produit-en-place.md` - source contract.
- `_condamad/reports/astro-canonical-runtime-transition-CS237-CS254-delivery-report.md` - primary delivered-state report.
- `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/05-executive-summary.md` - architecture decision summary.
- `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md` - mapped CS-246 through CS-254 roadmap.
- `docs/architecture/official-product-primitives-public-projections.md` - public primitive projection source.
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/generated/10-final-evidence.md` - registry implementation evidence.
- `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/generated/10-final-evidence.md` - manifest implementation evidence.
- `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/generated/10-final-evidence.md` - trace implementation evidence.
- `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/generated/10-final-evidence.md` - taxonomy implementation evidence.
- `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/generated/10-final-evidence.md` - proof gate evidence.
- `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/generated/10-final-evidence.md` - projection roadmap evidence.
- `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/generated/10-final-evidence.md` - doctrine governance evidence.
- `_condamad/stories/CS-253-first-temporal-technique-implementation-path/generated/10-final-evidence.md` - temporal selection evidence.
- `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/generated/10-final-evidence.md` - AI narrative input evidence.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - Delivery report, CS-245 architecture artifacts, CS-246 through CS-254 final evidence files, `app.openapi()`, `app.routes`, and scoped app-root status.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/product-architecture-current-state.md`.
- Static scans alone are not sufficient for this story because:
  - Raw runtime non-exposure and application non-change must be checked with loaded app evidence and scoped app-root status.

## Contract Shape

- Contract type:
  - Markdown architecture synthesis document.
- Fields:
  - `section_heading`: one of the nine mandatory synthesis headings.
  - `source_reference`: cited source path or story evidence path.
  - `primitive_name`: canonical primitive or runtime contract name.
  - `exposure_level`: public, internal, admin/debug, LLM-only, or blocked.
  - `decision_status`: delivered, framed, selected, blocked, or `needs-user-decision`.
  - `recommended_story`: concrete next action tied to a remaining blocker.
- Required fields:
  - `section_heading`
  - `source_reference`
  - `primitive_name`
  - `exposure_level`
  - `decision_status`
  - `recommended_story`
- Required headings:
  - `Résumé exécutif`
  - `Architecture produit en place`
  - `Primitives canoniques internes`
  - `Surfaces produit et niveaux d'exposition`
  - `Frontières calcul / interprétation / narration`
  - `Familles astrologiques et statut produit`
  - `Garde-fous et validations`
  - `Limites et décisions ouvertes`
  - `Prochaines stories recommandées`
- Required source citations:
  - Delivery report CS-237 through CS-254.
  - CS-245 executive summary.
  - CS-245 story candidates.
  - Public primitive projection roadmap.
  - CS-246 through CS-254 final evidence files.
- Required primitive coverage:
  - Registry, manifest, execution trace, taxonomy, astronomical proof, doctrine governance, temporal selection, and AI narrative input.
- Optional fields:
  - none.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - none; this story writes documentation only.
- Frontend type impact:
  - none; no frontend source is touched.
- Generated contract impact:
  - none; `app.openapi()` is unchanged because no API code is touched.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/reports/astro-canonical-runtime-transition-CS237-CS254-delivery-report.md`
  - `_story_briefs/cs-255-archi-synthese-architecture-produit-en-place.md`
  - `docs/architecture/official-product-primitives-public-projections.md`
- Comparison after implementation:
  - `docs/architecture/product-architecture-current-state.md`
  - `_condamad/stories/CS-255-product-architecture-current-state/evidence/validation.txt`
  - `_condamad/stories/CS-255-product-architecture-current-state/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture synthesis document plus CONDAMAD story/evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Product architecture synthesis | `docs/architecture/product-architecture-current-state.md` | `backend/app/**` |
| Implementation evidence source | `_condamad/stories/CS-246*/generated/10-final-evidence.md` through `CS-254*` | copied app code excerpts |
| Story evidence artifacts | `_condamad/stories/CS-255-product-architecture-current-state/evidence/` | application source folders |
| Future product decisions | future CONDAMAD stories after CS-255 | this synthesis document deciding policy |

## Mandatory Reuse / DRY Constraints

- Reuse the delivery report as the primary delivery ledger instead of rebuilding a second exhaustive report.
- Reuse CS-245 and CS-251 terms for canonical primitives, product projections, and forbidden raw runtime surfaces.
- Cite CS-246 through CS-254 final evidence rather than duplicating implementation proof tables.
- Keep one architecture synthesis document for the current product state.
- Do not add external packages, scripts, API schemas, frontend helpers, or generated clients.

## No Legacy / Forbidden Paths

- No legacy route path may be added.
- No compatibility route path may be added.
- No fallback branch may expose raw runtime data.
- Do not create aliases, shims, compatibility wrappers, or parallel architecture source documents.
- Do not reframe `ChartObjectRuntimeData`, `chart_objects`, raw calculation graph payloads, or traces brutes as public API.
- Do not modify backend app code, backend tests, frontend source, migrations, serializers, routes, OpenAPI generation, or UI files.

## Reintroduction Guard

- Guard scope:
  - Raw runtime surfaces must stay internal, admin/debug, or LLM-only according to source documents.
  - Current-state claims must stay tied to CS-237 through CS-254 evidence.
  - Application roots must remain unchanged.
- Deterministic guard:
  - `rg` checks required headings, source citations, primitive names, exposure levels, dependency direction, status terms, and open decisions.
  - `git status --short -- frontend/src backend/app backend/tests backend/app/tests backend/migrations` proves no application file change.
- Forbidden alternate route:
  - Do not satisfy the story by editing backend, frontend, tests, routes, migrations, or runtime contracts.

## Regression Guardrails

Scope vector:

- documentation-architecture: yes;
- product architecture synthesis: yes;
- app source change: no;
- frontend implementation: no;
- DB/migration/auth/i18n/style/build: no;
- raw runtime public exposure: forbidden.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| Registry gap | needs-investigation | The scoped resolver returned no exact local architecture-synthesis guardrail. Use story-local `rg` and `git status` guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 frontend CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this document covers astrology product architecture.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Product architecture synthesis | `docs/architecture/product-architecture-current-state.md` | Keep the current-state product architecture document. |
| Validation output | `_condamad/stories/CS-255-product-architecture-current-state/evidence/validation.txt` | Keep content scans and story execution validation. |
| Application surface status | `_condamad/stories/CS-255-product-architecture-current-state/evidence/app-surface-status.txt` | Prove backend and frontend roots stayed untouched. |
| Source checklist | `_condamad/stories/CS-255-product-architecture-current-state/evidence/source-checklist.md` | Record mandatory source coverage. |
| Review output | `_condamad/stories/CS-255-product-architecture-current-state/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this documentation-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/product-architecture-current-state.md` - new architecture synthesis document.
- `_condamad/stories/CS-255-product-architecture-current-state/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-255-product-architecture-current-state/evidence/app-surface-status.txt` - application non-change proof.
- `_condamad/stories/CS-255-product-architecture-current-state/evidence/source-checklist.md` - source coverage evidence.

Likely tests:

- `docs/architecture/product-architecture-current-state.md` - checked by `rg` and `python` validation commands; no test file is expected to change.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/**` - out of scope; no backend application source is touched.
- `backend/tests/**` - out of scope; no backend test is touched.
- `backend/app/tests/**` - out of scope; no backend app test is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `python -c "from pathlib import Path; assert Path('docs/architecture/product-architecture-current-state.md').exists()"`
- VC3: `rg -n "CS-237|CS-254|delivery report" docs/architecture/product-architecture-current-state.md`
- VC4: `rg -n "registry|manifest|trace|taxonomy|proof|governance|temporal|AI narrative" docs/architecture/product-architecture-current-state.md`
- VC5: `rg -n "public|internal|admin/debug|LLM-only|narration|interprétation|calcul" docs/architecture/product-architecture-current-state.md`
- VC6: `rg -n "ChartObjectRuntimeData|chart_objects|traces brutes|API publique" docs/architecture/product-architecture-current-state.md`
- VC7: `rg -n "calcul -> faits -> signaux -> narration/projection" docs/architecture/product-architecture-current-state.md`
- VC8: `rg -n "natal_chart_v1|transit_chart_v1|chemin sélectionné|exposition publique" docs/architecture/product-architecture-current-state.md`
- VC9: `rg -n "fixed_star_contacts|astrologer_debug_data|needs-user-decision" docs/architecture/product-architecture-current-state.md`
- VC10: `rg -n "Prochaines stories recommandées|décision produit|décision sécurité|preuve ephemeris" docs/architecture/product-architecture-current-state.md`
- VC11: `git status --short -- frontend/src backend/app backend/tests backend/app/tests backend/migrations`
- VC12: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-255-product-architecture-current-state/evidence/validation.txt').exists()"`

Before VC2 and VC12, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The synthesis may blur delivered runtime state with future target architecture.
- Raw runtime objects may be described as public product APIs.
- `natal_chart_v1` and `transit_chart_v1` may be collapsed into one runtime status.
- Open product, security, doctrine, and proof decisions may be resolved by documentation wording instead of a user decision.
- The implementation may modify application files while trying to prove the documentation claims.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all Python commands inside the activated venv.
- Treat the delivery report as the primary source.
- Treat CS-246 through CS-254 final evidence as proof sources, not files to rewrite.
- Keep all backend, frontend, test, migration, route, serializer, OpenAPI, and UI files out of scope.
- Preserve `needs-user-decision` blockers exactly as blockers.

## References

- `_story_briefs/cs-255-archi-synthese-architecture-produit-en-place.md`
- `_condamad/reports/astro-canonical-runtime-transition-CS237-CS254-delivery-report.md`
- `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/05-executive-summary.md`
- `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/generated/10-final-evidence.md`
- `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/generated/10-final-evidence.md`
- `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/generated/10-final-evidence.md`
- `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/generated/10-final-evidence.md`
- `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/generated/10-final-evidence.md`
- `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/generated/10-final-evidence.md`
- `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/generated/10-final-evidence.md`
- `_condamad/stories/CS-253-first-temporal-technique-implementation-path/generated/10-final-evidence.md`
- `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
