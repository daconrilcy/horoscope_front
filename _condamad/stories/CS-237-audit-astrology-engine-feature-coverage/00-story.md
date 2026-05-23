# Story CS-237 audit-astrology-engine-feature-coverage: Audit Astrology Engine Feature Coverage
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-237-audit-astrology-engine-feature-coverage-audit.md`.
- Main reference: `docs/recherches astro/2026-05-23-audit-calcul-theme-astral-post-cs-236.md`.
- Problem statement: produire un audit CONDAMAD de couverture fonctionnelle du moteur astrologique apres CS-236.
- Source-alignment evidence: the story preserves the requested audit folder, six standard files, matrix columns, status vocabulary, and no-app-change rule.

## Objective

Create one timestamped CONDAMAD audit folder under `_condamad/audits/astro-feature-coverage/` that classifies the astrology engine coverage.

The audit must decide which listed astrology techniques are implemented, partially implemented, reference-only, missing, or out-of-scope.

## Target State

- A latest audit folder exists under `_condamad/audits/astro-feature-coverage/`.
- `00-audit-report.md` contains the required matrix and a business conclusion ranking next recommended stories.
- `01-evidence-log.md` contains reproducible code, test, and documentation proof for every classified subject.
- `02-finding-register.md` records gaps, missing coverage, partial coverage, and product debts found by the audit.
- `03-story-candidates.md` lists prioritized implementation story candidates derived from the evidence.
- `04-risk-matrix.md` maps feature-coverage risks to user impact and technical risk.
- `05-executive-summary.md` gives a decision-ready summary for product and engineering follow-up.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-237-audit-astrology-engine-feature-coverage-audit.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-237`.
- Evidence 3: `docs/recherches astro/2026-05-23-audit-calcul-theme-astral-post-cs-236.md` - post-CS-236 astrology runtime context exists.
- Evidence 4: `backend/app/domain/astrology` - scoped inventory shows natal runtime, graph, aspects, dignity, dominance, conditions, and fixed-star surfaces.
- Evidence 5: `backend/tests/unit/domain/astrology` - scoped inventory shows astrology domain tests available for coverage evidence.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - registry consulted through the guardrail resolver for this audit scope.
- Source-alignment review result: PASS; no source concern was narrowed, deferred, or replaced by a code-change task.

## Domain Boundary

- Domain: backend-astrology-audit
- In scope:
  - Static inventory of backend astrology code, tests, seed/reference docs, and existing astrology research docs.
  - Coverage classification for every astrology technique named in the source brief.
  - Audit evidence separating calculation, reference data, runtime payload, public projection, and interpretive input.
  - Product prioritization of next stories from a complete astrology feature coverage view.
  - Required technique inventory:
    - Theme natal structurel.
    - Dignites essentielles.
    - Dignites accidentelles.
    - Conditions planetaires avancees.
    - Sect, hayz, rejoicing.
    - Parts arabes / lots.
    - Noeuds, Lilith, apsides.
    - Etoiles fixes.
    - Parans.
    - Midpoints.
    - Asteroides.
    - Chiron.
    - Transits.
    - Progressions.
    - Revolutions solaires et lunaires.
    - Synastrie.
    - Composite.
    - Profections.
    - Directions symboliques.
    - Firdaria / time lords si pertinent.
- Out of scope:
  - Frontend UI, API exposure, DB migrations, auth, i18n, styling, build tooling, and new runtime calculators.
  - Any implementation of a new astrology technique.
  - Public API changes or raw `chart_objects` exposure.
- Explicit non-goals:
  - No code change outside the audit artifacts.
  - No new endpoint, schema, projection, calculator, seed data, migration, or frontend screen.
  - No reinterpretation of source categories into a smaller audit scope.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend astrology domain audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Produce documentation artifacts only under the scoped audit folder.
  - Do not change runtime behavior, public payloads, database schema, or frontend behavior.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the audit cannot classify a required astrology technique from repository evidence.
- Additional validation rules:
  - The audit report must include every mandatory matrix column from the brief.
  - The audit report must use only the allowed status values from the brief.
  - The evidence log must map each required technique to concrete code, test, doc proof, or a documented absence scan.
  - The finding register must distinguish missing calculation, reference-only data, partial runtime coverage, and product-priority debt.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Runtime coverage claims must cite code, tests, docs, and scans proving actual backend behavior. |
| Baseline Snapshot | yes | The audit must persist a reproducible evidence baseline for post-CS-236 feature coverage. |
| Ownership Routing | yes | Audit artifacts have canonical CONDAMAD locations and must not be mixed into app code. |
| Allowlist Exception | no | No allowlist handling is authorized for a documentation-only audit. |
| Contract Shape | yes | The audit has required files, required matrix columns, and an allowed status vocabulary. |
| Batch Migration | no | No migration or multi-step conversion is in scope. |
| Reintroduction Guard | yes | The story must guard against adding app changes while producing the audit. |
| Persistent Evidence | yes | The audit folder itself is the review handoff evidence. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The timestamped audit folder exists. | Evidence profile: baseline_before_after_diff; `python` checks `_condamad/audits/astro-feature-coverage`. |
| AC2 | All six standard audit files exist. | Evidence profile: baseline_before_after_diff; `python` checks required filenames in latest audit folder. |
| AC3 | The required matrix columns are present. | Evidence profile: json_contract_shape; `rg` checks every column in `00-audit-report.md`. |
| AC4 | Every required technique is covered. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks named techniques in `00-audit-report.md`. |
| AC5 | Status values use the allowed vocabulary. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks allowed statuses in `00-audit-report.md`. |
| AC6 | Each status has concrete proof. | Evidence profile: baseline_before_after_diff; `rg` checks `01-evidence-log.md` for code, tests, docs, and absence scans. |
| AC7 | The audit separates coverage dimensions. | Evidence profile: baseline_before_after_diff; `rg` checks calculation, reference, runtime, projection, and input terms. |
| AC8 | Findings are registered. | Evidence profile: baseline_before_after_diff; `rg` checks `02-finding-register.md` for gap, missing, partial, and debt entries. |
| AC9 | Story candidates are prioritized. | Evidence profile: baseline_before_after_diff; `rg` checks `03-story-candidates.md` for priority and source-finding links. |
| AC10 | Product risks are classified. | Evidence profile: baseline_before_after_diff; `rg` checks `04-risk-matrix.md` for user impact and technical risk. |
| AC11 | The executive summary is decision-ready. | Evidence profile: baseline_before_after_diff; `rg` checks `05-executive-summary.md` for conclusion and next-story ranking. |
| AC12 | No application files are changed. | Evidence profile: no_legacy_contract; `python` or `git diff --name-only` verifies only audit artifacts changed. |

## Implementation Tasks

- [ ] Task 1: Create the latest audit folder under `_condamad/audits/astro-feature-coverage/`. (AC: AC1)
- [ ] Task 2: Create the six standard audit files with coherent cross-references. (AC: AC2)
- [ ] Task 3: Inventory backend astrology code, tests, seed/reference docs, and the post-CS-236 research document. (AC: AC4, AC6)
- [ ] Task 4: Classify every required technique with the allowed status vocabulary. (AC: AC3, AC4, AC5)
- [ ] Task 5: Document evidence for calculation, reference data, runtime payload, projection, and interpretive input coverage. (AC: AC6, AC7)
- [ ] Task 6: Register coverage gaps, partial areas, missing subjects, and product debts. (AC: AC8, AC10)
- [ ] Task 7: Prioritize next story candidates and link them to findings. (AC: AC9, AC11)
- [ ] Task 8: Run document validation and verify that no app file changed. (AC: AC1, AC2, AC12)
- [ ] Task 9: Verify the audit matrix names each required technique from the source brief explicitly. (AC: AC4)

## Files to Inspect First

- `_story_briefs/cs-237-audit-astrology-engine-feature-coverage-audit.md` - source contract.
- `docs/recherches astro/2026-05-23-audit-calcul-theme-astral-post-cs-236.md` - post-CS-236 runtime baseline.
- `backend/app/domain/astrology/**` - runtime, graph, calculators, contracts, and projections.
- `backend/tests/unit/domain/astrology/**` - deterministic domain coverage and architecture evidence.
- `backend/tests/integration/astrology/**` - integration coverage evidence.
- `backend/tests/architecture/**` - runtime boundary and public-surface guard evidence.
- `docs/db_seeder/astrology/**` - reference data coverage evidence.
- `docs/recherches astro/**` - product and research context for missing or future techniques.

## Runtime Source of Truth

- Primary source of truth:
  - `AST guard`, generated audit manifest, domain tests, integration tests, architecture tests, and source research docs.
- Secondary evidence:
  - Targeted `rg` scans proving presence, absence, reference-only data, or test coverage by technique.
- Static scans alone are not sufficient for implemented claims because:
  - Each implemented or partially implemented status must cite tests, runtime code paths, or documented runtime contracts.

## Contract Shape

- Contract type:
  - CONDAMAD domain audit folder.
- Fields:
  - `technique`: astrology technique, object, or condition name.
  - `current_status`: one allowed status value.
  - `coverage_level`: concise coverage depth summary.
  - `runtime_dependencies`: backend runtime dependencies or `none`.
  - `required_tables`: reference tables required or `none`.
  - `required_calculator`: calculator required or `none`.
  - `public_projection_required`: public projection decision.
  - `product_priority`: product priority ranking.
- Required fields:
  - `technique`
  - `current_status`
  - `coverage_level`
  - `runtime_dependencies`
  - `required_tables`
  - `required_calculator`
  - `public_projection_required`
  - `product_priority`
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
- Required matrix columns:
  - Technique / objet / condition
  - Statut actuel
  - Niveau de couverture
  - Dependances runtime
  - Tables necessaires
  - Calculateur necessaire
  - Projection publique necessaire
  - Priorite produit
- Allowed statuses:
  - `implemented`
  - `partially implemented`
  - `reference-only`
  - `missing`
  - `out-of-scope`
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-237-audit-astrology-engine-feature-coverage-audit.md`
  - `docs/recherches astro/2026-05-23-audit-calcul-theme-astral-post-cs-236.md`
- Comparison after implementation:
  - Latest child folder under `_condamad/audits/astro-feature-coverage/`.
- Expected invariant:
  - The only intended repository delta is the new audit folder and its standard CONDAMAD audit files.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Feature coverage audit | `_condamad/audits/astro-feature-coverage/` | `backend/app/**` |
| Evidence log | `_condamad/audits/astro-feature-coverage/` | `backend/tests/**` |
| Story candidates | `_condamad/audits/astro-feature-coverage/` | `_condamad/stories/**` |
| Research source | `docs/recherches astro/**` | New duplicated docs under `backend/app/**` |

## Mandatory Reuse / DRY Constraints

- Reuse the post-CS-236 research document as the primary narrative baseline.
- Reuse existing code, test, and docs evidence instead of duplicating large source excerpts into the audit.
- Use one canonical status vocabulary across report, evidence log, findings, story candidates, and summary.
- Keep technique naming consistent across all six audit files.
- Do not add external packages or custom audit tooling.

## No Legacy / Forbidden Paths

- No legacy route path may be added during this audit.
- No compatibility route path may be added during this audit.
- No fallback route path may be added during this audit.
- Do not create app-code aliases, shims, runtime fallback branches, or compatibility wrappers.
- Do not expose `chart_objects` publicly.
- Do not add API routes, database migrations, seed data, frontend screens, or calculators.

## Reintroduction Guard

- Forbidden app-code delta:
  - `backend/app/**`
  - `backend/tests/**`
  - `frontend/src/**`
  - `backend/migrations/**`
- Required guard:
  - `git diff --name-only` must show only the audit folder for implementation changes.
  - `rg -n "chart_objects" "$($auditFolder.FullName)\00-audit-report.md"` may document scope, not public exposure.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Local only as anti-drift: no API router change belongs to this audit. | `git diff --name-only`; bounded `rg`. |
| RG-003 `converge-api-v1-route-architecture` | Local only as anti-drift: no route registration or OpenAPI delta belongs to this audit. | `git diff --name-only`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Applicable pattern: validation paths in generated candidates must be concrete. | `rg` over `03-story-candidates.md`. |
| Registry gap | No exact backend astrology feature-coverage audit guardrail was present in the resolver output. | Resolver output reviewed. |

Non-applicable examples retained to prevent scope drift:

- RG-047 frontend inline styles are out of scope because no frontend files are touched.
- RG-052 frontend CSS namespace convergence is out of scope because no styling files are touched.
- RG-007 admin LLM observability routes are out of scope because this audit does not touch admin endpoints.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit report | `_condamad/audits/astro-feature-coverage/{timestamp}/00-audit-report.md` | Matrix, statuses, and business conclusion. |
| Evidence log | `_condamad/audits/astro-feature-coverage/{timestamp}/01-evidence-log.md` | Reproducible proof by technique. |
| Finding register | `_condamad/audits/astro-feature-coverage/{timestamp}/02-finding-register.md` | Gaps, missing areas, and product debts. |
| Story candidates | `_condamad/audits/astro-feature-coverage/{timestamp}/03-story-candidates.md` | Prioritized next stories. |
| Risk matrix | `_condamad/audits/astro-feature-coverage/{timestamp}/04-risk-matrix.md` | Product and technical risk classification. |
| Executive summary | `_condamad/audits/astro-feature-coverage/{timestamp}/05-executive-summary.md` | Decision summary. |
| Review output | `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this documentation-only audit.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/astro-feature-coverage/{timestamp}/00-audit-report.md` - coverage matrix and conclusion.
- `_condamad/audits/astro-feature-coverage/{timestamp}/01-evidence-log.md` - reproducible evidence.
- `_condamad/audits/astro-feature-coverage/{timestamp}/02-finding-register.md` - gaps and debts.
- `_condamad/audits/astro-feature-coverage/{timestamp}/03-story-candidates.md` - prioritized follow-up stories.
- `_condamad/audits/astro-feature-coverage/{timestamp}/04-risk-matrix.md` - risk classification.
- `_condamad/audits/astro-feature-coverage/{timestamp}/05-executive-summary.md` - decision summary.

Likely tests:

- Document validation through `condamad_domain_audit_validate.py`.
- Document lint through `condamad_domain_audit_lint.py`.
- Targeted `rg` checks against latest audit artifacts.

Files not expected to change:

- `backend/app/**` - out of scope; no backend runtime is touched.
- `backend/tests/**` - out of scope; no test code is touched.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-feature-coverage | Sort-Object Name -Descending | Select-Object -First 1`
- VC2: `rg -n "implemented|partially implemented|reference-only|missing|out-of-scope" "$($auditFolder.FullName)\00-audit-report.md"`
- VC3: `rg -n "chart_objects|natal_chart_v1|fixed|transits|synastrie|progressions" "$($auditFolder.FullName)\00-audit-report.md"`
- VC4: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py $auditFolder.FullName`
- VC5: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py $auditFolder.FullName`
- VC6: `python -c "from pathlib import Path; p=max(Path('_condamad/audits/astro-feature-coverage').iterdir()); assert (p/'00-audit-report.md').exists()"`
- VC7: `git diff --name-only`

Before VC4 and VC5, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The audit may overstate implemented coverage by treating reference tables or docs as runtime calculation.
- The audit may understate implemented coverage by missing tests under integration or architecture suites.
- The story candidate list may drift into implementation design without enough evidence links.
- A developer may accidentally change app code while producing audit artifacts.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all audit artifacts under the latest `_condamad/audits/astro-feature-coverage/` child folder.
- Treat `implemented` as requiring runtime code plus test or runtime-contract evidence.
- Treat `reference-only` as data or documentation without a proven calculator or runtime projection.
- Treat `missing` as a documented absence with bounded scans.
- Do not modify backend, frontend, migration, or API files.

## References

- `_story_briefs/cs-237-audit-astrology-engine-feature-coverage-audit.md`
- `docs/recherches astro/2026-05-23-audit-calcul-theme-astral-post-cs-236.md`
- `_condamad/stories/regression-guardrails.md`
