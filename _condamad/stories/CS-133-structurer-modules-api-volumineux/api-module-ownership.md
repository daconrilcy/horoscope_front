<!-- Carte d'ownership des sous-modules API crees par CS-133. -->

# CS-133 - Ownership modules API

| Surface | Owner | Responsabilite | Entry point public |
|---|---|---|---|
| `frontend/src/api/admin-prompts/index.ts` | domaine admin prompts API | contrats, requetes, hooks et helpers admin prompts, avec parsing d'erreur delegue au client canonique | `frontend/src/api/adminPrompts.ts` |
| `frontend/src/api/natal-chart/index.ts` | domaine natal chart API | contrats, requetes, hooks et effets navigateur natal, avec parsing d'erreur delegue au client canonique | `frontend/src/api/natalChart.ts` |
| `frontend/src/api/index.ts` | facade globale actuelle | export public stable, politique definie par CS-136 | `@api` |

## Guard executable

`frontend/src/tests/api-architecture.test.ts` garde:

- `adminPrompts.ts` et `natalChart.ts` comme entrypoints publics uniquement.
- l'absence de parser d'erreur local dans les sous-domaines migres.
