# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Product contract fields are closed. | `backend/app/domain/theme_natal/product_contract.py` defines `ThemeNatalReadingProductContract` with strict Pydantic `extra="forbid"` fields. | `python -B -m pytest -q backend/tests/unit/domain/theme_natal/test_product_contract_action_resolver.py --tb=short`; `evidence/product-contract-after.txt`. | PASS |
| AC2 | Product action values are closed. | `ThemeNatalReadingAction` exposes only `preview`, `generate_full`, `regenerate`, `download`. | Product contract pytest matrix PASS. | PASS |
| AC3 | Reading kind is `natal_reading`. | `ThemeNatalReadingKind.NATAL_READING` is the sole reading kind and default contract value. | Product contract pytest matrix PASS. | PASS |
| AC4 | Output variants match the target set. | `ThemeNatalOutputVariant` exposes only `free_preview`, `basic_full_reading`, `premium_full_reading`. | Product contract pytest matrix PASS; positive `rg` evidence in `evidence/product-contract-after.txt`. | PASS |
| AC5 | Persona mode stays separate. | `ThemeNatalPersonaMode` is a dedicated field independent from `output_variant`. | `test_persona_mode_is_separate_from_output_variant` PASS. | PASS |
| AC6 | Free preview resolves `free_preview`. | `resolve_theme_natal_reading_action` returns `ALLOWED` with `FREE_PREVIEW` and no generation key. | `test_free_preview_resolves_free_preview_without_generation_key` PASS. | PASS |
| AC7 | Free full generation resolves paywall. | Free `generate_full` returns `LOCKED_PAYWALL` with no contract. | `test_free_full_generation_is_paywalled` PASS. | PASS |
| AC8 | Basic preview avoids short generation. | Basic `preview` returns `ALLOWED` with `FREE_PREVIEW` and no legacy generation key. | `test_basic_preview_does_not_select_generation_contract` PASS; `evidence/legacy-generation-scan-after.txt` zero-hit on new roots. | PASS |
| AC9 | Basic full resolves target variant. | Basic full generation maps to `basic_full_reading` and `theme_natal.reading.basic_full_reading.v1`. | `test_paid_full_generation_resolves_target_variant` PASS. | PASS |
| AC10 | Premium full resolves target variant. | Premium full generation maps to `premium_full_reading` and `theme_natal.reading.premium_full_reading.v1`. | `test_paid_full_generation_resolves_target_variant` PASS. | PASS |
| AC11 | Resolver decision statuses are closed. | `ThemeNatalReadingDecisionStatus` defines only `allowed`, `locked_paywall`, `existing_reading`, `generate_with_contract_key`, `invalid_request`; validator restricts `contract_key` to generation decisions. | `test_decision_status_values_are_closed` and matrix tests PASS. | PASS |
| AC12 | Resolver has no framework imports. | Resolver imports only domain contract types; no API, SQLAlchemy, frontend, infra, services, or LLM imports. | `python -B -m pytest -q backend/tests/unit/domain/theme_natal/test_product_action_resolver_architecture.py --tb=short` PASS. | PASS |
| AC13 | Technical request inputs are rejected. | `ThemeNatalReadingActionRequest` and nested entitlement use strict Pydantic models; rejection test covers `use_case`, `use_case_level`, `variant_code`, `plan`, `forceRefresh`. | Product contract pytest PASS; `evidence/technical-input-scan-after.txt` records zero hits on new roots for the technical input scan. | PASS |
| AC14 | Story evidence artifacts are persisted. | Evidence files created under `_condamad/stories/CS-427-theme-natal-product-contract-action-resolver/evidence/`. | `python -B -c` evidence path check PASS in `evidence/validation.txt`. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
