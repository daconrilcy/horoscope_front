# Audit theme-astral-prompt-contract - CS-369

## Domain Closure Status

Status: `closed`.

Verdict: `valide avec risque residuel accepte`.

This run audits the `theme_astral` backend prompt contract after CS-361 through CS-368. It follows the user constraint that CS-369 is handled as audit-only: no application code, tests, migrations, seeds, frontend files, examples, architecture documents, or guardrails were changed. The only writes are audit artifacts under `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1418/`.

## Audit Boundary

In scope:

- `theme_astral_llm_input_v1` and provider payload skeleton.
- `interpretation_material` source selection and provider handoff.
- `delivery_profile`, `astrologer_voice`, and backend-only commercial plan handling.
- `output_contract` and versioned persistence surfaces.
- Old-carrier closure for `chart_json`, `natal_data`, and `llm_astrology_input_v1` in the `theme_astral` flow.
- Targeted tests, examples, docs, architecture, and prior same-domain audit history.

Out of scope:

- Frontend, auth, styling, unrelated LLM features, billing plan UI, broad natal prompt legacy outside `theme_astral`, and real LLM provider invocation.
- Code corrections requested by the original CS-369 story text, because the current user instruction explicitly requests audit-only execution.

## Prior Audit And Story History Consulted

| Item | Status | Evidence | Current classification |
|---|---|---|---|
| `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1152/` | CS-361 source audit | E-003, E-004 | closed by current implementation and tests |
| `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1203/` | CS-362 source audit | E-003, E-004 | closed by current implementation and tests |
| `_condamad/architecture/theme-astral-prompt-contract/2026-05-28-1217/archi-theme-astral-prompt-contract-v1.md` | CS-363 architecture | E-012 | implemented decision source |
| `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1409/` | CS-368 closure audit | E-003 | still-active findings: none |
| `_condamad/stories/story-status.md` | CS-361..CS-369 status | E-004 | CS-361..CS-368 done; CS-369 ready-to-dev |
| `_condamad/stories/regression-guardrails.md` | guardrail registry | E-002 | relevant invariants consulted; no update justified |

## Closure Analysis

- Prior CS-361 findings about rich, source-backed interpretation material are closed by `InterpretationMaterialBuilder`, `InterpretationMaterialSourceRepository`, and targeted material handoff tests (E-005, E-007, E-009).
- Prior CS-362 findings about provider shape drift, prompt-visible commercial plan labels, duplicated carriers, backend-only metadata leakage, and basic/premium confusion are closed by the canonical provider builder, gateway handoff checks, example scans, persistence tests, and architecture guard tests (E-005, E-007, E-008, E-009).
- Prior CS-363 architecture decisions are represented in contract constants, seed/persistence owners, runtime builder blocks, and docs (E-005, E-012).
- Prior CS-364 persistence/versioning expectations are covered by active family resolver, seed idempotency, output schema checks, and migration tests (E-005, E-007, E-009).
- Prior CS-365/CS-366/CS-367 implementation expectations are covered by tests proving sourced material, stable skeleton, backend-only delivery profile, and old-carrier rejection (E-007, E-009).
- No active in-domain implementation finding remains. The only recorded finding is F-001, an audit limitation caused by the explicit no-provider-call boundary.

## Adversarial Review Axes

| Axis | Verdict | Evidence | Notes |
|---|---|---|---|
| Contract and structure | PASS | E-005, E-006, E-007, E-009, E-012 | Fixed top-level and `input_data` skeleton are asserted in source and runtime tests across profiles. |
| Interpretation material | PASS | E-005, E-007, E-009 | Material builder refuses unsourced text and the provider payload receives `input_data.interpretation_material`. |
| Astrologer voice | PASS | E-005, E-007, E-009 | Voice is a separate block; tests prove it does not mutate astrological facts and persona seed disallows truth changes. |
| Security/backend-only | PASS | E-005, E-007, E-008, E-009 | Commercial labels are mapped before provider handoff and absent from provider examples and payload strings. |
| Legacy closure | PASS | E-005, E-007, E-009, E-011 | `theme_astral` requires canonical payload and rejects old carriers; remaining broad hits are non-domain or guard/test context. |
| Persistence/versioning | PASS | E-005, E-007, E-009, E-012 | Existing LLM persistence owners store prompt, output schema, persona, execution profile, and assembly references. |
| Report/evidence completeness | PASS | E-001, E-002, E-003, E-013 | This folder contains the standard audit report set plus the CS-369 adversarial deliverable. |

## Findings Summary

| ID | Severity | Confidence | Category | Evidence | Decision |
|---|---|---|---|---|---|
| F-001 | Info | High | observability-gap | E-001, E-013 | Accepted limitation: no real provider call in audit-only scope. |

No accepted Critical or High/Major finding requires correction.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` | used | E-005, E-006, E-007, E-009 | Canonical provider payload builder; owns stable skeleton, material handoff, delivery profile projection, output contract block. | No real provider call. |
| `backend/app/domain/llm/configuration/theme_astral_contracts.py` | used | E-005, E-006, E-007, E-009 | Canonical contract IDs, delivery profile resolver, input/response schemas, active contract family resolver. | DB behavior proven by tests, not manual production DB dump. |
| `backend/app/domain/llm/runtime/gateway.py` `build_user_payload` | used | E-005, E-006, E-007, E-009 | Enforces `theme_astral_llm_input_v1` for `theme_astral` and prevents old carriers from replacing it. | Gateway also owns other LLM flows outside this audit. |
| `backend/app/domain/astrology/interpretation/interpretation_material_builder.py` | used | E-005, E-006, E-007, E-009 | Single source-attributed material selector for calculated facts and delivery quotas. | Source breadth depends on supplied repository/runtime sources. |
| `backend/app/domain/astrology/interpretation/interpretation_material_contracts.py` | used | E-007, E-009 | DTO/key contract for material sections used by builder and tests. | Inspected through tests and imports, not line-by-line in this audit. |
| `backend/app/infra/db/repositories/interpretation_material_source_repository.py` | used | E-005, E-006, E-009 | Infra adapter from DB interpretation profile rows to domain material sources. | Runtime proof uses test DB/session, not production snapshot. |
| `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py` | used | E-005, E-006, E-007, E-009 | Seeds versioned prompt/output/persona/execution/assembly contract family. | Bootstrap was exercised by tests, not manually rerun outside tests. |
| `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` | test-only | E-007, E-009 | Guards canonical owner, stable skeleton, no commercial labels, material/voice/output blocks, profile quantity changes. | Test-only. |
| `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py` | test-only | E-007, E-009 | Guards gateway handoff and single `interpretation_material` occurrence. | Test-only. |
| `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py` | test-only | E-007, E-009 | Guards canonical carrier use, old-carrier rejection, and example shape stability. | Test-only. |
| `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py` | test-only | E-007, E-009 | AST/source guard for contract IDs and forbidden carriers in theme astral owner files. | Test-only. |
| `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py` | test-only | E-007, E-009 | Guards persistence, idempotency, backend-only labels, and invalid contract combinations. | Test-only. |
| `backend/tests/integration/test_theme_astral_prompt_contract_migration.py` | test-only | E-007, E-009 | Guards migration/ORM coherence for prompt contract persistence. | Test-only. |
| `backend/tests/integration/astrology/test_theme_astral_interpretation_material_input.py` | test-only | E-007, E-009 | Guards sourced material reaches provider input without provider call. | Test-only. |
| `_condamad/architecture/theme-astral-prompt-contract/2026-05-28-1217/archi-theme-astral-prompt-contract-v1.md` | used | E-012 | Architecture decision source for skeleton, delivery profile, material, voice, output contract, and old-path closure. | Governance artifact, not runtime code. |
| `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` | used | E-012 | Documents current prompt-generation contract and old-carrier classification. | Documentation evidence only. |
| `_condamad/examples/prompt-generation-cartography/**/free-provider-payload.json` | used | E-008 | Provider payload examples for free profile; negative scan proves no plan/old-carrier leakage. | Existing examples were inspected, not regenerated. |
| `_condamad/examples/prompt-generation-cartography/**/basic-provider-payload.json` | used | E-008 | Provider payload examples for basic profile; negative scan proves no plan/old-carrier leakage. | Existing examples were inspected, not regenerated. |
| `_condamad/examples/prompt-generation-cartography/**/premium-provider-payload.json` | used | E-008 | Provider payload examples for premium profile; negative scan proves no plan/old-carrier leakage. | Existing examples were inspected, not regenerated. |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | out-of-domain | E-011 | Canonical for other natal flows; current `theme_astral` gateway/tests prevent it from replacing `theme_astral_llm_input_v1`. | Not audited for deletion. |
| `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` | out-of-domain | E-011 | Uses commercial plan labels for client projection, not provider payload construction. | Not audited for frontend/client projection behavior. |
| `backend/app/core/sensitive_data.py` | out-of-domain | E-011 | Classifies `chart_json` and `natal_data` as sensitive data, not prompt-carrier ownership. | Not audited for sensitive-data policy. |
| `backend/app/domain/llm/governance/data/prompt_governance_registry.json` | used | E-012 | Registers `theme_astral_llm_input_v1` as a required prompt governance placeholder. | Registry row inspected via scan only. |
| `_condamad/stories/regression-guardrails.md` | used | E-002 | Guardrail registry consulted before findings and candidates. | No update made because no new durable invariant beyond existing tested behavior was discovered. |
| `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1418/00-audit-report.md` | used | E-001 | Standard CONDAMAD audit report for this run. | Audit artifact. |
| `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1418/04-review-adversariale-correction-theme-astral-prompt-contract.md` | used | E-001 | Explicit CS-369 adversarial review deliverable. | Audit artifact. |

## DRY / No Legacy / Dependency Direction

- DRY: no duplicate active `ThemeAstralProviderPayloadBuilder` owner was found; tests enforce a single owner (E-007, E-009).
- No Legacy: old carriers cannot drive `theme_astral` prompt construction without the canonical payload; tests prove rejection and broad scans classify residual tokens outside the audited domain (E-007, E-009, E-011).
- Mono-domain ownership: material selection stays in astrology interpretation domain, provider payload assembly in LLM runtime, persistence in existing LLM owners, and DB loading in infra repository (E-005).
- Dependency direction: audited domain files do not introduce API/frontend ownership into theme astral prompt construction (E-005, E-006).

## Commands Executed

Commands and results are recorded in `01-evidence-log.md`. Python, Ruff, and Pytest commands were run only after `.\.venv\Scripts\Activate.ps1`.

## Residual Risks

| Risk | Decision | Evidence | Follow-up |
|---|---|---|---|
| No real LLM provider call was executed. | accepted limitation | E-013 | Separate provider smoke/eval story only if product requires it. |
| Broad old-token hits remain in unrelated flows. | deferred non-domain context | E-011 | Audit another natal/admin/client/billing domain if needed. |
| Full backend test suite was not rerun. | accepted audit scope limit | E-009, E-010 | Targeted runtime contract tests and lint passed. |
