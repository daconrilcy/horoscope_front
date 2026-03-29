# Code Review Story 61.57: Validation locale webhook Stripe CLI

Date: 2026-03-29
Statut: corrigé

## Findings

1. `HIGH` `docs/billing-webhook-local-testing.md`
   L'AC5 n'était pas réellement satisfaite: la commande `stripe events resend ... --webhook-endpoint=we_123456` demandée par la story n'était pas documentée alors que la tâche était cochée et la story marquée `done`.

2. `MEDIUM` `docs/billing-webhook-local-testing.md`
   La runbook était rédigée en Bash alors que l'environnement cible du dépôt est Windows/PowerShell. Cela rendait la validation locale moins directement exécutable pour l'équipe.

3. `MEDIUM` `docs/billing-webhook-local-testing.md`
   La doc présentait comme "événements supportés" uniquement le sous-ensemble de 7 événements standardisés, alors que le backend gère aussi `customer.updated`, `customer.subscription.paused`, `customer.subscription.resumed` et `customer.subscription.trial_will_end`.

4. `MEDIUM` `scripts/stripe-listen-webhook.sh`
   Le script shell avait été enregistré avec un BOM UTF-8 devant le shebang, ce qui peut casser l'exécution sur des environnements POSIX.

## Corrections appliquées

- Ajout de la note et de la commande `--webhook-endpoint=we_123456` dans le runbook.
- Ajout d'un script PowerShell `scripts/stripe-listen-webhook.ps1` et bascule de la documentation vers des commandes Windows/PowerShell en premier.
- Clarification du périmètre: liste standardisée des 7 événements pour le listener par défaut, plus documentation explicite des événements supplémentaires déjà gérés par le backend.
- Suppression du BOM du script `scripts/stripe-listen-webhook.sh`.
- Ajout d'un test automatisé qui verrouille les points critiques de la doc et l'alignement entre les scripts `.ps1` et `.sh`.
