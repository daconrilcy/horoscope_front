# Implementation Plan

## Current architecture finding

The suite has exactly 9 imports from executable `test_*.py` modules. They cluster into four responsibilities: billing API setup, ops alert setup, prediction engine input builders, and canonical entitlement alert unit setup.

## Selected approach

- Move billing setup into `app.tests.integration.billing_helpers`.
- Move ops alert setup into `app.tests.integration.ops_alert_helpers`.
- Move prediction JSON/input builders into existing non-test `app.tests.regression.helpers`.
- Move canonical entitlement alert unit setup into `app.tests.unit.canonical_entitlement_alert_helpers`.
- Add an AST guard under `app/tests/unit` scanning `app/tests` and `tests`.

## Files to modify

- Billing and ops alert source/consumer tests.
- Engine regression helper and consumers.
- Canonical entitlement alert service tests.
- New architecture guard.
- CONDAMAD evidence files.

## Tests to add or update

- Add `app/tests/unit/test_backend_test_helper_imports.py`.
- Run targeted tests listed in `06-validation-plan.md`.

## No Legacy stance

No compatibility import, alias, or re-export from old `test_*.py` modules is allowed. All consumers must import the canonical helper owner directly.

## Rollback strategy

Revert the helper modules and import rewrites as one story-scoped patch if validation shows behavior changes.
