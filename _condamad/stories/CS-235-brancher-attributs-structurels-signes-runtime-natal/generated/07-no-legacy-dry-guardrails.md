# No Legacy / DRY Guardrails

## Forbidden Unless Explicitly Required By The Story

- Compatibility wrappers
- Transitional aliases
- Legacy import paths
- Duplicate active implementations
- Re-export modules preserving old imports
- Silent fallback behavior
- Tests that preserve legacy paths as nominal behavior

## CS-235 Result

- No compatibility wrapper, alias, fallback, or parallel runtime source was added.
- `SignReferenceData` remains the single domain-facing source of structural sign attributes.
- `SignRuntimeData` copies the four added attributes from references, without deriving values from `sign_code`.
- Guard patterns now include `SEASONAL_QUADRANT_BY_SIGN`, `FERTILITY_BY_SIGN`, `VOICE_BY_SIGN`, `FORM_BY_SIGN`, `HUMANE_BY_SIGN`, and `BESTIAL_BY_SIGN`.
- Targeted negative scan returned exit code 1, classified as PASS: no matches.
