# Guide : Gestion des Astrologues (V2)

## Architecture

Depuis la Story 60.21, la gestion des astrologues est découplée des personas LLM génériques. 
Chaque astrologue public possède désormais un profil enrichi dans la table `astrologer_profiles`, liée 1:1 à un `llm_personas`.

### Tables concernées

1.  **`llm_personas`** : Directives techniques pour le LLM (tone, verbosity, topics).
2.  **`astrologer_profiles`** : Informations publiques (nom, bio, photo, spécialités, genre).
3.  **`astrologer_prompt_profiles`** : Prompt spécifique à injecter pour ce persona, permettant un contrôle fin sans polluer la table de base.

## Procédure de mise à jour

### Ajouter un nouvel astrologue

1.  Créer une entrée dans `llm_personas`.
2.  Créer une entrée correspondante dans `astrologer_profiles` avec le même `persona_id`.
3.  (Optionnel) Créer un prompt spécifique dans `astrologer_prompt_profiles`.

### Modifier un profil public

Les modifications se font directement dans `astrologer_profiles`. Le frontend consomme les champs suivants :
- `display_name` (nom affiché)
- `first_name` / `last_name`
- `photo_url`
- `bio_short`
- `bio_long`
- `specialties` (JSON list)
- `public_style_label` (ex: "Mystique", "Analytique")

## Backfill et Seed

Le script `backend/scripts/backfill_astrologer_profiles.py` peut être relancé de manière idempotente pour synchroniser les informations enrichies des 6 profils canoniques.

Le seed initial `backend/scripts/seed_astrologers_6_profiles.py` reste la source de création des personas de base.
