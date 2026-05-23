# Story CS-238 audit-runtime-surface-exposure: Audit Runtime Surface Exposure
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-238-audit-runtime-surface-exposure-audit.md`.
- Problem statement: produire un audit CONDAMAD des surfaces runtime internes et decider leur exposition produit.
- Source-alignment evidence: the story preserves the requested audit folder, six standard files, mandatory matrix, and no-app-change rule.

## Objective

Create one timestamped CONDAMAD audit folder under `_condamad/audits/astro-runtime-surface-exposure/`.

The audit must decide whether each named runtime surface stays internal, gets a controlled public projection, feeds interpretation,
is reserved for admin/debug, or is deferred.

## Target State

- A latest audit folder exists under `_condamad/audits/astro-runtime-surface-exposure/`.
- `00-audit-report.md` contains the mandatory exposure matrix and explicit decisions for every named surface.
- `01-evidence-log.md` contains reproducible proof for each exposure decision.
- `02-finding-register.md` records risks, gaps, and open decisions tied to exposure safety.
- `03-story-candidates.md` qualifies and prioritizes CS-237, CS-238, and CS-239 follow-up candidates from the brief.
- `04-risk-matrix.md` documents exposure risk for stability, security, frontend coupling, and product confusion.
- `05-executive-summary.md` gives a decision-ready summary of public, internal, interpretation, admin/debug, and deferred surfaces.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-238-audit-runtime-surface-exposure-audit.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-238`.
- Evidence 3: `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md` - sibling audit story shape consulted.
- Evidence 4: `backend/tests/architecture/test_chart_runtime_surface_documentation.py` - runtime surface documentation guard exists.
- Evidence 5: `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py` - public contract guard keeps runtime internals out.
- Evidence 6: `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` - scoped scan found canonical `ChartObjectRuntimeData` construction.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - registry consulted through the guardrail resolver for this audit scope.
- Source-alignment review result: PASS; the audit scope keeps all named surfaces and forbids endpoint, serializer, and raw runtime exposure work.

## Domain Boundary

- Domain: backend-astrology-audit
- In scope:
  - Documentation-only audit of backend astrology runtime exposure decisions.
  - Classification of every runtime surface named by the brief.
  - Reproducible evidence from backend code, tests, architecture docs, public contract tests, and targeted scans.
  - Required surface inventory:
    - `chart_objects`.
    - `advanced_planetary_conditions`.
    - Fixed-star contacts.
    - Enriched sign profiles.
    - `interpretation_input`.
    - Internal aspect hints.
    - Condition profiles.
    - Dominance payloads.
    - Dignity payloads.
- Out of scope:
  - Frontend UI, API endpoint creation, public serializer modification, DB migrations, auth, i18n, styling, build tooling, and runtime calculators.
  - Raw public exposure of `ChartObjectRuntimeData`, `chart_objects`, or full calculation graph internals.
  - Implementing `chart_facts`, fixed-star public projection, or admin/debug endpoints.
- Explicit non-goals:
  - No code change outside the audit artifacts.
  - No new endpoint, schema, projection, serializer, frontend screen, seed data, migration, or calculation behavior.
  - No narrowing of the source surface list into a smaller audit.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend runtime exposure audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Produce documentation artifacts only under the scoped audit folder.
  - Do not change runtime behavior, public payloads, database schema, API routes, or frontend behavior.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the audit cannot assign an exposure recommendation to a required surface from repository evidence.
- Additional validation rules:
  - The audit report must include every mandatory matrix column from the brief.
  - The audit report must include every named runtime surface from the brief.
  - `ChartObjectRuntimeData` must never be recommended as a raw public contract.
  - The evidence log must map each recommendation to code, test, doc proof, or a documented bounded absence scan.
  - The finding register must distinguish stability, security, frontend coupling, product confusion, and open-decision risks.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Runtime exposure claims must cite code, tests, architecture docs, public contract tests, and scans. |
| Baseline Snapshot | yes | The audit must persist a reproducible baseline for post-CS-236 runtime surface exposure. |
| Ownership Routing | yes | Audit artifacts have canonical CONDAMAD locations and must not be mixed into app code. |
| Allowlist Exception | no | No allowlist handling is authorized for a documentation-only audit. |
| Contract Shape | yes | The audit has required files, mandatory matrix columns, and required named surfaces. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | The story must guard against adding endpoints, serializers, or app-code exposure while auditing. |
| Persistent Evidence | yes | The audit folder itself is the review handoff evidence. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The timestamped audit folder exists. | Evidence profile: baseline_before_after_diff; `python` checks `_condamad/audits/astro-runtime-surface-exposure`. |
| AC2 | All six standard audit files exist. | Evidence profile: baseline_before_after_diff; `python` checks required filenames in the latest audit folder. |
| AC3 | The mandatory matrix columns are present. | Evidence profile: json_contract_shape; `rg` checks each column in `00-audit-report.md`. |
| AC4 | Every required surface is covered. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks named surfaces in `00-audit-report.md`. |
| AC5 | Each surface has an exposure recommendation. | Evidence profile: baseline_before_after_diff; `rg` checks the recommendation vocabulary. |
| AC6 | Raw public exposure is rejected. | Evidence profile: no_legacy_contract; `pytest -q backend/tests/integration/astrology/test_natal_public_contract_compatibility.py` |
| AC7 | Each recommendation has concrete proof. | Evidence profile: baseline_before_after_diff; `rg` checks `01-evidence-log.md` for code, tests, docs, and bounded scans. |
| AC8 | Exposure risks are documented. | Evidence profile: baseline_before_after_diff; `rg` checks stability, security, frontend coupling, and product confusion. |
| AC9 | Findings are registered. | Evidence profile: baseline_before_after_diff; `rg` checks `02-finding-register.md` for risks, gaps, and open decisions. |
| AC10 | Story candidates are prioritized. | Evidence profile: baseline_before_after_diff; `rg` checks `03-story-candidates.md` for CS-237, CS-238, and CS-239. |
| AC11 | The executive summary is decision-ready. | Evidence profile: baseline_before_after_diff; `rg` checks `05-executive-summary.md` for conclusion and next-story ranking. |
| AC12 | No application files are changed. | Evidence profile: no_legacy_contract; `python` or `git diff --name-only` verifies only audit artifacts changed. |

## Implementation Tasks

- [ ] Task 1: Create the latest audit folder under `_condamad/audits/astro-runtime-surface-exposure/`. (AC: AC1)
- [ ] Task 2: Create the six standard audit files with coherent cross-references. (AC: AC2)
- [ ] Task 3: Inventory backend runtime, public contract, architecture, and interpretation-input evidence for named surfaces. (AC: AC4, AC7)
- [ ] Task 4: Fill the mandatory exposure matrix with one recommendation per named surface. (AC: AC3, AC4, AC5)
- [ ] Task 5: Document why `ChartObjectRuntimeData` remains non-public and cannot be exposed raw. (AC: AC6)
- [ ] Task 6: Record risks for stability, security, frontend coupling, product confusion, admin/debug access, and LLM use. (AC: AC8, AC9)
- [ ] Task 7: Prioritize CS-237, CS-238, and CS-239 candidates with justification and source-finding links. (AC: AC10, AC11)
- [ ] Task 8: Run document validation and verify that no app file changed. (AC: AC1, AC2, AC12)
- [ ] Task 9: Verify the audit report names every surface from the source brief explicitly. (AC: AC4)

## Files to Inspect First

- `_story_briefs/cs-238-audit-runtime-surface-exposure-audit.md` - source contract.
- `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md` - sibling audit story shape.
- `docs/architecture/astrology-runtime-surfaces.md` - existing runtime surface architecture inventory.
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` - canonical chart object runtime construction.
- `backend/app/domain/astrology/interpretation/**` - interpretation input projection and LLM-adjacent runtime evidence.
- `backend/app/domain/astrology/aspects/**` - structural aspect runtime and interpretive hint boundaries.
- `backend/app/domain/astrology/advanced_conditions/**` - advanced planetary conditions and condition profiles.
- `backend/app/domain/astrology/dignities/**` - dignity payload and scoring evidence.
- `backend/app/domain/astrology/dominance/**` - dominance payload and scoring evidence.
- `backend/app/domain/astrology/fixed_stars/**` - fixed-star contact evidence.
- `backend/tests/architecture/**` - architecture guardrails for runtime surface boundaries.
- `backend/tests/integration/astrology/**` - public contract and runtime integration evidence.
- `backend/tests/unit/domain/astrology/**` - deterministic domain evidence for named surfaces.

## Runtime Source of Truth

- Primary source of truth:
  - `AST guard`, architecture tests, integration tests, unit tests, domain code, public contract tests, and existing architecture docs.
- Secondary evidence:
  - Targeted `rg` scans proving presence, absence, internal-only use, public projection use, LLM use, or admin/debug absence by surface.
- Static scans alone are not sufficient for runtime exposure claims because:
  - Each public, internal, interpretation, admin/debug, or deferred recommendation must cite code, tests, docs, or bounded absence evidence.

## Contract Shape

- Contract type:
  - CONDAMAD domain audit folder.
- Fields:
  - `surface_interne`: runtime surface name from the brief.
  - `utilite_produit`: user or product value.
  - `risque_exposition`: security, stability, coupling, or product confusion risk.
  - `stabilite_contrat`: contract stability level.
  - `besoin_frontend`: public UI or client need.
  - `besoin_admin_debug`: protected operator need.
  - `besoin_llm_interpretation`: interpretation or LLM need.
  - `exposition_recommandee`: final recommendation.
- Required fields:
  - `surface_interne`
  - `utilite_produit`
  - `risque_exposition`
  - `stabilite_contrat`
  - `besoin_frontend`
  - `besoin_admin_debug`
  - `besoin_llm_interpretation`
  - `exposition_recommandee`
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
  - Surface interne
  - Utilité produit
  - Risque d'exposition
  - Stabilité du contrat
  - Besoin frontend
  - Besoin admin/debug
  - Besoin LLM/interprétation
  - Exposition recommandée
- Required recommendations:
  - `interne`
  - `projection publique dediee`
  - `interpretation/LLM uniquement`
  - `admin/debug protege`
  - `differee`
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-238-audit-runtime-surface-exposure-audit.md`
  - `docs/architecture/astrology-runtime-surfaces.md`
  - `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py`
- Comparison after implementation:
  - Latest child folder under `_condamad/audits/astro-runtime-surface-exposure/`.
- Expected invariant:
  - The only intended repository delta is the new audit folder and its standard CONDAMAD audit files.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Runtime exposure audit | `_condamad/audits/astro-runtime-surface-exposure/` | `backend/app/**` |
| Evidence log | `_condamad/audits/astro-runtime-surface-exposure/` | `backend/tests/**` |
| Story candidates | `_condamad/audits/astro-runtime-surface-exposure/` | `_condamad/stories/**` |
| Runtime architecture source | `docs/architecture/astrology-runtime-surfaces.md` | New duplicated docs under `backend/app/**` |

## Mandatory Reuse / DRY Constraints

- Reuse existing runtime surface architecture docs and tests as source evidence instead of duplicating large source excerpts.
- Use one canonical surface name per brief surface across all six audit files.
- Use one recommendation vocabulary across report, evidence log, findings, story candidates, risk matrix, and summary.
- Keep `ChartObjectRuntimeData` as the internal runtime object name and do not introduce a parallel raw public contract name.
- Do not add external packages or custom audit tooling.

## No Legacy / Forbidden Paths

- No legacy route path may be added during this audit.
- No compatibility route path may be added during this audit.
- No fallback route path may be added during this audit.
- Do not create app-code aliases, shims, runtime fallback branches, or compatibility wrappers.
- Do not expose `chart_objects` or `ChartObjectRuntimeData` publicly.
- Do not add API routes, serializers, database migrations, seed data, frontend screens, admin/debug handlers, or calculators.

## Reintroduction Guard

- Forbidden app-code delta:
  - `backend/app/**`
  - `backend/tests/**`
  - `frontend/src/**`
  - `backend/migrations/**`
- Required guard:
  - `git diff --name-only` must show only the audit folder for implementation changes.
  - `rg` must prove `ChartObjectRuntimeData` is discussed as internal, not as a raw public contract.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Local anti-drift: no API router change belongs to this audit. | `git diff --name-only`; bounded `rg`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Applicable pattern: candidate validation paths must be concrete. | `rg` over `03-story-candidates.md`. |
| Registry gap | No exact runtime surface exposure audit guardrail was present in the resolver output. | Resolver output reviewed. |

Non-applicable examples retained to prevent scope drift:

- RG-047 frontend inline styles are out of scope because no frontend files are touched.
- RG-052 frontend CSS namespace convergence is out of scope because no styling files are touched.
- RG-041 entitlement documentation is out of scope because runtime astrology exposure, not billing entitlement, is audited.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit report | `_condamad/audits/astro-runtime-surface-exposure/{audit-timestamp}/00-audit-report.md` | Matrix and explicit decisions. |
| Evidence log | `_condamad/audits/astro-runtime-surface-exposure/{audit-timestamp}/01-evidence-log.md` | Reproducible proof by surface. |
| Finding register | `_condamad/audits/astro-runtime-surface-exposure/{audit-timestamp}/02-finding-register.md` | Risks, gaps, and open decisions. |
| Story candidates | `_condamad/audits/astro-runtime-surface-exposure/{audit-timestamp}/03-story-candidates.md` | Prioritized follow-up stories. |
| Risk matrix | `_condamad/audits/astro-runtime-surface-exposure/{audit-timestamp}/04-risk-matrix.md` | Exposure risks by surface. |
| Executive summary | `_condamad/audits/astro-runtime-surface-exposure/{audit-timestamp}/05-executive-summary.md` | Decision summary. |
| Review output | `_condamad/stories/CS-238-audit-runtime-surface-exposure/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this documentation-only audit.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/astro-runtime-surface-exposure/{audit-timestamp}/00-audit-report.md` - exposure matrix and decisions.
- `_condamad/audits/astro-runtime-surface-exposure/{audit-timestamp}/01-evidence-log.md` - reproducible evidence.
- `_condamad/audits/astro-runtime-surface-exposure/{audit-timestamp}/02-finding-register.md` - risks, gaps, and open decisions.
- `_condamad/audits/astro-runtime-surface-exposure/{audit-timestamp}/03-story-candidates.md` - prioritized follow-up stories.
- `_condamad/audits/astro-runtime-surface-exposure/{audit-timestamp}/04-risk-matrix.md` - exposure risk classification.
- `_condamad/audits/astro-runtime-surface-exposure/{audit-timestamp}/05-executive-summary.md` - decision summary.

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

- VC1: `$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-runtime-surface-exposure | Sort-Object Name -Descending | Select-Object -First 1`
- VC2: `rg -n "chart_objects|ChartObjectRuntimeData|projection|admin/debug|frontend|LLM" "$($auditFolder.FullName)\00-audit-report.md"`
- VC3: `rg -n "Surface interne|Utilité produit|Risque d'exposition|Stabilité du contrat|Exposition recommandée" "$($auditFolder.FullName)\00-audit-report.md"`
- VC4: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py $auditFolder.FullName`
- VC5: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py $auditFolder.FullName`
- VC6: `python -c "from pathlib import Path; p=max(Path('_condamad/audits/astro-runtime-surface-exposure').iterdir()); assert (p/'00-audit-report.md').exists()"`
- VC7: `git diff --name-only`

Before VC4 and VC5, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The audit may overstate public readiness by treating internal runtime payloads as stable product contracts.
- The audit may understate interpretation value by classifying LLM-only surfaces as strictly internal.
- The candidate list may drift into implementation design before exposure decisions are proven.
- A developer may accidentally change app code while producing audit artifacts.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all audit artifacts under the latest `_condamad/audits/astro-runtime-surface-exposure/` child folder.
- Treat public projection as requiring a stable, intentionally reduced contract.
- Treat admin/debug exposure as requiring protected access design in a future story, not this audit.
- Treat interpretation/LLM use as a non-public projection decision.
- Do not modify backend, frontend, migration, serializer, or API files.

## References

- `_story_briefs/cs-238-audit-runtime-surface-exposure-audit.md`
- `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md`
- `docs/architecture/astrology-runtime-surfaces.md`
- `_condamad/stories/regression-guardrails.md`
