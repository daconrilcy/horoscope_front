# CS-109 - Implementation plan

## Etat observe

Le worktree contient deja les decisions runtime attendues: routes privacy/billing, suppression de `HomePage.tsx`, rattachement `TestimonialsSection`, allowlist alignee et tests ajoutes. La story CS-109 doit les verifier, combler les preuves persistantes, puis fermer les artefacts contradictoires.

## Plan

1. Creer la capsule generated CS-109 et les preuves closure-before/closure-after.
2. Faire verifier la tranche frontend par `condamad-frontend-dev`.
3. Mettre a jour audit `1914`, CS-108 evidence et story status pour retirer l'etat courant bloque.
4. Lancer les validations frontend, scans No Legacy et validations de story avec venv actif pour Python.
5. Produire la revue CONDAMAD finale et corriger les findings eventuels.

## No Legacy

La fermeture doit supprimer l'ambiguite active: pas de `HomePage`, pas de route de compatibilite billing, pas de `needs-user-decision` actif pour les cinq surfaces, pas de `dead/unmounted-page-candidate` actif pour `TestimonialsSection`.
