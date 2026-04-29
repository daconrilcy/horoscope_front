# Seed Validation Decision

Decision: `replace-consumer`

The product rule is active. A seed contract that declares `persona_strategy="required"` must not be accepted when it has no non-empty `required_prompt_placeholders` value. The seed path now validates canonical use case contracts before DB writes and raises `SeedValidationError` on invalid seed configuration.

Audit:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `test_seed_validation.py::test_seed_validation_required_persona_empty_allowed` | test | `historical-facade` | pytest | `test_seed_validation_rejects_required_persona_without_contract_placeholder` | replace-consumer | `backend/app/ops/llm/bootstrap/use_cases_seed.py::validate_use_case_seed_contracts` | Low: validation is pre-write and current canonical contracts pass. |

Implementation evidence:

- `validate_use_case_seed_contracts` validates empty keys, invalid persona strategies, and required persona contracts without any non-empty placeholder.
- `seed_use_cases` calls the validator before mutating the database.
- `test_seed_validation_rejects_required_persona_without_contract_placeholder` proves the required persona empty case raises.
- `test_seed_validation_rejects_required_persona_with_empty_placeholder_values` proves blank placeholder values raise.
- `test_seed_validation_accepts_current_canonical_contracts` proves current canonical seed data remains valid.
