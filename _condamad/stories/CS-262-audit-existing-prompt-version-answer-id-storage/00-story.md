# Story CS-262 audit-existing-prompt-version-answer-id-storage: Audit Existing Prompt Version And Answer Id Storage
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-262-audit-existing-prompt-version-answer-id-storage.md`.
- Related dependency: CS-259 defines the target `narrative_answer_audit_v1` audit contract.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: AI traceability storage may already exist for answer IDs, prompt versions, provider, model and prompt snapshots.
- Source-alignment evidence: PASS; the story preserves the audit-only objective, CS-259 comparison, no-app-change rule and migration-risk focus.

## Objective

Produce one targeted CONDAMAD audit of existing AI traceability storage before any new contract, builder, service, model, route or test is created.

The audit must classify the current repository support for `answer_id`, `prompt_version`, provider, model, full prompt retention and prompt reference storage.

## Target State

- A latest audit folder exists under `_condamad/audits/ai-traceability/`.
- `00-audit-report.md` classifies every CS-259-required storage field as `present`, `partial` or `absent`.
- `01-evidence-log.md` cites concrete code, DB model, migration, repository, service, route, test or doc locations for every classification.
- `02-finding-register.md` records gaps between existing storage and CS-259 `narrative_answer_audit_v1`.
- `03-story-candidates.md` lists follow-up stories only for verified gaps, with each candidate linked to a finding.
- `04-risk-matrix.md` lists migration and duplication risks before implementation work starts.
- `05-executive-summary.md` states whether the next implementation should extend existing surfaces or create new canonical storage.
- No application, test, frontend, DB migration, prompt, service, builder, model or route file is modified by this audit story.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-262-audit-existing-prompt-version-answer-id-storage.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-262`.
- Evidence 3: `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` - target audit contract read.
- Evidence 4: `backend/app/infra/db/models/llm/llm_observability.py` - scoped read found LLM call logs with prompt, provider and model metadata.
- Evidence 5: `backend/app/infra/db/models/user_natal_interpretation.py` - scoped read found persisted natal interpretation rows with `prompt_version_id`.
- Evidence 6: `backend/app/infra/db/models/llm/llm_audit.py` - scoped read found shared LLM audit timestamp helpers, not answer audit storage.
- Evidence 7: `backend/app/infra/db/repositories/llm/prompting_repository.py` - scoped inventory found a likely DB access owner for prompt data.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through `resolve_guardrails.py` and targeted ID lookup only.
- Evidence 9: `rg -l "answer_id|prompt_version|provider|model|prompt" backend/app backend/tests` - scoped inventory located candidate audit surfaces.
- Source-alignment review result: PASS; no source concern was narrowed into implementation or deferred without a recorded audit output.

## Domain Boundary

- Domain: backend-ai-traceability-audit
- In scope:
  - Static audit of backend models, repositories, services, routes, tests, migrations and docs related to AI answer traceability.
  - Classification of `answer_id`, `prompt_version`, provider, model, full prompt retention and prompt reference storage.
  - Gap comparison against CS-259 `narrative_answer_audit_v1`.
  - Migration-risk and duplication-risk analysis before implementation.
  - Documentation-only audit artifacts under `_condamad/audits/ai-traceability/`.
- Out of scope:
  - Frontend UI, public API exposure, DB schema edits, migrations, auth, i18n, styling, build tooling and generated clients.
  - Creating contracts, builders, services, models, routes, tests, prompt templates or provider integration.
  - Correcting gaps found by the audit.
  - Changing prompt content, GDPR retention policy or client-facing proof exposure.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No database table, migration, repository implementation, admin route or admin screen.
  - No prompt template change, LLM provider implementation or narrative renderer change.
  - No application source modification outside the audit artifacts.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend AI traceability audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Produce documentation artifacts only under the scoped audit folder.
  - Reuse CS-259 field names and existing repository terminology for traceability classification.
  - Keep backend runtime code, API routes, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Do not create parallel storage while an existing surface is only partially understood.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: repository evidence cannot determine whether a CS-259-required field is present, partial or absent.
- Additional validation rules:
  - The audit report must classify each required field from CS-259 as `present`, `partial` or `absent`.
  - The audit report must include `answer_id`, `prompt_version`, `provider`, `model`, full prompt retention and prompt reference storage.
  - The evidence log must cite concrete code, DB, migration, service, route, test or doc paths for every classification.
  - The finding register must separate storage gaps, prompt snapshot gaps, provider/model provenance gaps and migration risks.
  - The story candidates file must not invent implementation work without a linked finding.
  - Scoped status evidence must prove application source files stayed unchanged.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Existing DB models, repositories, services, tests and docs prove current traceability storage. |
| Baseline Snapshot | yes | The audit must persist a reproducible evidence baseline before any implementation follows. |
| Ownership Routing | yes | Audit artifacts and existing AI storage owners must stay separated from new app code. |
| Allowlist Exception | no | No allowlist handling is authorized for this documentation-only audit. |
| Contract Shape | yes | The audit has required files, classifications, fields and CS-259 comparison columns. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | The story must guard against adding storage, routes, prompts or migrations while auditing. |
| Persistent Evidence | yes | The audit folder itself is the review handoff evidence. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The latest audit folder exists. | Evidence profile: baseline_before_after_diff; `python` checks `_condamad/audits/ai-traceability`. |
| AC2 | All six standard audit files exist. | Evidence profile: baseline_before_after_diff; `python` checks required filenames in latest audit folder. |
| AC3 | CS-259 field coverage is classified. | Evidence profile: json_contract_shape; `rg` checks `present`, `partial` and `absent` in `00-audit-report.md`. |
| AC4 | `answer_id` storage is audited. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `answer_id` in report and evidence log. |
| AC5 | Prompt version storage is audited. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `prompt_version` in report and evidence log. |
| AC6 | Provider provenance is audited. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks provider fields in report and evidence log. |
| AC7 | Model provenance is audited. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks model fields in report and evidence log. |
| AC8 | Prompt retention is audited. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks full prompt, prompt_ref and snapshot terms. |
| AC9 | Backend paths are cited. | Evidence profile: ast_architecture_guard; AST guard and `rg` check backend paths. |
| AC10 | CS-259 gaps are registered. | Evidence profile: baseline_before_after_diff; `rg` checks CS-259 and narrative_answer_audit_v1 in findings. |
| AC11 | Migration risks are listed. | Evidence profile: baseline_before_after_diff; `rg` checks migration risk entries in `04-risk-matrix.md`. |
| AC12 | Application source stays unchanged. | Evidence profile: no_legacy_contract; `python` records scoped `git status --short` output. |

## Implementation Tasks

- [ ] Task 1: Create the latest audit folder under `_condamad/audits/ai-traceability/`. (AC: AC1)
- [ ] Task 2: Create the six standard audit files with cross-references and one classification vocabulary. (AC: AC2, AC3)
- [ ] Task 3: Inspect CS-259 and extract every required traceability field before auditing the repository. (AC: AC3, AC10)
- [ ] Task 4: Inventory backend AI answer, prompt, provider, model and snapshot storage surfaces with bounded scans. (AC: AC4, AC5, AC6, AC7, AC8)
- [ ] Task 5: Cite concrete code, DB, migration, service, route, test and documentation locations for every status. (AC: AC9)
- [ ] Task 6: Mark each CS-259-required field as `present`, `partial` or `absent`. (AC: AC3, AC4, AC5, AC6, AC7, AC8)
- [ ] Task 7: Register gaps between existing storage and `narrative_answer_audit_v1`. (AC: AC10)
- [ ] Task 8: List migration and duplication risks before implementation work starts. (AC: AC11)
- [ ] Task 9: Verify scoped status evidence proves no application source change. (AC: AC12)

## Files to Inspect First

- `_story_briefs/cs-262-audit-existing-prompt-version-answer-id-storage.md` - source contract.
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` - target field contract for comparison.
- `backend/app/infra/db/models/llm/llm_observability.py` - LLM call log and replay snapshot storage candidate.
- `backend/app/infra/db/models/llm/llm_prompt.py` - prompt version storage candidate.
- `backend/app/infra/db/models/llm/llm_release.py` - prompt release and snapshot storage candidate.
- `backend/app/infra/db/models/user_natal_interpretation.py` - persisted answer storage candidate.
- `backend/app/infra/db/repositories/llm/prompting_repository.py` - prompt data repository candidate.
- `backend/app/services/llm_generation/**` - generation and narrative service evidence surface.
- `backend/app/domain/llm/**` - runtime, prompting and configuration source evidence surface.
- `backend/tests/llm_orchestration/**` - LLM runtime test evidence surface.
- `backend/app/tests/integration/test_natal_interpretations_history.py` - persisted narrative answer test candidate.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - AST guard evidence from architecture and boundary tests for source-owner claims.
  - DB schema through SQLAlchemy models under `backend/app/infra/db/models/**` for persisted storage claims.
  - Repositories and services under `backend/app/infra/db/repositories/**` and `backend/app/services/**` for write/read behavior claims.
  - Existing tests under `backend/tests/**` and `backend/app/tests/**` for runtime coverage claims.
  - Existing migrations under `backend/migrations/**` for schema history claims.
  - CS-259 story for target `narrative_answer_audit_v1` field expectations.
  - Generated audit manifest from `01-evidence-log.md` for the final classification baseline.
- Secondary evidence:
  - Targeted `rg` scans for `answer_id`, `prompt_version`, `provider`, `model`, `prompt_ref`, prompt snapshots and full prompt storage.
- Static scans alone are not sufficient for present claims because:
  - A `present` status must cite a concrete storage owner and at least one runtime, repository, schema or test evidence path.

## Contract Shape

- Contract type:
  - CONDAMAD backend AI traceability audit folder.
- Fields:
  - `cs259_field`: exact target field or storage capability from CS-259.
  - `current_status`: one of `present`, `partial` or `absent`.
  - `current_owner`: code, DB, repository, service, route, test or doc owner.
  - `storage_shape`: table column, JSON field, relationship, encrypted payload, reference or missing surface.
  - `runtime_path`: service, repository, route or test path proving runtime usage.
  - `gap_to_cs259`: exact delta against `narrative_answer_audit_v1`.
  - `migration_risk`: schema, backfill, retention, duplication or privacy risk.
  - `recommended_next_action`: extend existing owner, create new owner, or request decision.
- Required fields:
  - `cs259_field`
  - `current_status`
  - `current_owner`
  - `storage_shape`
  - `runtime_path`
  - `gap_to_cs259`
  - `migration_risk`
  - `recommended_next_action`
- Optional fields:
  - none
- Status codes:
  - none; this is not an API route.
- Serialization names:
  - Markdown matrix columns keep stable snake_case names for field-level audit traceability.
- Required files:
  - `00-audit-report.md`
  - `01-evidence-log.md`
  - `02-finding-register.md`
  - `03-story-candidates.md`
  - `04-risk-matrix.md`
  - `05-executive-summary.md`
- Required field rows:
  - `answer_id`
  - `prompt_version`
  - `provider`
  - `model`
  - `full_prompt`
  - `prompt_ref`
  - `prompt_payload_snapshot`
- Allowed statuses:
  - `present`
  - `partial`
  - `absent`
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-262-audit-existing-prompt-version-answer-id-storage.md`
  - `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`
  - scoped `rg` inventory output over `backend/app`, `backend/tests`, `docs` and `_condamad`
  - scoped `git status --short -- backend/app backend/tests frontend/src`
- Comparison after implementation:
  - Latest child folder under `_condamad/audits/ai-traceability/`.
- Expected invariant:
  - The only intended repository delta is the new audit folder and its standard CONDAMAD audit files.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| AI traceability audit | `_condamad/audits/ai-traceability/` | `backend/app/**` |
| Evidence log | `_condamad/audits/ai-traceability/` | `backend/tests/**` |
| Finding register | `_condamad/audits/ai-traceability/` | new DB models or migrations |
| Story candidates | `_condamad/audits/ai-traceability/` | `_condamad/stories/**` |
| Existing prompt storage evidence | existing backend LLM owners | duplicated audit storage implementation |

## Mandatory Reuse / DRY Constraints

- Reuse CS-259 field names and target contract language for the comparison matrix.
- Reuse existing backend models, repositories, services, tests, migrations and docs as evidence instead of creating parallel proof.
- Use one canonical classification vocabulary across all six audit files.
- Keep each field name consistent across report, evidence log, findings, candidates, risk matrix and summary.
- Do not add external packages, custom audit tooling, app code, tests, migrations, services, routes, models, builders or prompt files.

## No Legacy / Forbidden Paths

- No legacy route path may be added during this audit.
- No compatibility storage path may be added during this audit.
- No fallback storage branch may be added during this audit.
- Do not create aliases, shims, wrappers or parallel documents that claim to implement `narrative_answer_audit_v1`.
- Do not add API routes, database migrations, seed data, frontend screens, builders, services, tests, prompt templates or provider calls.
- Forbidden surfaces:
  - `backend/app/**`
  - `backend/tests/**`
  - `frontend/src/**`
  - `backend/migrations/**`
  - prompt template files
  - generated OpenAPI clients

## Reintroduction Guard

- Guard target:
  - audit work cannot create a second storage design before existing storage is classified;
  - each CS-259 field must be explicitly classified as `present`, `partial` or `absent`;
  - findings cannot omit migration risks for existing answer, prompt, provider or model storage;
  - application source, tests, migrations, prompts and frontend files cannot change under this story.
- Guard mechanism:
  - targeted `rg` checks for required field names and status vocabulary in the audit report;
  - scoped `git status --short -- backend/app backend/tests frontend/src backend/migrations`;
  - persisted evidence under the latest `_condamad/audits/ai-traceability/` folder.
- Guard owner:
  - `_condamad/audits/ai-traceability/{timestamp}/00-audit-report.md`;
  - `_condamad/audits/ai-traceability/{timestamp}/01-evidence-log.md`;
  - `_condamad/audits/ai-traceability/{timestamp}/04-risk-matrix.md`.
- Guard evidence:
  - `rg -n "answer_id|prompt_version|provider|model|full_prompt|prompt_ref|prompt_payload_snapshot" "$($auditFolder.FullName)\00-audit-report.md"`;
  - `rg -n "present|partial|absent" "$($auditFolder.FullName)\00-audit-report.md"`;
  - `git status --short -- backend/app backend/tests frontend/src backend/migrations`.

## Regression Guardrails

Scope vector:

- backend AI traceability audit documentation: yes;
- backend LLM storage owners referenced: yes;
- prompt-generation validation paths referenced: yes;
- API route change: no;
- frontend implementation: no;
- DB, auth, i18n, style, build and migration implementation: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend app paths are referenced only as evidence, not modified. | `git status`; bounded `rg`. |
| RG-022 | Prompt-generation evidence paths must point to concrete collected tests. | `rg`; `pytest`; evidence log. |
| Registry gap | No exact AI traceability storage audit guardrail exists in resolver output. | Story-local scans and status proof. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this audit targets AI traceability storage.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit report | `_condamad/audits/ai-traceability/{timestamp}/00-audit-report.md` | Field classification and CS-259 comparison. |
| Evidence log | `_condamad/audits/ai-traceability/{timestamp}/01-evidence-log.md` | Reproducible code, DB, test and doc proof. |
| Finding register | `_condamad/audits/ai-traceability/{timestamp}/02-finding-register.md` | Verified gaps and storage deltas. |
| Story candidates | `_condamad/audits/ai-traceability/{timestamp}/03-story-candidates.md` | Follow-up stories linked to findings. |
| Risk matrix | `_condamad/audits/ai-traceability/{timestamp}/04-risk-matrix.md` | Migration, duplication and privacy risks. |
| Executive summary | `_condamad/audits/ai-traceability/{timestamp}/05-executive-summary.md` | Decision summary for next implementation. |
| Review output | `_condamad/stories/CS-262-audit-existing-prompt-version-answer-id-storage/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this documentation-only audit.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/ai-traceability/{timestamp}/00-audit-report.md` - field classification and CS-259 comparison.
- `_condamad/audits/ai-traceability/{timestamp}/01-evidence-log.md` - concrete repository evidence.
- `_condamad/audits/ai-traceability/{timestamp}/02-finding-register.md` - verified gaps and field deltas.
- `_condamad/audits/ai-traceability/{timestamp}/03-story-candidates.md` - prioritized follow-up stories.
- `_condamad/audits/ai-traceability/{timestamp}/04-risk-matrix.md` - migration and duplication risks.
- `_condamad/audits/ai-traceability/{timestamp}/05-executive-summary.md` - decision summary.

Likely tests:

- Document validation through targeted `python` file checks.
- Targeted `rg` checks against latest audit artifacts.
- Scoped `git status --short -- backend/app backend/tests frontend/src backend/migrations`.

Files not expected to change:

- `backend/app/**` - out of scope; no backend runtime is touched.
- `backend/tests/**` - out of scope; no test code is touched.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `$auditFolder = Get-ChildItem -Directory .\_condamad\audits\ai-traceability | Sort-Object Name -Descending | Select-Object -First 1`
- VC3: `python -c "from pathlib import Path; p=max(Path('_condamad/audits/ai-traceability').iterdir()); assert (p/'00-audit-report.md').exists()"`
- VC4: `python -c "from pathlib import Path; p=max(Path('_condamad/audits/ai-traceability').iterdir()); assert len(list(p.glob('*.md'))) >= 6"`
- VC5: `rg -n "answer_id|prompt_version|provider|model|full_prompt|prompt_ref|prompt_payload_snapshot" "$($auditFolder.FullName)\00-audit-report.md"`
- VC6: `rg -n "present|partial|absent" "$($auditFolder.FullName)\00-audit-report.md"`
- VC7: `rg -n "backend/app|backend/tests|backend/migrations|docs|_condamad" "$($auditFolder.FullName)\01-evidence-log.md"`
- VC8: `rg -n "CS-259|narrative_answer_audit_v1|gap|migration" "$($auditFolder.FullName)\02-finding-register.md"`
- VC9: `rg -n "migration|duplication|backfill|privacy|retention" "$($auditFolder.FullName)\04-risk-matrix.md"`
- VC10: `rg -n "answer_id|prompt_version|provider|model|prompt" .\backend .\docs .\_condamad`
- VC11: `git status --short -- backend/app backend/tests frontend/src backend/migrations`
- VC12: `ruff format .`
- VC13: `ruff check .`
- VC14: `pytest -q`

Before VC3, VC4, VC12, VC13 and VC14, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The audit may overstate coverage by treating a prompt version foreign key as full CS-259 prompt provenance.
- The audit may understate coverage by missing encrypted replay snapshots or existing LLM call log metadata.
- A later implementation could duplicate partial storage instead of extending the verified canonical owner.
- Migration planning could miss backfill, retention or privacy risks around existing generated answer rows.
- A documentation story could drift into DB, route, prompt, provider, test or frontend implementation.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep all audit artifacts under the latest `_condamad/audits/ai-traceability/` child folder.
- Treat `present` as requiring a concrete storage owner plus code, DB, repository, migration or test evidence.
- Treat `partial` as requiring a named gap against CS-259.
- Treat `absent` as requiring a documented absence scan.
- Do not modify backend, frontend, migration, prompt, route, service, builder, model or test files.

## References

- `_story_briefs/cs-262-audit-existing-prompt-version-answer-id-storage.md`
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`
- `backend/app/infra/db/models/llm/llm_observability.py`
- `backend/app/infra/db/models/llm/llm_prompt.py`
- `backend/app/infra/db/models/llm/llm_release.py`
- `backend/app/infra/db/models/user_natal_interpretation.py`
- `backend/app/infra/db/repositories/llm/prompting_repository.py`
- `_condamad/stories/regression-guardrails.md`
