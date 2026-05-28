# Audit theme-astral-prompt-contract - CS-377

## Domain Closure Status

Status: `open`.

Verdict global: corrections requises avant cloture finale.

Ce run audite le contrat backend LLM `theme_astral` apres CS-372 a CS-376. Il reste read-only sur le code applicatif: aucun fichier backend, frontend, test, migration, documentation produit ou exemple n'a ete corrige par cet audit.

## Audit Boundary

In scope: contrat `theme_astral_llm_input_v1`, profils `essential`, `expanded`, `complete`, `birth_context`, exemples JSON, documentation, persistence, tests, scan anti-carriers historiques, plan commercial backend-only, provider smoke CS-376.

Out of scope: correction des findings, provider externe sans opt-in explicite, frontend, auth, styling, refonte de l'architecture LLM.

## Prior Audit And Story History Consulted

| Item | Status | Evidence | Current classification |
|---|---|---|---|
| `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1418/` | prior same-domain audit | E-003 | prior provider limitation still active as F-002; new example drift found by E-011 |
| `CS-372-aligner-profils-livraison-theme-astral-db-provider` | done | E-004, E-008, E-009 | delivery profile runtime and tests PASS |
| `CS-373-structurer-birth-context-theme-astral-llm-input` | done | E-004, E-008, E-011 | runtime tests PASS but target examples drift |
| `CS-374-renforcer-exemples-json-theme-astral-textes-interpretation` | done | E-004, E-012 | source examples acceptable with explicit mixed source status |
| `CS-375-mettre-a-jour-docs-structure-json-theme-astral` | done | E-004, E-011, E-012 | docs mostly aligned, but example README now masks stale provider payload birth fields |
| `CS-376-validation-provider-smoke-theme-astral` | done | E-004, E-010 | smoke is implemented and opt-in; real provider path skipped without opt-in |
| `_condamad/stories/regression-guardrails.md` | consulted | E-002 | RG-002 and RG-022 mapped; no new guardrail update justified in this audit |

## Closure Analysis

- Closed: CS-372 delivery profiles are coherent in constants, seed, persistence tests, provider builder tests, and example profile names (E-007, E-008, E-009).
- Closed: runtime `birth_context` builder and persistence schema are covered by tests and source inspection (E-007, E-008).
- Still active: final example payloads under the mandated `1973-04-24-1100-paris-theme-astral-v1` directory do not carry structured Paris birth data even though the scenario and documentation say they should (F-001, E-011).
- Still active as accepted limitation: the real external provider call remains skipped unless the opt-in marker and credentials are available (F-002, E-010).
- Deferred non-domain: broad `plan`, `free`, `basic`, `premium`, `chart_json`, `natal_data`, and `llm_astrology_input_v1` hits in unrelated natal, admin, entitlement, and test flows are outside this `theme_astral` provider contract audit (E-009).

## Verdict Global

`theme_astral` runtime code, DB persistence and targeted tests are healthy, but the final contract cannot be closed while the official example payloads contradict the structured birth-context requirement. Decision: corrections required.

## Findings Par Severite

| ID | Severity | Confidence | Type | Category | Evidence | Decision |
|---|---|---|---|---|---|---|
| F-001 | Medium | High | bug | runtime-contract-drift | E-011, E-013 | Correction required in CS-378 or equivalent |
| F-002 | Info | High | accepted risk | observability-gap | E-010, E-013 | Accepted limitation unless a credentialed provider smoke is explicitly opted in |
| F-003 | Info | High | accepted risk | runtime-contract-drift | E-012 | Source quality is acceptable but still partly fixture-backed and clearly documented |

## Matrice De Conformite CS-372 A CS-376

| Story | Verdict | Evidence | Notes |
|---|---|---|---|
| CS-372 | PASS | E-004, E-007, E-008, E-009 | `essential`, `expanded`, `complete` are runtime and DB canonical. |
| CS-373 | PARTIAL | E-004, E-008, E-011 | Runtime PASS; official examples fail the structured Paris birth-data expectation. |
| CS-374 | PASS | E-004, E-012 | Examples have sourced material and explicit `production-like` fixture disclosure. |
| CS-375 | PARTIAL | E-004, E-011, E-012 | Docs explain `birth_context`, but example README says fields are exposed while payload fields are null. |
| CS-376 | PASS with skipped external path | E-004, E-010 | Smoke test exists, standard run skips provider call without opt-in. |

## Matrice Des Scans

| Scan | Result | Interpretation | Evidence |
|---|---|---|---|
| Delivery profile scan | PASS | Required names and owners are present; broad hits include out-of-domain examples and tests. | E-008 |
| Old-carrier and plan scan | PASS with classified hits | Active target provider examples have no forbidden commercial or old-carrier values; broad hits are tests or non-domain runtime flows. | E-009, E-013 |
| Birth context example check | FAIL | Target provider payloads keep `birth_date`, `birth_time_local`, and place fields null while `chart_id` embeds the scenario. | E-011 |
| Example source quality check | PASS | `interpretation_material` has non-empty text and explicit `source_ref`; fixture-backed families are disclosed. | E-012 |
| Provider smoke status | SKIPPED | Opt-in provider marker test is implemented and skipped without explicit external-call prerequisites. | E-010 |

## Commandes Executees

Commands and results are recorded in `01-evidence-log.md`. Python, Ruff, and Pytest commands were run after `.\.venv\Scripts\Activate.ps1`.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `backend/app/domain/llm/configuration/theme_astral_contracts.py` | used | E-007, E-008 | Canonical contract IDs, delivery profile maps, schema, DB resolver. | No production DB dump. |
| `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` | used | E-007, E-008 | Canonical provider payload builder and `birth_context` projection. | Provider external behavior not exercised. |
| `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py` | used | E-007, E-009 | Seeds canonical active prompt contract families and archives stale depths. | Tested through integration, not manually reseeded here. |
| `backend/app/domain/astrology/interpretation/interpretation_material_builder.py` | used | E-007, E-012 | Builds sourced interpretation material for provider payloads. | Source breadth depends on available seeded data. |
| `backend/app/infra/db/repositories/interpretation_material_source_repository.py` | used | E-007, E-012 | DB adapter for interpretation source material. | Test DB only. |
| `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` | test-only | E-007, E-008 | Guards skeleton, plan mapping, material, birth context, and old-carrier/plan absence. | Test-only. |
| `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py` | test-only | E-007, E-008 | Guards DB persistence, schemas, active profile resolution, stale depth archival. | Test-only. |
| `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py` | test-only | E-007, E-008 | Guards canonical handoff and old-carrier rejection. | Test-only. |
| `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py` | test-only | E-007, E-009 | AST/source guard for forbidden old carriers in target runtime owners. | Test-only. |
| `backend/tests/llm_orchestration/test_theme_astral_provider_smoke.py` | test-only | E-010 | Opt-in provider smoke owner with default skip. | Real provider call skipped. |
| `backend/pyproject.toml` provider smoke marker | used | E-010 | Registers `provider_smoke` marker for opt-in external tests. | Marker only. |
| `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/free-provider-payload.json` | used | E-011, E-012 | Official free provider example; contains source material but stale/null birth fields. | Needs correction before closure. |
| `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/basic-provider-payload.json` | used | E-011, E-012 | Official basic provider example; contains source material but stale/null birth fields. | Needs correction before closure. |
| `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/premium-provider-payload.json` | used | E-011, E-012 | Official premium provider example; contains source material but stale/null birth fields. | Needs correction before closure. |
| `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/intermediate-data.json` | used | E-011 | Scenario metadata records Paris, France and Europe/Paris. | Does not repair provider payload contradiction. |
| `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md` | used | E-011, E-012 | Documents scenario and source nature. | Contradicts actual null provider birth fields. |
| `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md` | used | E-008, E-011 | Compares profile density and claims structured fields. | Does not expose null-value drift. |
| `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` | used | E-008, E-011 | Canonical documentation for JSON shape and backend-only plan resolution. | Example contradiction remains outside this doc. |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | out-of-domain | E-009 | Active for other natal flows, not canonical `theme_astral` provider contract. | Not audited for deletion. |
| `backend/app/domain/llm/runtime/adapter.py` | out-of-domain | E-009 | Broad old-carrier and plan hits belong to non-theme-astral adapter flows. | Not audited here. |
| `backend/app/services/llm_generation/natal/interpretation_service.py` | out-of-domain | E-009 | Natal generation uses old/natal contract terms outside audited provider path. | Not audited here. |
| `_condamad/stories/regression-guardrails.md` | used | E-002 | Existing guardrails consulted before findings. | No update made. |

## DRY No Legacy Dependency Direction

- DRY: no duplicate active provider builder was found; runtime tests route through the canonical builder (E-007, E-008).
- No Legacy: target runtime guard rejects `chart_json`, `natal_data`, and `llm_astrology_input_v1` in theme astral owners (E-007, E-009).
- Mono-domain ownership: LLM runtime owns provider payload; astrology interpretation owns material; infra repository owns DB source loading (E-007, E-012).
- Dependency direction: no evidence of frontend or API ownership inside the target provider contract path was found during this audit.

## Risques Residuels

| Risk | Decision | Evidence | Follow-up |
|---|---|---|---|
| Official examples contradict structured birth-context closure. | bug | E-011 | Regenerate or patch examples and validator in CS-378. |
| Real provider acceptance remains unexecuted. | accepted risk | E-010 | Run opt-in provider smoke only with explicit credentials and approval. |
| Some source material remains production-like fixture-backed. | accepted risk | E-012 | Accept because README names fixture ownership and no table exists today. |

## Decision

Corrections required: close F-001 before final closure. F-002 and F-003 do not block closure if the product accepts the documented limitations.
