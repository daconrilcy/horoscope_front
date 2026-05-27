# Story CS-340 frontiere-provenance-prompt-audit: Close Natal LLM Prompt Audit Boundary Validation
Status: done

## Trigger / Source

- Mode: Brief direct with repo-informed evidence.
- Source brief: `_story_briefs/cs-340-cloturer-validation-frontiere-provenance-prompt-audit-llm-natal.md`.
- Source problem: prove after CS-339 that `llm_astrology_input_v1` keeps audit-only provenance data outside the natal LLM prompt.
- Prerequisite: CS-339 must be completed before executing the validation report work.
- Source-alignment review: PASS. The ACs, tasks, evidence, non-goals, and guardrails map to the prompt/audit closure stakes.

## Objective

Produce the final validation report proving that the natal LLM prompt receives only prompt-visible blocks while audit evidence keeps
`projection_hash`, `llm_input_hash`, version, grounding, and evidence references under audit ownership.

## Target State

- A timestamped report exists under `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/`.
- The report directory name follows the `YYYY-MM-DD-HHMM` timestamp format required by the source brief.
- The report distinguishes the complete `llm_astrology_input_v1` object from the prompt-visible projection.
- Tests inspect the payload handed to the provider boundary, not only builders or intermediate objects.
- Scans classify every remaining `projection_hash`, `llm_input_hash`, and `provenance` occurrence by owner.
- Remaining occurrences are classified as audit/persistence owned, internal non-prompt contract, guard test, historical evidence, or debt to fix.
- CS-330 through CS-338 delivery evidence is reconciled with the CS-339 correction boundary.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-340-cloturer-validation-frontiere-provenance-prompt-audit-llm-natal.md` - source brief read.
- Evidence 2: `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md` - prerequisite correction brief read.
- Evidence 3: `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md` - audit hash source read.
- Evidence 4: `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md` - prompt guard source read.
- Evidence 5: `_condamad/reports/cs-330-cs-331-cs-332-cs-333-cs-334-cs-335-cs-336-cs-337-cs-338-delivery-report.md` - delivery source read.
- Evidence 6: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-340`.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - guardrails resolved by scope vector without registry enrichment.
- Evidence 8: targeted `rg` found current prompt/audit symbols in `backend/app` and `backend/tests`.
- Repository structure alert: none. `backend` and `frontend` roots exist in this workspace.
- Prerequisite alert: `_condamad/stories/story-status.md` currently lists CS-339 as `ready-to-dev`, not `done`.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend validation of the natal LLM prompt/audit boundary.
  - Report generation under `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/`.
  - Targeted tests and scans for prompt-visible, audit-only, hash, provenance, and provider handoff evidence.
- Out of scope:
  - Frontend UI, public API route changes, database schema changes, auth, i18n, styling, build tooling, and migrations.
  - Reworking the CS-339 correction unless a blocking validation failure proves the correction is incomplete.
  - Real provider calls or editorial prompt rewrites unrelated to the prompt/audit boundary.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No new LLM feature, provider integration, persistence policy, or hash semantics change.
  - No broad cleanup of historical `_condamad` or `_story_briefs` references.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend validation report contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Produce evidence and a report for the prompt/audit boundary only.
  - Change tests only to close missing validation coverage for this boundary.
  - Change runtime code only when validation proves CS-339 left the boundary incomplete.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-339 remains unimplemented or the validation proves that prompt/audit ownership is still ambiguous.
- Additional validation rules:
  - The report must classify residual terms instead of requiring total absence.
  - The provider handoff payload must be validated through `pytest` coverage or an equivalent `AST guard`.
  - The audit payload must be validated separately from the prompt-visible projection.
  - The placeholder scan must cover prompts, schemas, and registries for modern natal use cases.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, provider-boundary tests, and `AST guard` evidence prove the final payload boundary. |
| Baseline Snapshot | yes | Before and after scan artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Prompt-visible fields and audit-only fields must keep separate canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this closure validation. |
| Contract Shape | yes | The report must define prompt-visible blocks and audit-only fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | `chart_json`, `natal_data`, and audit-only prompt leakage must stay guarded. |
| Persistent Evidence | yes | Report and validation artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The boundary validation report exists in a `YYYY-MM-DD-HHMM` directory. | Evidence profile: baseline_before_after_diff; `python` checks the report path. |
| AC2 | Tests no longer require `provenance.llm_input_hash` in the prompt. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `backend/tests`. |
| AC3 | Provider handoff payload excludes audit-only fields. | Evidence profile: json_contract_shape; `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py`. |
| AC4 | Persistent audit keeps the full brief-required audit field set. | Evidence profile: json_contract_shape; audit persistence pytest. |
| AC5 | Modern natal use cases avoid hash provenance placeholders. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `{{provenance}}` and hash placeholders. |
| AC6 | Backend validation commands pass. | Evidence profile: no_legacy_contract; `pytest -q tests --tb=short`; `ruff check .`. |
| AC7 | Remaining prompt/audit terms are classified. | Evidence profile: baseline_before_after_diff; `python` checks the report sections. |
| AC8 | CS-339 is complete before closure execution. | Evidence profile: baseline_before_after_diff; `python` checks `story-status.md` for CS-339 `done`. |

AC4 full audit field set: `projection_hash`, `llm_input_hash`, `llm_input_version`, `grounding_status`, and `evidence_refs`.

## Implementation Tasks

- [ ] Task 1: Verify CS-339 is `done` in `_condamad/stories/story-status.md` before running closure validation. (AC: AC8)
- [ ] Task 2: Run targeted tests proving prompt-visible blocks and provider handoff payload ownership. (AC: AC2, AC3)
- [ ] Task 3: Run audit and hash tests proving audit-only fields remain persisted and hash behavior remains stable. (AC: AC4)
- [ ] Task 4: Run prompt, schema, registry, and test scans for provenance and hash placeholders. (AC: AC2, AC5, AC7)
- [ ] Task 5: Produce the timestamped validation report with summary, definitions, files, scan results, commands, and risks. (AC: AC1, AC7)
- [ ] Task 6: Run backend lint and full backend tests after the report and any validation-only fixes. (AC: AC6)
- [ ] Task 7: Persist validation outputs and final evidence artifacts for review handoff. (AC: AC1, AC6, AC7)

## Files to Inspect First

- `_condamad/stories/story-status.md` - confirm CS-339 is `done` before closure execution.
- `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md` - correction scope to validate.
- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md` - audit hash expectations.
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md` - prompt boundary guard expectations.
- `_condamad/reports/cs-330-cs-331-cs-332-cs-333-cs-334-cs-335-cs-336-cs-337-cs-338-delivery-report.md` - prior evidence.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - prompt-visible and audit-only contract owner.
- `backend/app/domain/llm/runtime/gateway.py` - provider handoff projection owner.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - modern natal placeholder owner.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - audit persistence input owner.
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - prompt boundary tests.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - static prompt/audit guard.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py` - audit persistence tests.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest` coverage for gateway/provider-boundary behavior and audit persistence.
  - `AST guard` coverage for prompt projection ownership in `backend/app/domain/llm/runtime/gateway.py`.
  - Loaded runtime objects from the backend test suite, not historical reports alone.
- Secondary evidence:
  - Targeted `rg` scans for `provenance`, `projection_hash`, `llm_input_hash`, `audit_only`, and `prompt_visible`.
- Static scans alone are not sufficient for this story because:
  - The final payload just before provider handoff must be proven by executable tests.

## Contract Shape

- Contract type:
  - Backend validation report and internal LLM prompt/audit boundary.
- Fields:
  - `prompt_visible_blocks`: list of blocks authorized for the natal LLM prompt.
  - `audit_only_fields`: list of fields authorized for audit and persistence.
  - `verified_files`: list of runtime and test files inspected during closure.
  - `scan_results`: classified occurrences of prompt/audit boundary terms.
  - `validation_commands`: commands executed with result and scope.
  - `residual_risks`: bounded risks remaining after validation.
- Required fields:
  - `prompt_visible_blocks`
  - `audit_only_fields`
  - `verified_files`
  - `scan_results`
  - `validation_commands`
  - `residual_risks`
- Optional fields:
  - none
- Status codes:
  - none; this story does not change a public API route.
- Serialization names:
  - Report headings are emitted as Markdown section titles.
- Prompt-visible blocks:
  - `facts`
  - `signals`
  - `limits`
  - `evidence`
  - `shaping`
- Audit-only fields:
  - `provenance`
  - `projection_hash`
  - `llm_input_hash`
  - `llm_input_version`
  - `grounding_status`
  - `evidence_refs`
  - `provider_response`
  - `persisted_answer`
- Required report sections:
  - Correction summary.
  - Final prompt-visible block definition.
  - Final audit-only field definition.
  - Runtime and test files verified.
  - Scan results.
  - Validation commands executed.
  - Residual risks.
- Required occurrence categories:
  - audit/persistence owned.
  - internal non-prompt contract.
  - guard test.
  - historical evidence.
  - debt to fix.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/evidence/boundary-scan-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/evidence/boundary-scan-after.txt`
- Expected invariant:
  - Prompt-visible references stay limited to the canonical prompt blocks while audit-only terms remain ownerised outside the prompt.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Prompt-visible block list | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | hardcoded divergent list in gateway |
| Provider handoff projection | `backend/app/domain/llm/runtime/gateway.py` | service-layer ad hoc prompt payload |
| Audit persistence fields | `backend/app/services/llm_generation/natal/interpretation_service.py` | prompt-visible projection |
| Modern natal placeholders | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | hash or provenance prompt placeholder |
| Closure evidence report | `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/` | story body only |

Audit persistence fields include `projection_hash`, `llm_input_hash`, `llm_input_version`, `grounding_status`, and `evidence_refs`.

## Mandatory Reuse / DRY Constraints

- Reuse the canonical prompt-visible list from `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]`.
- Reuse existing backend tests for hash, evidence, audit, gateway, and legacy boundary validation.
- Do not duplicate prompt/audit role definitions in a new helper without routing through the canonical contract owner.
- Do not add external packages.
- Keep the report factual and derived from executed commands, not manual restatement of broad registry content.

## No Legacy / Forbidden Paths

- No legacy `chart_json` or `natal_data` prompt path may be accepted as a closure result.
- No compatibility prompt path may be added for provenance or hash fields.
- No fallback prompt path may be added for audit-only fields.
- Forbidden prompt fields for the modern natal provider payload:
  - `provenance`
  - `projection_hash`
  - `llm_input_hash`
  - `provider_response`
  - `persisted_answer`

## Reintroduction Guard

- Guard exact forbidden prompt symbols with targeted `pytest`, `AST guard`, and `rg` checks.
- Required negative scan:
  - `rg -n "{{provenance}}|{{projection_hash}}|{{llm_input_hash}}" app tests`
- Required boundary scan:
  - `rg -n "provenance|projection_hash|llm_input_hash|audit_only|prompt_visible" app tests ..\_condamad ..\_story_briefs`
- Required payload tests:
  - `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
  - `pytest -q tests/architecture/test_llm_astrology_input_payload_boundaries.py`

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-022 `align-prompt-generation-story-validation-paths` | Active validation commands must target collected backend tests. | `pytest` targeted paths; report command log. |
| RG-002 `refactor-api-v1-routers` | Needs-investigation only for backend layout drift; API routers are not in scope. | `rg` ownership scan; no API route edits. |
| Registry gap | No exact route-specific guardrail applies to this non-API backend validation story. | Resolver output recorded in final evidence. |

Non-applicable example: frontend style and CSS guardrails are out of scope because no frontend surface is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation report | `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/YYYY-MM-DD-HHMM/validation-frontiere-provenance.md` | Keep closure conclusions. |
| Scan before | `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/evidence/boundary-scan-before.txt` | Preserve baseline scan. |
| Scan after | `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/evidence/boundary-scan-after.txt` | Preserve classified scan. |
| Validation output | `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/evidence/validation-output.txt` | Keep command results. |
| Final evidence | `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/generated/10-final-evidence.md` | Keep implementation evidence. |
| Review output | `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/generated/11-code-review.md` | Keep automatic review handoff. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this single boundary validation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/YYYY-MM-DD-HHMM/validation-frontiere-provenance.md` - closure report.
- `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/evidence/boundary-scan-before.txt` - scan evidence.
- `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/evidence/boundary-scan-after.txt` - scan evidence.
- `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/evidence/validation-output.txt` - command evidence.
- `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/generated/10-final-evidence.md` - final handoff.

Likely tests:

- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - provider-boundary payload checks.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - static prompt/audit boundary guard.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - contract role checks.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py` - hash stability checks.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py` - evidence refs checks.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py` - audit persistence checks.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public API route changes are touched.
- `backend/app/infra/**` - out of scope; no persistence adapter or schema change is touched.
- `backend/alembic/**` - out of scope; no migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\.venv\Scripts\Activate.ps1`, then `cd backend`.

- VC1:
  `python -c "from pathlib import Path; text=Path('../_condamad/stories/story-status.md').read_text(encoding='utf-8'); assert '| CS-339 |' in text"`
- VC1 status gate:
  ```powershell
  python -c @'
  from pathlib import Path
  rows = Path("../_condamad/stories/story-status.md").read_text(encoding="utf-8").splitlines()
  assert "| done |" in [row for row in rows if row.startswith("| CS-339 |")][0]
  '@
  ```
- VC2: `ruff format .`
- VC3: `ruff check .`
- VC4 unit:
  `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py tests/unit/domain/astrology/test_llm_astrology_input_hash.py --tb=short`
- VC4 evidence:
  `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_evidence.py --tb=short`
- VC4 boundary:
  `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py tests/architecture/test_llm_astrology_input_payload_boundaries.py --tb=short`
- VC4 audit:
  `pytest -q tests/integration/test_llm_legacy_extinction.py tests/integration/llm/test_natal_llm_astrology_input_audit.py --tb=short`
- VC5: `pytest -q tests --tb=short`
- VC6: `rg -n "provenance|projection_hash|llm_input_hash|audit_only|prompt_visible" app tests ..\_condamad ..\_story_briefs`
- VC7: `rg -n "{{provenance}}|{{projection_hash}}|{{llm_input_hash}}" app tests`
- VC8:
  ```powershell
  python -c @'
  from pathlib import Path
  import re
  root = Path("../_condamad/reports/frontiere-provenance-prompt-audit-llm-natal")
  assert any(
      re.fullmatch(r"\d{4}-\d{2}-\d{2}-\d{4}", path.parent.name)
      for path in root.glob("*/validation-frontiere-provenance.md")
  )
  '@
  ```
- VC9:
  ```powershell
  python -c @'
  from pathlib import Path
  root = Path("../_condamad/reports/frontiere-provenance-prompt-audit-llm-natal")
  text = next(root.glob("*/validation-frontiere-provenance.md")).read_text(encoding="utf-8")
  assert "prompt-visible" in text
  '@
  ```
- VC9 sections:
  ```powershell
  python -c @'
  from pathlib import Path
  root = Path("../_condamad/reports/frontiere-provenance-prompt-audit-llm-natal")
  text = next(root.glob("*/validation-frontiere-provenance.md")).read_text(encoding="utf-8")
  assert "audit-only" in text and "Risques residuels" in text
  '@
  ```

## Regression Risks

- CS-339 may still be pending; the closure validation must stop until the prerequisite row is `done`.
- A scan may show legitimate audit terms; the report must classify ownership instead of treating every hit as a defect.
- Historical `_condamad` and `_story_briefs` references can be noisy; classify them as historical evidence when they are not executable.
- Provider handoff coverage can be too shallow; keep tests focused on the final payload passed to the provider boundary.
- Full backend tests may expose unrelated failures; record unrelated failures separately and do not soften the prompt/audit boundary result.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Start by verifying CS-339 status in `_condamad/stories/story-status.md`.
- Use PowerShell on Windows and activate `.\.venv\Scripts\Activate.ps1` before every Python, Ruff, Pytest, or script command.
- Keep report language factual and classify residual occurrences by owner.
- Do not modify frontend files.
- Do not call a real LLM provider.

## References

- `_story_briefs/cs-340-cloturer-validation-frontiere-provenance-prompt-audit-llm-natal.md`
- `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md`
- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `_condamad/reports/cs-330-cs-331-cs-332-cs-333-cs-334-cs-335-cs-336-cs-337-cs-338-delivery-report.md`
- `_condamad/stories/regression-guardrails.md`
