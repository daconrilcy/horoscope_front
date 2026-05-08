# Execution Brief - CS-108

## Story key

`CS-108-statuer-pages-publiques-candidates-layout`

## Primary objective

Statuer les cinq residus de layout frontend issus de CS-107 sans ajouter de route non decidee et sans suppression silencieuse.

## Boundaries

- In scope: registre executable `PAGE_LAYOUT_OWNER_CLASSIFICATIONS`, preuves CS-108 avant/apres, inventaire CS-107 aligne, guards page-architecture si necessaire.
- Out of scope: contenu legal, contrat Stripe/backend, CSS/design-system, refonte de layouts, suppression physique des pages.

## Required preflight

- Lire `AGENTS.md`.
- Lire la story CS-108, l'audit source F-101/SC-101 et `regression-guardrails.md`.
- Lire les fichiers frontend cibles et l'inventaire CS-107.
- Preserver les changements preexistants CS-103 a CS-107.

## Write rules

- Ne pas router `PrivacyPolicyPage`, `BillingSuccessPage` ou `BillingCancelPage` sans decision produit/legal/billing sourcee.
- Ne pas supprimer `HomePage` ni `TestimonialsSection` dans cette story.
- Ne pas introduire wildcard, alias, redirect, shim, fallback ou compatibilite.
- Toute entree bloquee doit avoir owner, reason et exit avec echeance ou artefact de sortie.

## Completion definition

- Les cinq residus ont une decision explicite dans l'allowlist et les artefacts.
- Les tests `page-architecture layout`, `App router BillingSuccessPage` et `npm run lint` passent.
- Les scans cibles prouvent l'absence de route non decidee et de preuve `PASS with limitation`.
- `generated/10-final-evidence.md` et `generated/11-code-review.md` sont complets.

## Halt conditions

- Une decision de routage ou suppression est requise mais absente.
- Une validation frontend obligatoire echoue sans correction sure.
- Un changement necessite de modifier un contrat backend, CSS/design-system ou une dependance.
