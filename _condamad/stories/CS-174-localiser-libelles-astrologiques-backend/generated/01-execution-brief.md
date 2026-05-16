# Execution Brief - CS-174

## Objectif

Localiser les libelles affichables des signes astrologiques backend via `languages` et `astral_sign_translations`, sans conserver de mapping applicatif `SIGN_NAMES_FR` dans les surfaces ciblees.

## Bornes

- Modifier uniquement le backend et les preuves CONDAMAD.
- Conserver les codes canoniques existants dans les payloads et prompts.
- Ajouter les champs de libelles requis par `00-story.md`.
- Ne pas toucher au frontend ni au mapping PDF hors perimetre.

## Done Conditions

- Resolver canonique sous `backend/app/services/reference_data`.
- Tests resolver, chart JSON, contextes natals et guards anti-retour.
- Scans negatifs `SIGN_NAMES_FR` et imports resolver dans `app/domain/astrology`.
- Evidence finale et statut synchronises.
