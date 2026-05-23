# Story CS-240 audit-reference-governance: Audit Reference Governance
Status: ready-to-dev

## Trigger / Source

- Source type: audit-to-story with repository-informed boundary.
- Source reference: `_story_briefs/cs-240-audit-reference-governance-audit.md`.
- Problem statement: produire un audit CONDAMAD qui classe les sources des regles astrologiques, seuils, poids et profils.
- Source-alignment evidence: the story preserves the requested audit folder, six standard files, mandatory governance matrix, and no-migration rule.

## Objective

Create one timestamped CONDAMAD audit folder under `_condamad/audits/astro-reference-governance/`.

The audit must decide where each critical astrology rule currently lives: DB reference, Python code, tests, or doctrinal documentation.

## Target State

- A latest audit folder exists under `_condamad/audits/astro-reference-governance/`.
- `00-audit-report.md` contains the mandatory matrix and governance decisions for every named rule family.
- `01-evidence-log.md` contains reproducible proof for DB, Python, test, and documentation sources.
- `02-finding-register.md` records duplicated, unversioned, ambiguous, or undocumented rule ownership.
- `03-story-candidates.md` qualifies and prioritizes CS-249, CS-250, and CS-251.
- `04-risk-matrix.md` documents governance risks tied to duplicated or unclear rule sources.
- `05-executive-summary.md` gives a decision-ready summary of source ownership and next governance stories.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-240-audit-reference-governance-audit.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-240`.
- Evidence 3: `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md` - sibling audit story shape consulted.
- Evidence 4: `_condamad/stories/CS-238-audit-runtime-surface-exposure/00-story.md` - sibling runtime audit story shape consulted.
- Evidence 5: `_condamad/stories/CS-239-audit-chart-object-capability-payload/00-story.md` - sibling taxonomy audit shape consulted.
- Evidence 6: `docs/db_seeder/astrology/astral_accidental_dignity_rules.json` - scoped scan found DB rules with threshold-like values.
- Evidence 7: `backend/app/domain/astrology` - scoped inventory found astrology runtime, reference, dignity, dominance, aspect, and fixed-star surfaces.
- Evidence 8: `backend/tests/unit/domain/astrology` - scoped inventory found domain tests covering astrology rules and calculators.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through the guardrail resolver for this audit scope.
- Source-alignment review result: PASS; all rule families, matrix columns, candidate stories, and no-rule-migration constraints are preserved.

## Domain Boundary

- Domain: backend-astrology-audit
- In scope:
  - Documentation-only audit of astrology rule source governance.
  - Static search of thresholds, weights, profiles, and rule ownership in `backend/app`.
  - Inventory of astrology DB reference tables and seed artifacts under `docs/db_seeder/astrology`.
  - Distinction between doctrinal rule, runtime parameter, test fixture, and product presentation.
  - Identification of rules that are duplicated, unversioned, ambiguous, or modifiable without code.
  - Required rule families:
    - Orbes.
    - Poids de dominance.
    - Seuils de combustion.
    - Seuils de cazimi.
    - Seuils d'under beams.
    - Seuils de vitesse.
    - Seuils de station.
    - Poids des maisons.
    - Poids des dignites.
    - Profils de signes.
    - Regles fixed stars.
    - Regles d'aspects.
    - Regles d'interpretation.
- Out of scope:
  - Frontend UI, API endpoint creation, DB migrations, auth, i18n, styling, build tooling, and runtime calculator changes.
  - Moving rules between Python and DB.
  - Modifying seeds, creating tables, or changing reference data.
- Explicit non-goals:
  - No code change outside the audit artifacts.
  - No new endpoint, schema, projection, serializer, frontend screen, seed data, migration, or calculation behavior.
  - No narrowing of the required rule family list into a smaller audit.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend astrology governance audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Produce documentation artifacts only under the scoped audit folder.
  - Do not change runtime behavior, public payloads, database schema, API routes, seeds, or frontend behavior.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the audit cannot assign source ownership to a required rule family from repository evidence.
- Additional validation rules:
  - The audit report must include every mandatory matrix column from the brief.
  - The audit report must include every required rule family from the brief.
  - The evidence log must map each ownership decision to DB seed, Python code, test proof, documentation, or a bounded absence scan.
  - The finding register must distinguish duplicated rule, unversioned rule, ambiguous owner, missing doctrine, and non-runtime documentation.
  - The story candidates file must qualify CS-249, CS-250, and CS-251 with priority and source-finding links.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Governance claims must cite code, tests, DB seed artifacts, docs, and scans proving actual source ownership. |
| Baseline Snapshot | yes | The audit must persist a reproducible baseline for astrology rule source ownership. |
| Ownership Routing | yes | Audit artifacts have canonical CONDAMAD locations and must not be mixed into app code or seed folders. |
| Allowlist Exception | no | No allowlist handling is authorized for this documentation-only audit. |
| Contract Shape | yes | The audit has required files, mandatory matrix columns, required rule families, and candidate stories. |
| Batch Migration | no | No migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | The story must guard against rule movement, seed edits, migrations, and app-code changes while auditing. |
| Persistent Evidence | yes | The audit folder itself is the review handoff evidence. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The timestamped audit folder exists. | Evidence profile: baseline_before_after_diff; `python` checks `_condamad/audits/astro-reference-governance`. |
| AC2 | All six standard audit files exist. | Evidence profile: baseline_before_after_diff; `python` checks required filenames in the latest audit folder. |
| AC3 | The mandatory matrix columns are present. | Evidence profile: json_contract_shape; `rg` checks every column in `00-audit-report.md`. |
| AC4 | Every required rule family is covered. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks named rule families in `00-audit-report.md`. |
| AC5 | Source ownership is classified. | Evidence profile: baseline_before_after_diff; `rg` checks DB, Python, versioned, tested, doctrine, and modifiable terms. |
| AC6 | Each ownership decision has proof. | Evidence profile: baseline_before_after_diff; `pytest -q backend/tests/unit/domain/astrology/test_runtime_ref.py`. |
| AC7 | Hardcoded thresholds are listed. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks threshold, weight, orb, cazimi, and station terms. |
| AC8 | Rule source class is explicit. | Evidence profile: baseline_before_after_diff; `pytest -q backend/tests/unit/domain/astrology/test_runtime_ref.py`. |
| AC9 | Modifiable-without-code rules are identified. | Evidence profile: baseline_before_after_diff; `rg` checks the modifiable-without-code governance column. |
| AC10 | Governance findings are registered. | Evidence profile: baseline_before_after_diff; `rg` checks duplicated, unversioned, and ambiguous terms. |
| AC11 | Candidate stories are prioritized. | Evidence profile: baseline_before_after_diff; `rg` checks `03-story-candidates.md` for CS-249, CS-250, and CS-251. |
| AC12 | No application files are changed. | Evidence profile: no_legacy_contract; `python` or `git diff --name-only` verifies only audit artifacts changed. |

## Implementation Tasks

- [ ] Task 1: Create the latest audit folder under `_condamad/audits/astro-reference-governance/`. (AC: AC1)
- [ ] Task 2: Create the six standard audit files with coherent cross-references. (AC: AC2)
- [ ] Task 3: Search backend astrology code for thresholds, weights, profiles, and ownership signals. (AC: AC4, AC6, AC7)
- [ ] Task 4: Inventory astrology seed and reference artifacts under `docs/db_seeder/astrology`. (AC: AC5, AC8, AC9)
- [ ] Task 5: Fill the mandatory governance matrix for every required rule family. (AC: AC3, AC4, AC5, AC9)
- [ ] Task 6: Register duplicated, unversioned, ambiguous, and undocumented rule ownership findings. (AC: AC10)
- [ ] Task 7: Prioritize CS-249, CS-250, and CS-251 with source-finding links and sequencing rationale. (AC: AC11)
- [ ] Task 8: Run document validation and verify that no app, seed, migration, or frontend file changed. (AC: AC1, AC2, AC12)
- [ ] Task 9: Verify the audit report names every required rule family from the source brief explicitly. (AC: AC4)

## Files to Inspect First

- `_story_briefs/cs-240-audit-reference-governance-audit.md` - source contract.
- `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md` - sibling audit story shape.
- `_condamad/stories/CS-238-audit-runtime-surface-exposure/00-story.md` - sibling runtime audit story shape.
- `_condamad/stories/CS-239-audit-chart-object-capability-payload/00-story.md` - sibling taxonomy audit story shape.
- `backend/app/domain/astrology/**` - runtime, reference, calculators, profiles, and projections.
- `backend/tests/unit/domain/astrology/**` - deterministic evidence for rule behavior and hardcoded thresholds.
- `backend/tests/integration/astrology/**` - integration evidence for reference-backed behavior.
- `backend/tests/architecture/**` - architecture evidence for runtime and contract boundaries.
- `docs/db_seeder/astrology/**` - DB reference seed ownership and versioning evidence.
- `docs/architecture/astrology-runtime-surfaces.md` - documented runtime boundary context.
- `docs/**` - bounded doctrinal or research context found by the audit validation searches.

## Runtime Source of Truth

- Primary source of truth:
  - `AST guard`, domain unit tests, integration tests, architecture tests, Python source files, DB seed artifacts, and architecture docs.
- Secondary evidence:
  - Targeted `rg` scans proving source ownership, duplication, hardcoded thresholds, versioning markers, and bounded absence by rule family.
- Static scans alone are not sufficient for governance claims because:
  - Each classification must cite DB seed evidence, Python source evidence, test coverage, documentation evidence, or a documented absence scan.

## Contract Shape

- Contract type:
  - CONDAMAD domain audit folder.
- Fields:
  - `regle_metier`: required rule family from the brief.
  - `source_actuelle`: current file, table, test, or documentation source.
  - `db_ou_python`: source classification as DB, Python, test, documentation, mixed, or missing.
  - `versionnee`: whether the source has explicit versioning or reference-version ownership.
  - `testee`: whether deterministic tests prove the rule.
  - `doctrine_astrologique_associee`: doctrinal source or documented absence.
  - `modifiable_sans_code`: whether the rule can change through reference data rather than code.
- Required fields:
  - `regle_metier`
  - `source_actuelle`
  - `db_ou_python`
  - `versionnee`
  - `testee`
  - `doctrine_astrologique_associee`
  - `modifiable_sans_code`
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
  - Règle métier
  - Source actuelle
  - DB ou Python
  - Versionnée
  - Testée
  - Doctrine astrologique associée
  - Modifiable sans code
- Required candidate stories:
  - `CS-249`
  - `CS-250`
  - `CS-251`
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-240-audit-reference-governance-audit.md`
  - `backend/app/domain/astrology`
  - `docs/db_seeder/astrology`
- Comparison after implementation:
  - Latest child folder under `_condamad/audits/astro-reference-governance/`.
- Expected invariant:
  - The only intended repository delta is the new audit folder and its standard CONDAMAD audit files.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Reference governance audit | `_condamad/audits/astro-reference-governance/` | `backend/app/**` |
| Evidence log | `_condamad/audits/astro-reference-governance/` | `backend/tests/**` |
| Story candidates | `_condamad/audits/astro-reference-governance/` | `_condamad/stories/**` |
| Seed ownership source | `docs/db_seeder/astrology/**` | New duplicated docs under `backend/app/**` |
| Runtime rule source | `backend/app/domain/astrology/**` | New audit-only helpers under app code |

## Mandatory Reuse / DRY Constraints

- Reuse existing Python source, DB seed artifacts, tests, and docs as source evidence.
- Use one canonical rule family name across all six audit files.
- Use one governance classification vocabulary across report, evidence log, findings, candidates, risk matrix, and summary.
- Do not duplicate large source excerpts; cite bounded files, symbols, test paths, and scan commands.
- Do not add external packages or custom audit tooling.

## No Legacy / Forbidden Paths

- No legacy route path may be added during this audit.
- No compatibility route path may be added during this audit.
- No fallback route path may be added during this audit.
- Do not create app-code aliases, shims, runtime fallback branches, or compatibility wrappers.
- Do not move rules between DB and Python during this audit.
- Do not modify seeds, create tables, add migrations, update calculators, or change tests.
- Do not add API routes, serializers, frontend screens, admin/debug handlers, or runtime validation code.

## Reintroduction Guard

- Forbidden app-code delta:
  - `backend/app/**`
  - `backend/tests/**`
  - `docs/db_seeder/**`
  - `backend/migrations/**`
  - `frontend/src/**`
- Required guard:
  - `git diff --name-only` must show only the audit folder for implementation changes.
  - `rg` must prove governance findings are documented in audit artifacts, not implemented as seed or runtime changes.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Local anti-drift: no API router change belongs to this audit. | `git diff --name-only`; bounded `rg`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Applicable pattern: candidate validation paths must be concrete. | `rg` over `03-story-candidates.md`. |
| Registry gap | No exact astrology reference governance audit guardrail was present in the resolver output. | Resolver output reviewed. |

Non-applicable examples retained to prevent scope drift:

- RG-047 frontend inline styles are out of scope because no frontend files are touched.
- RG-052 frontend CSS namespace convergence is out of scope because no styling files are touched.
- RG-041 entitlement documentation is out of scope because astrology reference governance, not billing entitlement, is audited.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit report | `_condamad/audits/astro-reference-governance/{audit-timestamp}/00-audit-report.md` | Matrix and governance decisions. |
| Evidence log | `_condamad/audits/astro-reference-governance/{audit-timestamp}/01-evidence-log.md` | Reproducible proof by rule family. |
| Finding register | `_condamad/audits/astro-reference-governance/{audit-timestamp}/02-finding-register.md` | Duplicated or unclear ownership. |
| Story candidates | `_condamad/audits/astro-reference-governance/{audit-timestamp}/03-story-candidates.md` | Prioritized follow-up stories. |
| Risk matrix | `_condamad/audits/astro-reference-governance/{audit-timestamp}/04-risk-matrix.md` | Governance risk classification. |
| Executive summary | `_condamad/audits/astro-reference-governance/{audit-timestamp}/05-executive-summary.md` | Decision summary. |
| Review output | `_condamad/stories/CS-240-audit-reference-governance/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this documentation-only audit.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/astro-reference-governance/{audit-timestamp}/00-audit-report.md` - matrix and governance decisions.
- `_condamad/audits/astro-reference-governance/{audit-timestamp}/01-evidence-log.md` - reproducible evidence.
- `_condamad/audits/astro-reference-governance/{audit-timestamp}/02-finding-register.md` - duplicated, unversioned, and ambiguous rules.
- `_condamad/audits/astro-reference-governance/{audit-timestamp}/03-story-candidates.md` - prioritized CS-249 through CS-251.
- `_condamad/audits/astro-reference-governance/{audit-timestamp}/04-risk-matrix.md` - governance risk classification.
- `_condamad/audits/astro-reference-governance/{audit-timestamp}/05-executive-summary.md` - decision summary.

Likely tests:

- Document validation through `condamad_domain_audit_validate.py`.
- Document lint through `condamad_domain_audit_lint.py`.
- Targeted `rg` checks against latest audit artifacts.
- `pytest -q backend/tests/unit/domain/astrology/test_runtime_ref.py` for existing reference runtime evidence.
- `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` for existing condition contract evidence.

Files not expected to change:

- `backend/app/**` - out of scope; no backend runtime is touched.
- `backend/tests/**` - out of scope; no test code is touched.
- `docs/db_seeder/**` - out of scope; no seed or reference data is touched.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-reference-governance | Sort-Object Name -Descending | Select-Object -First 1`
- VC2: `rg -n "Règle métier|Source actuelle|DB ou Python|Versionnée|Testée|Doctrine astrologique associée|Modifiable" "$($auditFolder.FullName)\00-audit-report.md"`
- VC3: `rg -n "orb|combust|cazimi|under_beams|station|dominance|dignit|fixed_star|threshold|weight" backend/app docs/db_seeder docs`
- VC4: `rg -n "duplicated|unversioned|ambiguous|dupliquée|non versionnée|ambiguë" "$($auditFolder.FullName)\02-finding-register.md"`
- VC5: `rg -n "CS-249|CS-250|CS-251|priority|priorité" "$($auditFolder.FullName)\03-story-candidates.md"`
- VC6: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py $auditFolder.FullName`
- VC7: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py $auditFolder.FullName`
- VC8: `pytest -q backend/tests/unit/domain/astrology/test_runtime_ref.py`
- VC9: `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
- VC10: `python -c "from pathlib import Path; p=max(Path('_condamad/audits/astro-reference-governance').iterdir()); assert (p/'00-audit-report.md').exists()"`
- VC11: `git diff --name-only`

Before VC6, VC7, VC8, VC9, and VC10, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The audit may overstate DB ownership by treating seed presence as proof of runtime consumption.
- The audit may overstate Python ownership by counting tests or documentation as rule owners.
- Hardcoded thresholds may be missed when named differently from the brief vocabulary.
- Candidate stories may drift into migration design before source ownership is proven.
- A developer may accidentally change app code or seed data while producing audit artifacts.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all audit artifacts under the latest `_condamad/audits/astro-reference-governance/` child folder.
- Treat DB ownership as proven only by reference artifact plus runtime consumption or explicit governance decision.
- Treat Python ownership as proven only by source code or deterministic test evidence.
- Treat documentation-only doctrine as non-runtime evidence unless code or seed consumption is cited.
- Do not modify backend, frontend, migration, seed, serializer, dataclass, validator, graph, or calculator files.

## References

- `_story_briefs/cs-240-audit-reference-governance-audit.md`
- `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md`
- `_condamad/stories/CS-238-audit-runtime-surface-exposure/00-story.md`
- `_condamad/stories/CS-239-audit-chart-object-capability-payload/00-story.md`
- `docs/db_seeder/astrology/astral_accidental_dignity_rules.json`
- `_condamad/stories/regression-guardrails.md`
