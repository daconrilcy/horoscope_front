# Story CS-322 rapports-evidence-plan-plausible-reconciliation: Reconcile Reports And Evidence After Plan/Plausible Decisions
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-322-reconcilier-rapports-evidence-apres-decision-plan-plausible.md`.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: earlier closure reports still describe a backend/product divergence and Plausible/Matomo target after CS-320 and CS-321 decisions.
- Source stakes: keep closure history understandable, align current delivery language, and avoid any application runtime change.
- Source-alignment evidence: PASS; the story maps every brief concern to report, evidence, scan, and no-runtime-change proof.

## Objective

Reconcile targeted CONDAMAD reports, architecture notes, briefs, and final evidence so they reflect the current decisions:
all plans calculate and interpret, commercial differentiation is LLM/front shaping, and Plausible is the analytics preparation target.

The implementation must preserve historical traceability while removing obsolete current-status wording from the targeted closure artifacts.

## Target State

- `_condamad/reports/CS-312-CS-316-delivery-report.md` no longer treats all-plan `client_interpretation_projection_v1` availability as a divergence.
- Current delivery language states that backend execution aligns with the product decision for `free`, `basic`, and `premium`.
- Follow-up language points to CS-320 for LLM/front differentiation and to CS-321/CS-323 for Plausible and Matomo code removal.
- Targeted evidence or closure notes are updated only where they present a superseded decision as current state.
- A reconciliation journal exists under the CS-322 story capsule.
- Backend, frontend, tests, migrations, build tooling, auth, i18n, style, and provider runtime code stay unchanged.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-322-reconcilier-rapports-evidence-apres-decision-plan-plausible.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-322`.
- Evidence 3: `_condamad/reports/CS-312-CS-316-delivery-report.md` - report still contains routed backend follow-up wording.
- Evidence 4: `docs/architecture/natal-projection-plan-matrix-product-decision.md` - current plan decision read.
- Evidence 5: `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md` - follow-up already reoriented to LLM/front.
- Evidence 6: `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md` - current LLM/front differentiation source read.
- Evidence 7: `_story_briefs/cs-321-preparer-integration-plausible-analytics.md` - Plausible-first analytics decision read.
- Evidence 8: `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/generated/10-final-evidence.md` - stale closure wording inspected.
- Evidence 9: `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md` - provider limitation wording inspected.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - scoped resolver output selected no local exact guardrail for this docs-only story.
- Source-alignment review result: PASS; no source concern is narrowed into runtime work or deferred without a named follow-up.

## Domain Boundary

- Domain: condamad-reporting-evidence
- In scope:
  - Reconcile CS-312 to CS-316 delivery report wording.
  - Reconcile targeted closure evidence or notes that still state an obsolete plan or provider decision as current.
  - Persist a CS-322 reconciliation journal under the story capsule.
  - Run targeted scans over `_condamad/reports`, `docs/architecture`, `_story_briefs`, and selected final evidence files.
  - Prove no backend or frontend runtime files changed.
- Out of scope:
  - Backend API, services, domain code, DB schema, migrations, frontend UI, auth, i18n, styling, build tooling, and provider runtime.
  - Activating Plausible, configuring Matomo, adding dashboards, or changing analytics event emission.
  - Implementing CS-320 LLM/front differentiation or CS-323 Matomo code removal.
  - Registry enrichment for `_condamad/stories/regression-guardrails.md`.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS, browser validation, or UI state change.
  - No backend route, entitlement behavior, projection builder, provider adapter, persistence, migration, or test behavior change.
  - No rewrite of historical facts; only current-status wording and forward-looking closure notes may be reconciled.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a CONDAMAD report and evidence reconciliation contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only targeted reports, targeted final evidence notes, CS-322 evidence, and story tracker metadata.
  - Keep runtime application files and tests unchanged.
  - Preserve historical delivery context while correcting current decision wording.
  - Keep Plausible as the preparation target and Matomo as not currently used.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a targeted artifact records a still-active owner decision that conflicts with CS-320 or CS-321.
- Additional validation rules:
  - The report must state that `client_interpretation_projection_v1` remains available for `free`, `basic`, and `premium`.
  - The report must point follow-up work to CS-320, CS-321, and CS-323 rather than backend entitlement restriction.
  - Provider wording must distinguish repo-local closure, Plausible preparation, and Matomo not currently used.
  - A targeted `git diff --name-only` check must prove no backend or frontend runtime file changed.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `git diff`, targeted `rg`, and unchanged app paths prove this is a reporting-only change. |
| Baseline Snapshot | yes | Before/after report and scan artifacts prove the allowed wording delta. |
| Ownership Routing | yes | Reports, story evidence, and architecture notes have distinct canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this reconciliation. |
| Contract Shape | yes | The reconciliation journal needs exact decision, artifact, change, and evidence fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Stale wording and runtime drift must stay absent from targeted surfaces. |
| Persistent Evidence | yes | Scan outputs, diff proof, and the reconciliation journal must be kept for review. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | CS-312 to CS-316 report uses current plan wording. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks stale plan phrases in `_condamad/reports`. |
| AC2 | The report states backend all-plan alignment. | Evidence profile: json_contract_shape; `rg` checks all-plan terms in the report. |
| AC3 | Current follow-up routing is explicit. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks follow-up references. |
| AC4 | Provider wording is Plausible-first. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks Plausible and Matomo wording in targeted docs. |
| AC5 | Runtime files stay unchanged. | Evidence profile: no_legacy_contract; `python` records scoped diff; `AST guard`. |
| AC6 | Reconciliation journal is persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-322 evidence journal path. |
| AC7 | Stale contradiction scans are clean. | Evidence profile: repo_wide_negative_scan; `rg` scans targeted report, docs, briefs, and evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect the source brief and the seven prerequisite artifacts named in the brief. (AC: AC1, AC2, AC3, AC4)
- [ ] Task 2: Capture a targeted before-scan for stale plan and provider wording. (AC: AC7)
- [ ] Task 3: Update the CS-312 to CS-316 delivery report with current plan and Plausible-first decisions. (AC: AC1, AC2, AC3, AC4)
- [ ] Task 4: Update only targeted closure evidence notes that present superseded decisions as current. (AC: AC1, AC4)
- [ ] Task 5: Create the CS-322 reconciliation journal with artifact-level decisions and evidence links. (AC: AC6)
- [ ] Task 6: Run the targeted stale wording scans and provider wording scans. (AC: AC7)
- [ ] Task 7: Prove backend and frontend runtime paths are unchanged. (AC: AC5)
- [ ] Task 8: Persist validation output under the CS-322 story capsule. (AC: AC6, AC7)

## Files to Inspect First

- `_story_briefs/cs-322-reconcilier-rapports-evidence-apres-decision-plan-plausible.md` - source brief.
- `_condamad/reports/CS-312-CS-316-delivery-report.md` - primary report to reconcile.
- `docs/architecture/natal-projection-plan-matrix-product-decision.md` - current product plan decision.
- `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md` - already reoriented follow-up.
- `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md` - LLM/front differentiation source.
- `_story_briefs/cs-321-preparer-integration-plausible-analytics.md` - Plausible preparation source.
- `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/generated/10-final-evidence.md` - targeted closure evidence.
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md` - targeted provider evidence.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `git diff --name-only -- backend frontend` for unchanged runtime surfaces.
  - `AST guard` status from scoped diff inspection over backend and frontend runtime paths.
  - `app.routes` and `app.openapi()` are deliberately unchanged because this story does not edit backend app files.
  - Targeted `rg` scans over `_condamad/reports`, `docs/architecture`, `_story_briefs`, and selected generated final evidence files.
  - The CS-322 reconciliation journal under `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/`.
- Secondary evidence:
  - `git diff --check` for whitespace integrity.
  - `ruff check .` and `pytest -q` only when Python validation is requested for broader repository confidence with the venv active.
- Static scans alone are not sufficient for this story because scoped diff evidence must prove runtime surfaces are unchanged.

## Contract Shape

- Contract type:
  - CONDAMAD report and evidence reconciliation artifact.
- Fields:
  - `artifact_path`: targeted report, brief, architecture note, or final evidence path.
  - `decision_topic`: plan-availability, differentiation-owner, analytics-provider, or closure-status.
  - `before_term`: stale wording or classification found before the update.
  - `after_term`: current wording aligned to CS-320, CS-321, or CS-323.
  - `evidence_command`: `rg`, `git diff`, or `python` command proving the row.
  - `runtime_surface`: always `unchanged` for backend and frontend paths.
- Required fields:
  - `artifact_path`
  - `decision_topic`
  - `after_term`
  - `evidence_command`
  - `runtime_surface`
- Optional fields:
  - `before_term`
  - `owner_note`
- Required sections:
  - source decisions;
  - artifact reconciliation ledger;
  - stale wording scan results;
  - provider wording scan results;
  - no-runtime-change proof.
- Status codes:
  - none; this is not an API route.
- Serialization names:
  - Markdown table columns stay stable for CONDAMAD review.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/stale-wording-before.txt`
  - `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/report-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/stale-wording-after.txt`
  - `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/report-after.md`
  - `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/reconciliation-journal.md`
  - `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/validation.txt`
- Expected invariant:
  - The only intended repository delta is targeted CONDAMAD report/evidence wording, CS-322 evidence, and tracker status.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Delivery status wording | `_condamad/reports/CS-312-CS-316-delivery-report.md` | backend or frontend source |
| Product plan decision | `docs/architecture/natal-projection-plan-matrix-product-decision.md` | React entitlement matrix |
| LLM/front differentiation follow-up | `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md` | backend access restriction |
| Plausible preparation follow-up | `_story_briefs/cs-321-preparer-integration-plausible-analytics.md` | Matomo runtime activation |
| Matomo code removal follow-up | future CS-323 brief or story | CS-322 runtime implementation |
| Reconciliation evidence | CS-322 `evidence/` directory | application test folders |

## Mandatory Reuse / DRY Constraints

- Reuse CS-320 as the source for plan-aware LLM/front differentiation wording.
- Reuse CS-321 as the source for Plausible preparation wording.
- Reuse the existing CS-312 to CS-316 delivery report instead of creating a parallel report.
- Use one CS-322 reconciliation journal for artifact-level decisions and scan evidence.
- Do not add external packages, runtime files, tests, migrations, providers, routes, services, components, styles, or build outputs.

## No Legacy / Forbidden Paths

- No legacy backend entitlement follow-up may be introduced for `client_interpretation_projection_v1`.
- No compatibility wording may preserve a current product/backend divergence after CS-320.
- No fallback analytics target may present Plausible/Matomo as a shared current preparation target.
- Do not create aliases, shims, wrappers, provider adapters, dashboards, or parallel report files.
- Forbidden surfaces:
  - `backend/**`
  - `frontend/**`
  - `shared/**`
  - migration folders
  - build outputs
  - `_condamad/stories/regression-guardrails.md`

## Reintroduction Guard

- Guard target:
  - current reports must not reintroduce `Delivered with routed backend follow-up` for the CS-315 plan decision;
  - current reports must not reintroduce `product/backend divergence` or `premium-only` as the active access model;
  - provider wording must not reintroduce `Plausible/Matomo` as a shared preparation target;
  - backend and frontend runtime paths must remain outside the diff.
- Guard mechanism:
  - targeted `rg` stale wording scans;
  - targeted `rg` Plausible/Matomo scans;
  - `git diff --name-only -- _condamad/reports docs/architecture _story_briefs backend frontend`;
  - `git diff --check`.
- Guard owner:
  - `_condamad/reports/CS-312-CS-316-delivery-report.md`;
  - CS-322 reconciliation journal and validation transcript.
- Guard evidence:
  - `rg -n "premium-only|refus.*free|refus.*basic|routed backend follow-up|product/backend divergence|Plausible/Matomo" _condamad/reports docs/architecture _story_briefs`;
  - `git diff --name-only -- _condamad/reports docs/architecture _story_briefs backend frontend`.

## Regression Guardrails

Scope vector:

- CONDAMAD report and final evidence wording: yes;
- architecture decision note and story briefs: yes;
- backend implementation: no;
- frontend implementation: no;
- DB, auth, i18n, style, build, migration, and analytics runtime: no.

Selected guardrails:

| Guardrail | Applicability | Evidence |
|---|---|---|
| Story-local report guard | Current delivery language must match CS-320 and CS-321 decisions. | targeted `rg`; journal. |
| Story-local no-runtime guard | Backend and frontend runtime paths stay outside the diff. | `git diff --name-only`. |
| Registry gap | Resolver returned no exact report/evidence reconciliation guardrail. | resolver output in validation. |

Non-applicable examples that prevent scope drift:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is not selected because the change is a report reconciliation, not policy redesign.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Report before snapshot | `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/report-before.md` | Preserve the starting report state. |
| Report after snapshot | `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/report-after.md` | Preserve the reconciled report state. |
| Stale wording before scan | `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/stale-wording-before.txt` | Prove initial stale terms. |
| Stale wording after scan | `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/stale-wording-after.txt` | Prove targeted stale terms are gone. |
| Reconciliation journal | `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/reconciliation-journal.md` | Track artifact-level decisions. |
| Validation log | `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/validation.txt` | Keep final validation commands and results. |
| Review output | `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this reconciliation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/reports/CS-312-CS-316-delivery-report.md` - reconcile current delivery language.
- `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/generated/10-final-evidence.md` - reconcile targeted stale closure note.
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md` - reconcile provider target wording only.
- `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/**` - persist journal and validations.
- `_condamad/stories/story-status.md` - register CS-322 status.

Likely tests:

- `backend/tests/api/test_projection_real_conditions.py` - existing runtime parity evidence may be rerun unchanged.
- `frontend/src/tests/useAnalytics.test.tsx` - existing analytics provider evidence may be rerun unchanged.
- No test source is expected to change; these paths are validation owners only.

Files not expected to change:

- `backend/**` - out of scope; no backend runtime, tests, migrations, or scripts are touched.
- `frontend/**` - out of scope; no frontend runtime, tests, CSS, package files, or build output are touched.
- `shared/**` - out of scope; no shared contracts are touched.
- `_condamad/stories/regression-guardrails.md` - out of scope; normal story generation must not enrich the registry.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `. .\.venv\Scripts\Activate.ps1`
- VC2: `rg -n "premium-only|refus.*free|refus.*basic|routed backend follow-up|product/backend divergence|Plausible/Matomo" _condamad/reports docs/architecture _story_briefs`
- VC3: `rg -n "Plausible|Matomo|noop|client_interpretation_projection_v1|free|basic|premium" _condamad/reports/CS-312-CS-316-delivery-report.md`
- VC4: `rg -n "Plausible|Matomo|client_interpretation_projection_v1|free|basic|premium" docs/architecture/natal-projection-plan-matrix-product-decision.md`
- VC5: `rg -n "Plausible|Matomo|client_interpretation_projection_v1|free|basic|premium" _story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md`
- VC6: `rg -n "CS-320|CS-321|CS-323|LLM|front|Plausible" _condamad/reports/CS-312-CS-316-delivery-report.md`
- VC7: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/reconciliation-journal.md').exists()"`
- VC8: `git diff --check`
- VC9: `git diff --name-only -- _condamad/reports docs/architecture _story_briefs backend frontend`
- VC10: `ruff check .`
- VC11: `pytest -q`

Before VC7, VC10, and VC11, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The report could rewrite history instead of clarifying the current decision.
- A closure artifact could still point maintainers toward backend entitlement restriction instead of CS-320 plan-aware shaping.
- Provider wording could keep Matomo as an active preparation target despite CS-321 choosing Plausible.
- A docs-only reconciliation could drift into backend, frontend, analytics runtime, or test changes.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep report edits factual: preserve historical context and correct only current decision or next-action wording.
- Do not modify backend, frontend, shared, migration, package, build, provider runtime, or test source files.
- Do not enrich `_condamad/stories/regression-guardrails.md`.

## References

- `_story_briefs/cs-322-reconcilier-rapports-evidence-apres-decision-plan-plausible.md`
- `_condamad/reports/CS-312-CS-316-delivery-report.md`
- `docs/architecture/natal-projection-plan-matrix-product-decision.md`
- `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md`
- `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md`
- `_story_briefs/cs-321-preparer-integration-plausible-analytics.md`
- `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/generated/10-final-evidence.md`
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
