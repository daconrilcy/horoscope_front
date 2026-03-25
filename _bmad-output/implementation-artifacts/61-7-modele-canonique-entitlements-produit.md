# Story 61.7: Modèle canonique des entitlements produit par plan

Status: done

## Story

En tant que système backend,
je veux introduire un modèle canonique de plans, features, mappings plan→feature et quotas par feature,
afin de découpler les droits produit de la structure historique des tables de billing et de permettre une évolution simple des accès, quotas et périodes sans recoder la logique métier dans chaque service.

## Contexte métier et enjeu architectural

### Problème avec l’existant

Le projet dispose déjà d’un socle billing fonctionnel, mais il est construit de manière statique et couplée :

- Les plans B2C et B2B existent déjà dans `billing_plans` et `enterprise_billing_plans`.
- Les quotas sont codés sous forme de colonnes dédiées dans ces tables (ex : `daily_message_limit`).
- Les services de quotas lisent directement ces colonnes.
- Les fonctionnalités ne sont pas cataloguées dans une table centrale.
- Le lien entre plan et fonctionnalité est implicite dans le code.
- La logique d’accès produit reste dispersée entre billing, quotas, feature flags et services métier.

Cette story introduit un modèle canonique d’entitlements produit qui coexiste avec l’existant pendant une phase transitoire.

### Historique d’implémentation à respecter

#### 1. Plans : déjà traités partiellement

Stories associées :
- 4.1 : Souscription B2C
- 4.3 : Upgrade / Modification
- 7.5 : Plans B2B

État actuel :
- `billing_plans` existe déjà.
- `enterprise_billing_plans` existe déjà.
- ces tables définissent déjà des niveaux de plans et des limites fixes.

#### 2. Features : traitées partiellement / implicitement

Stories associées :
- Epic 11.2 : Feature flags

État actuel :
- pas de table `features` centrale ;
- les fonctionnalités sont soit pilotées par `feature_flag.py`, soit codées directement dans les services métier.

#### 3. Mapping plan → feature : non traité

État actuel :
- aucune table de liaison entre plan et fonctionnalité ;
- le lien est aujourd’hui statique et codé en dur.

#### 4. Quotas par feature : non traités comme brique canonique

Stories associées :
- 4.2 : Quotas journaliers
- 7.3 : Limites B2B

État actuel :
- les quotas sont portés par des colonnes dédiées dans les tables de plans ;
- `QuotaService` et `B2BUsageService` lisent directement ces colonnes.

### Décision d’architecture

Cette story ne remplace pas le billing historique.
Elle introduit un modèle canonique d’entitlements produit qui coexiste avec l’existant.

Pendant cette phase transitoire :

- `billing_plans` et `enterprise_billing_plans` restent en place ;
- les nouvelles tables canoniques sont créées à côté ;
- les services métier existants ne sont pas encore migrés ;
- le futur `EntitlementService` sera introduit dans une story suivante, avec lecture canonique puis fallback legacy si nécessaire.

### Séparation conceptuelle à préserver

Cette story prépare un modèle où les trois notions suivantes restent distinctes :

- **plan commercial** : `free`, `trial`, `basic`, `premium`
- **statut de billing** : porté ailleurs par le billing / Stripe / l’état d’abonnement
- **entitlement final** : résultat calculé à partir du plan, du billing status et de la consommation

Important :
- `trial` dans cette story est un **plan commercial canonique**
- `trialing` Stripe n’est **pas** traité ici
- cette story ne calcule **pas encore** le droit final utilisateur

## Acceptance Criteria

1. **Tables canoniques créées** : Les tables `plan_catalog`, `feature_catalog`, `plan_feature_bindings`, `plan_feature_quotas` et `feature_usage_counters` sont créées avec leurs PK/FK, index et contraintes d’unicité. (AC: 1)
2. **Migration Alembic** : Une migration Alembic propre est fournie, posant les tables, les indexes de performance requis et les contraintes métier minimales utiles au futur moteur d’entitlements. (AC: 1)
3. **Modèles ORM** : Les modèles SQLAlchemy sont créés dans `backend/app/infra/db/models/product_entitlements.py`, respectant les standards du projet. (AC: 1)
4. **Catalogue des plans initialisé** : Le seed initial crée les plans `free`, `trial`, `basic`, `premium` de manière idempotente. (AC: 2)
5. **Catalogue des features initialisé** : Le seed initial crée les features `natal_chart_short`, `natal_chart_long`, `astrologer_chat`, `thematic_consultation`. (AC: 3)
6. **Bindings initiaux présents** : Chaque plan a ses bindings configurés, y compris les `variant_code` attendus pour `natal_chart_long`. (AC: 4)
7. **Quotas initiaux présents** : Les quotas sont configurés avec `quota_key`, `quota_limit`, `period_unit`, `period_value` et `reset_mode`, y compris pour les cas `week`, `month` et `lifetime`. (AC: 5)
8. **Coexistence garantie** : Aucune table legacy n’est modifiée ou supprimée. Aucun service métier existant (`QuotaService`, `BillingService`, services applicatifs legacy) n’est redirigé vers les nouvelles tables dans cette story. (AC: 6)
9. **Documentation technique** : Un fichier `docs/architecture/product-entitlements-model.md` décrit le nouveau modèle, la stratégie de coexistence et la trajectoire de migration. (AC: 8)
10. **Compteurs de consommation structurés** : `feature_usage_counters` contient les colonnes nécessaires au futur calcul canonique des quotas (`user_id`, `feature_code`, `quota_key`, `period_unit`, `period_value`, `reset_mode`, `window_start`, `window_end`, `used_count`) ainsi qu’une contrainte d’unicité composite par fenêtre. (AC: 1)
11. **Contraintes numériques et Enums** : Le schéma applique les contraintes suivantes : `quota_limit > 0`, `period_value >= 1`, `used_count >= 0`. Une contrainte additionnelle exige `window_end` si la période n'est pas `lifetime`. Tous les Enums utilisent `native_enum=False` avec validation SQLAlchemy. (AC: 1)

## Tasks / Subtasks

- [x] **Modèles de données et Migration** (AC: 1, 2, 3, 10, 11)
  - [x] Créer `backend/app/infra/db/models/product_entitlements.py`
  - [x] Définir `PlanCatalogModel`, `FeatureCatalogModel`, `PlanFeatureBindingModel`, `PlanFeatureQuotaModel`, `FeatureUsageCounterModel`
  - [x] Générer et affiner la migration Alembic `add_product_entitlements_tables` (ajout manuel des contraintes complexes)
  - [x] Ajouter les indexes sur `plan_code`, `feature_code`, `(plan_id, feature_id)`, `(user_id, feature_code)`, `(user_id, feature_code, quota_key)`
  - [x] Poser l’unicité composite de `plan_feature_quotas` sur `(plan_feature_binding_id, quota_key, period_unit, period_value, reset_mode)`
  - [x] Poser l’unicité composite de `feature_usage_counters` sur `(user_id, feature_code, quota_key, period_unit, period_value, reset_mode, window_start)`
  - [x] Poser les contraintes minimales sur `quota_limit`, `period_value` et `used_count`
  - [x] Poser la contrainte de cohérence sur `window_end` (requis sauf pour `lifetime`)

- [x] **Initialisation et Seeds** (AC: 4, 5, 6, 7)
  - [x] Créer un script de seed idempotent et convergent `backend/scripts/seed_product_entitlements.py`
  - [x] Le script doit pouvoir être exécuté indépendamment après migration, sans effet de bord en cas de réexécution
  - [x] Le script doit mettre à jour les données existantes et supprimer les quotas obsolètes
  - [x] Le script doit ouvrir la session DB selon les conventions existantes du projet
  - [x] Injecter les 4 plans B2C de référence
  - [x] Injecter le catalogue de features initial
  - [x] Injecter les bindings et quotas détaillés dans le draft (`free`, `trial`, `basic`, `premium`)
  - [x] Injecter les `variant_code` attendus pour `natal_chart_long` :
    - [x] `trial` → `single_astrologer`
    - [x] `basic` → `single_astrologer`
    - [x] `premium` → `multi_astrologer`

- [x] **Validation et Tests** (AC: 6, 8, 10, 11)
  - [x] Créer `backend/app/tests/unit/test_product_entitlements_models.py` pour valider les contraintes
  - [x] Vérifier l’unicité de `plan_code`
  - [x] Vérifier l’unicité de `feature_code`
  - [x] Vérifier l’unicité de `(plan_id, feature_id)`
  - [x] Vérifier l’unicité composite de `plan_feature_quotas`
  - [x] Vérifier l’unicité composite de `feature_usage_counters`
  - [x] Vérifier les contraintes numériques minimales (`quota_limit`, `period_value`, `used_count`)
  - [x] Vérifier la présence des 4 plans seedés
  - [x] Vérifier la présence des 4 features seedées
  - [x] Vérifier les bindings attendus par plan
  - [x] Vérifier les `variant_code` attendus pour `natal_chart_long`
  - [x] Vérifier les quotas attendus (`day`, `week`, `month`, `lifetime`)
  - [x] Valider l’idempotence du seed par double exécution
  - [x] Vérifier que les tests existants (`test_billing_service.py`, `test_quota_service.py`) passent toujours sans modification
  - [x] Vérifier qu’aucun service legacy n’importe `product_entitlements.py` hors tests, seeds ou documentation liée à cette story

- [x] **Documentation** (AC: 9)
  - [x] Rédiger `docs/architecture/product-entitlements-model.md`
  - [x] Expliquer la transition legacy → canonique
  - [x] Expliquer la séparation entre plan commercial, billing status et entitlement final
  - [x] Expliquer le rôle de chaque table
  - [x] Expliquer que les services métier ne sont pas encore migrés dans cette story
  - [x] Expliquer la roadmap des stories suivantes

## Dev Notes

### Architecture Guardrails

- **Backend Stack** : Python 3.13, FastAPI, SQLAlchemy 2.0 (`Mapped` / `mapped_column` syntax).
- **Naming** : Utiliser le suffixe `Model` pour les classes SQLAlchemy.
- **Coexistence stricte** : Cette story ne doit modifier aucun import ou usage applicatif existant de `billing_plans`, `enterprise_billing_plans`, `QuotaService`, `B2BUsageService`, `BillingService` ou services métier legacy pour les faire pointer vers les nouvelles tables.
- **Pas de migration applicative dans cette story** : Les nouvelles tables sont introduites, mais aucun flux métier existant ne doit encore les consommer.
- **Idempotence** : Les seeds doivent utiliser des "upserts" ou des checks d’existence pour éviter les doublons en CI/CD.

### Enums canoniques

Utiliser des Enums Python fermés pour éviter les variantes de nommage :

- `audience`
  - `b2c`
  - `b2b`
  - `internal`

- `access_mode`
  - `disabled`
  - `unlimited`
  - `quota`

- `period_unit`
  - `day`
  - `week`
  - `month`
  - `year`
  - `lifetime`

- `reset_mode`
  - `calendar`
  - `rolling`
  - `lifetime`

- `source_origin`
  - `manual`
  - `migrated_from_billing_plan`
  - `migrated_from_enterprise_plan`

### Source Tree Components

- `backend/app/infra/db/models/product_entitlements.py` : nouveaux modèles
- `backend/migrations/versions/` : nouvelle migration
- `backend/scripts/seed_product_entitlements.py` : script de population initiale
- `docs/architecture/product-entitlements-model.md` : documentation technique

### Database Schema Highlights

#### `plan_catalog`

Table canonique des plans produit.
Minimum attendu :
- `id`
- `plan_code` unique
- `plan_name`
- `audience`
- `source_type`
- `source_id` nullable
- `is_active`
- timestamps

#### `feature_catalog`

Catalogue canonique des fonctionnalités produit.
Minimum attendu :
- `id`
- `feature_code` unique
- `feature_name`
- `description` nullable
- `is_metered`
- `is_active`
- timestamps

#### `plan_feature_bindings`

Association plan → feature avec mode d’accès.
Minimum attendu :
- `plan_id`
- `feature_id`
- `is_enabled`
- `access_mode`
- `variant_code` nullable
- `source_origin`
- timestamps

#### `plan_feature_quotas`

Quotas configurables par binding.
Doit permettre plusieurs quotas sur un même binding, y compris sur une même `quota_key` si la période diffère.
Exemples valides :
- `messages / day`
- `messages / month`

Minimum attendu :
- `plan_feature_binding_id`
- `quota_key`
- `quota_limit`
- `period_unit`
- `period_value`
- `reset_mode`
- `source_origin`
- timestamps

#### `feature_usage_counters`

Compteurs de consommation canoniques.
Cette table doit déjà être pensée comme support du futur moteur de consommation, même si elle n’est pas encore branchée en production.

Minimum attendu :
- `user_id`
- `feature_code`
- `quota_key`
- `period_unit`
- `period_value`
- `reset_mode`
- `window_start`
- `window_end` nullable pour `lifetime`
- `used_count`
- timestamps

### Sémantique des périodes

Le modèle doit être compatible avec les sémantiques suivantes :

- `day` : jour calendaire
- `week` : semaine ISO
- `month` : mois calendaire
- `year` : année calendaire
- `lifetime` : jamais de reset

Le moteur de résolution des fenêtres sera introduit dans une story suivante, mais le schéma doit déjà le permettre sans migration complémentaire.

### Données de seed attendues

#### Plans

- `free`
- `trial`
- `basic`
- `premium`

#### Features

- `natal_chart_short`
- `natal_chart_long`
- `astrologer_chat`
- `thematic_consultation`

#### Bindings attendus

##### `free`

- `natal_chart_short` : enabled, `unlimited`
- `natal_chart_long` : disabled
- `astrologer_chat` : disabled
- `thematic_consultation` : disabled

##### `trial`

- `natal_chart_short` : enabled, `unlimited`
- `natal_chart_long` : enabled, `quota`, `variant_code = single_astrologer`
- `astrologer_chat` : disabled
- `thematic_consultation` : enabled, `quota`

##### `basic`

- `natal_chart_short` : enabled, `unlimited`
- `natal_chart_long` : enabled, `quota`, `variant_code = single_astrologer`
- `astrologer_chat` : enabled, `quota`
- `thematic_consultation` : enabled, `quota`

##### `premium`

- `natal_chart_short` : enabled, `unlimited`
- `natal_chart_long` : enabled, `quota`, `variant_code = multi_astrologer`
- `astrologer_chat` : enabled, `quota`
- `thematic_consultation` : enabled, `quota`

#### Quotas attendus

##### `trial`

- `natal_chart_long`
  - `quota_key = interpretations`
  - `quota_limit = 1`
  - `period_unit = lifetime`
  - `period_value = 1`
  - `reset_mode = lifetime`

- `thematic_consultation`
  - `quota_key = consultations`
  - `quota_limit = 1`
  - `period_unit = week`
  - `period_value = 1`
  - `reset_mode = calendar`

##### `basic`

- `natal_chart_long`
  - `quota_key = interpretations`
  - `quota_limit = 1`
  - `period_unit = lifetime`
  - `period_value = 1`
  - `reset_mode = lifetime`

- `astrologer_chat`
  - `quota_key = messages`
  - `quota_limit = 5`
  - `period_unit = day`
  - `period_value = 1`
  - `reset_mode = calendar`

- `thematic_consultation`
  - `quota_key = consultations`
  - `quota_limit = 1`
  - `period_unit = week`
  - `period_value = 1`
  - `reset_mode = calendar`

##### `premium`

- `natal_chart_long`
  - `quota_key = interpretations`
  - `quota_limit = 5`
  - `period_unit = lifetime`
  - `period_value = 1`
  - `reset_mode = lifetime`

- `astrologer_chat`
  - `quota_key = messages`
  - `quota_limit = 2000`
  - `period_unit = month`
  - `period_value = 1`
  - `reset_mode = calendar`

- `thematic_consultation`
  - `quota_key = consultations`
  - `quota_limit = 2`
  - `period_unit = day`
  - `period_value = 1`
  - `reset_mode = calendar`

### References

- [Source: architecture.md#Data Architecture]
- [Source: backend/app/infra/db/models/billing.py] (modèle legacy pour inspiration)
- [Source: backend/app/tests/unit/test_quota_service.py] (base pour futurs tests de consommation)

## Hors périmètre explicite

Cette story ne doit pas :

- remplacer la logique Stripe ;
- décider du billing status final ;
- fusionner B2B et B2C dans un seul moteur opérationnel ;
- implémenter le fallback hybride ;
- migrer `QuotaService` ;
- migrer `B2BUsageService` ;
- migrer les endpoints front ;
- faire consommer les nouvelles tables par les services métier existants.

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Flash

### Implementation Plan
1. Vérification des artefacts existants (Modèles, Migration, Seed, Tests).
2. Correction du fichier de test `backend/app/tests/unit/test_product_entitlements_models.py` (fix de la fixture de cleanup pour éviter les erreurs de contrainte d'intégrité sur SQLite).
3. Exécution et validation des tests unitaires (7/7 passés).
4. Création de la documentation technique `docs/architecture/product-entitlements-model.md`.
5. Mise à jour de l'état de la story vers `review`.

### File List
- `backend/app/infra/db/models/product_entitlements.py`
- `backend/scripts/seed_product_entitlements.py`
- `docs/architecture/product-entitlements-model.md`
- `backend/app/tests/unit/test_product_entitlements_models.py`
- `backend/migrations/versions/3d0bd31c3b51_add_product_entitlements_tables.py`
- `backend/app/infra/db/models/__init__.py` (export des modèles)
