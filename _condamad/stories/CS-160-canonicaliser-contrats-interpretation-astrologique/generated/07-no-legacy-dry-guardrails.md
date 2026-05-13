# No Legacy / DRY Guardrails CS-160

## Canonical Ownership

- Raisons de force maison: `backend/app/domain/astrology/interpretation`.
- Score runtime maison: `HouseStrengthRuntimeData.normalized_score`, expose en
  JSON sous `strength.score` pour compatibilite publique documentee.
- Niveau qualitatif: `HouseStrengthLevel`.

## Forbidden Patterns

- Strings libres ajoutees a `strength.reasons`.
- `reasons.append("...")` dans `app/domain/astrology`.
- Listes de strings passees directement a `HouseStrengthRuntimeData`.
- Comparaison brute `strength.score >` ou `<` dans `app/domain/prediction`.
- Import de `app.domain.prediction` ou symboles produit depuis astrology.
- Dictionnaire comme nouveau contrat d'interpretation astrologique.

## Required Negative Evidence

- Scans RG-095 et RG-096 executes.
- Hits restants classes comme enum owner, test guard, serializer public stable ou
  reference historique hors runtime.

## Review Checklist

- Un seul contrat runtime de force maison reste actif.
- Le payload public garde des strings stables pour `strength.reasons`.
- Aucun fallback produit n'est ajoute dans astrology.
- Les tests prouvent les enums et le niveau.
