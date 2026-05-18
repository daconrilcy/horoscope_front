# Execution Brief - CS-185

## Objectif

Brancher `astral_sign_profiles`, `astral_elements`, `astral_modalities` et
`astral_polarities` comme source runtime des profils structurels de signes
natals.

## Perimetre

- Backend uniquement.
- Pas de migration schema.
- Pas de changement frontend.
- Pas de nouvelle dependance.
- Refus explicite des profils manquants, incomplets ou `unknown`.

## Done Conditions

- `AstrologyRuntimeReferenceRepository.load("1.0.0")` retourne 12 signes
  profiles depuis la DB.
- `SignReferenceData` et `SignRuntimeData` portent `element`, `modality` et
  `polarity`.
- Le builder conserve ces profils pour les signes sans occupant.
- Les tests repository, builder, signature et guards passent.
- Les artefacts `evidence/` avant/apres, OpenAPI et guard sont produits.

## Halt Conditions

- Besoin d'une migration pour un champ non present au schema actuel.
- Besoin de modifier le contrat HTTP public sans decision separee.
- Validation backend impossible a stabiliser sans elargir le scope.
