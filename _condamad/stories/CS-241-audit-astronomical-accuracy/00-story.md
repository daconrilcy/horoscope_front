# Story CS-241 audit-astronomical-accuracy: Audit Astronomical Accuracy
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-241-audit-astronomical-accuracy-audit.md`.
- Related context: post-CS-236 notes state that simplified and `swisseph` calculation paths still coexist.
- Problem statement: produce a CONDAMAD audit proving the real astronomical reliability of the astrology engine.
- Source-alignment evidence: the story preserves the requested audit folder, six standard files, sensitive time cases, and candidate stories.

## Objective

Create one timestamped CONDAMAD audit folder under `_condamad/audits/astro-astronomical-accuracy/`.

The audit must document real `swisseph` usage, ephemeris configuration, temporal accuracy risks, house-system edge behavior, and golden chart needs.

## Target State

- A latest audit folder exists under `_condamad/audits/astro-astronomical-accuracy/`.
- `00-audit-report.md` contains the astronomical reliability analysis and the required golden chart recommendations.
- `01-evidence-log.md` contains reproducible proof for calculation paths, ephemeris configuration, temporal handling, and house behavior.
- `02-finding-register.md` records astronomical precision risks and guarantee gaps separately from architecture risks.
- `03-story-candidates.md` qualifies and prioritizes CS-240, CS-241, and CS-242 from the audit findings.
- `04-risk-matrix.md` maps precision and reproducibility risks to user impact and technical risk.
- `05-executive-summary.md` gives a decision-ready summary for engineering and product follow-up.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-241-audit-astronomical-accuracy-audit.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-241`.
- Evidence 3: `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md` - sibling audit story shape consulted.
- Evidence 4: `_condamad/stories/CS-240-audit-reference-governance/00-story.md` - sibling governance audit shape consulted.
- Evidence 5: `backend/app/domain/astrology/swisseph_runtime.py` - scoped scan found a Swiss Ephemeris runtime surface.
- Evidence 6: `backend/app/core/ephemeris.py` - scoped scan found ephemeris bootstrap and configuration surface.
- Evidence 7: `backend/app/domain/astrology/natal_preparation.py` - scoped scan found timezone, UTC, DST, and local-time validation logic.
- Evidence 8: `backend/app/tests/golden/pro_dataset_v1.json` - scoped scan found a versioned `swisseph` golden dataset surface.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through the guardrail resolver for this audit scope.
- Source-alignment review result: PASS; the audit deliverables, verification points, golden charts, and no-code-change limits are preserved.

## Domain Boundary

- Domain: backend-astrology-audit
- In scope:
  - Documentation-only audit of astronomical accuracy for backend astrology calculations.
  - Inventory of simplified calculation paths and `swisseph` calculation paths.
  - Analysis of active calculation mode by environment.
  - Analysis of ephemeris file version, path, hash evidence needs, and reproducibility risks.
  - Analysis of UTC, timezone, DST, UT versus TT, ayanamsa, topocentric, altitude, high-latitude, and Placidus edge handling.
  - Required golden chart recommendations:
    - Paris normal case.
    - DST ambiguous time.
    - DST nonexistent time.
    - High latitude case.
    - Sidereal Lahiri case.
    - Topocentric case.
    - Whole sign case.
    - Placidus edge case.
  - Qualification of candidate stories CS-240, CS-241, and CS-242.
- Out of scope:
  - Frontend UI, API endpoint creation, DB migrations, auth, i18n, styling, build tooling, and production configuration changes.
  - Removing the simplified engine.
  - Adding golden tests or changing calculation behavior.
- Explicit non-goals:
  - No code change outside the audit artifacts.
  - No new endpoint, schema, projection, serializer, frontend screen, seed data, migration, or calculation behavior.
  - No narrowing of the required astronomical risk list into a smaller audit.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend astronomical accuracy audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Produce documentation artifacts only under the scoped audit folder.
  - Do not change runtime behavior, public payloads, database schema, API routes, seeds, or frontend behavior.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the audit cannot determine the active calculation mode or ephemeris evidence requirement from repository proof.
- Additional validation rules:
  - The audit report must document active calculation mode by environment.
  - The audit report must separate astronomical risks from architecture risks.
  - The audit report must define an objective for each required golden chart.
  - The evidence log must cite code, tests, docs, configuration, generated evidence, or bounded absence scans.
  - The story candidates file must qualify CS-240, CS-241, and CS-242 with source-finding links.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Accuracy claims must cite code, tests, config, docs, and scans proving actual backend calculation behavior. |
| Baseline Snapshot | yes | The audit must persist a reproducible baseline for astronomical accuracy and ephemeris evidence. |
| Ownership Routing | yes | Audit artifacts have canonical CONDAMAD locations and must not be mixed into app code or test suites. |
| Allowlist Exception | no | No allowlist handling is authorized for this documentation-only audit. |
| Contract Shape | yes | The audit has required files, required verification points, required golden charts, and candidate stories. |
| Batch Migration | no | No migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | The story must guard against changing calculation behavior while auditing it. |
| Persistent Evidence | yes | The audit folder itself is the review handoff evidence. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The timestamped audit folder exists. | Evidence profile: baseline_before_after_diff; `python` checks `_condamad/audits/astro-astronomical-accuracy`. |
| AC2 | All six standard audit files exist. | Evidence profile: baseline_before_after_diff; `python` checks required filenames in the latest audit folder. |
| AC3 | Active calculation mode is documented. | Evidence profile: baseline_before_after_diff; `rg` checks environment and engine terms in `00-audit-report.md`. |
| AC4 | The Swiss path is inventoried. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `swisseph` calculation symbols. |
| AC5 | Ephemeris evidence needs are listed. | Evidence profile: baseline_before_after_diff; `rg` checks ephemeris version, hash, path, and reproducibility terms. |
| AC6 | Temporal accuracy risks are covered. | Evidence profile: baseline_before_after_diff; `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`. |
| AC7 | House edge behavior is assessed. | Evidence profile: baseline_before_after_diff; `rg` checks high latitude, Placidus, and whole sign terms. |
| AC8 | Golden chart objectives are defined. | Evidence profile: json_contract_shape; `rg` checks all eight required golden chart names in `00-audit-report.md`. |
| AC9 | Astronomical risks are separated. | Evidence profile: baseline_before_after_diff; `rg` checks precision, reproducibility, architecture, and guarantee terms. |
| AC10 | Candidate stories are qualified. | Evidence profile: baseline_before_after_diff; `rg` checks `03-story-candidates.md` for CS-240, CS-241, and CS-242. |
| AC11 | Audit validation commands pass. | Evidence profile: baseline_before_after_diff; `python` runs the CONDAMAD audit validator. |
| AC12 | No application files are changed. | Evidence profile: no_legacy_contract; `python` or `git diff --name-only` verifies only audit artifacts changed. |
| AC13 | The simplified path is inventoried. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks simplified calculation symbols. |

## Implementation Tasks

- [ ] Task 1: Create the latest audit folder under `_condamad/audits/astro-astronomical-accuracy/`. (AC: AC1)
- [ ] Task 2: Create the six standard audit files with coherent cross-references. (AC: AC2)
- [ ] Task 3: Inventory the `swisseph` calculation path across backend astrology surfaces. (AC: AC3, AC4)
- [ ] Task 4: Inventory the simplified calculation path across backend astrology surfaces. (AC: AC13)
- [ ] Task 5: Document active calculation mode by environment from config, code, docs, and bounded scans. (AC: AC3, AC4, AC13)
- [ ] Task 6: Assess ephemeris path, version, hash evidence needs, and reproducibility risks. (AC: AC5, AC9)
- [ ] Task 7: Assess UTC, timezone, DST, UT versus TT, ayanamsa, topocentric, altitude, and house edge behavior. (AC: AC6, AC7)
- [ ] Task 8: Define objective and evidence expectation for each required golden chart. (AC: AC8)
- [ ] Task 9: Register astronomical precision findings separately from architecture findings. (AC: AC9)
- [ ] Task 10: Qualify CS-240, CS-241, and CS-242 with priority, source finding, and validation evidence. (AC: AC10)
- [ ] Task 11: Run document validation and verify that no app, test, migration, config, or frontend file changed. (AC: AC1, AC2, AC11, AC12)

## Files to Inspect First

- `_story_briefs/cs-241-audit-astronomical-accuracy-audit.md` - source contract.
- `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md` - sibling audit story shape.
- `_condamad/stories/CS-240-audit-reference-governance/00-story.md` - sibling audit story shape.
- `docs/recherches astro/2026-05-23-audit-calcul-theme-astral-post-cs-236.md` - post-CS-236 calculation context.
- `backend/app/domain/astrology/swisseph_runtime.py` - Swiss Ephemeris runtime surface.
- `backend/app/core/ephemeris.py` - ephemeris bootstrap and configuration surface.
- `backend/app/domain/astrology/ephemeris_provider.py` - planetary position provider surface.
- `backend/app/domain/astrology/houses_provider.py` - house-system provider surface.
- `backend/app/domain/astrology/natal_preparation.py` - timezone, UTC, DST, and input preparation surface.
- `backend/app/domain/astrology/natal_calculation.py` - calculation orchestration and engine selection surface.
- `backend/app/tests/golden/**` - golden dataset evidence.
- `backend/tests/unit/domain/astrology/**` - deterministic astronomy and runtime test evidence.
- `docs/recherches astro/**` - bounded research and doctrine context for astronomical expectations.

## Runtime Source of Truth

- Primary source of truth:
  - `AST guard`, generated audit manifest, domain tests, integration tests, Python source files, config surfaces, and golden datasets.
- Secondary evidence:
  - Targeted `rg` scans proving engine mode, ephemeris metadata, time conversion, house behavior, and bounded absence.
- Static scans alone are not sufficient for astronomical reliability claims because:
  - Each claim must cite runtime code, deterministic tests, configuration evidence, generated audit evidence, or documented absence scans.

## Contract Shape

- Contract type:
  - CONDAMAD domain audit folder.
- Fields:
  - `controle`: astronomical verification point from the source brief.
  - `surface_actuelle`: current code, config, test, documentation, or missing surface.
  - `preuve_reproductible`: evidence command, file, test, generated artifact, or bounded absence scan.
  - `risque_astronomique`: precision or reproducibility risk.
  - `risque_architecture`: ownership or maintainability risk kept separate from astronomical risk.
  - `golden_chart_associee`: required golden chart or `none`.
  - `story_candidate`: CS-240, CS-241, CS-242, or `none`.
- Required fields:
  - `controle`
  - `surface_actuelle`
  - `preuve_reproductible`
  - `risque_astronomique`
  - `risque_architecture`
  - `golden_chart_associee`
  - `story_candidate`
- Optional fields:
  - none
- Status codes:
  - none; this is not an API route.
- Serialization names:
  - Markdown matrix columns keep the exact French labels from this story contract.
- Required files:
  - `00-audit-report.md`
  - `01-evidence-log.md`
  - `02-finding-register.md`
  - `03-story-candidates.md`
  - `04-risk-matrix.md`
  - `05-executive-summary.md`
- Required verification points:
  - `swisseph` production usage.
  - Simplified engine restriction outside test and dev.
  - Ephemeris version and hash.
  - Position reproducibility.
  - UTC, timezone, and DST.
  - UT versus TT.
  - Sidereal ayanamsa.
  - Topocentric and altitude handling.
  - High-latitude houses.
  - Placidus unstable behavior.
  - Reference chart comparison.
- Required candidate stories:
  - `CS-240`
  - `CS-241`
  - `CS-242`
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-241-audit-astronomical-accuracy-audit.md`
  - `docs/recherches astro/2026-05-23-audit-calcul-theme-astral-post-cs-236.md`
  - `backend/app/domain/astrology`
  - `backend/app/core/ephemeris.py`
  - `backend/app/tests/golden`
- Comparison after implementation:
  - Latest child folder under `_condamad/audits/astro-astronomical-accuracy/`.
- Expected invariant:
  - The only intended repository delta is the new audit folder and its standard CONDAMAD audit files.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Astronomical accuracy audit | `_condamad/audits/astro-astronomical-accuracy/` | `backend/app/**` |
| Evidence log | `_condamad/audits/astro-astronomical-accuracy/` | `backend/tests/**` |
| Story candidates | `_condamad/audits/astro-astronomical-accuracy/` | `_condamad/stories/**` |
| Golden chart recommendations | `_condamad/audits/astro-astronomical-accuracy/` | New tests under `backend/**` |
| Ephemeris evidence requirement | `_condamad/audits/astro-astronomical-accuracy/` | Runtime config edits |

## Mandatory Reuse / DRY Constraints

- Reuse existing Python source, config surfaces, tests, golden datasets, and docs as source evidence.
- Use one canonical verification-point name across all six audit files.
- Use one candidate-story vocabulary across report, evidence log, findings, candidates, risk matrix, and summary.
- Do not duplicate large source excerpts; cite bounded files, symbols, test paths, generated artifacts, and scan commands.
- Do not add external packages or custom audit tooling.

## No Legacy / Forbidden Paths

- No legacy route path may be added during this audit.
- No compatibility route path may be added during this audit.
- No fallback route path may be added during this audit.
- Do not create app-code aliases, shims, runtime fallback branches, or compatibility wrappers.
- Do not remove the simplified engine during this audit.
- Do not add golden tests, change production configuration, edit ephemeris settings, or alter calculation behavior.
- Do not add API routes, serializers, frontend screens, admin/debug handlers, seed data, migrations, or runtime validation code.

## Reintroduction Guard

- Forbidden app-code delta:
  - `backend/app/**`
  - `backend/tests/**`
  - `backend/app/tests/**`
  - `backend/migrations/**`
  - `docs/db_seeder/**`
  - `frontend/src/**`
- Required guard:
  - `git diff --name-only` must show only the audit folder for implementation changes.
  - `rg` must prove accuracy findings are documented in audit artifacts, not implemented as runtime or test changes.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Local anti-drift: no API router change belongs to this audit. | `git diff --name-only`; bounded `rg`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Applicable pattern: candidate validation paths must be concrete. | `rg` over `03-story-candidates.md`. |
| Registry gap | No exact astronomical accuracy audit guardrail was present in the resolver output. | Resolver output reviewed. |

Non-applicable examples retained to prevent scope drift:

- RG-047 frontend inline styles are out of scope because no frontend files are touched.
- RG-052 frontend CSS namespace convergence is out of scope because no styling files are touched.
- RG-041 entitlement documentation is out of scope because astronomical accuracy, not billing entitlement, is audited.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit report | `_condamad/audits/astro-astronomical-accuracy/{audit-timestamp}/00-audit-report.md` | Reliability analysis and golden charts. |
| Evidence log | `_condamad/audits/astro-astronomical-accuracy/{audit-timestamp}/01-evidence-log.md` | Reproducible proof by verification point. |
| Finding register | `_condamad/audits/astro-astronomical-accuracy/{audit-timestamp}/02-finding-register.md` | Precision and guarantee gaps. |
| Story candidates | `_condamad/audits/astro-astronomical-accuracy/{audit-timestamp}/03-story-candidates.md` | Prioritized CS-240 through CS-242. |
| Risk matrix | `_condamad/audits/astro-astronomical-accuracy/{audit-timestamp}/04-risk-matrix.md` | Precision and reproducibility risks. |
| Executive summary | `_condamad/audits/astro-astronomical-accuracy/{audit-timestamp}/05-executive-summary.md` | Decision summary. |
| Review output | `_condamad/stories/CS-241-audit-astronomical-accuracy/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this documentation-only audit.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/astro-astronomical-accuracy/{audit-timestamp}/00-audit-report.md` - reliability analysis and golden charts.
- `_condamad/audits/astro-astronomical-accuracy/{audit-timestamp}/01-evidence-log.md` - reproducible evidence.
- `_condamad/audits/astro-astronomical-accuracy/{audit-timestamp}/02-finding-register.md` - precision and guarantee gaps.
- `_condamad/audits/astro-astronomical-accuracy/{audit-timestamp}/03-story-candidates.md` - prioritized CS-240 through CS-242.
- `_condamad/audits/astro-astronomical-accuracy/{audit-timestamp}/04-risk-matrix.md` - precision and reproducibility risk classification.
- `_condamad/audits/astro-astronomical-accuracy/{audit-timestamp}/05-executive-summary.md` - decision summary.

Likely tests:

- Document validation through `condamad_domain_audit_validate.py`.
- Document lint through `condamad_domain_audit_lint.py`.
- Targeted `rg` checks against latest audit artifacts.
- `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py` for existing timezone contract evidence.
- `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` for existing natal result contract evidence.

Files not expected to change:

- `backend/app/**` - out of scope; no backend runtime is touched.
- `backend/tests/**` - out of scope; no test code is touched.
- `backend/app/tests/**` - out of scope; no golden test code or dataset is touched.
- `docs/db_seeder/**` - out of scope; no seed or reference data is touched.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-astronomical-accuracy | Sort-Object Name -Descending | Select-Object -First 1`
- VC2: `rg -n "swisseph|ephemeris|calculate_planet_positions|calculate_houses|timezone|UTC|ayanamsa|topocentric|placidus" backend/app backend/tests docs`
- VC3: `rg -n "Paris|DST|Lahiri|topocentric|Placidus|whole sign" "$($auditFolder.FullName)\00-audit-report.md"`
- VC4: `rg -n "CS-240|CS-241|CS-242|priority|priorité" "$($auditFolder.FullName)\03-story-candidates.md"`
- VC5: `rg -n "precision|reproductibility|reproductibilité|architecture|guarantee|garantie" "$($auditFolder.FullName)\02-finding-register.md"`
- VC6: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py $auditFolder.FullName`
- VC7: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py $auditFolder.FullName`
- VC8: `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`
- VC9: `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- VC10: `python -c "from pathlib import Path; p=max(Path('_condamad/audits/astro-astronomical-accuracy').iterdir()); assert (p/'00-audit-report.md').exists()"`
- VC11: `git diff --name-only`

Before VC6, VC7, VC8, VC9, and VC10, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The audit may overstate reliability by treating `swisseph` imports or datasets as proof of production use.
- The audit may understate risk by ignoring timezone ambiguity, nonexistent local times, UT versus TT, or high-latitude house instability.
- Ephemeris evidence may be recorded without a reproducible version or hash requirement.
- Golden chart recommendations may drift into test implementation instead of audit planning.
- A developer may accidentally change app code, tests, config, or seed data while producing audit artifacts.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all audit artifacts under the latest `_condamad/audits/astro-astronomical-accuracy/` child folder.
- Treat `swisseph` reliability as proven only by actual runtime path, configuration evidence, and deterministic proof.
- Treat ephemeris reliability as incomplete without version and hash evidence or a documented evidence gap.
- Treat every golden chart as an audit recommendation with objective, input profile, expected evidence, and follow-up story link.
- Do not modify backend, frontend, migration, seed, serializer, dataclass, validator, graph, golden test, or calculator files.

## References

- `_story_briefs/cs-241-audit-astronomical-accuracy-audit.md`
- `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md`
- `_condamad/stories/CS-240-audit-reference-governance/00-story.md`
- `docs/recherches astro/2026-05-23-audit-calcul-theme-astral-post-cs-236.md`
- `backend/app/domain/astrology/swisseph_runtime.py`
- `backend/app/core/ephemeris.py`
- `backend/app/tests/golden/pro_dataset_v1.json`
- `_condamad/stories/regression-guardrails.md`
