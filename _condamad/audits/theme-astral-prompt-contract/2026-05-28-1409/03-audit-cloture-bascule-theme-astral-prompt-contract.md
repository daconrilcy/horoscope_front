# Audit cloture bascule theme astral prompt contract

## Verdict

`valide avec risques residuels acceptes`.

The switch is closed for the `theme_astral` prompt contract. The accepted residual risk is that no real LLM provider call was executed, because CS-368 explicitly forbids provider calls. Current proof is based on code inspection, prior deliverables, targeted tests, lint, examples, and scans.

## Statut des criteres CS-361 a CS-367

| Story | Status | Proof |
|---|---|---|
| CS-361 | closed | `interpretation_material` now reaches provider payload through sourced builder/repository and targeted tests. |
| CS-362 | closed | free/basic/premium share stable payload skeleton; plan labels are backend-only. |
| CS-363 | closed | architecture target exists and is represented in current runtime constants/builders. |
| CS-364 | closed | existing LLM DB/config owners carry prompt, input, response, delivery, persona, assembly, and execution profile refs. |
| CS-365 | closed | canonical material builder selects source-attributed material from calculated facts. |
| CS-366 | closed | canonical provider payload builder emits one payload carrier and avoids duplicated prompt data. |
| CS-367 | closed | gateway rejects missing canonical payload and guards old carriers. |

## Preuve d'utilisation des textes d'interpretation

`backend/app/infra/db/repositories/interpretation_material_source_repository.py` loads planet, house, and aspect interpretation profiles from DB models into `InterpretationMaterialSource`. `backend/app/domain/astrology/interpretation/interpretation_material_builder.py` selects only sourced items with `source_ref`, `fact_ref`, and text/hint material. `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` places the result under `input_data.interpretation_material`. Targeted pytest command: 10 passed, 9 deselected.

## Preuve de structure stable entre delivery profiles

The provider payload top-level keys are fixed: `runtime_contract`, `safety_contract`, `astrologer_voice`, `feature_context`, `delivery_profile`, `input_data`, `output_contract`. The `input_data` keys are fixed: `birth_context`, `astrological_facts`, `interpretation_material`, `selected_themes`, `limits`. Tests assert identical skeletons for `free`, `basic`, and `premium`; only budgets and values vary.

## Preuve de non-exposition du plan commercial

Commercial plans are accepted only as backend inputs to `resolve_theme_astral_provider_delivery_profile`. Provider-visible payloads expose non-commercial `delivery_profile` values. Tests assert that string values do not contain `plan`, `free`, `basic`, or `premium`, and examples use `delivery_profile` rather than commercial labels.

## Preuve de persistence/versioning DB

CS-364 evidence and current tests prove the active family through existing LLM owners: prompt versions, assembly configs, output schemas, personas, execution profiles, and contract constants. Current targeted persistence and migration tests pass.

## Preuve de suppression legacy

For `theme_astral`, `LLMGateway.build_user_payload` requires `theme_astral_llm_input_v1` and raises `InputValidationError` if old carriers are supplied without it. `test_theme_astral_prompt_contract_bigbang.py` and `test_theme_astral_prompt_contract_guard.py` cover rejection and guard behavior. Remaining `llm_astrology_input_v1`, `chart_json`, and `natal_data` hits are natal/admin/test contexts, not active `theme_astral` provider runtime.

## Commandes executees

- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests/integration/llm/test_theme_astral_provider_payload_handoff.py tests/llm_orchestration/test_theme_astral_provider_payload_builder.py tests/integration/test_theme_astral_prompt_contract_persistence.py tests/integration/test_theme_astral_prompt_contract_migration.py tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py tests/architecture/test_theme_astral_prompt_contract_guard.py --tb=short` -> PASS, 10 passed, 9 deselected.
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` -> PASS.
- `rg -n "theme_astral_prompt_v1|theme_astral_llm_input_v1|interpretation_material|delivery_profile|astrologer_voice" backend\app backend\tests _condamad\examples\prompt-generation-cartography _condamad\docs\prompt-generation-cartography` -> PASS with canonical hits.
- `rg -n "NATAL_SHORT_PROMPT|NATAL_COMPLETE_PROMPT|theme_astral_prompt_contract_v1|llm_astrology_input_v1|chart_json|natal_data" backend\app\domain\llm\runtime backend\app\domain\llm\configuration backend\app\ops\llm\bootstrap backend\tests\integration\llm backend\tests\architecture backend\tests\llm_orchestration` -> PASS with hits classified as natal/admin/test/guard or theme astral rejection evidence.
- `git diff --name-only -- backend\app backend\tests backend\migrations frontend\src _condamad\examples _condamad\architecture _condamad\stories\regression-guardrails.md` -> PASS before audit artifact writes, no protected-source diff.

## Risques residuels

| Risk | Decision |
|---|---|
| No real LLM provider call. | accepted; forbidden by CS-368. |
| Old carriers still exist for non-theme-astral natal/admin/test flows. | accepted non-domain context. |
| Some interpretation material families beyond planet/house/aspect remain driven by explicit builder inputs/tests rather than a new DB adapter in this audit. | accepted; source-attributed material reaches the payload and missing sections remain explicit. |

