# Implementation Plan

1. Résoudre les orbes natales par paire de corps via les règles canoniques ciblées.
2. Charger les profils d'aspects publics par `reference_version_id` du snapshot.
3. Ajuster les tests unitaires qui créent des aspects sans profil ou sans `orb_max`.
4. Corriger l'attente de version Alembic devenue obsolète si le test cible la tête actuelle.
5. Relancer les tests ciblés et Ruff dans le venv.

## No Legacy

Aucun alias, shim ou chemin de compatibilité. Les absences de référence restent explicites pour les snapshots persistés; les doubles de tests sans référence ne déclenchent pas de recherche par version active.
