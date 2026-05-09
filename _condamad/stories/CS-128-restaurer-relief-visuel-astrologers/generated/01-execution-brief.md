# Execution Brief

<!-- Capsule d'execution CONDAMAD pour restaurer le relief visuel /astrologers. -->

## Story

- Story key: `CS-128-restaurer-relief-visuel-astrologers`
- Objective: restaurer le relief visuel compact de `/astrologers` sans regonfler `frontend/src/App.css`.
- Domain: `frontend/src/features/astrologers` plus owners CSS App existants `tokens.css`, `cards.css`, `media.css`.

## Boundaries

- Modifier seulement les styles et guards necessaires a la matiere visuelle des cartes.
- Ne pas changer API, routes, donnees, copie, navigation, rotation, badges visibles ou profil.
- Ne pas creer de nouveau fichier sous `frontend/src/styles/app/`.
- Ne pas ajouter de dependance.
- Garder `frontend/src/App.css` import-only.

## Required Evidence

- Artefacts before/after dans le dossier de story.
- Guards Vitest pour material card, featured, icon, avatar/chips, App.css et selectors interdits.
- Scans negatifs `App.css`, `astrologer-*`, `style=`.
- Validation frontend ciblee, lint, build.
- Validation story sous venv active.

## Halt Conditions

- Besoin d'un nouveau module CSS ou d'une dependance.
- Besoin de rendre visibles les badges provider/default/featured sur la liste compacte.
- Echec de validation lie a la story sans correction sure.
