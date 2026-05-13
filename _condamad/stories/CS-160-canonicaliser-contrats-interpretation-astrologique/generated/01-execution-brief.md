# Execution Brief CS-160

## Story

- Key: `CS-160-canonicaliser-contrats-interpretation-astrologique`
- Source: `_condamad/stories/CS-160-canonicaliser-contrats-interpretation-astrologique/00-story.md`

## Objective

Canonicaliser le contrat runtime de force des maisons: raisons enumerees, score
documente comme normalise, niveau qualitatif stable, et payload public compatible.

## Boundaries

- Modifier uniquement les surfaces backend liees a la force maison, au runtime
  maison, a la serialization chart et aux preuves CONDAMAD.
- Ne pas migrer le scoring produit ni les poids prediction.
- Ne pas introduire de dependance.
- Ne pas creer de wrapper, alias, fallback ou contrat dictionnaire concurrent.

## Done Conditions

- `HouseStrengthReason` et `HouseStrengthLevel` sont produits par le runtime.
- `strength.score` reste stable en JSON public et represente le score normalise.
- Les tests ciblés prouvent le contrat typed et la compatibilite JSON.
- Les scans RG-096 sont executes et classes.
- `generated/10-final-evidence.md` et `story-status.md` sont synchronises.

## Halt Conditions

- Une raison existante ne peut pas etre mappee sans changer de sens.
- Une validation obligatoire echoue sans correction sure dans le scope.
- Un changement prediction devient necessaire pour satisfaire la story.
