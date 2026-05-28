# Audit theme-astral-prompt-contract - CS-368

## Domain Closure Status

Status: `closed`.

Verdict: `valide avec risques residuels acceptes`.

The audited domain is the read-only closure of the `theme_astral` prompt contract switch after CS-361 through CS-367. No application code, backend tests, migrations, seeds, frontend files, examples, architecture documents, or guardrail registry entries were changed by this audit. The only new audit surfaces are under `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1409/`.

## Prior Audit And Story History Consulted

| Item | Status | Evidence | Current classification |
|---|---|---|---|
| `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1152/` | CS-361 source audit | E-003 | closed by CS-365 plus current handoff proof |
| `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1203/` | CS-362 source audit | E-003 | closed by CS-366/CS-367 plus current shape proof |
| `_condamad/architecture/theme-astral-prompt-contract/2026-05-28-1217/archi-theme-astral-prompt-contract-v1.md` | CS-363 architecture | E-003 | implemented decision source |
| `_condamad/stories/CS-364-*/generated/10-final-evidence.md` | persistence/versioning story | E-004 | closed; current status tracker says done |
| `_condamad/stories/CS-365-*/generated/10-final-evidence.md` | interpretation material story | E-004 | closed; current status tracker says done |
| `_condamad/stories/CS-366-*/generated/10-final-evidence.md` | provider payload story | E-004 | closed; current status tracker says done |
| `_condamad/stories/CS-367-*/generated/10-final-evidence.md` | bigbang story | E-004 | closed; current status tracker says done |
| `_condamad/stories/regression-guardrails.md` | guardrail registry | E-002 | relevant invariants consulted; no update justified |

## Closure Analysis

- Prior active CS-361 findings about missing rich table-backed material reaching the LLM payload are closed by `InterpretationMaterialBuilder`, `InterpretationMaterialSourceRepository`, `ThemeAstralProviderPayloadBuilder`, and the targeted handoff/material tests (E-005, E-006, E-009).
- Prior active CS-362 findings about provider shape drift, plan leakage, duplicated carriers, backend-only metadata exposure, and basic/premium wording are closed by the stable provider payload builder, bigbang gateway enforcement, regenerated examples, and tests (E-005, E-006, E-007, E-009).
- No active in-domain implementation finding remains for `theme_astral` prompt contract closure.
- Deferred non-domain context: `llm_astrology_input_v1`, `chart_json`, `natal_data`, and old natal prompt seeds still exist for other natal/admin/test flows. They are not active `theme_astral` provider carriers under the current gateway and guard tests (E-007, E-009).
- Residual accepted risk: no real LLM provider call was executed because the story forbids provider calls. Closure is based on builder, gateway, DB, test, example, and scan evidence.

## Statut des criteres CS-361 a CS-367

| Story | Closure status | Evidence | Notes |
|---|---|---|---|
| CS-361 | closed | E-003, E-005, E-009 | Table-backed/audited material now reaches `input_data.interpretation_material`. |
| CS-362 | closed | E-003, E-006, E-007, E-009 | Provider skeleton is stable; plan labels are absent from prompt-visible payload. |
| CS-363 | closed | E-003, E-005, E-006 | Architecture decisions are represented in runtime contract constants and builder skeleton. |
| CS-364 | closed | E-004, E-009 | Prompt, input, response, delivery, persona, and assembly/versioning use existing LLM persistence owners. |
| CS-365 | closed | E-004, E-005, E-009 | Material builder and repository bridge DB interpretation tables into sourced material. |
| CS-366 | closed | E-004, E-006, E-009 | Canonical provider payload builder emits the target skeleton once. |
| CS-367 | closed | E-004, E-007, E-009 | Gateway rejects missing canonical `theme_astral_llm_input_v1` and old carriers cannot replace it. |

## Preuve d'utilisation des textes d'interpretation

`InterpretationMaterialSourceRepository` adapts planet, house, and aspect interpretation profile DB rows into `InterpretationMaterialSource` values. `InterpretationMaterialBuilder` selects source-attributed items only when they match calculated facts and contain source text or writing hints. `ThemeAstralProviderPayloadBuilder` writes the resulting block to `input_data.interpretation_material`. Targeted tests prove material handoff without provider call (E-005, E-009).

## Preuve de structure stable entre delivery profiles

The provider builder declares fixed top-level keys `runtime_contract`, `safety_contract`, `astrologer_voice`, `feature_context`, `delivery_profile`, `input_data`, and `output_contract`. It also declares fixed `input_data` keys. Tests and examples cover `free`, `basic`, and `premium`; quantities vary through budgets, not through structural keys (E-006, E-009).

## Preuve de non-exposition du plan commercial

`resolve_theme_astral_provider_delivery_profile` maps backend commercial plans to non-commercial delivery profiles before provider handoff. The provider builder test asserts that JSON string values do not contain `plan`, `free`, `basic`, or `premium`, and the regenerated examples expose `delivery_profile` rather than a commercial plan field (E-006, E-008, E-009).

## Preuve de persistence/versioning DB

CS-364 final evidence and current tests prove reuse of existing LLM owners: prompt versions, assembly configs, output schemas, personas, execution profiles, and active contract family resolution. Current targeted tests for persistence and migration pass (E-004, E-009).

## Preuve de suppression legacy

The gateway special-cases `theme_astral`: it requires `theme_astral_llm_input_v1` and raises `InputValidationError` when only old carriers are supplied. The old `theme_astral_llm_input_v1_builder.py` path is asserted absent by tests. Scans still find natal/admin/test references to `llm_astrology_input_v1`, `chart_json`, and `natal_data`, but the in-domain tests classify those as non-theme-astral or guard evidence (E-007, E-009).

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1409/00-audit-report.md` | used | E-001 | Standard domain-auditor closure report. | Audit artifact only. |
| `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1409/03-audit-cloture-bascule-theme-astral-prompt-contract.md` | used | E-001 | Explicit CS-368 deliverable path shape. | Audit artifact only. |
| `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` | used | E-005, E-006 | Canonical provider payload builder and stable skeleton owner. | No real provider call by story rule. |
| `backend/app/domain/llm/configuration/theme_astral_contracts.py` | used | E-005, E-009 | Versioned constants, schemas, delivery profile mapping, active contract resolver. | DB proof relies on tests, not manual DB dump. |
| `backend/app/domain/llm/runtime/gateway.py` `build_user_payload` | used | E-005, E-007, E-009 | Enforces canonical `theme_astral_llm_input_v1` payload and rejects old carriers for `theme_astral`. | Other natal paths remain out of domain. |
| `backend/app/domain/astrology/interpretation/interpretation_material_builder.py` | used | E-005, E-009 | Selects source-attributed interpretation material from calculated facts. | Source breadth is limited by available repository adapters. |
| `backend/app/infra/db/repositories/interpretation_material_source_repository.py` | used | E-005, E-009 | Loads planet, house, and aspect DB interpretation profiles into material sources. | Runtime source loading is test-backed, no production DB snapshot included. |
| `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py` | used | E-006, E-009 | Seeds canonical prompt/output/persona/execution/assembly contract family. | Bootstrap execution not rerun during this read-only audit. |
| `_condamad/examples/prompt-generation-cartography/**/free-provider-payload.json` | used | E-008 | Example provider payload for free profile. | Existing example inspected, not regenerated by this audit. |
| `_condamad/examples/prompt-generation-cartography/**/basic-provider-payload.json` | used | E-008 | Example provider payload for basic profile. | Existing example inspected, not regenerated by this audit. |
| `_condamad/examples/prompt-generation-cartography/**/premium-provider-payload.json` | used | E-008 | Example provider payload for premium profile. | Existing example inspected, not regenerated by this audit. |
| `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` | test-only | E-006, E-009 | Guards stable skeleton, material/voice/output blocks, no plan labels, no duplicate carrier. | Test-only surface. |
| `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py` | test-only | E-009 | Guards gateway handoff and single material occurrence. | Test-only surface. |
| `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py` | test-only | E-009 | Guards active contract persistence/readback. | Test-only surface. |
| `backend/tests/integration/test_theme_astral_prompt_contract_migration.py` | test-only | E-009 | Guards migration/ORM metadata coherence for contract persistence. | Test-only surface. |
| `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py` | test-only | E-007, E-009 | Guards old carrier rejection and canonical prompt contract. | Test-only surface. |
| `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py` | test-only | E-007, E-009 | AST/source guard against old theme astral carriers. | Test-only surface. |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | out-of-domain | E-007 | Still canonical for other natal flows, not `theme_astral` provider payload. | Not audited for deletion. |
| `backend/app/ops/llm/bootstrap/seed_29_prompts.py` | out-of-domain | E-007 | Legacy/current natal prompt seed references `llm_astrology_input_v1`; not active `theme_astral`. | Not audited for natal closure. |
| `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py` | out-of-domain | E-007 | Natal v3 prompt seed references `llm_astrology_input_v1`; not active `theme_astral`. | Not audited for natal closure. |
| `_condamad/stories/regression-guardrails.md` | used | E-002 | Existing RG-002/RG-022 and LLM prompt guardrails consulted. | No new durable invariant was added because CS-368 is audit-only and no registry enrichment is authorized. |

## Findings Summary

No active in-domain finding remains. The closure verdict is not `valide` only because the story forbids a real provider call; that limitation is an accepted residual risk, not an implementation finding.

## Commands executees

Commands are reproduced in `01-evidence-log.md`. Python, Ruff, and Pytest commands were run after `.\.venv\Scripts\Activate.ps1`.

## Risques residuels

| Risk | Decision | Evidence | Follow-up |
|---|---|---|---|
| No real LLM provider call was executed. | accepted | E-009 | None; explicit story non-goal. |
| Old natal carriers still exist for other natal/admin/test flows. | accepted non-domain context | E-007 | None for `theme_astral`; audit another natal domain if needed. |
| Source material breadth is currently planet/house/aspect-backed by repository adapter, with other material sections sourced through builder inputs/tests. | accepted | E-005, E-009 | No blocker for closure because provider payload receives sourced material and missing sections remain explicit. |

