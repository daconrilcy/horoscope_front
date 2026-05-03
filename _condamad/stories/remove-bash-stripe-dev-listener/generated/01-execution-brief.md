# Execution Brief

## Story key

`remove-bash-stripe-dev-listener`

## Objective

Retirer `scripts/stripe-listen-webhook.sh` et faire de `scripts/stripe-listen-webhook.ps1` l'unique listener Stripe local supporte, en mode developpement Windows / PowerShell uniquement.

## Boundaries

- Domaine unique: `scripts/`, documentation locale Stripe, tests backend de garde.
- Aucun changement runtime backend webhook Stripe.
- Aucun support Git Bash, WSL, CI, production ou deploiement pour la Stripe CLI locale.

## Preflight

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Capturer `git status --short`.
- Capturer le scan baseline des references Bash/Git Bash/WSL avant suppression.

## Write rules

- Supprimer le script Bash au lieu de le repointer.
- Ne pas creer de wrapper, alias, fallback ou script de remplacement.
- Garder `scripts/start-dev-stack.ps1 -WithStripe` sur le script PowerShell.
- Garder l'ownership `scripts/ownership-index.md` aligne avec les fichiers racine restants.

## Done conditions

- AC1 a AC6 ont preuve code et validation.
- Tests cibles passent.
- Negative scan actif sans hit pour Bash/Git Bash/WSL.
- `generated/10-final-evidence.md` est complete.

## Halt conditions

- Nouveau consommateur first-party imposant Git Bash/WSL.
- Test cible lie a la story en echec sans correction sure.
- Changement necessaire hors perimetre de la story.
