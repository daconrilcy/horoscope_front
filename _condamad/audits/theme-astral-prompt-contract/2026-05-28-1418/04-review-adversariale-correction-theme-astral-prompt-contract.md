# Review adversariale correction theme astral prompt contract

## Verdict global

`valide avec risque residuel accepte`.

No accepted Critical or Major/High defect was found in the current `theme_astral` prompt contract. No application runtime correction was required; the audit review only corrected audit evidence and a backend DB test-harness classification guard needed for full validation.

## Findings tries par severite

| ID | Severite | Decision | Preuves | Commentaire |
|---|---|---|---|---|
| F-001 | Info | accepte avec risque | E-001, E-013 | No real LLM provider invocation was executed; this is a scoped audit limitation, not an implementation defect. |

No Critical, Major/High, Medium, or Low real finding was accepted.

## Preuves sourcees

- Contract and skeleton: `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` declares fixed top-level keys and `input_data` keys, then asserts skeleton drift locally (E-005, E-006).
- Provider profile mapping: `backend/app/domain/llm/configuration/theme_astral_contracts.py` maps backend commercial plans to non-commercial provider profiles and exposes versioned contract IDs/schemas (E-005, E-006).
- Interpretation material: `backend/app/domain/astrology/interpretation/interpretation_material_builder.py` selects only source-attributed material; `backend/app/infra/db/repositories/interpretation_material_source_repository.py` adapts DB interpretation profiles to material sources (E-005, E-006).
- Gateway old-path closure: `backend/app/domain/llm/runtime/gateway.py` requires `theme_astral_llm_input_v1` for `theme_astral`; targeted tests prove `chart_json`, `natal_data`, and `llm_astrology_input_v1` do not replace it (E-005, E-007, E-009).
- Persistence/versioning: `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py` and persistence tests prove prompt, schema, persona, execution profile, and assembly rows are explicit and idempotent (E-005, E-007, E-009).
- Examples: provider payload JSON examples have no commercial plan labels or old carriers (E-008).

## Decisions

| Axis | Decision | Evidence |
|---|---|---|
| `theme_astral_llm_input_v1` | accepted | E-005, E-007, E-009 |
| Provider payload skeleton | accepted | E-005, E-007, E-009 |
| `interpretation_material` reachability | accepted | E-005, E-007, E-009 |
| Delivery profile backend-only plan handling | accepted | E-005, E-007, E-008, E-009 |
| `astrologer_voice` style-only boundary | accepted | E-005, E-007, E-009 |
| `output_contract` and persistence | accepted | E-005, E-007, E-009 |
| Old-path closure | accepted | E-007, E-009, E-011 |

## Corrections appliquees

No application runtime correction was applied. During this audit review, `backend/app/tests/unit/test_backend_db_test_harness.py` was updated to classify the intentional in-memory SQLite/create_all usage in `backend/tests/unit/infra/db/repositories/test_interpretation_material_source_repository.py`, then the targeted guard and full backend suite passed (E-014, E-015).

## Tests ajoutes ou modifies

None. Existing targeted tests were executed as evidence.

## Commandes executees

- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py tests/integration/llm/test_theme_astral_provider_payload_handoff.py tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py tests/architecture/test_theme_astral_prompt_contract_guard.py tests/integration/test_theme_astral_prompt_contract_persistence.py tests/integration/test_theme_astral_prompt_contract_migration.py tests/integration/astrology/test_theme_astral_interpretation_material_input.py --tb=short`
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .`
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .`
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q`
- Targeted `rg` scans listed in `01-evidence-log.md`.

## Risques residuels

- No real LLM provider call was executed. Accepted because provider invocation is out of scope.
- Broad old-token hits remain outside `theme_astral` in natal/admin/test/billing/evaluation contexts. Deferred as non-domain.
- Backend validation is complete for local contract behavior: format check, lint, targeted tests, and full `pytest -q` passed.
