# Execution Brief

## Story key

`CS-181-supprimer-constantes-astrologiques-hardcodees`

## Objectif

Supprimer les constantes astrologiques métier DB-backed et les fallbacks legacy du backend, avec preuves avant/après, registre d'exceptions exact et guards anti-réintroduction.

## Bornes

- Inclure `backend/app/services/natal`, `backend/app/domain/astrology`, `backend/app/domain/prediction`, `backend/app/services/prediction` seulement quand la duplication astrology DB-backed est concernée.
- Exclure `frontend/**`, migrations DB et changement de contrat API public.
- Ne pas créer de référentiel JSON ou mapping concurrent.

## Règles d'écriture

- Utiliser les contrats runtime, repositories et catalogues canoniques existants.
- Supprimer les fallbacks plutôt que les repointer.
- Classer toute constante conservée avec fichier, symbole, raison et décision de permanence.
- Ajouter une garde déterministe pour les mappings d'aspects et les fallbacks natal.

## Définition de complétion

- AC1 à AC7 ont code evidence et validation evidence.
- `hardcoded-astrology-before.md`, `hardcoded-astrology-after.md`, `astrology-constant-exceptions.md` et `guard-evidence.md` existent.
- Tests ciblés, guards, lint et scans requis passent dans le venv.
- Review CONDAMAD finale propre avant statut `done`.

## Conditions d'arrêt

- Source canonique manquante pour une constante métier DB-backed non classable.
- Changement nécessaire de contrat API public.
- Tests requis en échec sans correction sûre.
