<!-- Commentaire global: ce document definit la matrice cible des permissions admin sans activer de nouveau role runtime. -->

# Admin Permission Matrix

## Objectif

Cette matrice fixe la cible de permissions pour les futurs roles internes sur les donnees admin. Elle sert de contrat de conception pour les
prochaines stories d'API admin, mais ne change pas le comportement applicatif actuel.

Etat operationnel courant:

- `ADMIN` est le seul role interne operationnel aujourd'hui sur les surfaces admin.
- `MARKETER`, `TECHNO` et `ASTRO_EXPERT` sont des roles cibles non actifs.
- Aucun acces courant n'est accorde a `MARKETER`, `TECHNO` ou `ASTRO_EXPERT` tant qu'une implementation RBAC explicite, testee et livree
  n'existe pas.
- Les acces client B2C sont exclus de cette matrice admin; ils restent gouvernes par les contrats produit client, abonnements et consultations.

## Domaines de donnees

| data_domain | Classification | Categories principales | Regle de masquage par defaut |
|---|---|---|---|
| `business` | Donnees commerciales et operationnelles | abonnements, facturation, entitlements, exports, indicateurs, support commercial | visible pour `ADMIN`; agrege ou masque pour les roles cibles |
| `technical` | Donnees techniques d'exploitation | logs applicatifs, erreurs, integrations, couts LLM, latence, reconciliations | visible pour `ADMIN`; limite au diagnostic non personnel pour `TECHNO` cible |
| `astrology` | Donnees astrologiques et contenus d'interpretation | themes, interpretations, qualite astrologique, templates, contenus experts | donnees de naissance sensibles masquees hors contexte admin explicitement approuve |
| `debug` | Donnees de debug et de reproduction | traces, prompts, replay, payloads de diagnostic | masquage strict; replay et prompts separes des traces techniques |

Les données de naissance sont des donnees sensibles. Elles doivent rester masquees ou minimiser les champs affiches hors contexte admin
explicitement approuve. Un futur role cible ne doit jamais deduire un acces aux donnees de naissance depuis un acces de lecture generale.

## Actions couvertes

| action | Definition | Contraintes |
|---|---|---|
| `read` | Lire une fiche, un journal ou une synthese admin. | Respecter le masquage du domaine et de la categorie. |
| `search` | Rechercher, filtrer ou paginer dans une surface admin. | Les criteres sensibles restent limites aux contextes explicitement approuves. |
| `export` | Extraire un jeu de donnees admin. | Export interdit ou agrege par defaut pour les roles cibles. |
| `replay` | Rejouer un appel, un prompt ou un payload de diagnostic. | Reserve aux contextes techniques controles; decision ouverte pour toute exposition non-admin. |
| `correct` | Corriger une donnee, un contenu, un entitlement ou un statut. | Aucune correction par roles cibles sans RBAC et workflow d'audit dedies. |

## Matrice role x domaine

| role_code | data_domain | data_category | action | current_access | target_access | masking_rule | decision_status | rbac_activation_state |
|---|---|---|---|---|---|---|---|---|
| `ADMIN` | `business` | abonnements, facturation, entitlements, exports | `read`, `search`, `export`, `correct` | autorise | acces complet admin existant | visible sauf secrets et tokens | decided | active |
| `ADMIN` | `technical` | logs, erreurs, integrations, couts LLM, latence | `read`, `search`, `export`, `replay` | autorise | acces complet admin existant | secrets masques | decided | active |
| `ADMIN` | `astrology` | interpretations, contenus, donnees de naissance, qualite astrologique | `read`, `search`, `export`, `correct` | autorise | acces complet admin existant | donnees de naissance sensibles, masquage hors contexte approuve | decided | active |
| `ADMIN` | `debug` | traces | `read`, `search`, `export` | autorise | acces complet admin existant | identifiants et secrets masques | decided | active |
| `ADMIN` | `debug` | prompts | `read`, `search`, `export`, `correct` | autorise | acces complet admin existant | contenu sensible masque si lie a un client | decided | active |
| `ADMIN` | `debug` | replay | `read`, `search`, `replay` | autorise | acces complet admin existant | payloads minimises et secrets masques | decided | active |
| `MARKETER` | `business` | indicateurs, plans, contenu marketing, exports agreges | `read`, `search`, `export` | refuse | cible limitee aux agregats non personnels | aggregated | open | inactive until RBAC |
| `MARKETER` | `technical` | logs, erreurs, couts LLM, latence | `read`, `search`, `export`, `replay`, `correct` | refuse | refuse par defaut | denied | decided | inactive until RBAC |
| `MARKETER` | `astrology` | contenus publics, templates, donnees de naissance | `read`, `search`, `export`, `correct` | refuse | contenu non personnel a definir; naissance refusee | masked | open | inactive until RBAC |
| `MARKETER` | `debug` | traces, prompts, replay | `read`, `search`, `export`, `replay`, `correct` | refuse | refuse | denied | decided | inactive until RBAC |
| `TECHNO` | `business` | abonnements, facturation, exports | `read`, `search`, `export`, `correct` | refuse | refuse sauf diagnostic incident approuve | masked | open | inactive until RBAC |
| `TECHNO` | `technical` | logs, erreurs, integrations, couts LLM, latence | `read`, `search`, `export`, `replay` | refuse | cible de diagnostic technique | masked | open | inactive until RBAC |
| `TECHNO` | `astrology` | interpretations, themes, donnees de naissance | `read`, `search`, `export`, `correct` | refuse | refuse hors incident technique approuve | denied | open | inactive until RBAC |
| `TECHNO` | `debug` | traces | `read`, `search`, `export` | refuse | cible de diagnostic avec masquage | masked | open | inactive until RBAC |
| `TECHNO` | `debug` | prompts | `read`, `search`, `export`, `correct` | refuse | lecture limitee a definir | masked | open | inactive until RBAC |
| `TECHNO` | `debug` | replay | `read`, `search`, `replay` | refuse | replay a definir avec audit strict | open decision | open | inactive until RBAC |
| `ASTRO_EXPERT` | `business` | abonnements, facturation, exports | `read`, `search`, `export`, `correct` | refuse | refuse | denied | decided | inactive until RBAC |
| `ASTRO_EXPERT` | `technical` | logs, erreurs, integrations, couts LLM, latence | `read`, `search`, `export`, `replay`, `correct` | refuse | refuse | denied | decided | inactive until RBAC |
| `ASTRO_EXPERT` | `astrology` | interpretations, qualite astrologique, templates, donnees de naissance | `read`, `search`, `correct` | refuse | cible d'expertise avec naissance masquee par defaut | masked | open | inactive until RBAC |
| `ASTRO_EXPERT` | `debug` | traces | `read`, `search` | refuse | refuse sauf trace qualite non personnelle | masked | open | inactive until RBAC |
| `ASTRO_EXPERT` | `debug` | prompts | `read`, `search`, `correct` | refuse | cible de revue astrologique a definir | masked | open | inactive until RBAC |
| `ASTRO_EXPERT` | `debug` | replay | `read`, `search`, `replay` | refuse | refuse par defaut | denied | open | inactive until RBAC |

## Regles de masquage

- Les donnees de naissance sont sensibles et masquees hors contexte admin explicitement approuve.
- Les traces techniques, prompts et donnees de replay sont des surfaces distinctes; une permission sur l'une n'ouvre pas les deux autres.
- Les secrets, tokens, cles API, identifiants Stripe complets et payloads bruts restent masques ou refuses.
- Les exports des roles cibles doivent etre agreges, minimises ou refuses tant qu'une story RBAC ne definit pas un controle explicite.
- Toute action `correct` par un role cible exige une decision produit, une trace d'audit et une implementation RBAC dediee.

## Decisions ouvertes

- OPEN-ADMIN-PERM-001: niveau exact d'agregation autorise pour les exports `MARKETER`.
- OPEN-ADMIN-PERM-002: conditions d'acces `TECHNO` aux prompts et aux donnees de replay.
- OPEN-ADMIN-PERM-003: limites d'acces `ASTRO_EXPERT` aux interpretations liees a des donnees de naissance.
- OPEN-ADMIN-PERM-004: workflow d'audit requis avant toute action `correct` hors `ADMIN`.
- OPEN-ADMIN-PERM-005: regles finales de retention RGPD pour traces, prompts et replay.

## Hors matrice

Cette matrice ne couvre pas les acces client B2C, les comptes B2B, les permissions d'abonnement client, la creation de comptes internes,
les routes frontend, les migrations, les seeds, les claims de token et les guards runtime. Ces sujets demandent des stories separees.
