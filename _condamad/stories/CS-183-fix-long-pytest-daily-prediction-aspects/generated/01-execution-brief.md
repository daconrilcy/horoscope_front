# Execution Brief

## Objectif principal

Corriger les causes racines des échecs longs liés aux aspects des prédictions
quotidiennes sans introduire de fallback legacy ni de duplication active.

## Bornes

- Backend uniquement.
- Surfaces prévues: résolution des aspects, routeurs quotidiens, tests associés,
  capsule CONDAMAD.
- Préserver les changements utilisateur existants.

## Conditions de fin

- Tests ciblés des routes quotidiennes/API, moteur et sensibilité natale relancés.
- Lint Ruff relancé.
- Evidence finale et registre de story mis à jour.

## Halt conditions

- Incohérence de contrat runtime nécessitant un choix produit.
- Migration impossible à valider sans casser les données existantes.
