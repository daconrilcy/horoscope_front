# Story CS-338 cloturer-extinction-legacy-injection-llm-natale: Close Natal LLM Legacy Injection Extinction
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-338-cloturer-extinction-legacy-injection-llm-natale.md`.
- Related prerequisites: CS-336 and CS-337 are source prerequisites for this closure story.
- Mandatory source reads:
  - `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md`.
  - `_story_briefs/cs-337-supprimer-tests-et-mocks-legacy-injection-llm.md`.
  - `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`.
- Selected mode: Repo-informed story, because the closure report must cite current backend surfaces and test paths.
- Source alignment evidence: this story closes the brief stake by requiring a final report proving that only
  `llm_astrology_input_v1` feeds the natal LLM prompt path.

## Objective

Verify and document that `llm_astrology_input_v1` is the only active interpreted astrology input for the natal LLM path.
The implementation must audit code, tests, prompt schemas, registries, and documentation, then persist a final closure report.

## Target State

- One final report exists under `_condamad/reports/extinction-legacy-injection-llm-natale/2026-05-27-0000/`.
- The report classifies every remaining `chart_json`, `natal_data`, `evidence_catalog`, `legacy`, and `fallback` reference.
- The runtime natal LLM path rejects hidden parallel carriers and proves `llm_astrology_input_v1` as the canonical input.
- Backend tests and architecture guards cover the modern path without maintaining obsolete natal LLM mocks.
- Documentation no longer describes `chart_json` or `natal_data` as active natal LLM input.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-338-cloturer-extinction-legacy-injection-llm-natale.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-338`.
- Evidence 3: `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md` - prerequisite removal scope read.
- Evidence 4: `_story_briefs/cs-337-supprimer-tests-et-mocks-legacy-injection-llm.md` - prerequisite test cleanup scope read.
- Evidence 5: `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`.
- Evidence 6: targeted `rg` found active inspection points in `backend/app/domain/llm/runtime/gateway.py`.
- Evidence 7: targeted `rg` found natal service entry points in `backend/app/services/llm_generation/natal/interpretation_service.py`.
- Evidence 8: targeted `rg` found current guard paths such as `backend/tests/integration/test_llm_legacy_extinction.py`.
- Evidence 9: guardrails resolved with `resolve_guardrails.py` for backend-domain, LLM runtime, no-legacy, and persistent evidence scope.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend LLM runtime audit for the natal prompt input path.
  - Backend tests, prompts, input schemas, and use-case registries tied to natal LLM injection.
  - Final validation report generation under `_condamad/reports`.
  - Documentation correction only when it describes obsolete natal LLM input as active.
- Out of scope:
  - Frontend UI, public endpoints, database schema, auth, i18n, styling, build tooling, and migrations.
  - Editorial prompt wording changes unrelated to input carrier ownership.
  - New LLM features, provider behavior, retries, security policy, or astrologer profile behavior.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No compatibility route, adapter, alias, shim, or fallback may be introduced.
  - No broad rewrite of unrelated LLM prompt-generation behavior.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story closes removal of old natal LLM carrier facades and forbids preserving them.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Only remove or classify residual natal LLM carrier surfaces found by the closure audit.
  - Only update documentation that still presents obsolete natal LLM carriers as active.
  - Only add or update deterministic guards proving the single `llm_astrology_input_v1` path.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: a remaining reference is externally active or product-owned outside the natal LLM path.
- Additional validation rules:
  - The final report must distinguish textual historical references from runtime-executed natal LLM input.
  - Runtime proof must include `AST guard`, loaded config evidence, or `pytest -q backend/tests/integration/test_llm_legacy_extinction.py`.
  - The closure cannot be marked complete with unclassified matches for the required scan terms.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `AST guard`, loaded LLM config, and targeted `pytest` prove the active natal LLM input path. |
| Baseline Snapshot | yes | Before and after scan artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Residual references need canonical ownership classification. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this closure story. |
| Contract Shape | yes | The report has required sections and classification values. |
| Batch Migration | no | No batch migration or multi-domain conversion is in scope. |
| Reintroduction Guard | yes | Legacy carriers must not return to the natal LLM path. |
| Persistent Evidence | yes | Closure artifacts must be retained for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The final closure report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path pattern. |
| AC2 | The report proves a single natal LLM input path. | Evidence profile: no_legacy_contract; `pytest -q backend/tests/integration/test_llm_legacy_extinction.py`. |
| AC3 | Remaining legacy terms are classified. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scan output is classified in the report. |
| AC4 | Backend tests run without obsolete natal LLM mocks. | Evidence profile: no_legacy_contract; `pytest -q backend/tests --tb=short`. |
| AC5 | Modern guards cover `llm_astrology_input_v1`. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/integration/test_llm_legacy_extinction.py`. |
| AC6 | Documentation stops presenting old carriers as active. | Evidence profile: repo_wide_negative_scan; `rg` scans `_condamad` and `_story_briefs`. |
| AC7 | Reintroduction guard blocks old carriers. | Evidence profile: reintroduction_guard; `AST guard` plus `rg` verify forbidden active usage. |
| AC8 | External ambiguity blocks closure. | Evidence profile: external_usage_blocker; `rg` plus `Manual check:` list blockers and owner. |

## Implementation Tasks

- [ ] Task 1: Read the mandatory CS-336, CS-337, and transition report sources before editing. (AC: AC1, AC2)
- [ ] Task 2: Audit `backend/app/domain/llm/runtime/gateway.py` for active natal input carrier behavior. (AC: AC2, AC7)
- [ ] Task 3: Audit `backend/app/domain/llm/runtime/contracts.py` for carrier ownership and schema shape. (AC: AC2, AC3)
- [ ] Task 4: Audit `backend/app/domain/llm/configuration/canonical_use_case_registry.py` for natal schema carriers. (AC: AC2, AC3)
- [ ] Task 5: Audit `backend/app/domain/llm/prompting/prompt_renderer.py` for natal placeholder behavior. (AC: AC2, AC3)
- [ ] Task 6: Audit `backend/app/services/llm_generation/natal/interpretation_service.py` for natal runtime wiring. (AC: AC2, AC7)
- [ ] Task 7: Audit backend tests for obsolete mocks, fixtures, and expectations tied to old natal LLM carriers. (AC: AC3, AC4)
- [ ] Task 8: Add or update deterministic guards proving old carriers cannot feed the natal LLM path. (AC: AC5, AC7)
- [ ] Task 9: Update documentation that still presents old carriers as active natal LLM input. (AC: AC6)
- [ ] Task 10: Produce the final closure report with scan outputs, classification, validation commands, and residual risks. (AC: AC1, AC3, AC8)

## Files to Inspect First

- `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md`
- `_story_briefs/cs-337-supprimer-tests-et-mocks-legacy-injection-llm.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/contracts.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/integration/test_llm_legacy_extinction.py`
- `backend/tests/integration/test_llm_runtime_suppression.py`
- `backend/app/tests/unit/test_gateway_input_validation_payload.py`

## Runtime Source of Truth

- Primary source of truth:
  - `AST guard`, loaded LLM use-case configuration, and targeted `pytest` over the backend runtime tests.
- Secondary evidence:
  - Targeted `rg` scans for `chart_json`, `natal_data`, `evidence_catalog`, `legacy`, `fallback`, and `transition-condition`.
- Static scans alone are not sufficient for this story because:
  - The closure must prove whether a remaining reference is executed by the natal LLM path.

## Contract Shape

- Contract type:
  - Final closure report and backend runtime guard contract.
- Fields:
  - `classification`: one allowed classification value for each residual term.
  - `proof`: command output, file path, or source artifact proving the classification.
  - `risk`: residual risk for every deletion or user-decision item.
- Required fields:
  - `Item`, `Type`, `Classification`, `Consumers`, `Canonical replacement`, `Decision`, `Proof`, and `Risk`.
- Optional fields:
  - none
- Status codes:
  - none; no API status code changes are authorized.
- Serialization names:
  - report table headers are emitted exactly as required by `Removal Audit Format`.
- Frontend type impact:
  - none; no frontend type or generated client is in scope.
- Required report sections:
  - `Resume de l'etat final`
  - `Surfaces legacy supprimees`
  - `Tests et mocks legacy supprimes`
  - `References restantes et justification`
  - `Preuves du chemin unique llm_astrology_input_v1`
  - `Commandes de validation executees`
  - `Risques residuels`
- Classification values:
  - `hors-chemin-llm-ownerise`
  - `garde-negative`
  - `archive-documentaire`
  - `dette-a-supprimer-avant-cloture`
  - `decision-utilisateur-requise`
- Generated contract impact:
  - No OpenAPI, generated client, or public API contract change is authorized.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/evidence/legacy-scan-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/evidence/legacy-scan-after.txt`
- Expected invariant:
  - The only allowed surface delta is removal or documented reclassification of natal LLM legacy carrier usage.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Natal LLM input carrier | `backend/app/domain/llm/runtime/contracts.py` | Prompt placeholders named `chart_json` or `natal_data` |
| Natal LLM runtime wiring | `backend/app/domain/llm/runtime/gateway.py` | Service-local carrier reconstruction |
| Natal use-case schema | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | Test-only schema aliases |
| Closure report | `_condamad/reports/extinction-legacy-injection-llm-natale/2026-05-27-0000/validation-extinction-legacy.md` | Story file only |

## Mandatory Reuse / DRY Constraints

- Reuse existing LLM runtime contracts and test helpers instead of creating a parallel carrier contract.
- Reuse existing backend test locations for LLM runtime and integration guards.
- Reuse existing report conventions under `_condamad/reports`.
- Do not duplicate scan logic across unrelated tests; centralize reusable guard helpers in the smallest existing test module.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy natal LLM input carrier may remain active.
- No compatibility path may feed the natal LLM prompt.
- No fallback path may reconstruct `llm_astrology_input_v1` from obsolete carriers.
- Forbidden active input carriers:
  - `chart_json`
  - `natal_data`
  - `evidence_catalog` derived from `chart_json`
  - `transition-condition`
- Forbidden implementation routes:
  - wrappers that preserve obsolete natal LLM input behavior;
  - aliases that make old carrier names accepted by the prompt path;
  - mocks that recreate old carrier behavior to keep tests green.

## Removal Classification Rules

- `canonical-active`: reference is the canonical `llm_astrology_input_v1` path or a required modern guard.
- `external-active`: reference is externally consumed by public docs, generated artifacts, or product-owned contracts.
- `historical-facade`: reference preserves old carrier behavior for the natal LLM path.
- `dead`: reference has no production, test, documentation, generated contract, or known external consumer.
- `needs-user-decision`: reference cannot be classified after all required scans.

## Removal Audit Format

The final report must include this table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

- Allowed decisions are `keep`, `delete`, `replace-consumer`, and `needs-user-decision`.
- Every `delete` or `needs-user-decision` item must include a concrete risk.
- The report must state why each kept reference is outside active natal LLM input execution.
- Persisted audit artifact: the table must be written inside the final closure report path.

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Natal LLM input | `llm_astrology_input_v1` | `chart_json`, `natal_data`, `evidence_catalog` as prompt carrier |
| Runtime composition | `LLMGateway` typed request path | `_legacy_dicts_to_request` feeding natal prompt execution |
| Prompt variables | Modern use-case schema | `required_prompt_placeholders` requiring `chart_json` for natal use cases |
| Evidence and audit | Final report plus backend guards | Unclassified textual matches |

## Delete-Only Rule

- A removable old carrier must be deleted, not repointed.
- Do not redirect old carrier names to the modern contract.
- Do not preserve wrappers, aliases, re-export paths, shims, or soft-disabled old paths.
- Do not replace deletion with runtime branching that keeps the old name accepted.

## External Usage Blocker

- External usage blocker: active
- Blocking rule: a reference classified as `external-active` must not be deleted without a user decision.
- Required evidence: the report must name the external surface, consumer, deletion risk, and safest next action.

## Generated Contract Check

- Generated contract check: active
- Required check:
  - Loaded LLM use-case configuration must not expose old natal LLM carriers as generated prompt input schema.
- Evidence:
  - `python` or `pytest` must inspect the loaded configuration and persist the result in the final report.

## Reintroduction Guard

- The implementation must require an architecture guard so old natal LLM carriers cannot be reintroduced.
- Add or update deterministic guards that fail when old natal LLM carriers become active again.
- Guard must inspect at least one deterministic source:
  - `AST guard` over backend runtime code;
  - forbidden symbols or states;
  - loaded use-case configuration;
  - targeted `pytest` exercising natal LLM execution.
- Required forbidden active symbols:
  - `chart_json` as natal prompt input;
  - `natal_data` as natal prompt input;
  - `evidence_catalog` derived from `chart_json` as natal prompt input;
  - `_legacy_dicts_to_request` on the natal prompt execution path.

## Regression Guardrails

Scope vector:

- Operation: remove
- Domain: backend-domain
- Paths: `backend/app/domain/llm`, `backend/app/services/llm_generation/natal`, `backend/tests`
- Contracts: no-legacy, runtime-source-of-truth, persistent-evidence

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend routing must stay untouched by this backend-domain story. | `rg` targeted scan; no API file edits. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validation commands must target collected pytest files. | `pytest` targeted paths in plan. |
| Registry gap | No exact guardrail exists for natal LLM legacy carrier extinction. | Report gap in final evidence. |

Non-applicable examples:

- RG-047 frontend inline styles is out of scope because no frontend surface is touched.
- RG-052 frontend CSS migration namespaces is out of scope because no styling surface is touched.
- RG-041 entitlement documentation is out of scope because this story targets natal LLM carrier closure.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before scan | `_condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/evidence/legacy-scan-before.txt` | Capture initial residual references. |
| After scan | `_condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/evidence/legacy-scan-after.txt` | Capture final residual references. |
| Validation output | `_condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/evidence/validation-output.txt` | Persist commands run. |
| Closure report | `_condamad/reports/extinction-legacy-injection-llm-natale/2026-05-27-0000/validation-extinction-legacy.md` | Final closure proof. |
| Review output | `_condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist is authorized; every remaining term must be classified in the closure report.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/llm/runtime/gateway.py` - remove active old carrier handling from natal prompt execution.
- `backend/app/domain/llm/runtime/contracts.py` - remove old carrier schema acceptance from natal LLM input when active.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - remove natal prompt schema references to old carriers.
- `backend/app/domain/llm/prompting/prompt_renderer.py` - enforce prompt variable boundaries for natal use cases.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - ensure natal runtime wiring uses `llm_astrology_input_v1`.
- `backend/tests/integration/test_llm_legacy_extinction.py` - add or update the closure guard.
- `backend/tests/integration/test_llm_runtime_suppression.py` - keep runtime suppression coverage aligned.
- `_condamad/reports/extinction-legacy-injection-llm-natale/2026-05-27-0000/validation-extinction-legacy.md` - write report.
- `_condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/evidence/validation-output.txt` - persist validation output.

Likely tests:

- `backend/tests/integration/test_llm_legacy_extinction.py`
- `backend/tests/integration/test_llm_runtime_suppression.py`
- `backend/app/tests/unit/test_gateway_input_validation_payload.py`
- `backend/tests/llm_orchestration/test_llm_execution_request.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/alembic/**` - out of scope; no migration is touched.
- `backend/app/api/**` - out of scope unless a documentation import scan proves a direct blocker.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `pytest -q tests --tb=short`
- VC6: `pytest -q tests/integration/test_llm_legacy_extinction.py`
- VC7: `pytest -q tests/integration/test_llm_runtime_suppression.py`
- VC8: `pytest -q app/tests/unit/test_gateway_input_validation_payload.py`
- VC9: `rg -n "chart_json|natal_data|evidence_catalog|legacy|fallback|transition-condition" app tests ..\_condamad ..\_story_briefs`
- VC10: `rg -n "llm_astrology_input_v1" app tests ..\_condamad ..\_story_briefs`
- VC11: `python -c "from pathlib import Path; p=Path('..')/'_condamad'/'reports'/'extinction-legacy-injection-llm-natale'; assert p.exists()"`
- VC12: `python -c "from pathlib import Path; assert Path('tests/integration/test_llm_legacy_extinction.py').exists()"`

## Regression Risks

- Textual scan matches can be misread as active runtime behavior; the report must classify each reference.
- Removing too broadly can break non-LLM projections still owned outside this path.
- Retaining mocks can preserve obsolete behavior while making tests pass.
- Documentation drift can describe a double process as active after runtime convergence.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the venv before every Python, Ruff, or Pytest command.
- Keep the final report factual: classify residual terms, cite commands, and state blockers instead of hiding ambiguity.
- Do not update `_condamad/stories/regression-guardrails.md` during this implementation.

## References

- `_story_briefs/cs-338-cloturer-extinction-legacy-injection-llm-natale.md`
- `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md`
- `_story_briefs/cs-337-supprimer-tests-et-mocks-legacy-injection-llm.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `_condamad/stories/regression-guardrails.md#RG-002`
- `_condamad/stories/regression-guardrails.md#RG-022`
