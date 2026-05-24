# Delivery Report - Astro Canonical Runtime Transition CS-237..CS-254

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-05-24 09:19:29 +02:00 |
| Repository | `C:\dev\horoscope_front` |
| Branch | `main` |
| Commit range | Not evidenced |
| Current HEAD | `a7f18163` |
| Stories covered | CS-237..CS-254 |
| Source documents | `_condamad/audits/astro-feature-coverage/2026-05-23-1905`, `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919`, `_condamad/audits/astro-chart-object-capability-payload`, `_condamad/audits/astro-reference-governance`, `_condamad/audits/astro-astronomical-accuracy`, `_condamad/audits/astro-calculation-graph-readiness`, `_condamad/audits/astro-calculation-interpretation-boundary`, `_condamad/audits/astro-product-data-needs/2026-05-23-2024`, `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155`, `docs/architecture/official-product-primitives-public-projections.md` |
| Diff source | Audit folders, architecture package, implementation story final evidence files and current repository inspection; exact commit range not evidenced |
| Validation source | Audit/architecture artifacts for CS-237..CS-245; story-time `generated/10-final-evidence.md` and review evidence for CS-246..CS-254; user-provided manual full validation `pytest -q --long` |

## 1. Executive summary

The full initiative CS-237..CS-254 is evidenced as `Delivered`: `_condamad/stories/story-status.md` marks every story in the range as `done`, CS-237..CS-244 are audit stories delivered through `_condamad/audits`, CS-245 is an architecture transition story delivered through `_condamad/architecture/astro-canonical-runtime-transition`, CS-246..CS-254 are backend implementation stories delivered through code, tests, final evidence and review artifacts, and the user-provided full validation `pytest -q --long` passed with `4350 passed, 12 skipped in 976.99s (0:16:16)`.

The report therefore separates two delivery types: audit/architecture outputs for CS-237..CS-245, and implementation outputs for CS-246..CS-254. The absence of implementation final-evidence files for CS-237..CS-245 is not treated as a delivery gap because those stories did not implement backend runtime changes.

## 2. Initial context and trigger

The trigger was the audit chain CS-237..CS-244 followed by CS-245 architecture transition planning. `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/05-executive-summary.md` states that `ChartObjectRuntimeData` and `CalculationGraph` are adopted as canonical internal primitives, raw public exposure is rejected, and future families must pass through registry, manifest/schema, trace, cache/invalidation and projection contracts before product/API/frontend use.

CS-245 mapped architecture candidates `SC-ARCH-001` to `SC-ARCH-008` into concrete story IDs CS-246..CS-254 in `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md`.

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| CS-237 | Audit astrology engine feature coverage. | `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md`; `_condamad/audits/astro-feature-coverage/2026-05-23-1905` | No application files changed. |
| CS-238 | Audit runtime surface exposure. | `_condamad/stories/CS-238-audit-runtime-surface-exposure/00-story.md`; `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919` | No endpoint, serializer or raw runtime exposure work. |
| CS-239 | Audit chart object capability payload. | `_condamad/stories/CS-239-audit-chart-object-capability-payload/00-story.md`; `_condamad/audits/astro-chart-object-capability-payload` | No runtime change. |
| CS-240 | Audit reference governance. | `_condamad/stories/CS-240-audit-reference-governance/00-story.md`; `_condamad/audits/astro-reference-governance` | No rule migration. |
| CS-241 | Audit astronomical accuracy. | `_condamad/stories/CS-241-audit-astronomical-accuracy/00-story.md`; `_condamad/audits/astro-astronomical-accuracy` | Audit only. |
| CS-242 | Audit calculation graph readiness. | `_condamad/stories/CS-242-audit-calculation-graph-readiness/00-story.md`; `_condamad/audits/astro-calculation-graph-readiness` | Audit only. |
| CS-243 | Audit calculation/interpretation boundary. | `_condamad/stories/CS-243-audit-calculation-interpretation-boundary/00-story.md`; `_condamad/audits/astro-calculation-interpretation-boundary` | Audit only. |
| CS-244 | Audit product data needs. | `_condamad/stories/CS-244-audit-product-data-needs/00-story.md`; `_condamad/audits/astro-product-data-needs/2026-05-23-2024` | No app/test/migration/seeder change during audit. |
| CS-245 | Architecture transition report. | `_condamad/stories/CS-245-canonical-astrology-runtime-transition/00-story.md`; `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155` | No implementation story generated from source labels before remap. |
| CS-246 | Define canonical astrology graph family registry. | `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/generated/10-final-evidence.md` | No API/frontend/migration exposure. |
| CS-247 | Add graph manifest and node IO schema contract. | `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/generated/10-final-evidence.md` | No public API, frontend or DB exposure. |
| CS-248 | Add calculation graph execution trace contract. | `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/generated/10-final-evidence.md` | No public execution trace or replay snapshot. |
| CS-249 | Define chart object capability and object taxonomy matrix. | `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/generated/10-final-evidence.md` | No new calculators for lots, asteroids, Chiron or midpoints. |
| CS-250 | Harden astronomical proof before public temporal runtime. | `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/generated/10-final-evidence.md` | No public temporal endpoint or frontend. |
| CS-251 | Define official product primitives and public projection roadmap. | `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/generated/10-final-evidence.md`; `docs/architecture/official-product-primitives-public-projections.md` | No route, serializer, frontend or LLM narration change. |
| CS-252 | Define astrology doctrine and school governance model. | `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/generated/10-final-evidence.md` | No seed, migration, serializer or frontend change. |
| CS-253 | Select first temporal technique implementation path. | `_condamad/stories/CS-253-first-temporal-technique-implementation-path/generated/10-final-evidence.md` | No executable public temporal runtime. |
| CS-254 | Define AI scoring and narrative input contract. | `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/generated/10-final-evidence.md` | No provider integration or public API surface. |

## 4. Delivery summary

### Audit and architecture delivery

CS-237 delivered the feature coverage audit under `_condamad/audits/astro-feature-coverage/2026-05-23-1905`, identifying natal runtime strengths and predictive/non-planetary gaps.

CS-238 delivered the runtime surface exposure audit under `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919`, rejecting raw public exposure of internal runtime surfaces.

CS-239 to CS-244 delivered the remaining audit set under `_condamad/audits`: chart object capability payload, reference governance, astronomical accuracy, calculation graph readiness, calculation/interpretation boundary, and product data needs.

CS-245 delivered the architecture transition package under `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155`, remapping audit findings into CS-246..CS-254.

### Backend implementation delivery

CS-246 added the canonical graph-family registry in `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`, declaring mandatory family codes and explicit blockers for non-natal families.

CS-247 added graph manifest and validation ownership through `calculation_graph_manifest.py` and `calculation_graph_manifest_validator.py`, deriving the natal manifest from the existing graph definition rather than duplicating node lists.

CS-248 added internal execution trace ownership via `calculation_graph_execution_trace.py` and runner integration in `calculation_graph_runner.py`, with trace redaction of raw input/output values.

CS-249 added `chart_object_capability_taxonomy.py` as the canonical matrix owner for object family capability and taxonomy decisions.

CS-250 added `astronomical_proof.py`, sensitive golden cases, ephemeris trace evidence and public temporal runtime gate tests before CS-253 can be treated as public-ready.

CS-251 produced the canonical public projection roadmap in `docs/architecture/official-product-primitives-public-projections.md`, naming `structured_facts`, `beginner_summary`, `expert_technical_projection`, `fixed_star_contacts`, `astrologer_debug_data` and `llm_input`, while keeping raw runtime surfaces internal or LLM-only.

CS-252 added `astrology_doctrine_governance.py` and architecture guardrails for rule family ownership, doctrine ownership and unresolved decisions.

CS-253 added `temporal_technique_selection.py`, selecting `transit_chart_v1` as the first temporal path while keeping rejected candidates explicit and no public runtime surface exposed.

CS-254 added `ai_narrative_input_contracts.py` and `ai_narrative_input_builder.py`, separating structural facts, interpretive signals, masking policy, source versions and projection links from prompt/provider integration.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| CS-237 | Feature coverage audit identifies implemented, partial, reference-only and missing astrology capabilities. | `astro-feature-coverage/2026-05-23-1905/00-audit-report.md` | Audit matrix and finding register list predictive gaps and non-planetary object gaps. | `story-status.md` row is `done`; audit folder exists; editorial review `generated/11-code-review.md` is `CLEAN`. | Delivered |
| CS-238 | Raw runtime surfaces are classified and raw public exposure rejected. | `astro-runtime-surface-exposure/2026-05-23-1919/00-audit-report.md` | Exposure matrix classifies `chart_objects`, advanced conditions and other runtime surfaces. | `story-status.md` row is `done`; audit folder exists; editorial review is `CLEAN`. | Delivered |
| CS-239 | Chart-object capability/payload audit maps capabilities, producers and consumers. | `_condamad/audits/astro-chart-object-capability-payload` | Audit artifacts and story ACs require active object/capability inventory. | `story-status.md` row is `done`; audit folder exists; editorial review is `CLEAN`. | Delivered |
| CS-240 | Reference governance audit classifies source ownership and hardcoded rule families. | `_condamad/audits/astro-reference-governance` | Audit artifacts feed CS-252 governance model. | `story-status.md` row is `done`; audit folder exists; editorial review is `CLEAN`. | Delivered |
| CS-241 | Astronomical accuracy audit defines proof gaps before temporal runtime. | `_condamad/audits/astro-astronomical-accuracy`; CS-250 final evidence | Audit findings feed CS-250 proof hardening. | `story-status.md` row is `done`; audit folder exists; CS-250 validation PASS closes the downstream hardening path. | Delivered |
| CS-242 | Calculation graph readiness audit feeds registry, manifest and trace stories. | `_condamad/audits/astro-calculation-graph-readiness`; CS-245 candidates | Audit findings feed CS-246, CS-247 and CS-248. | `story-status.md` row is `done`; audit folder exists; CS-246..CS-248 validation PASS. | Delivered |
| CS-243 | Calculation/interpretation boundary audit feeds AI narrative input contract. | `_condamad/audits/astro-calculation-interpretation-boundary`; CS-254 story | Audit findings feed CS-254 boundary contract. | `story-status.md` row is `done`; audit folder exists; CS-254 validation PASS and review `CLEAN`. | Delivered |
| CS-244 | Product data needs audit feeds public projection roadmap. | `astro-product-data-needs/2026-05-23-2024`; `official-product-primitives-public-projections.md` | Audit findings feed CS-251 public primitive roadmap. | `story-status.md` row is `done`; audit folder exists; CS-251 validation PASS and review `CLEAN`. | Delivered |
| CS-245 | Architecture transition maps audits to implementation stories. | `astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md` | CS-246..CS-254 match remapped candidate sequence. | `story-status.md` row is `done`; architecture review `06-architecture-review.md` and summary say PASS after correction. | Delivered |
| CS-246 | Registry declares mandatory graph families and blocks non-ready families. | CS-245 `SC-ARCH-001` | `astrology_graph_family_registry.py`, registry tests. | Targeted pytest 23 passed; `backend\tests` 881 passed, 201 deselected; `ruff check backend` PASS. | Delivered |
| CS-247 | Manifest/node IO schemas and comparison are explicit. | CS-245 `SC-ARCH-002` | `calculation_graph_manifest.py`, validator, natal manifest tests. | Targeted 26 passed; full tests 897 passed, 201 deselected after review fix; `ruff check .` PASS; review `CLEAN`. | Delivered |
| CS-248 | Execution trace contract is internal, ordered and redacted. | CS-245 `SC-ARCH-003` | `calculation_graph_execution_trace.py`, runner hook. | Targeted 23 passed; `backend\tests` 904 passed, 201 deselected; API/OpenAPI assertions PASS. | Delivered |
| CS-249 | Capability taxonomy has one owner and unresolved families are blocked. | CS-245 `SC-ARCH-004` | `chart_object_capability_taxonomy.py`. | Targeted 21 passed; `backend\tests` 913 passed, 201 deselected; negative scans PASS. | Delivered |
| CS-250 | Astronomical proof gate hardens temporal readiness. | CS-245 `SC-ARCH-006A` | `astronomical_proof.py`, golden cases, temporal gate. | Targeted proof suite PASS; 22 passed guard suite; full backend pytest 3201 passed, 1 skipped, 1182 deselected. | Delivered |
| CS-251 | Product primitives are official and raw surfaces remain internal. | CS-245 `SC-ARCH-005`; CS-244 findings | `docs/architecture/official-product-primitives-public-projections.md`, public contract guards. | Targeted 17 passed, 3 deselected; full pytest 3159 passed, 1 skipped, 1182 deselected; review `CLEAN`. | Delivered |
| CS-252 | Doctrine/rule ownership and blockers are governed. | CS-245 `SC-ARCH-007`; CS-240 findings | `astrology_doctrine_governance.py`, governance guards. | Targeted 24 passed; `backend\tests` 945 passed, 201 deselected; API neutrality PASS. | Delivered |
| CS-253 | First temporal path is selected without public runtime exposure. | CS-245 `SC-ARCH-006`; CS-250 gate | `temporal_technique_selection.py`, single-path guard. | Unit 7 passed; architecture 4 passed; API neutrality 14 passed; full backend 3228 passed, 1 skipped, 1182 deselected; review `CLEAN`. | Delivered |
| CS-254 | AI scoring/narrative input is structured, versioned and provider-neutral. | CS-245 `SC-ARCH-008`; CS-243/CS-244 findings | `ai_narrative_input_contracts.py`, `ai_narrative_input_builder.py`. | Targeted 53 passed after review fix; full backend 3236 passed, 1 skipped, 1182 deselected; `ruff check .` PASS; review `CLEAN`. | Delivered |

## 6. Evidence of completion

### Code evidence

- `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`: canonical graph-family registry and explicit unknown/duplicate rejection for CS-246.
- `backend/app/domain/astrology/runtime/calculation_graph_manifest.py` and `calculation_graph_manifest_validator.py`: canonical graph manifest/schema and validation for CS-247.
- `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py` and `calculation_graph_runner.py`: internal execution trace and runner attachment for CS-248.
- `backend/app/domain/astrology/runtime/chart_object_capability_taxonomy.py`: object capability/taxonomy matrix owner for CS-249.
- `backend/app/domain/astrology/runtime/astronomical_proof.py`: production astronomical proof manifest, tolerance owner and ephemeris trace for CS-250.
- `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`: doctrine/rule source governance owner for CS-252.
- `backend/app/domain/astrology/runtime/temporal_technique_selection.py`: selected `transit_chart_v1` temporal path and explicit rejected candidates for CS-253.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` and `ai_narrative_input_builder.py`: provider-neutral AI narrative input contract and builder for CS-254.

### Test evidence

- `backend/tests/unit/domain/astrology/test_astrology_graph_family_registry.py`: CS-246 registry shape, blockers and lookup behavior.
- `backend/tests/unit/domain/astrology/test_calculation_graph_manifest.py` and `test_natal_calculation_graph_manifest.py`: CS-247 manifest schema, validation and comparison behavior.
- `backend/tests/unit/domain/astrology/test_calculation_graph_execution_trace.py` and `test_calculation_graph_runner.py`: CS-248 trace contract, errors, cache redaction and runner behavior.
- `backend/tests/unit/domain/astrology/test_chart_object_capability_taxonomy.py`: CS-249 taxonomy rows and explicit unresolved decisions.
- `backend/tests/unit/domain/astrology/test_astronomical_proof.py` and `test_astronomical_golden_cases.py`: CS-250 proof, trace, tolerance and sensitive cases.
- `backend/tests/unit/domain/astrology/test_astrology_doctrine_governance.py`: CS-252 source owner and doctrine governance rules.
- `backend/tests/unit/domain/astrology/test_temporal_technique_selection.py`: CS-253 selection, rejection and CS-250 gate behavior.
- `backend/tests/unit/domain/astrology/interpretation/test_ai_narrative_input_contract.py`: CS-254 contract version, sections, masking and projection links.
- Architecture guards: `test_api_contract_neutrality.py`, `test_chart_runtime_surface_guardrails.py`, `test_astrology_doctrine_governance_guardrails.py`, `test_temporal_family_single_path.py`, `test_temporal_public_runtime_gate.py`, `test_ai_narrative_input_boundary.py`.

### Documentation evidence

- `_condamad/audits/astro-feature-coverage/2026-05-23-1905`: CS-237 audit output.
- `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919`: CS-238 audit output.
- `_condamad/audits/astro-chart-object-capability-payload`: CS-239 audit output.
- `_condamad/audits/astro-reference-governance`: CS-240 audit output.
- `_condamad/audits/astro-astronomical-accuracy`: CS-241 audit output.
- `_condamad/audits/astro-calculation-graph-readiness`: CS-242 audit output.
- `_condamad/audits/astro-calculation-interpretation-boundary`: CS-243 audit output.
- `_condamad/audits/astro-product-data-needs/2026-05-23-2024`: CS-244 audit output.
- `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/05-executive-summary.md`: architecture decision summary and implementation gate.
- `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md`: remapped roadmap from `SC-ARCH-*` to CS-246..CS-254.
- `docs/architecture/official-product-primitives-public-projections.md`: official public primitive roadmap and raw surface exclusions.

### Operational evidence

- CS-237..CS-244 are marked `done` in `_condamad/stories/story-status.md` and have audit artifacts under `_condamad/audits`.
- CS-245 is marked `done` in `_condamad/stories/story-status.md` and has architecture artifacts under `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155`.
- CS-246..CS-254 `generated/10-final-evidence.md` files record activated-venv Python validation commands and results.
- User-provided manual validation: `pytest -q --long` passed with `4350 passed, 12 skipped in 976.99s (0:16:16)`.
- CS-247, CS-251, CS-253 and CS-254 have `generated/11-code-review.md` review evidence with `CLEAN` verdicts.
- Current report-time `git status --short` shows the user-updated `_condamad/stories/story-status.md` and this untracked reports folder.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| CS-246 final evidence | targeted/full suite | PASS | `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/generated/10-final-evidence.md` | `ruff check backend`; targeted 23 passed; backend tests 881 passed, 201 deselected. |
| CS-247 final evidence | targeted/full suite | PASS | `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/generated/10-final-evidence.md` | Targeted 26 passed, later 22 passed after fix; full backend tests 897 passed, 201 deselected; review `CLEAN`. |
| CS-248 final evidence | targeted/full suite | PASS | `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/generated/10-final-evidence.md` | Targeted 23 passed; backend tests 904 passed, 201 deselected. |
| CS-249 final evidence | targeted/full suite | PASS | `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/generated/10-final-evidence.md` | Targeted 21 passed; backend tests 913 passed, 201 deselected. |
| CS-250 final evidence | targeted/full suite | PASS | `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/generated/10-final-evidence.md` | Full backend pytest 3201 passed, 1 skipped, 1182 deselected. |
| CS-251 final evidence | targeted/full suite | PASS | `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/generated/10-final-evidence.md` | Targeted 17 passed, 3 deselected; full pytest 3159 passed, 1 skipped, 1182 deselected; review `CLEAN`. |
| CS-252 final evidence | targeted/full suite | PASS | `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/generated/10-final-evidence.md` | Targeted 24 passed; backend tests 945 passed, 201 deselected. |
| CS-253 final evidence | targeted/full suite | PASS | `_condamad/stories/CS-253-first-temporal-technique-implementation-path/generated/10-final-evidence.md` | Full backend 3228 passed, 1 skipped, 1182 deselected; review `CLEAN`. |
| CS-254 final evidence | targeted/full suite | PASS | `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/generated/10-final-evidence.md` | Targeted 53 passed; full backend 3236 passed, 1 skipped, 1182 deselected; `ruff check .` PASS; review `CLEAN`. |
| User-provided manual full validation | full suite | PASS | `pytest -q --long`: `4350 passed, 12 skipped in 976.99s (0:16:16)` | Command reported by user after manual execution; not rerun by Codex. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- CS-237..CS-245 are audit/architecture stories, not backend implementation stories; their expected delivery artifacts are the `_condamad/audits` and `_condamad/architecture` outputs.

### Known limits

- Codex did not rerun `ruff`, `pytest`, app startup or frontend checks while editing this report; full-suite pytest evidence is user-provided manual output.
- CS-246..CS-254 final evidence often mentions dirty worktree context during story execution; report-time `git status --short` is clean, but exact commit range is not evidenced.
- Full backend pytest counts differ across stories because each was run at a different point in the transition sequence.

### Assumptions

- Audit folders under `_condamad/audits/astro-*` are treated as the realized CS-237..CS-244 audit outputs because the user identified those stories as completed audit work and CS-245 cites them as source-of-truth audit bundles.
- Architecture folder `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155` is treated as the CS-245 delivery artifact because it contains the plan, evidence log, gap register, story candidates, risk matrix, executive summary and architecture review.

## 9. Residual risks

- Fixed-star public/gated/rejected policy remains unresolved: `docs/architecture/official-product-primitives-public-projections.md` marks `fixed_star_contacts` as `needs-user-decision`, blocking CS-257 public exposure.
- Debug/astrologer product surface remains unresolved: `astrologer_debug_data` requires audience/auth/retention decisions before API/frontend work.
- Temporal runtime is selected but not publicly implemented: CS-253 selects `transit_chart_v1` and proves no public route/OpenAPI/frontend exposure.
- External ephemeris deployment risk remains: CS-250 records use of `pyswisseph` Moshier integrated data when no external ephemeris bootstrap path exists.
- Governance strictness risk remains: CS-252 notes future existing-domain files with rule markers must be classified in `GOVERNED_RULE_SOURCE_SURFACES`.

## 10. Evidence gaps

- Exact commit range for the delivered initiative is not evidenced.
- Manual validation output is user-provided and not backed by a persisted log file in this report.

## 11. Recommended next actions

1. Product decision: choose `fixed_star_contacts` policy (`public`, `gated` or `rejected`) before CS-257.
2. Product/security decision: define whether `astrologer_debug_data` is a protected operator/admin surface, an astrologer workflow surface, or out of scope.
3. Draft CS-255 and CS-256 from `docs/architecture/official-product-primitives-public-projections.md` for expert technical projection and beginner summary.
4. Before public temporal runtime implementation, keep CS-250 proof artifacts and CS-253 no-public-surface guardrails in the required validation plan.

## 12. Final delivery status

`Delivered`

CS-237..CS-244 are delivered audit stories with outputs under `_condamad/audits`; CS-245 is a delivered architecture transition story with outputs under `_condamad/architecture/astro-canonical-runtime-transition`; CS-246..CS-254 are delivered backend implementation stories with code, tests, architecture guards, lint and review evidence.
