<!-- Commentaire global: ce document fixe le vocabulaire cible des roles internes sans ouvrir de nouveaux acces applicatifs. -->

# Internal Role Model

## Objectif

Ce document est la source canonique du vocabulaire des roles internes pour les futures surfaces d'administration et d'exploitation.
Il decrit une cible produit et technique: il ne modifie pas l'authentification, ne cree pas de compte, ne change pas les routes et
n'accorde aucun acces supplementaire.

## Etat operationnel actuel

Dans le vocabulaire cible de cette story, `ADMIN` est le seul role interne operationnel aujourd'hui. Il correspond au role runtime
`admin` deja utilise par les surfaces `/admin` et conserve un acces complet aux fonctions d'administration existantes.

Le registre runtime contient aussi des roles preexistants comme `user`, `support`, `ops` et `enterprise_admin`. Ils ne font pas partie du
modele interne cible `ADMIN` / `MARKETER` / `TECHNO` / `ASTRO_EXPERT`, ne sont pas des alias de ces roles et ne doivent pas etre utilises
pour activer implicitement `MARKETER`, `TECHNO` ou `ASTRO_EXPERT`.

`MARKETER`, `TECHNO` et `ASTRO_EXPERT` sont des roles cibles. Ils ne donnent aucun acces courant, ne doivent pas etre ajoutes aux
constantes RBAC actives et restent inactifs tant qu'une implementation RBAC explicite et testee n'a pas ete livree.

## Frontiere des sujets

Les roles internes representent des collaborateurs ou operateurs de la plateforme. Ils sont separes des clients B2C, qui restent des
utilisateurs finaux de l'application, de leurs abonnements et de leurs consultations personnelles.

Les roles internes sont aussi separes des comptes B2B, de leurs administrateurs d'entreprise, de leurs quotas et de leurs contrats
d'usage. Un compte B2B ou un client B2C ne devient pas un membre interne par conversion de role.

## Vocabulaire canonique

### `ADMIN`

- business_intent: administrer la plateforme, traiter les incidents et superviser les operations.
- current_state: `active`.
- access_grant: acces complet aux surfaces admin existantes via le role runtime `admin`.
- subject_boundary: interne uniquement; distinct des clients B2C et des comptes B2B.
- surface_family: admin dashboard, audit, content, logs, support, billing, users, prompts, exports, reconciliation.
- future_permission_dependency: CS-271 devra decomposer cet acces complet en permissions explicites.

### `MARKETER`

- business_intent: preparer les actions marketing, suivre les indicateurs commerciaux et piloter les contenus non sensibles.
- current_state: `target-only`.
- access_grant: Aucun acces courant; aucune route, API, UI ou donnee n'est ouverte par ce role.
- subject_boundary: interne uniquement; distinct des clients B2C et des comptes B2B.
- surface_family: admin dashboard, content, billing aggregates, exports limites.
- future_permission_dependency: CS-271 devra definir les permissions marketing autorisees et les exclusions de donnees sensibles.

### `TECHNO`

- business_intent: diagnostiquer les incidents techniques, les journaux, les integrations et la qualite operationnelle.
- current_state: `target-only`.
- access_grant: Aucun acces courant; aucune route, API, UI ou donnee n'est ouverte par ce role.
- subject_boundary: interne uniquement; distinct des clients B2C et des comptes B2B.
- surface_family: logs, audit, support, technical diagnostics, LLM operations, reconciliation.
- future_permission_dependency: CS-271 devra definir les permissions techniques et les actions interdites.

### `ASTRO_EXPERT`

- business_intent: evaluer la qualite astrologique, les contenus d'interpretation, les prompts et les retours d'expertise.
- current_state: `target-only`.
- access_grant: Aucun acces courant; aucune route, API, UI ou donnee n'est ouverte par ce role.
- subject_boundary: interne uniquement; distinct des clients B2C et des comptes B2B.
- surface_family: content, prompts, audit, support, astrology expertise, review workflows.
- future_permission_dependency: CS-271 devra definir les permissions d'expertise astrologique et les limites sur les donnees client.

## Surfaces admin concernees

Les surfaces identifiees pour une future decoupe de permissions viennent de la documentation d'administration existante:

- admin dashboard;
- audit et journaux logs;
- content et prompts;
- support;
- users, billing, entitlements, exports et reconciliation;
- diagnostics techniques et operations LLM;
- expertise astrologique et workflows de revue.

Cette story ne modifie aucune de ces surfaces. Toute activation de `MARKETER`, `TECHNO` ou `ASTRO_EXPERT` doit attendre CS-271 et une
story d'implementation RBAC dediee.
