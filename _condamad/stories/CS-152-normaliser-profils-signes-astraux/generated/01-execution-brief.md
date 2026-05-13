# Execution Brief

## Story

- Key: `CS-152-normaliser-profils-signes-astraux`
- Objective: normaliser le référentiel des signes astraux côté backend.
- Source: `_condamad/stories/CS-152-normaliser-profils-signes-astraux/00-story.md`

## Boundaries

- Modifier uniquement le backend, les migrations, les tests ciblés et les preuves CONDAMAD.
- Ne pas créer de compatibilité active pour `signs` ou `sign_rulerships`.
- Garder la clé JSON publique `signs` si les contrats existants l'utilisent.
- Ne pas modifier le frontend.

## Required Work

- Renommer le modèle et la table des signes en `AstralSignModel` / `astral_signs`.
- Ajouter `astral_elements`, `astral_modalities`, `astral_polarities` et `astral_sign_profiles`.
- Renommer les maîtrises en `AstralSignRulershipModel` / `astral_sign_rulerships`.
- Supprimer le versioning des maîtrises et ajouter `system`.
- Charger les mots-clés depuis `docs/recherches astro/signs_keywords.json`.
- Adapter les repositories, seeds, migrations et tests ciblés.

## Halt Conditions

- Fichier de keywords absent ou illisible.
- Migration Alembic impossible sans décision utilisateur.
- Validation ciblée backend impossible à réparer localement.
