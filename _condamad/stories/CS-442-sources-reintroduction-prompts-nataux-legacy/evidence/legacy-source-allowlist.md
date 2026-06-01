# Legacy Source Allowlist

Allowed residual classes: historical proof, explicit rejection/extinction guard, readonly persisted-row compatibility, or non-prompt action token. No residual entry is a seedable prompt source.

| Residual owner | Residual token | Class | Rationale | Guard/proof |
|---|---|---|---|---|
| `backend/app/domain/llm/prompting/context.py` | `natal_interpretation` field/name | readonly historical context | Reads persisted historical interpretation text for non-modern contexts; not a prompt seed/catalogue/admin source. | after scan; architecture suite |
| `backend/app/domain/llm/prompting/schemas.py` | `offer_natal_interpretation` | non-prompt action token | Chat action intent string, not old prompt key. | after scan |
| `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | `offer_natal_interpretation` | non-prompt action token | Output schema action enum, not old prompt key. | after scan |
| `backend/app/domain/llm/prompting/tests/__init__.py` | `LEGACY_NATAL_FEATURE = "natal_interpretation"` | test-only compatibility fixture | Governance test helper labels legacy mapping only. | orchestration suite |
| `backend/scripts/diagnose_natal_interpretation_duplicates.py` | `user_natal_interpretations` table/model | readonly diagnostic | Diagnoses persisted historical rows; does not create prompts or seed use cases. | after scan |
| `backend/scripts/fix_schemas_strict.py` | `offer_natal_interpretation` | non-prompt schema action token | Schema action enum, not old prompt source. | after scan |
| `backend/tests/**` and `backend/app/tests/**` | old natal keys | rejection/extinction/read-only tests | Existing tests assert deleted endpoints, historical row handling, or anti-return guards. | targeted pytest suites PASS |
| `_condamad/**` | old natal keys | historical proof | Story, report and evidence references only. | final evidence |
