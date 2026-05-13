# Implementation Plan

## Initial Findings

- `SignModel` utilise encore la table `signs`.
- `SignRulershipModel` utilise encore `sign_rulerships` et `reference_version_id`.
- Le seed prediction compte et purge les maîtrises par version.
- Le payload public de référence expose encore la clé JSON `signs`; ce contrat reste inchangé.

## Plan

1. Capturer les artefacts baseline.
2. Ajouter une migration Alembic de convergence vers `astral_*`.
3. Renommer les modèles actifs et exports.
4. Adapter repositories et seed pour profils, taxonomies et maîtrises non versionnées.
5. Adapter les tests ciblés et les guards.
6. Exécuter format, lint, tests, scans et revue.

## No Legacy Stance

Aucun alias actif des anciennes tables ou classes n'est conservé. Les anciens noms ne doivent survivre que dans l'historique Alembic et les artefacts CONDAMAD.
