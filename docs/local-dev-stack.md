# Stack locale de developpement

Ce document decrit le lancement local supporte pour backend et frontend sous
Windows / PowerShell. Le chemin canonique du script est
`scripts/start-dev-stack.ps1`.

## Demarrage standard

Depuis la racine du depot:

```powershell
.\scripts\start-dev-stack.ps1
```

Cette commande ouvre Windows Terminal avec deux onglets:

- backend FastAPI sur `127.0.0.1:8001`;
- frontend Vite sur `127.0.0.1:5173`.

Stripe n'est pas requis pour ce demarrage standard.

## Demarrage avec webhooks Stripe

Pour tester les webhooks Stripe en local:

```powershell
.\scripts\start-dev-stack.ps1 -WithStripe
```

Le parametre `-WithStripe` ajoute un onglet qui execute
`scripts/stripe-listen-webhook.ps1`. Dans ce mode uniquement, la Stripe CLI doit
etre installee et disponible dans le `PATH`; sinon le script echoue avec une
erreur explicite invitant a installer Stripe CLI ou a relancer sans `-WithStripe`.

La procedure detaillee des evenements Stripe reste documentee dans
`docs/billing-webhook-local-testing.md`.
