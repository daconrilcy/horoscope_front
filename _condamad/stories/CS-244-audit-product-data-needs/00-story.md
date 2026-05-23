# Story CS-244 audit-product-data-needs: Audit Product Data Needs
Status: ready-to-dev

## Trigger / Source

- Source type: audit-to-story with repository-informed boundary.
- Source reference: `_story_briefs/cs-244-audit-product-data-needs-audit.md`.
- Related context: CS-237 to CS-243 created audit-ready contracts for astrology coverage, runtime exposure, chart objects, references, accuracy, graph readiness, and boundaries.
- Problem statement: produce a CONDAMAD audit that starts from astrology product screens and classifies the data each screen needs before exposing internal surfaces.
- Source-alignment evidence: PASS; the story preserves the requested audit folder, six standard files, matrix, target screens, and CS-255 to CS-257.

## Objective

Create one timestamped CONDAMAD audit folder under `_condamad/audits/astro-product-data-needs/`.

The audit must map every target screen to required data, existence, public exposure, stability, projection, translation, score, and complexity masking needs.

## Target State

- A latest audit folder exists under `_condamad/audits/astro-product-data-needs/`.
- `00-audit-report.md` contains the mandatory matrix and a data-needs section for every target screen.
- `01-evidence-log.md` contains reproducible proof for frontend screens, API clients, backend projections, runtime data, translations, scores, and absence scans.
- `02-finding-register.md` lists missing data, non-exposable internal data, unstable contracts, ambiguous needs, and recommended closure route.
- `03-story-candidates.md` qualifies CS-255, CS-256, and CS-257 with priority, source finding, validation evidence, and stop condition.
- `04-risk-matrix.md` maps product, contract, frontend, public projection, translation, score, and complexity risks.
- `05-executive-summary.md` gives a decision-ready summary for beginner, expert, astrologer, debug, AI interpretation, PDF, and public-user needs.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-244-audit-product-data-needs-audit.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-244`.
- Evidence 3: `_condamad/stories/CS-243-audit-calculation-interpretation-boundary/00-story.md` - sibling audit story shape consulted.
- Evidence 4: `backend/app/domain/astrology` - scoped backend astrology domain root exists for audit evidence.
- Evidence 5: `backend/app/services` - scoped service root exists for projection and product data evidence.
- Evidence 6: `frontend/src/pages` - scoped frontend page root exists for screen-driven evidence.
- Evidence 7: `frontend/src/api` - scoped frontend API client root exists for public projection evidence.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through the guardrail resolver for this audit scope.
- Source-alignment review result: PASS; no source concern was narrowed, deferred, or replaced by implementation work.

## Domain Boundary

- Domain: astrology-product-data-audit
- In scope:
  - Documentation-only audit of data needs for the target astrology product screens.
  - Screen-first inventory for the source brief screens from simple natal chart through public-user UI.
  - Mapping of each required datum to existence, public exposure, stability, dedicated projection, translation, score, and complexity masking.
  - Identification of data that exists internally but must not be exposed raw to the frontend.
  - Qualification of candidate stories CS-255, CS-256, and CS-257.
- Out of scope:
  - Frontend UI changes, API endpoint creation, serializers, DB migrations, auth, i18n implementation, styling, build tooling, and production configuration changes.
  - Modifying projections, runtime calculators, translators, scorers, serializers, public payloads, tests, or routes.
- Explicit non-goals:
  - No frontend route, screen, component, CSS, client generation, or UI validation.
  - No endpoint, serializer, schema, seed, migration, runtime calculator, score engine, translation file, or PDF renderer change.
  - No replacement of implementation work for CS-255, CS-256, or CS-257.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this screen-first astrology product data needs audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Produce documentation artifacts only under the scoped audit folder.
  - Do not change frontend screens, API endpoints, serializers, projections, translators, scorers, PDF output, runtime logic, tests, routes, or database schema.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: repository evidence cannot classify a required screen, datum, public exposure status, or projection owner.
- Additional validation rules:
  - The audit report must include every mandatory matrix column from the source brief.
  - The audit report must include every target screen from the source brief.
  - The evidence log must cite frontend files, backend files, tests, docs, generated evidence, or bounded absence scans for every screen.
  - Beginner, expert, astrologer, debug, AI interpretation, PDF, and public-user needs must be separated.
  - Story candidates CS-255, CS-256, and CS-257 must include source-finding links, validation evidence, and stop conditions.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Data-need claims must cite source files, tests, docs, frontend clients, backend projections, and scans proving actual surfaces. |
| Baseline Snapshot | yes | The audit must persist a reproducible baseline for screen, data, projection, translation, score, and masking evidence. |
| Ownership Routing | yes | Audit artifacts have canonical CONDAMAD locations and must not be mixed into app code or test suites. |
| Allowlist Exception | no | No allowlist handling is authorized for this documentation-only audit. |
| Contract Shape | yes | The audit has required files, required matrix columns, target screens, findings, risks, and candidate stories. |
| Batch Migration | no | No migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | The story must guard against implementing frontend, endpoint, serializer, projection, translation, score, or PDF changes while auditing. |
| Persistent Evidence | yes | The audit folder itself is the review handoff evidence. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The timestamped audit folder exists. | Evidence profile: baseline_before_after_diff; `python` checks `_condamad/audits/astro-product-data-needs`. |
| AC2 | All six standard audit files exist. | Evidence profile: baseline_before_after_diff; `python` checks required filenames in the latest audit folder. |
| AC3 | The mandatory matrix columns are present. | Evidence profile: json_contract_shape; `rg` checks each column in `00-audit-report.md`. |
| AC4 | Every target screen is covered. | Evidence profile: baseline_before_after_diff; `rg` checks all target screen labels in `00-audit-report.md`. |
| AC5 | Beginner needs are separated. | Evidence profile: baseline_before_after_diff; `rg` checks beginner and public-user terms in audit artifacts. |
| AC6 | Expert needs are separated. | Evidence profile: baseline_before_after_diff; `rg` checks expert and astrologer terms in audit artifacts. |
| AC7 | Debug needs are separated. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py`. |
| AC8 | Non-exposable internal data is registered. | Evidence profile: no_legacy_contract; `rg` checks non-exposable and internal terms in `02-finding-register.md`. |
| AC9 | Projection recommendations are documented. | Evidence profile: json_contract_shape; `pytest -q backend/app/tests/unit/test_chart_result_service.py`. |
| AC10 | Translation needs are documented. | Evidence profile: baseline_before_after_diff; `pytest -q backend/app/tests/unit/test_astrology_translation_resolver.py`. |
| AC11 | Score needs are documented. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py`. |
| AC12 | Complexity masking is documented. | Evidence profile: baseline_before_after_diff; `rg` checks complexity masking terms in `00-audit-report.md`. |
| AC13 | Candidate stories are qualified. | Evidence profile: baseline_before_after_diff; `rg` checks `03-story-candidates.md` for CS-255, CS-256, and CS-257. |
| AC14 | Audit validation commands pass. | Evidence profile: baseline_before_after_diff; `python` runs the CONDAMAD audit validator. |
| AC15 | No application files are changed. | Evidence profile: no_legacy_contract; `python` or `git diff --name-only` verifies only audit artifacts changed. |

## Implementation Tasks

- [ ] Task 1: Create the latest audit folder under `_condamad/audits/astro-product-data-needs/`. (AC: AC1)
- [ ] Task 2: Create the six standard audit files with coherent cross-references. (AC: AC2)
- [ ] Task 3: Build the mandatory matrix with every required column. (AC: AC3)
- [ ] Task 4: Cover all target screens from simple natal chart through public-user UI. (AC: AC4)
- [ ] Task 5: Separate beginner, expert, astrologer, debug, AI interpretation, PDF, and public-user needs. (AC: AC5, AC6, AC7)
- [ ] Task 6: Map required data to existence, public exposure, stability, projection, translation, score, and masking decisions. (AC: AC8, AC9, AC10, AC11, AC12)
- [ ] Task 7: Register missing data, non-exposable internal data, unstable contracts, and ambiguous needs. (AC: AC8)
- [ ] Task 8: Qualify CS-255, CS-256, and CS-257 with priority, source finding, validation evidence, and stop condition. (AC: AC13)
- [ ] Task 9: Run document validation and verify that no app, test, migration, config, or frontend file changed. (AC: AC1, AC2, AC14, AC15)

## Files to Inspect First

- `_story_briefs/cs-244-audit-product-data-needs-audit.md` - source contract.
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md` - public natal projection predecessor.
- `_condamad/stories/CS-202-natal-expert-panel/00-story.md` - expert natal panel predecessor.
- `_condamad/stories/CS-207-traditional-advanced-final-audit-documentation/00-story.md` - traditional analysis audit predecessor.
- `_condamad/stories/CS-222-fixed-star-conjunction-runtime-from-chart-objects/00-story.md` - fixed-star runtime predecessor.
- `_condamad/stories/CS-243-audit-calculation-interpretation-boundary/00-story.md` - sibling audit story shape.
- `frontend/src/pages` - page-level product screens and screen entry points.
- `frontend/src/features/natal-chart` - natal chart expert and interpretation components.
- `frontend/src/api/natalChart.ts` - public natal API client.
- `frontend/src/api/natal-chart` - generated or structured natal API client surface.
- `frontend/src/types/astrology.ts` - frontend astrology data types.
- `backend/app/api/v1/routers` - public API routes that may expose astrology data.
- `backend/app/services` - service layer that may build public projections.
- `backend/app/domain/astrology` - canonical astrology runtime and data owners.
- `backend/app/domain/llm` - AI interpretation and LLM contract surfaces.
- `backend/app/tests/unit/test_chart_result_service.py` - persisted natal payload evidence.
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py` - runtime exposure guard.
- `backend/tests/architecture/test_astrology_runtime_boundary.py` - astrology runtime boundary guard.

## Runtime Source of Truth

- Primary source of truth:
  - `AST guard`, generated audit manifest, frontend source files, API clients, Python source files, unit tests, architecture tests, and docs.
- Secondary evidence:
  - Targeted `rg` scans proving screen terms, projection terms, public payload terms, translation terms, score terms, and complexity masking terms.
- Static scans alone are not sufficient for screen-to-data claims because:
  - Each claim must cite source files, tests, generated audit evidence, documented absence scans, or deterministic architecture guards.

## Contract Shape

- Contract type:
  - CONDAMAD product data needs audit folder.
- Fields:
  - `Écran`: one target screen from the source brief.
  - `Donnée nécessaire`: the datum needed by that screen.
  - `Existe`: yes, no, partial, or unknown with evidence.
  - `Publique`: public, internal-only, mixed, or unknown with evidence.
  - `Stable`: stable, unstable, inferred, or unknown with evidence.
  - `Projection dédiée`: recommended projection owner or `none`.
  - `Traduction`: required translation owner or `none`.
  - `Score`: required score owner or `none`.
  - `Complexité à masquer`: explicit masking rule or `none`.
  - `Story recommandée`: CS-255, CS-256, CS-257, later, blocked, or none.
- Required fields:
  - `Écran`
  - `Donnée nécessaire`
  - `Existe`
  - `Publique`
  - `Stable`
  - `Projection dédiée`
  - `Traduction`
  - `Score`
  - `Complexité à masquer`
  - `Story recommandée`
- Optional fields:
  - none
- Status codes:
  - none; this is not an API route.
- Serialization names:
  - Markdown matrix columns keep the exact French labels from the source brief.
- Required files:
  - `00-audit-report.md`
  - `01-evidence-log.md`
  - `02-finding-register.md`
  - `03-story-candidates.md`
  - `04-risk-matrix.md`
  - `05-executive-summary.md`
- Required target screens:
  - `thème natal simple`
  - `thème expert`
  - `debug astrologique`
  - `analyse de dominantes`
  - `analyse des aspects`
  - `analyse traditionnelle`
  - `analyse des étoiles fixes`
  - `interprétation IA`
  - `export PDF`
  - `interface astrologue`
  - `interface utilisateur grand public`
- Required candidate stories:
  - `CS-255`
  - `CS-256`
  - `CS-257`
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-244-audit-product-data-needs-audit.md`
  - `frontend/src/pages`
  - `frontend/src/features/natal-chart`
  - `frontend/src/api`
  - `frontend/src/types`
  - `backend/app/api/v1/routers`
  - `backend/app/services`
  - `backend/app/domain/astrology`
  - `backend/app/domain/llm`
  - `backend/tests/architecture`
- Comparison after implementation:
  - Latest child folder under `_condamad/audits/astro-product-data-needs/`.
- Expected invariant:
  - The only intended repository delta is the new audit folder and its standard CONDAMAD audit files.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Product data needs audit | `_condamad/audits/astro-product-data-needs/` | `frontend/src/**` |
| Evidence log | `_condamad/audits/astro-product-data-needs/` | `backend/tests/**` |
| Finding register | `_condamad/audits/astro-product-data-needs/` | Runtime, serializer, projection, or UI files |
| Story candidates | `_condamad/audits/astro-product-data-needs/` | `_condamad/stories/**` |
| Product recommendations | `_condamad/audits/astro-product-data-needs/` | API, serializer, projection, translator, or scorer code |

## Mandatory Reuse / DRY Constraints

- Reuse the source brief screens, matrix columns, questions, expected validations, and candidate story IDs as the audit contract.
- Reuse existing code, tests, docs, prior story evidence, and architecture guards instead of duplicating large source excerpts.
- Use one canonical screen vocabulary across report, evidence log, findings, candidates, risk matrix, and summary.
- Use one canonical decision vocabulary for existence, public exposure, stability, projection, translation, score, and masking.
- Do not add external packages or custom audit tooling.

## No Legacy / Forbidden Paths

- No legacy route path may be added during this audit.
- No compatibility route path may be added during this audit.
- No fallback route path may be added during this audit.
- Do not create app-code aliases, shims, runtime fallback branches, or compatibility wrappers.
- Do not modify frontend screens, API clients, endpoints, serializers, projections, translators, scorers, PDF output, tests, seeds, or migrations.
- Do not expose internal data only because it already exists.
- Do not treat raw runtime internals as stable public product projections.

## Reintroduction Guard

- Forbidden app-code delta:
  - `frontend/src/**`
  - `backend/app/**`
  - `backend/tests/**`
  - `backend/app/tests/**`
  - `backend/migrations/**`
  - `docs/db_seeder/**`
- Required guard:
  - `git diff --name-only` must show only the audit folder for implementation changes.
  - `rg` must prove screen needs and data exposure decisions are documented in audit artifacts, not implemented in frontend or backend files.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| Registry gap | No exact product data needs audit guardrail was present in the resolver output. | Resolver output reviewed. |
| Local no-app-delta guard | The audit must not change frontend, API, serializer, projection, score, or translation code. | `git diff --name-only`; bounded `rg`. |

Non-applicable examples retained to prevent scope drift:

- RG-047 frontend inline styles are out of scope because no frontend files are modified.
- RG-052 frontend CSS namespace convergence is out of scope because no styling files are modified.
- RG-041 entitlement documentation is out of scope because astrology product data needs are audited.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit report | `_condamad/audits/astro-product-data-needs/{timestamp}/00-audit-report.md` | Matrix and needs by screen. |
| Evidence log | `_condamad/audits/astro-product-data-needs/{timestamp}/01-evidence-log.md` | Reproducible proof by screen and datum. |
| Finding register | `_condamad/audits/astro-product-data-needs/{timestamp}/02-finding-register.md` | Missing, non-exposable, unstable, or ambiguous data. |
| Story candidates | `_condamad/audits/astro-product-data-needs/{timestamp}/03-story-candidates.md` | Prioritized CS-255 through CS-257. |
| Risk matrix | `_condamad/audits/astro-product-data-needs/{timestamp}/04-risk-matrix.md` | Product, contract, frontend, and complexity risks. |
| Executive summary | `_condamad/audits/astro-product-data-needs/{timestamp}/05-executive-summary.md` | Decision summary. |
| Review output | `_condamad/stories/CS-244-audit-product-data-needs/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this documentation-only audit.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/astro-product-data-needs/{timestamp}/00-audit-report.md` - matrix and needs by screen.
- `_condamad/audits/astro-product-data-needs/{timestamp}/01-evidence-log.md` - reproducible evidence.
- `_condamad/audits/astro-product-data-needs/{timestamp}/02-finding-register.md` - missing, non-exposable, unstable, or ambiguous data.
- `_condamad/audits/astro-product-data-needs/{timestamp}/03-story-candidates.md` - prioritized CS-255 through CS-257.
- `_condamad/audits/astro-product-data-needs/{timestamp}/04-risk-matrix.md` - risk classification.
- `_condamad/audits/astro-product-data-needs/{timestamp}/05-executive-summary.md` - decision summary.

Likely tests:

- Document validation through `condamad_domain_audit_validate.py`.
- Document lint through `condamad_domain_audit_lint.py`.
- Targeted `rg` checks against latest audit artifacts.
- `pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py` for runtime surface evidence.
- `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py` for astrology boundary evidence.
- `pytest -q backend/app/tests/unit/test_chart_result_service.py` for public projection evidence.
- `pytest -q backend/app/tests/unit/test_astrology_translation_resolver.py` for translation evidence.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/**` - out of scope; no backend runtime is touched.
- `backend/tests/**` - out of scope; no test code is touched.
- `backend/app/tests/**` - out of scope; no app-local tests are touched.
- `backend/migrations/**` - out of scope; no database migration is touched.
- `docs/db_seeder/**` - out of scope; no seed or reference data is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-product-data-needs | Sort-Object Name -Descending | Select-Object -First 1`
- VC2: `rg -n "thème natal|expert|debug|dominantes|aspects|étoiles fixes|PDF|frontend|projection" "$($auditFolder.FullName)\00-audit-report.md"`
- VC3: `rg -n "Existe|Publique|Stable|Projection dédiée|Traduction|Score|Complexité à masquer" "$($auditFolder.FullName)\00-audit-report.md"`
- VC4: `rg -n "débutant|expert|astrologue|debug|interprétation IA|export PDF|grand public" "$($auditFolder.FullName)\00-audit-report.md"`
- VC5: `rg -n "non exposable|interne|projection publique|traduction|score|masquer" "$($auditFolder.FullName)\02-finding-register.md"`
- VC6: `rg -n "CS-255|CS-256|CS-257" "$($auditFolder.FullName)\03-story-candidates.md"`
- VC7: `pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py`
- VC8: `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py`
- VC9: `pytest -q backend/app/tests/unit/test_chart_result_service.py`
- VC10: `pytest -q backend/app/tests/unit/test_astrology_translation_resolver.py`
- VC11: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py $auditFolder.FullName`
- VC12: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py $auditFolder.FullName`
- VC13: `python -c "from pathlib import Path; p=max(Path('_condamad/audits/astro-product-data-needs').iterdir()); assert (p/'00-audit-report.md').exists()"`
- VC14: `git diff --name-only`

Before VC7, VC8, VC9, VC10, VC11, VC12, and VC13, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The audit may expose raw internal runtime data because the field already exists.
- Beginner, expert, astrologer, debug, AI, PDF, and public-user needs may be merged into one unclear product contract.
- A screen may receive a projection recommendation without proving the required datum exists.
- Translation, score, or complexity masking needs may be skipped for a screen that displays astrological meaning.
- Candidate stories may drift into implementation design without evidence links or stop conditions.
- A developer may accidentally change app code, tests, config, serializers, projections, or frontend files while producing audit artifacts.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all audit artifacts under the latest `_condamad/audits/astro-product-data-needs/` child folder.
- Start from product screens before classifying backend data, projections, translations, scores, and complexity masking.
- Treat internal data, public projection data, translated labels, scores, and simplified display data as separate concerns.
- Do not modify frontend, backend, migration, seed, serializer, projection, translator, scorer, PDF, route, or test files.

## References

- `_story_briefs/cs-244-audit-product-data-needs-audit.md`
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md`
- `_condamad/stories/CS-202-natal-expert-panel/00-story.md`
- `_condamad/stories/CS-207-traditional-advanced-final-audit-documentation/00-story.md`
- `_condamad/stories/CS-222-fixed-star-conjunction-runtime-from-chart-objects/00-story.md`
- `_condamad/stories/CS-243-audit-calculation-interpretation-boundary/00-story.md`
- `frontend/src/pages`
- `frontend/src/features/natal-chart`
- `frontend/src/api`
- `frontend/src/types/astrology.ts`
- `backend/app/api/v1/routers`
- `backend/app/services`
- `backend/app/domain/astrology`
- `backend/app/domain/llm`
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`
- `backend/tests/architecture/test_astrology_runtime_boundary.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `backend/app/tests/unit/test_astrology_translation_resolver.py`
- `_condamad/stories/regression-guardrails.md`
