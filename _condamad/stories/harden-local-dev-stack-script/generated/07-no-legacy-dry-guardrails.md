# No Legacy / DRY Guardrails

## Canonical Behavior

- `scripts/start-dev-stack.ps1` starts backend and frontend by default.
- Stripe webhook listening is an explicit opt-in branch controlled by `-WithStripe`.
- The only Stripe listener implementation remains `scripts/stripe-listen-webhook.ps1`.

## Forbidden Patterns

- Unconditional `Get-Command stripe`.
- Unconditional `stripe-listen-webhook.ps1` tab creation.
- `SkipStripe` or any inverse compatibility switch.
- Silent fallback when `-WithStripe` is requested and Stripe CLI is missing.
- Inline duplication of the Stripe listener command.

## Required Evidence

- Pytest guard proving default arguments contain no Stripe tab or Stripe CLI requirement.
- Pytest guard proving `-WithStripe` creates the Stripe tab and keeps Stripe CLI validation conditional.
- Negative scan for `fallback|compat|alias|SkipStripe` in `scripts/start-dev-stack.ps1`.
- Documentation scan for `start-dev-stack.ps1` and `WithStripe`.

## Guardrail Classification

- `RG-015` applies because a new backend scripts-quality test is added and must be registered in `ops-quality-test-ownership.md`.
- `RG-023` applies because `scripts/start-dev-stack.ps1` is under the root scripts ownership surface; `scripts/ownership-index.md` must remain coherent.

## Review Checklist

- No second Stripe listener implementation exists.
- No hidden default Stripe dependency remains.
- No compatibility alias or fallback switch was added.
- Docs present backend/frontend as default and Stripe as opt-in.
