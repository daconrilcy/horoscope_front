# No Legacy / DRY Guardrails

## Canonical path

- Local Stripe listener: `scripts/stripe-listen-webhook.ps1`.
- Local stack integration: `scripts/start-dev-stack.ps1 -WithStripe`.
- Ownership registry: `scripts/ownership-index.md`.

## Forbidden surfaces

- `scripts/stripe-listen-webhook.sh`
- `stripe-listen-webhook.sh`
- Git Bash or WSL support as nominal local Stripe listener path
- `#!/usr/bin/env bash` for a Stripe listener under `scripts/`
- `blocked-support-decision` for the removed Bash listener
- Any replacement `.sh`, `.bash`, `.cmd`, `.bat`, Python or Node listener for the same responsibility

## Required negative evidence

- `rg -n "stripe-listen-webhook\\.sh|Git Bash|WSL|#!/usr/bin/env bash" scripts docs backend/app/tests`
- `rg --files scripts | rg "stripe-listen-webhook\\.sh"`
- Targeted pytest guards for ownership, local Stripe assets, and dev stack.

## Exceptions

Historical references are allowed only under `_condamad/audits/**` and the story evidence files. No active docs, tests, or scripts may keep Bash/Git Bash/WSL as supported.

## Review checklist

- One local listener implementation remains.
- No compatibility wrapper or alias exists.
- Documentation says dev-only Windows / PowerShell.
- Ownership index exactly matches current root scripts.
- Tests fail if the Bash listener file or docs return.
