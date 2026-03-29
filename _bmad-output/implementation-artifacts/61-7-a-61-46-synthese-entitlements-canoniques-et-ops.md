# Synthèse des implémentations — stories 61.7 à 61.46

## Objectif du chantier

Le lot de stories `61.7` à `61.46` a transformé le système de droits produit d'un modèle historique couplé au billing en une plateforme canonique d'entitlements, avec :

- un modèle de données centralisé pour les plans, features, bindings et quotas ;
- une bascule progressive des flux métier B2C puis B2B vers ce modèle ;
- des compteurs d'usage cohérents avec les scopes métier B2C/B2B ;
- des garde-fous de cohérence au runtime, au démarrage, en CI et au moment des écritures ;
- une traçabilité complète des mutations canoniques ;
- une couche ops complète de revue, SLA, alerting, retry, triage et suppression durable du bruit.

## Vue d'ensemble

Le chantier s'est déroulé en six phases :

1. `61.7` à `61.10` : fondations du modèle canonique et moteur de quotas.
2. `61.11` à `61.17` : migration des principaux flux B2C et suppression du legacy quota B2C.
3. `61.18` à `61.26` : migration B2B vers le canonique puis séparation native des compteurs entreprise.
4. `61.27` à `61.30` : garde-fous structurels de cohérence et de scope.
5. `61.31` à `61.38` : centralisation des écritures, audit trail des mutations et work queue ops avec SLA.
6. `61.39` à `61.46` : alerting ops, retry, triage manuel et batch, puis règles durables d'auto-suppression.

## 1. Fondations du canonique (`61.7` à `61.10`)

### `61.7` — Modèle canonique d'entitlements

Introduction du socle de données canonique pour découpler les droits produit du legacy billing :

- catalogues de plans et de features ;
- bindings plan → feature ;
- quotas par feature ;
- séparation explicite entre accès, quotas et variantes produit.

Cette base a permis d'arrêter de coder les droits directement dans les services métier ou dans des colonnes historiques de tables billing.

### `61.8` — Backfill initial depuis les plans legacy

Mise en place d'un backfill idempotent qui peuple le modèle canonique à partir de `billing_plans` et `enterprise_billing_plans`, avec traçabilité d'origine :

- migration des plans B2C et B2B réels présents en base ;
- création/mise à jour des bindings et quotas dérivables ;
- annotation des données selon leur origine (`manual`, migré depuis legacy, etc.) ;
- explicitation des éléments non dérivables ou nécessitant un traitement manuel.

Le canonique n'est donc pas seulement seedé "à la main" : il reflète l'état réel de la base legacy.

### `61.9` — `EntitlementService` en lecture

Création d'un service central de lecture des droits :

- priorité à la lecture canonique ;
- fallback legacy quand la feature n'est pas encore couverte ;
- contrat unique de sortie pour les services métier (`FeatureEntitlement`).

Cette story a posé la façade de lecture commune sans encore migrer les flux métier.

### `61.10` — Moteur de fenêtres et de consommation

Mise en place du moteur de quota réutilisable :

- `QuotaWindowResolver` pour calculer les fenêtres `day`, `week`, `month`, `year`, `lifetime` ;
- `QuotaUsageService` pour lire et consommer les quotas dans `feature_usage_counters` ;
- types partagés (`QuotaDefinition`, `FeatureEntitlement`, `UsageState`).

À partir de là, le runtime pouvait s'appuyer sur des compteurs réels au lieu de simples limites configurées.

## 2. Migration B2C et retrait du legacy quota (`61.11` à `61.17`)

### `61.11` à `61.13` — Migration des flux métier majeurs

Les trois principales features B2C ont été migrées vers le moteur canonique :

- `astrologer_chat`
- `thematic_consultation`
- `natal_chart_long`

Pour chacune :

- création d'une gate dédiée ;
- contrôle d'accès sur entitlement canonique ;
- consommation réelle avant exécution métier ;
- erreurs fonctionnelles cohérentes (`403` accès, `429` quota) ;
- rollback transactionnel si l'opération échoue après consommation ;
- exposition des informations de quota au front ;
- support de `variant_code` quand nécessaire (`natal_chart_long`).

Le legacy n'a subsisté que là où il était explicitement prévu en fallback transitoire.

### `61.14` — Endpoint `GET /v1/entitlements/me`

Création d'une source unique pour l'UX front :

- endpoint authentifié et en lecture seule ;
- exposition systématique des principales features ;
- retour de l'état d'accès, de la raison, des variantes et des quotas ;
- aucun effet de bord ni consommation.

Le front dispose désormais d'un contrat unique pour afficher états `loading/error/empty`, CTA désactivés et quotas restants.

### `61.15` à `61.17` — Décommission du quota legacy B2C

Cette phase a retiré progressivement les anciens chemins B2C :

- suppression du chemin legacy spécifique à `astrologer_chat` ;
- consolidation canonique des quotas B2C ;
- retrait de l'endpoint legacy `GET /v1/billing/quota` ;
- nettoyage du module `QuotaService`.

Résultat : après `61.17`, les usages B2C majeurs ne dépendent plus du vieux système de quota.

## 3. Migration B2B et compteurs natifs entreprise (`61.18` à `61.26`)

### `61.18` à `61.24` — Bascule progressive du runtime B2B

Le flux B2B a ensuite été migré vers le canonique :

- `61.18` : contrôle d'accès B2B API prioritairement canonique, avec fallback settings limité aux cas non mappés ;
- `61.19` : observabilité des comptes encore sur fallback ;
- `61.20` : résorption des blockers empêchant la bascule complète ;
- `61.21` : suppression du fallback settings sur `b2b_api_access` et décommission de `B2BUsageService` côté accès ;
- `61.22` : migration de `GET /v1/b2b/usage/summary` vers la lecture canonique ;
- `61.23` et `61.24` : nettoyage final du code et des reliquats DB legacy B2B.

À l'issue de cette séquence, le runtime B2B lit ses droits et quotas depuis le canonique, plus depuis les settings historiques.

### `61.25` — Compteurs B2B natifs

Cette story est structurante : le B2B n'utilise plus le contournement par `admin_user_id`.

Mise en place de :

- la table `enterprise_feature_usage_counters` ;
- `EnterpriseQuotaUsageService` ;
- la migration des flux runtime B2B vers des compteurs indexés par `enterprise_account_id`.

Le modèle de données reflète enfin l'identité métier réelle du B2B : le compte entreprise, pas un utilisateur administrateur.

### `61.26` — Alignement des outils ops et nettoyage

Les outils ops et traitements annexes ont été alignés sur les compteurs natifs entreprise, avec suppression des reliquats liés à `admin_user_id`.

Résultat : la séparation B2C/B2B n'est plus seulement conceptuelle, elle est effective dans les compteurs, les services et les outils d'exploitation.

## 4. Garde-fous de cohérence canonique (`61.27` à `61.30`)

### `61.27` — Registre de scope et séparation stricte B2C/B2B

Introduction d'un registre central `FEATURE_SCOPE_REGISTRY` pour déclarer si une feature de quota est B2C ou B2B, avec erreurs explicites si le mauvais service est utilisé.

Effet direct :

- `QuotaUsageService` refuse les features B2B ;
- `EnterpriseQuotaUsageService` refuse les features B2C ;
- les nouveaux `feature_code` doivent être enregistrés explicitement.

### `61.28` à `61.30` — Validation multi-niveaux

Trois niveaux de protection complémentaires ont ensuite été posés :

- `61.28` : validation statique de cohérence entre registre, gates et seed ;
- `61.29` : enforcement au démarrage et en CI ;
- `61.30` : validation DB de cohérence entre registre, `feature_catalog`, `plan_catalog`, bindings et quotas.

Ces stories empêchent les dérives silencieuses :

- feature inconnue ;
- mauvais scope B2C/B2B ;
- binding incohérent avec l'audience du plan ;
- binding `QUOTA` sans quota ;
- quotas présents sur un binding `UNLIMITED` ou `DISABLED`.

## 5. Gouvernance des écritures et pilotage ops des mutations (`61.31` à `61.38`)

### `61.31` — Écriture canonique centralisée

Création de `CanonicalEntitlementMutationService` comme point d'entrée unique pour créer ou modifier les bindings et quotas canoniques.

Les validations ne sont plus seulement lues au démarrage ou en CI : elles sont appliquées au moment même de l'écriture.

Cela a sécurisé :

- les scripts de seed ;
- les backfills ;
- les réparations ops ;
- l'idempotence des mises à jour de configuration canonique.

### `61.32` à `61.34` — Audit trail des mutations

Cette phase a ajouté la traçabilité complète des mutations canoniques :

- audit trail persistant des changements ;
- exposition ops en lecture ;
- normalisation des diffs ;
- scoring de risque.

Le système ne se contente plus de muter la configuration : il sait expliquer ce qui a changé et qualifier le niveau de risque.

### `61.35` à `61.38` — Revue ops, work queue et SLA

Le chantier est ensuite passé de la simple traçabilité au pilotage opérationnel :

- `61.35` : revue manuelle par les opérateurs (`pending_review`, `acknowledged`, `expected`, `investigating`, `closed`) ;
- `61.36` : historisation append-only des transitions de revue ;
- `61.37` : work queue ops des mutations à risque ;
- `61.38` : couche SLA avec statuts `within_sla`, `due_soon`, `overdue`.

Résultat :

- les mutations à risque sont visibles dans une file priorisable ;
- leur traitement est qualifié, historisé et mesuré ;
- l'urgence opérationnelle est calculée explicitement.

## 6. Alerting ops, retry, triage et suppression durable du bruit (`61.39` à `61.46`)

### `61.39` à `61.42` — Alerting et retry pilotable

Cette séquence a ajouté une vraie couche d'alerting ops sur la review queue SLA :

- `61.39` : génération d'alertes idempotentes et persistées pour les cas `due_soon` et `overdue` ;
- `61.40` : retry/replay contrôlé des alertes échouées ;
- `61.41` : endpoints ops pour lister les alertes, filtrer, résumer et piloter le retry ;
- `61.42` : retry batch des alertes `failed`.

L'alerting devient traçable, observable et opérable sans SQL manuel.

### `61.43` à `61.45` — Triage manuel et batch

Ensuite, le système a ajouté les outils pour retirer le bruit opérationnel :

- `61.43` : handling manuel par alerte (`suppressed`, `resolved`) avec commentaire et clé de suppression ;
- `61.44` : historisation append-only des transitions de handling ;
- `61.45` : triage batch piloté pour nettoyer rapidement un backlog entier.

Le backlog d'alertes peut alors être traité à l'unité ou en masse, avec traçabilité complète.

### `61.46` — Règles durables de suppression

Dernière étape du lot : passage du traitement ponctuel à la suppression réutilisable.

Ajouts clés :

- table de règles de suppression durables ;
- moteur central de matching des règles actives ;
- prise en compte des règles dans les listings, résumés et mécanismes de retry ;
- priorité conservée au handling manuel quand il existe.

Différence de fond :

- `61.45` nettoie le backlog actuel ;
- `61.46` évite que le même bruit revienne demain.

## État final atteint à la story `61.46`

À ce stade, le système dispose :

- d'un modèle canonique complet pour les entitlements produit ;
- d'un runtime B2C et B2B majoritairement gouverné par ce canonique ;
- de compteurs d'usage séparés proprement entre B2C et B2B ;
- de validations de cohérence à tous les niveaux critiques ;
- d'un service unique pour les mutations canoniques ;
- d'un audit trail exploitable par les opérations ;
- d'une work queue ops avec revue, historique et SLA ;
- d'un sous-système d'alerting persistant, retryable, triable et débruité par règles.

En synthèse, les stories `61.7` à `61.46` ont fait passer le projet :

- d'une logique de droits dispersée et couplée au billing legacy,
- à une plateforme canonique gouvernée, observable et opérable de bout en bout.

## Lecture rapide par sous-ensembles

### Socle canonique

- `61.7` à `61.10`

### Migration B2C

- `61.11` à `61.17`

### Migration B2B

- `61.18` à `61.26`

### Garde-fous et cohérence

- `61.27` à `61.30`

### Mutations canoniques et review queue

- `61.31` à `61.38`

### Alerting ops et suppression du bruit

- `61.39` à `61.46`
