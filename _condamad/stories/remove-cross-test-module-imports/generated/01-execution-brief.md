# Execution Brief

## Story key

`remove-cross-test-module-imports`

## Primary objective

Remplacer les 9 imports croises depuis des modules `test_*.py` par des imports vers des helpers non executables, sans changer le comportement ni les assertions des tests consommateurs.

## Boundaries

- Scope limite aux tests backend sous `backend/app/tests` et `backend/tests`.
- Extraire seulement les helpers deja partages par import croise.
- Ajouter une garde deterministe qui echoue si un test importe un autre module `test_*.py`.
- Conserver les fixtures DB et assertions existantes hors deplacement strictement necessaire.

## Non-goals

- Pas de refonte de la topologie globale des tests.
- Pas de changement d'API, de services runtime ou de frontend.
- Pas de duplication locale des helpers extraits.
- Pas d'alias ou re-export depuis les anciens modules de test.
- Pas de nouveau dossier racine sous `backend/`.

## Preflight checks

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Capturer `git status --short`.
- Capturer le scan avant des imports croises.

## Write rules

- Utiliser des modules non executables pour les helpers partages.
- Garder les imports consommateurs directs vers les nouveaux proprietaires.
- Ne pas supprimer de test.
- Ne pas creer de dependance.

## Done conditions

- Le scan des imports croises retourne zero hit.
- Les helpers partages ont un proprietaire non executable.
- Les tests cibles passent.
- La garde anti-reintroduction passe.
- Les preuves finales sont renseignees.

## Halt conditions

- Un helper importe est en fait une assertion de test impossible a extraire sans changer le sens du test.
- Une validation obligatoire echoue sans correction claire dans le scope.
- Un changement destructif ou hors story devient necessaire.
