# Implementation Plan - CS-117

1. Capturer le baseline exact des imports, fichiers et exceptions auth.
2. Deleguer la tranche `frontend/**` via `condamad-frontend-dev`.
3. Deplacer les deux formulaires et le CSS sous `features/auth`.
4. Repointer pages/tests et retirer seulement les deux exceptions auth.
5. Capturer l'evidence after et executer les tests, lint et scans requis.
6. Lancer la revue CONDAMAD, corriger les findings acceptes, puis synchroniser le statut.

## No Legacy

Aucun wrapper, alias, fallback, re-export ou ancien chemin sous
`frontend/src/components/**` n'est autorise pour les formulaires auth.
