# Source Checklist - CS-271

## Sources consultees

| Source | Couverture | Statut |
|---|---|---|
| `_story_briefs/cs-271-define-permission-matrix-for-business-technical-astrology-debug-data.md` | Objectif, perimetre inclus, hors perimetre, AC et validations attendues. | PASS |
| `_condamad/stories/story-status.md` | Ligne `CS-271`, chemin story et brief source. | PASS |
| `_condamad/stories/CS-270-internal-role-model/00-story.md` | Dependances de vocabulaire roles internes. | PASS |
| `docs/architecture/internal-role-model.md` | Roles cibles et etat non actif hors RBAC. | PASS |
| `backend/app/core/rbac.py` | Source runtime des roles actifs. | PASS |
| `docs/admin-implementation-overview.md` | Surface admin actuelle et comportement admin-only. | PASS |

## Alignement brief

- Les domaines `business`, `technical`, `astrology` et `debug` sont couverts par la matrice.
- Les roles `ADMIN`, `MARKETER`, `TECHNO` et `ASTRO_EXPERT` sont couverts.
- Les actions `read`, `search`, `export`, `replay` et `correct` sont explicites.
- Les donnees de naissance sont sensibles et masquees hors contexte admin explicitement approuve.
- Les traces, prompts et replay sont des categories separees.
- Les acces client B2C restent hors matrice admin.
- `MARKETER`, `TECHNO` et `ASTRO_EXPERT` restent non actifs tant que RBAC n'est pas implemente.
- Les permissions incertaines sont marquees comme decisions ouvertes.

## Neutralite runtime

- Aucun fichier `backend/app`, `frontend/src` ou `backend/migrations` n'a ete modifie pour CS-271.
- Le test de contrat importe `VALID_ROLES` depuis `backend/app/core/rbac.py` et verifie l'absence des roles cibles.
- La matrice est documentaire et ne cree aucun endpoint, guard, seed, migration, client genere ou changement B2C.
