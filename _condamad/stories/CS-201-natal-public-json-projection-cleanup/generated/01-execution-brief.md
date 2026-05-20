# Execution Brief

## Story

- Key: `CS-201-natal-public-json-projection-cleanup`
- Objective: stabiliser la projection JSON publique du theme natal sans recalcul astrologique ni changement de route/API.

## Boundaries

- Modifier seulement la projection publique, ses tests backend et les preuves CONDAMAD.
- Garder `json_builder.py` comme serialiseur de faits deja presents dans `NatalResult`.
- Ne pas toucher au frontend, aux routes API, aux migrations, aux seeds ou aux moteurs de domaine.

## Required Evidence

- Tests de projection et de persistance.
- Scans d'imports/mots interdits.
- Snapshots avant/apres sous `evidence/`.
- Validation markdown avec impact contrat genere et absence de changement score/faits.

## Halt Conditions

- Besoin de renommer ou supprimer un champ public non explicitement autorise.
- Besoin de recalculer une donnee manquante depuis `json_builder.py`.
- Validation backend impossible pour une raison non compensable.
