<!-- Commentaire global: ce document fixe le contrat interne astrology_full_data_v1 sans creer de route, schema public, client frontend ou payload runtime. -->

# Contrat `astrology_full_data_v1`

`astrology_full_data_v1` est une projection interne, protected, non client et
expert-oriented pour la revue astrologique complete par `ADMIN` aujourd'hui et
par `ASTRO_EXPERT` uniquement comme role futur `target-only`.

Ce contrat documente le contenu metier astrologique autorise. Il ne cree pas de
builder, serializer, route, schema OpenAPI, migration, table, replay, log
technique ou client frontend.

## Forme contractuelle

| Champ | Regle |
|---|---|
| `projection_id` | Valeur exacte: `astrology_full_data_v1`. |
| `classification` | Interne, protected, expert-oriented, non client et not client-safe. |
| `authorized_consumers` | `ADMIN` aujourd'hui; `ASTRO_EXPERT` uniquement comme role futur `target-only`. |
| `denied_consumers` | Clients B2C, public-user surfaces, API publique, clients generes et exports frontend publics. |
| `source_dependencies` | `structured_facts_v1`, source versions, doctrine/school metadata et `evidence_refs`. |
| `permission_source` | Matrice interne CS-271, documentee dans `docs/architecture/admin-permission-matrix.md`. |
| `openapi_policy` | OpenAPI-neutral; `astrology_full_data_v1` ne doit pas apparaitre dans `app.openapi()` ni dans `app.routes`. |

## Familles astrologiques

La projection peut decrire les familles astrologiques suivantes lorsque leur
source est stable, versionnee et rattachee a une preuve:

- `chart_objects_summary`: synthese des objets du theme, codes stables, roles
  astrologiques, visibilite metier et liens vers les familles detaillees.
- `positions`: positions normalisees, signes, degres, vitesse, retrogradation,
  maison associee et unite explicite.
- `houses`: cusps, systeme de maisons, axes, rulerships, interceptions ou
  absences documentees selon la doctrine.
- `dignities`: dignites essentielles et accidentelles, scores, raisons et
  source versions.
- `conditions`: conditions planetaires, phase, combustion, cazimi, secte,
  visibilite et modificateurs traditionnels.
- `aspects`: aspects majeurs et mineurs autorises, orbes, objets source/cible,
  exactitude, separant/appliquant et doctrine/school metadata.
- `dominance`: dominantes planetaires, elementaires, modales ou de maisons,
  methode, score et version de calcul.
- `fixed-star policy`: contacts d'etoiles fixes uniquement comme donnee interne
  policy-bound; aucune client exposure, aucun raw fixed-star catalog data et
  aucun dump de conjonctions brutes ne sont autorises par cette story.
- `sources`: moteur de calcul, catalogues, source versions, doctrine, school,
  horodatage de generation contractuel, hash de projection et `evidence_refs`.

## Frontiere diagnostics

`astrology_full_data_v1` reste separe de `admin_chart_diagnostics_v1`.

Le contrat exclut les surfaces suivantes:

- raw runtime traces;
- calculation debug payloads;
- replay payloads complets;
- provider debug dumps;
- prompt internals;
- unrestricted technical diagnostics;
- `ChartObjectRuntimeData` comme payload direct;
- fallback silencieux qui melangerait donnees expertes et diagnostics
  techniques.

Les diagnostics techniques peuvent etre documentes dans un contrat separe, mais
ils ne deviennent pas une famille de donnees de `astrology_full_data_v1`.

## Politique de donnees personnelles

Les champs personnels sont masques par defaut ou explicitement justifies par un
besoin expert approuve:

- `birth date`: masque par defaut; retention autorisee seulement si la
  verification astrologique exige la date exacte.
- `birth time`: masque par defaut; retention autorisee seulement si la precision
  des maisons, angles ou lots depend de l'heure.
- `birth place`: masque par defaut; precision geographique reduite hors contexte
  approuve.
- `user id`: masque ou pseudonymise; aucun identifiant client brut dans une vue
  B2C ou export public.
- `chart id`: masque ou remplace par une reference de travail; retention
  justifiee seulement pour audit, correction ou correlation interne.

Tout acces doit conserver la justification du champ sensible retenu, la regle de
masking appliquee et le lien vers la decision CS-271 pertinente.

## Dependances de source

La projection depend de `structured_facts_v1` pour la base factuelle stable et
hashable. Elle peut enrichir cette base avec des source versions, doctrine,
school metadata et `evidence_refs`, mais elle ne remplace pas la calculation
truth du runtime canonique.

Les references de preuve doivent rester tracables:

- `structured_facts_v1` pour les faits normalises;
- source versions pour moteurs, catalogues, doctrines et ecoles;
- doctrine/school metadata pour qualifier les regles astrologiques;
- `evidence_refs` pour relier les champs exposes aux sources stabilisees;
- hash ou projection id pour relier la projection aux audits internes.

## Acces et logs

L'acces courant est limite a `ADMIN`. `ASTRO_EXPERT` reste un consommateur futur
`target-only`: ce contrat ne l'active pas dans le RBAC, ne cree pas de claim et
ne modifie aucune constante runtime.

Chaque decision d'acces doit pouvoir journaliser au minimum:

- `actor`: identifiant interne de l'acteur;
- `role`: role interne evalue, par exemple `ADMIN` ou futur `ASTRO_EXPERT`;
- `projection id`: valeur `astrology_full_data_v1`;
- `chart_or_answer_reference`: reference masquee du theme ou de la reponse;
- `action`: lecture, correction, revue ou export interne;
- `decision`: autorise, refuse, masque ou partiellement masque;
- `masking_rule`: regle appliquee aux champs sensibles;
- `timestamp`: date technique de decision;
- `correlation_id`: identifiant de correlation pour relier audit, appel et log.

## Non-objectifs

Cette story ne publie pas `astrology_full_data_v1` dans une route, un schema
OpenAPI, un client public ou une interface frontend. Elle n'active pas
`ASTRO_EXPERT`, ne cree pas `admin_chart_diagnostics_v1`, ne persiste aucune
projection et ne modifie pas les permissions runtime.
