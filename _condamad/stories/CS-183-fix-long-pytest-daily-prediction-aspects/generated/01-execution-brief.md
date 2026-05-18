# Execution Brief

## Objectif principal

Corriger les causes racines des échecs longs liés aux aspects daily sans introduire de fallback legacy ni de duplication active.

## Bornes

- Backend uniquement.
- Surfaces prévues: résolution des aspects, routeurs daily, tests associés, capsule CONDAMAD.
- Préserver les changements utilisateur existants.

## Conditions de fin

- Tests ciblés daily/API, moteur et sensibilité natale relancés.
- Lint Ruff relancé.
- Evidence finale et registre de story mis à jour.

## Halt conditions

- Incohérence de contrat runtime nécessitant un choix produit.
- Migration impossible à valider sans casser les données existantes.
