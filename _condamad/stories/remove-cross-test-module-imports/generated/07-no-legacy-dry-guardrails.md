# No Legacy / DRY Guardrails

## Forbidden patterns

- Import actif depuis un module executable `test_*.py`.
- Alias ou re-export depuis les anciens modules de tests.
- Copie locale des helpers extraits dans chaque consommateur.
- Nouveau dossier racine sous `backend/`.
- Compatibilite transitoire pour les anciens imports.

## Canonical destinations

| Responsibility | Canonical owner |
|---|---|
| Billing API reusable helpers | `app.tests.integration.billing_helpers` |
| Ops alert reusable helpers | `app.tests.integration.ops_alert_helpers` |
| Regression engine JSON/input helpers | `app.tests.regression.helpers` |
| Canonical entitlement alert unit helpers | `app.tests.unit.canonical_entitlement_alert_helpers` |
| Cross-test import guard | `app/tests/unit/test_backend_test_helper_imports.py` |

## Required negative evidence

- `rg -n "from app\.tests\.(integration|unit|regression)\.test_|from tests\.integration\.test_" app/tests tests -g test_*.py` must return zero hit.
- The architecture guard must parse imports with AST and fail on imports from modules whose basename starts with `test_`.

## Regression guardrails

- `RG-005` applies because helpers must not move API/service ownership into test helpers.
- `RG-006` applies because the new architecture guard must remain readable and independent.

## Review checklist

- No helper is duplicated in multiple test files.
- No old test module re-exports helper names.
- No production code changed.
- Tests still assert the same behavior.
- Any broad legacy keyword hits are classified if they are in touched files.
