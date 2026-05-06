<!-- Preuve before des libelles consultations contenant le vocabulaire legacy. -->

# CS-072 Consultation Labels Before

## Commandes de baseline

| Commande | Repertoire | Resultat | Synthese |
|---|---|---|---|
| `rg -n "legacy|Legacy" frontend/src/i18n/consultations.ts` | racine repo | PASS | 12 hits `(Legacy)` dans les libelles consultation `type_dating`, `type_pro`, `type_event`, `type_free`. |

## Hits initiaux

| Cle | Langue | Libelle before | Classification before |
|---|---|---|---|
| `type_dating` | `fr` | `Dating / Rendez-vous amoureux (Legacy)` | `historical-facade` |
| `type_dating` | `en` | `Dating / Romantic meetup (Legacy)` | `historical-facade` |
| `type_dating` | `es` | `Cita / Encuentro romántico (Legacy)` | `historical-facade` |
| `type_pro` | `fr` | `Choix professionnel (Legacy)` | `historical-facade` |
| `type_pro` | `en` | `Professional choice (Legacy)` | `historical-facade` |
| `type_pro` | `es` | `Elección profesional (Legacy)` | `historical-facade` |
| `type_event` | `fr` | `Événement important (Legacy)` | `historical-facade` |
| `type_event` | `en` | `Important event (Legacy)` | `historical-facade` |
| `type_event` | `es` | `Evento importante (Legacy)` | `historical-facade` |
| `type_free` | `fr` | `Question libre (Legacy)` | `historical-facade` |
| `type_free` | `en` | `Free question (Legacy)` | `historical-facade` |
| `type_free` | `es` | `Pregunta libre (Legacy)` | `historical-facade` |

## Decision before

Les identifiants de consultation restent inchanges. Seule la mention visible
`(Legacy)` doit disparaitre des libelles utilisateur.
