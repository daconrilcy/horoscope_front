# Story Candidates - AI Traceability Audit

## SC-001 Canonical Narrative Answer Audit Persistence

- Source finding: F-001
- Suggested story title: Implement canonical `answer_id` storage for `narrative_answer_audit_v1`
- Suggested archetype: data-model-boundary-convergence
- Primary domain: backend-ai-traceability-persistence
- Required contracts: CS-259 `narrative_answer_audit_v1`; CS-262 audit evidence; No Legacy / DRY.
- Draft objective: Add or extend exactly one canonical persistence owner for narrative answer audit rows with stable `answer_id` and explicit links to persisted answer payloads and LLM trace records.
- Closure intent: full-closure
- Must include: Exact owner selection between extending `user_natal_interpretations` and creating a dedicated audit table; no parallel answer identity; migration/backfill for existing rows; no public API exposure; no wildcard allowlist.
- Validation hints: `rg -n "\banswer_id\b|narrative_answer_audit_v1" backend/app backend/tests backend/migrations`; schema/migration tests proving unique stable `answer_id`; scoped `git status`.
- Blockers: Stop if product requires a non-DB answer identity scheme or if existing row identity must remain the public answer identifier.

### Exhaustive Files To Modify

- Application files: exact selection rule is the chosen canonical persistence owner, its repository/service integration, and migration files needed for `answer_id`.
- Governance/test files: targeted backend tests for schema, repository writes, and no duplicate storage owner.
- Deferred non-domain concerns: frontend/admin API exposure remains out of domain.

### Before / After Classification Requirements

- Before: `backend/app/infra/db/models/user_natal_interpretation.py` is `used` but partial for answer identity.
- After: selected persistence owner must be `used` and the non-selected storage alternative must remain absent or be classified with evidence.

## SC-002 Persist CS-259 Hash And Grounding Fields

- Source finding: F-002
- Suggested story title: Persist projection, LLM input and grounding metadata for narrative answers
- Suggested archetype: data-model-boundary-convergence
- Primary domain: backend-ai-traceability-persistence
- Required contracts: CS-259 `projection_hash`, `llm_input_hash`, `grounding_status`; rejected-answer workflow when implemented.
- Draft objective: Store or receive canonical `projection_hash`, `llm_input_hash`, and `grounding_status` for generated and rejected narrative answers through the chosen audit owner.
- Closure intent: full-closure
- Must include: Exact hash source ownership; explicit distinction between existing `input_hash` and CS-259 `llm_input_hash`; accepted `grounding_status` enum; rejected row behavior; no fallback branch that silently marks unknown grounding as grounded.
- Validation hints: `rg -n "projection_hash|llm_input_hash|grounding_status" backend/app backend/tests backend/migrations`; repository tests for generated and rejected answer rows; negative public exposure scan.
- Blockers: Stop if upstream projection or LLM input hash owners are not implemented or cannot supply deterministic hashes.

### Exhaustive Files To Modify

- Application files: selected audit persistence model/repository/service; hash source adapters only if the owning upstream domain already exposes them.
- Governance/test files: schema tests, write/read tests, public masking guard.
- Deferred non-domain concerns: final evidence-section validation can remain in CS-289 domain.

### Before / After Classification Requirements

- Before: `backend/app/domain/llm/runtime/observability_service.py` is `used` for `input_hash` but not proven as `llm_input_hash`.
- After: `llm_input_hash` either maps to a proven existing hash with evidence or becomes a distinct persisted field.

## SC-003 Route Prompt Provider Model Provenance Without Duplication

- Source finding: F-003
- Suggested story title: Link answer audit rows to existing prompt and LLM observability provenance
- Suggested archetype: repository-ownership-refactor
- Primary domain: backend-ai-traceability-persistence
- Required contracts: CS-259 prompt/provider/model provenance; No Legacy / DRY.
- Draft objective: Define and implement the canonical joins or copied snapshots that connect each answer audit row to prompt version, provider and model data already owned by LLM storage.
- Closure intent: full-closure
- Must include: Exact routing for `prompt_version_id`, LLM call log ID or request/trace correlation, provider field owner, model field owner, release snapshot fields; duplicate-owner scan.
- Validation hints: `rg -n "prompt_version_id|executed_provider|model|llm_call_logs|llm_prompt_versions" backend/app backend/tests`; tests proving persistence survives missing optional call log references.
- Blockers: Stop if retention decisions make call logs unavailable for required audit lifetime; then request a snapshot policy decision.

### Exhaustive Files To Modify

- Application files: selected audit persistence owner and repository/service mapping to LLM prompt/observability owners.
- Governance/test files: tests for joins, missing call-log handling and no duplicate provenance store.
- Deferred non-domain concerns: admin query API remains CS-267.

### Before / After Classification Requirements

- Before: `llm_call_logs`, `llm_call_log_operational_metadata`, `llm_prompt_versions` and `llm_release_snapshots` are `used` source surfaces.
- After: each provenance field in the audit owner must cite one canonical source or snapshot rule.

## SC-004 Add Audit Storage Completeness Guards

- Source finding: F-005
- Suggested story title: Guard `narrative_answer_audit_v1` storage completeness and no duplicate owner
- Suggested archetype: architecture-guard-hardening
- Primary domain: backend-ai-traceability-tests
- Required contracts: CS-259 field list; CS-262 no-duplicate-storage rule; regression guardrails RG-002 and RG-022.
- Draft objective: Add deterministic backend tests/scans that fail when required CS-259 fields are missing or when a second active answer-audit storage owner appears.
- Closure intent: full-closure
- Must include: No-wildcard allowlist of accepted audit storage owner(s); required field scan; migration/schema assertion; public API masking check; No Legacy duplicate-owner scan.
- Validation hints: targeted pytest for schema/repository guards plus `rg -n "narrative_answer_audit_v1|answer_id|projection_hash|llm_input_hash|grounding_status" backend/app backend/tests`.
- Blockers: Stop if no canonical persistence owner exists yet; this candidate should be implemented together with or immediately after SC-001/SC-002.

### Exhaustive Files To Modify

- Application files: none unless tests require exposing existing constants from the chosen owner.
- Governance/test files: backend architecture/schema guard tests and an exact owner allowlist artifact if repository convention requires one.
- Deferred non-domain concerns: global guardrail registry enrichment should happen only after implementation creates a durable invariant.

### Before / After Classification Requirements

- Before: no exact guard for CS-259 storage completeness exists.
- After: guard files are `test-only` and cite the canonical owner list without wildcard folder exceptions.

## Needs User Decision

- F-004 requires a decision before an implementation candidate can be closure-ready: choose full prompt retention, `prompt_ref` plus payload snapshot, or a hybrid policy with exact encryption, retention window and backfill behavior.

## Deferred Non-Domain Context

- Admin API reads belong to CS-267 and must not be implemented by this audit.
- Rejected-answer workflow behavior belongs to CS-290, after persistence exists.
- Frontend exposure and generated clients remain out of domain for this audit.
