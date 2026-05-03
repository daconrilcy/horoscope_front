# Story Candidates - scripts-ops

No immediate `yes` story candidate is produced by this audit.

The only unresolved finding, `F-001`, is intentionally marked `needs-user-decision` rather than `yes`: implementation should wait for an explicit decision on whether Git Bash / WSL support is part of the supported local Stripe development surface.

If the decision is to remove Bash support, generate a follow-up story from `F-001` to delete `scripts/stripe-listen-webhook.sh`, update `docs/billing-webhook-local-testing.md`, and adapt the two targeted guards that currently prove parity and blocked support status.

If the decision is to support Bash, update `scripts/ownership-index.md` and docs to record the cross-platform support policy, then keep parity coverage in `test_stripe_webhook_local_dev_assets.py`.
