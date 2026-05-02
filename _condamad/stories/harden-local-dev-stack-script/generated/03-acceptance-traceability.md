# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | La branche par defaut ignore Stripe. | `scripts/start-dev-stack.ps1` adds explicit `-WithStripe` and does not check/start Stripe unless set. | `pytest -q app/tests/unit/test_start_dev_stack_script.py` passed. | PASS |
| AC2 | Stripe explicite exige la CLI. | `Get-Command stripe` is inside the `-WithStripe` branch with a clear error. | `pytest -q app/tests/unit/test_start_dev_stack_script.py` passed. | PASS |
| AC3 | La doc nomme `WithStripe`. | `docs/local-dev-stack.md` and `docs/development-guide-backend.md` describe default and `-WithStripe` usage. | `rg -n "start-dev-stack.ps1|WithStripe" docs` returned expected hits. | PASS |
| AC4 | Aucun fallback silencieux ou alias n'est ajoute. | `scripts/start-dev-stack.ps1` has no `SkipStripe`, compatibility switch, alias, or fallback behavior. | `rg -n "fallback|compat|alias|SkipStripe" scripts/start-dev-stack.ps1` returned zero hits. | PASS |
| AC5 | La story valide. | CONDAMAD story remains valid/linted; final evidence completed. | Story validate and lint commands passed after venv activation. | PASS_WITH_LIMITATIONS |
