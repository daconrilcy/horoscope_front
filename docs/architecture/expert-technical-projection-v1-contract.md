<!-- Commentaire global: ce document fixe le contrat interne expert_technical_projection_v1 sans creer de route, schema public, client frontend ou payload runtime. -->

# Contrat `expert_technical_projection_v1`

`expert_technical_projection_v1` est une projection astrologique interne pour
analyse technique expert. Elle est `interne`, `non client` et `not client-safe`:
elle ne constitue pas une surface B2C, un contrat OpenAPI public, un client
frontend, ni une reponse destinee a l'utilisateur final.

## Forme du contrat

| Champ | Regle |
|---|---|
| `projection_id` | Valeur exacte: `expert_technical_projection_v1`. |
| `classification` | `interne`, `non client`, `not client-safe`, reservee aux usages admin/expert controles. |
| `authorized_consumers` | `ADMIN` aujourd'hui; `ASTRO_EXPERT` uniquement comme role futur `target-only`. |
| `denied_consumers` | Clients B2C, surfaces public-user, clients frontend generes et routes publiques. |
| `permission_source` | Matrice interne CS-271, documentee dans `docs/architecture/admin-permission-matrix.md`. |
| `source_links` | `structured_facts_v1`, structured signals et `evidence_refs`. |

## Consommateurs autorises

- `ADMIN`: seul consommateur operationnel courant, sous politiques admin
  internes, logs et decisions de permissions existantes.
- `ASTRO_EXPERT`: consommateur futur `target-only`; ce contrat ne l'active pas
  dans le RBAC, les claims, les constantes backend ou les routes.

Toute demande B2C est refusee par principe de contrat. Cette projection ne doit
pas etre serialisee vers une page client, un SDK public, une route publique ou un
schema OpenAPI public.

## Familles astrologiques autorisees

La projection peut assembler des donnees techniques mais signifiantes, a partir
de sources stabilisees:

- `dignity`: dignites essentielles ou accidentelles lisibles par un expert.
- `conditions`: conditions planetaires, etats, visibilite technique et contexte
  d'interpretation expert.
- `dominance`: dominances, ponderations stabilisees et facteurs de synthese
  utiles au diagnostic astrologique.
- `aspects`: aspects techniques, orbes, sources et relations entre objets
  astrologiques.
- `houses`: maisons, axes, secteurs et metadata de systeme de maisons.
- source metadata: version de calcul, source de faits, hash ou reference stable
  lorsque disponible.

## Liens de preuves

`expert_technical_projection_v1` doit relier ses assertions aux contrats deja
owners:

- `structured_facts_v1` pour la base factuelle stable;
- structured signals pour les signaux interpretatifs pre-narratifs;
- `evidence_refs` pour les references de preuves auditables.

Ces liens servent a expliquer l'origine d'une information sans exposer les
payloads internes qui ont permis de la calculer.

## Exclusions techniques

La projection exclut explicitement:

- raw runtime traces;
- prompt internals;
- replay payloads complets;
- provider debug dumps;
- unrestricted technical diagnostics;
- `ChartObjectRuntimeData`, graphes runtime bruts et dumps de calcul non
  stabilises.

Un champ necessaire a l'analyse expert doit etre reformule en fait, signal ou
reference de preuve stable. Aucun fallback silencieux ne peut transformer un
payload debug brut en champ accepte.

## Permissions et logs d'acces

Les permissions se rattachent a CS-271. Ce document ne cree pas de matrice
parallele et ne remplace pas la future activation RBAC.

Chaque decision d'acces a cette projection doit journaliser au minimum:

- `actor`: identifiant de l'acteur demandeur;
- `role`: role interne evalue, par exemple `ADMIN` ou futur `ASTRO_EXPERT`;
- `projection id`: valeur `expert_technical_projection_v1`;
- `chart_or_answer_reference`: reference du theme, calcul ou reponse auditee;
- `action`: lecture, recherche, export ou autre action controlee;
- `decision`: autorisee ou refusee, avec raison exploitable;
- `timestamp`: horodatage de decision;
- `correlation_id`: identifiant de correlation pour relier audit, appel et log.

## Neutralite runtime

Cette story ne cree aucun endpoint, serializer, service, builder, modele,
migration, seed, client frontend ou schema OpenAPI. `app.routes` et
`app.openapi()` doivent rester neutres: le token
`expert_technical_projection_v1` ne doit pas apparaitre dans le contrat HTTP
public.
