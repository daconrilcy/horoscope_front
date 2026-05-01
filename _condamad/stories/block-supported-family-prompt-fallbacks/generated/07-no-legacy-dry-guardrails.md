# No Legacy / DRY Guardrails

## Forbidden keys

`PROMPT_FALLBACK_CONFIGS` must not contain:

- `chat`
- `chat_astrologer`
- `guidance_contextual`
- `natal_interpretation`
- `horoscope_daily`

## Canonical runtime source

- Supported families resolve prompts through governed assemblies and canonical profiles.
- Production missing assembly must raise `GatewayConfigError` with `error_code="missing_assembly"`.
- Non-prod bootstrap remains bounded by the existing gateway guard and exact fallback allowlist.

## Exact fallback exceptions

The remaining keys in `PROMPT_FALLBACK_CONFIGS` are exactly:

- `astrologer_selection_help`
- `event_guidance`
- `guidance_daily`
- `guidance_weekly`
- `natal_interpretation_short`
- `natal_long_free`
- `test_guidance`
- `test_natal`

They are documented in `fallback-exception-audit.md` and guarded by `test_prompt_fallback_config_exceptions_are_exact`.

## Required negative evidence

- `test_supported_use_cases_are_absent_from_prompt_fallback_configs`
- `test_supported_use_cases_do_not_build_fallback_config`
- `test_prompt_fallback_config_exceptions_are_exact`
- `test_production_rejects_missing_assembly_for_supported_families`

## Hit classification

| Pattern | Classification | Action |
|---|---|---|
| `PROMPT_FALLBACK_CONFIGS` in `catalog.py` | allowed bounded registry | Guarded by exact allowlist. |
| `PROMPT_FALLBACK_CONFIGS` in tests | test_guard_expected_hit | Required for reintroduction guard. |
| `legacy_use_case_fallback` in `runtime/contracts.py` | out_of_scope_with_justification | Enum value used by existing observability contract, not a prompt fallback owner. |
| `legacy_use_case_fallback` in `test_ops_monitoring_llm_api.py` | allowed_historical_reference | Existing observability fixture outside this story scope. |

## Reviewer checklist

- Confirm no removed prompt text remains under `PROMPT_FALLBACK_CONFIGS`.
- Confirm exact exception list is intentionally strict.
- Confirm production rejection covers `chat`, `guidance`, `natal`, `horoscope_daily`.
