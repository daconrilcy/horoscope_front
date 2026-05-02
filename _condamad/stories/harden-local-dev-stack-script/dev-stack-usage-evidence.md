# Dev Stack Usage Evidence

## Commandes supportees

```powershell
.\scripts\start-dev-stack.ps1
```

- Demarre backend et frontend.
- Ne requiert pas Stripe CLI.
- N'ouvre pas d'onglet Stripe.

```powershell
.\scripts\start-dev-stack.ps1 -WithStripe
```

- Demarre backend, frontend et listener Stripe.
- Requiert Stripe CLI dans le `PATH`.
- Echoue explicitement si Stripe CLI est absent.

## Preuve attendue

- `pytest -q app/tests/unit/test_start_dev_stack_script.py` verifie la branche
  par defaut et la branche `-WithStripe`.
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start-dev-stack.ps1 -Help`
  doit afficher l'aide sans exiger Stripe CLI.
