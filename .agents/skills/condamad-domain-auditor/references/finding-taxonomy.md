# Finding Taxonomy

## Categories

- `boundary-violation`: a domain owns behavior that belongs elsewhere.
- `dependency-direction-violation`: an import or runtime dependency points against the allowed direction.
- `legacy-surface`: an old route, wrapper, alias, shim, fallback, or re-export remains active.
- `duplicate-responsibility`: two active implementations own the same decision.
- `missing-canonical-owner`: responsibility exists without a single authoritative owner.
- `runtime-contract-drift`: runtime behavior differs from source contracts or documented routes.
- `missing-guard`: no guard prevents reintroduction of a forbidden surface.
- `missing-test-coverage`: no focused tests prove the expected behavior or denial path.
- `security-risk`: authentication, secret, data exposure, or unsafe processing risk.
- `policy-bypass`: authorization or entitlement policy can be skipped.
- `data-integrity-risk`: persistence or mutation state can become inconsistent.
- `observability-gap`: missing logs, metrics, traces, or audit trail for operationally relevant behavior.
- `needs-user-decision`: the correct target state depends on product or architecture direction.

## Severities

- `Critical`: production, security, data-loss, or policy-bypass risk.
- `High`: architecture violation, No Legacy violation, missing guard, or active duplicate implementation.
- `Medium`: maintainability risk or incomplete validation.
- `Low`: improvement opportunity.
- `Info`: observation only.

## Confidence

Use `High`, `Medium`, or `Low`.

Confidence reflects evidence quality, not severity.
