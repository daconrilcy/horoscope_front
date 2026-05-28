# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Stable identifiers are persisted. | `theme_astral_prompt_contract_v1`, `theme_astral_llm_input_v1`, `theme_astral_response_contract_v1` in `theme_astral_contracts.py`, canonical use case/output schema registry, and DB seed. | `python -B -m pytest -q tests\integration\test_theme_astral_prompt_contract_persistence.py tests\integration\test_theme_astral_prompt_contract_migration.py --tb=short` PASS; manifest JSON persisted. | PASS |
| AC2 | Active-read returns the canonical family. | `resolve_active_theme_astral_prompt_contract(db, depth=...)` reads published assembly/prompt/schema/persona/profile. | `test_active_read_returns_canonical_family_without_plan_leakage` PASS. | PASS |
| AC3 | Prompt templates use versioned registry storage. | Prompt text is stored in `llm_prompt_versions` through `seed_theme_astral_prompt_contract.py`; no provider/gateway change. | Targeted tests PASS; `rg` owner scan confirms identifiers are in LLM registry owners/tests. | PASS |
| AC4 | Delivery profile hides plan names. | `THEME_ASTRAL_DELIVERY_PROFILES` exposes `essential`/`deep` non-commercial depths; active read omits plan labels. | Negative assertions for `free/basic/premium` in prompt/read model PASS; scan hits only those negative assertions. | PASS |
| AC5 | Astrologer voice links to persona style. | Seed creates/enables `LlmPersonaModel.code == theme_astral_astrologer_voice_v1`; resolver emits style-only `astrologer_voice`. | `test_theme_astral_seed_persists_stable_contract_family` and active-read test PASS. | PASS |
| AC6 | Seeds are idempotent. | Seed archives duplicate active rows and updates one published prompt/profile plus two depth assemblies. | `test_theme_astral_seed_is_idempotent_for_active_rows` PASS. | PASS |
| AC7 | Invalid version combinations fail. | Resolver raises explicit `ValueError` for unsupported depth and incompatible output schema. | `test_invalid_theme_astral_version_combinations_fail_deterministically` PASS. | PASS |
| AC8 | Migration state matches ORM metadata. | Existing LLM tables cover all persistence needs; no new migration/table added. | `test_theme_astral_contract_reuses_existing_llm_tables_at_head` PASS; full backend pytest PASS. | PASS |
| AC9 | No parallel registry is introduced. | Reuses canonical use case/output schema/prompt/persona/profile/assembly plus governance placeholder registry. | `rg -n "theme_astral_prompt_contracts|llm_theme_astral_contracts|class .*ThemeAstral.*Model|__tablename__\s*=\s*['\"]theme_astral" backend\app backend\tests -g "*.py"` => PASS no matches. | PASS |
| AC10 | Story evidence artifacts are persisted. | Baseline and manifest stored under story `evidence/`; final evidence and traceability updated. | `condamad_validate.py` PASS after evidence update. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
