# No Legacy / DRY Guardrails

## Forbidden unless explicitly required by the story

- Compatibility wrappers
- Transitional aliases
- Legacy import paths
- Duplicate active implementations
- Re-export modules preserving old imports
- Silent fallback behavior
- Tests that preserve legacy paths as nominal behavior

## Required when relevant

- One canonical path per responsibility
- Negative search evidence for removed symbols or imports
- Tests or architecture guards that fail if a legacy path is reintroduced
- Explicit errors instead of silent fallback for missing canonical configuration

## CS-439 applied guardrails

- Public product-action data is normalized only from `theme_natal*` schema payloads; old interpretation envelopes are not accepted by the modern hook.
- `NatalInterpretation.tsx` must not branch on `natal_long_free`, `natal_interpretation_short`, `forceRefresh`, `force_refresh`, `use_case_level`, or `shouldRefreshShortAfterBasicUpgrade`.
- `NatalInterpretationContent.tsx` must not decide rendering from old `use_case` values.
- `variant_code` is allowed only for entitlement display/gate state, not command body construction.
- Positive frontend fixtures for old public natal use cases are forbidden; `natalPublicDomGuard.test.tsx` may retain denylist literals.

## Reviewer questions

- Did we delete the legacy path or only move the problem?
- Did we preserve an old path “temporarily”?
- Did any test import the old namespace?
- Did any doc, registry, or config still reference the old path?
