<!-- Commentaire global: ce document fixe le contrat canonique beginner_summary_v1 sans creer d'implementation runtime ni de surface publique. -->

# Contrat `beginner_summary_v1`

## Role

`beginner_summary_v1` est la projection B2C deterministe destinee aux contextes public-user, beginner, free et basic.

Ce contrat documente une forme cible lisible pour un client debutant. Il ne cree pas de builder, de route API, de schema OpenAPI, de table, de migration, de client frontend, de serializer runtime, de prompt LLM, de narration longue ou de projection premium.

Le registre produit conserve le primitif `beginner_summary`; `beginner_summary_v1` en precise la version contractuelle simple pour les usages gratuits ou basiques.

## Source factuelle

`structured_facts_v1` est l'upstream factual source de `beginner_summary_v1`.

La projection debutante consomme uniquement une selection lisible issue de cette base. `structured_facts_v1` n'est pas un direct public payload et ne doit pas etre expose comme dump complet dans le resume B2C.

## Forme de projection

| Champ | Regle |
|---|---|
| `projection_id` | Valeur exacte: `beginner_summary_v1`. |
| `audience` | `public-user`, `beginner`, `free`, `basic`. |
| `source_projection` | Valeur exacte: `structured_facts_v1`. |
| `allowed_fields` | Ensemble limite aux signes principaux, a l'ascendant quand disponible, a la maison dominante quand disponible et aux thèmes dominants. |
| `state` | Une des valeurs deterministes: `loading`, `empty`, `degraded`, `unavailable`. |
| `degraded_reason` | Raison controlee presente uniquement quand `state` vaut `degraded`, par exemple `no_time`. |
| `display_messages` | Messages courts, stables, rattaches a un code controle. |
| `excluded_surfaces` | Donnees techniques completes, full facts, raw runtime, debug, audit, traces internes et champs premium. |

Les signes principaux couvrent uniquement les etiquettes client utiles, par exemple Soleil et Lune. Les degres, orbes, scores bruts, graphes de calcul et payloads runtime restent exclus.

## Etats deterministes

| Etat | Trigger deterministe | Message controle |
|---|---|---|
| `loading` | Trigger: les faits amont ou la projection controlee ne sont pas encore disponibles pour l'affichage. | `BGS_LOADING`: "Votre resume est en preparation." |
| `empty` | Trigger: aucun fait minimal exploitable n'est disponible pour construire les signes principaux. | `BGS_EMPTY`: "Aucun resume debutant n'est disponible pour ces donnees." |
| `degraded` | Trigger: les faits de base existent, mais une donnee de naissance limite la precision, notamment l'heure de naissance manquante. | `BGS_DEGRADED_NO_TIME`: "Votre resume est affiche sans ascendant ni maisons detaillees car l'heure de naissance manque." |
| `unavailable` | Trigger: une erreur controlee, une source indisponible ou une incoherence de faits empeche toute projection fiable. | `BGS_UNAVAILABLE`: "Le resume debutant est temporairement indisponible." |

Ces etats sont exclusifs pour un rendu donne. Un consommateur futur doit choisir l'etat le plus restrictif applicable: `unavailable`, puis `empty`, puis `degraded`, puis l'affichage nominal.

## Comportement sans heure de naissance

Quand l'heure de naissance est absente, inconnue ou egale au mode degrade `no_time`, `beginner_summary_v1` passe en `degraded` avec `degraded_reason: "no_time"`.

Dans ce mode:

- l'ascendant est retenu hors du payload affiche;
- la maison dominante est retenue hors du payload affiche;
- tout champ house-dependent est retenu, y compris les affirmations derivees des maisons;
- les thèmes dominants restent autorises seulement s'ils ne dependent pas de l'ascendant, des maisons ou d'une heure precise;
- le message `BGS_DEGRADED_NO_TIME` explique la limite sans exposer de detail technique.

Le contrat reprend l'intention du contexte natal degrade existant: une heure inconnue ne doit pas produire de certitude sur l'ascendant ou les maisons.

## Erreurs controlees

`beginner_summary_v1` expose uniquement des controlled error messages.

| Code | Etat | Message public | Detail expose |
|---|---|---|---|
| `BGS_LOADING` | `loading` | "Votre resume est en preparation." | Aucun. |
| `BGS_EMPTY` | `empty` | "Aucun resume debutant n'est disponible pour ces donnees." | Aucun. |
| `BGS_DEGRADED_NO_TIME` | `degraded` | "Votre resume est affiche sans ascendant ni maisons detaillees car l'heure de naissance manque." | Raison controlee `no_time` seulement. |
| `BGS_UNAVAILABLE` | `unavailable` | "Le resume debutant est temporairement indisponible." | Aucun. |

Les messages ne doivent jamais inclure de raw runtime, debug, audit, traceback, identifiant interne, payload technique, prompt, reponse LLM brute ou full facts.

## Exclusions

`beginner_summary_v1` n'est pas:

- une projection expert ou premium;
- une copie de `structured_facts_v1`;
- un contrat de hash ou d'audit;
- un schema OpenAPI;
- un client frontend;
- un objet de base de donnees;
- un prompt ou une narration LLM longue.

La compatibilite free/basic impose un resume court, comprehensible et controle. Toute projection premium ou expert doit rester dans un contrat separe.
