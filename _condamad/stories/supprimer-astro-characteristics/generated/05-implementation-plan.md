# Implementation Plan

1. Retirer `AstroCharacteristicModel` et sa relation de `reference.py`.
2. Simplifier `ReferenceRepository`: plus d'import JSON pour traits DB, plus de seed/clone/clear/complete/read de characteristics.
3. Ajouter une migration Alembic qui drop `astro_characteristics` en upgrade et la recree en downgrade pour reversibilite.
4. Adapter les tests importeurs: suppression du modele dans les cleanups, contrat public sans `characteristics`, migration head sans table.
5. Ajouter un guard cible si pertinent pour bloquer la reintroduction active du modele/table.
6. Executer tests cibles, scans, Ruff, pytest, puis completer evidence et registres.

Rollback: revert du patch code/tests/migration/capsule et downgrade Alembic de la nouvelle revision si applique localement.
