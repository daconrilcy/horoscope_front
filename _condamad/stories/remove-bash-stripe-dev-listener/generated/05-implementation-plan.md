# Implementation Plan

## Current finding

The repository has two local Stripe listener scripts with the same events and target. PowerShell is already used by `start-dev-stack.ps1 -WithStripe`; Bash remains documented and registered as `needs-user-decision`.

## Selected approach

Delete the Bash script and update all active first-party references to state that local Stripe CLI listener support is dev-only and Windows / PowerShell-only.

## Changes

- Persist baseline scan and removal audit.
- Delete `scripts/stripe-listen-webhook.sh`.
- Remove Bash row and `blocked-support-decision` from `scripts/ownership-index.md`.
- Update local Stripe runbook to remove Git Bash/WSL and Bash examples.
- Update tests to assert Bash absence and PowerShell-only canonical behavior.
- Persist after-scan and final evidence.

## No Legacy stance

No wrapper, alias, fallback, replacement shell script, or documentation exception is allowed.

## Rollback

Restore the deleted Bash file and ownership/docs/test references from git only if the story is rejected; do not keep a partial compatibility path.
