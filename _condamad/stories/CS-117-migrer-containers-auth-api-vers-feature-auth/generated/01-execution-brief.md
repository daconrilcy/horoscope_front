# Execution Brief - CS-117

## Objectif

Migrer les containers auth `SignInForm` et `SignUpForm` depuis
`frontend/src/components/**` vers `frontend/src/features/auth/**`, sans changer
le comportement visible des routes `/login` et `/register`.

## Frontieres

- In scope: fichiers auth exacts, imports des pages/tests auth, suppression des
  deux exceptions auth dans `COMPONENT_API_IMPORT_EXCEPTIONS`, preuves
  before/after et evidence finale.
- Out of scope: contrats API auth, backend, routes, layouts, autres exceptions
  composants, domaines non-auth cites par l'audit.

## Conditions d'arret

- Stop si un consommateur runtime hors pages/tests auth depend encore des
  anciens chemins.
- Stop si la migration requiert un wrapper, alias, fallback, re-export ou
  nouvelle dependance.

## Done

- Anciens fichiers auth supprimes de `components`.
- Consommateurs repointes vers `features/auth`.
- Guards/tests/lint/scans de la story executes ou limites documentees.
- `generated/10-final-evidence.md` et `story-status.md` synchronises.
