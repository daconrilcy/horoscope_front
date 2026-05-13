# Implementation Plan CS-160

## Findings

- Le producteur runtime actif est `backend/app/domain/astrology/interpretation/house_strength.py`.
- Le chemin `backend/app/domain/astrology/calculators/house_strength.py` cite par la story n'existe pas.
- Le serializer public lit `strength.score` et `strength.reasons`; ces noms JSON doivent rester stables.

## Plan

1. Ajouter les enums et dataclasses de contrat sous `interpretation/house_strength_contracts.py`.
2. Remplacer `HouseStrengthRuntimeData` par un contrat runtime typed avec
   `normalized_score`, `level`, `reasons` enumerees et propriete `score`.
3. Migrer `HouseStrengthEvaluator` vers les enums sans append de strings brutes.
4. Serialiser `reasons` en valeurs JSON et ajouter `level`.
5. Adapter les tests ciblés et ajouter des guards contre les raisons ad hoc.
6. Capturer les artefacts before/after et la preuve de scan.

## Rollback

- Revenir aux fichiers touchés par la story uniquement.
- Ne pas toucher aux fichiers non suivis preexistants hors capsule CS-160.
