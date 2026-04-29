# Seed Validation Current Behavior

Repository inspection found the canonical seed surface in:

- `backend/app/ops/llm/bootstrap/use_cases_seed.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`

Before implementation:

- `SeedValidationError` existed but no pre-write contract validation executed in `seed_use_cases`.
- `backend/app/tests/unit/test_seed_validation.py` acknowledged that validation did not raise yet and ended with `pass`.
- Canonical use case contracts already expressed active persona strategy with `persona_strategy="required"` and non-empty `required_prompt_placeholders`.

Classification:

| Item | Type | Classification | Decision | Proof |
|---|---|---|---|---|
| `test_seed_validation.py::test_seed_validation_required_persona_empty_allowed` | test | `historical-facade` | replace | Facade body was `pass`; canonical seed contract surface is active. |
| required persona seed validation | behavior | `canonical-active` | keep with executable validation | `SeedValidationError` existed and seed contracts already carry persona strategy metadata. |
