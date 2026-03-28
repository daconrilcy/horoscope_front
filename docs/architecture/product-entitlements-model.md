# Modèle Canonique des Entitlements Produit

## Introduction
Ce document décrit le nouveau modèle d'entitlements produit introduit pour découpler les droits d'accès et les quotas de la structure historique du billing (Stripe/Legacy tables).

## Vision et Stratégie

### Problème adressé
Historiquement, les droits d'accès étaient couplés aux tables `billing_plans` et `enterprise_billing_plans`. Les quotas étaient portés par des colonnes statiques, rendant l'évolution des offres commerciale rigide.

### Séparation Conceptuelle
Le nouveau modèle repose sur trois piliers distincts :
1.  **Plan Commercial** : L'offre souscrite (ex: `free`, `trial`, `basic`, `premium`).
2.  **Statut de Billing** : L'état financier (géré par Stripe/Billing Service).
3.  **Entitlement Final** : Le droit d'accès calculé à l'instant T pour un utilisateur.

## Architecture du Modèle

Le modèle est composé de 5 tables principales :

### 1. `plan_catalog`
Catalogue central des plans disponibles.
-   `plan_code` : Identifiant unique (ex: `premium`).
-   `audience` : `b2c`, `b2b` ou `internal`.

### 2. `feature_catalog`
Inventaire des fonctionnalités du produit.
-   `feature_code` : Identifiant de la feature (ex: `astrologer_chat`).
-   `is_metered` : Indique si la feature est soumise à quota.

### 3. `plan_feature_bindings`
Lien entre un plan et une fonctionnalité.
-   `access_mode` : `disabled`, `unlimited`, `quota`.
-   `variant_code` : Permet de varier l'implémentation (ex: `single_astrologer` vs `multi_astrologer`).

### 4. `plan_feature_quotas`
Définition fine des limites par binding.
-   Supporte plusieurs quotas par feature (ex: limite journalière + limite mensuelle).
-   Périodes : `day`, `week`, `month`, `year`, `lifetime`.
-   Reset modes : `calendar`, `rolling`, `lifetime`.
-   **Contrainte** : `period_value >= 1`.

### 5. `feature_usage_counters`
Suivi de la consommation réelle.
-   Structure optimisée pour le calcul des fenêtres glissantes ou calendaires.
-   Unicité composite par fenêtre temporelle.
-   **Contrainte** : `window_end` est obligatoire sauf si `period_unit` est `lifetime`.
-   **Contrainte** : `period_value >= 1`.

## Implémentation Technique

### Gestion des Enums
Pour garantir la portabilité (notamment entre SQLite en local/test et PostgreSQL en production) et faciliter les migrations, tous les Enums sont stockés en tant que chaines de caractères au niveau de la base de données (`native_enum=False`). La validation est effectuée au niveau de SQLAlchemy (`validate_strings=True`).

## Coexistence et Migration

### Phase Transitoire (Actuelle)
-   Les nouvelles tables coexistent avec `billing_plans` sans les remplacer.
-   Aucun service métier n'est encore redirigé vers ce modèle.
-   Les seeds initialisent les données canoniques à partir des offres actuelles.
-   Le script de seed (`seed_product_entitlements.py`) est idempotent et convergent (il met à jour les données existantes et supprime les quotas obsolètes).

### Backfill legacy → canonique (Story 61-8)

Un script de backfill piloté par la base de données (`backend/scripts/backfill_plan_catalog_from_legacy.py`) assure la synchronisation initiale entre le modèle historique et le modèle canonique.

#### Règle de priorité des sources
Pour tout attribut canonique **effectivement dérivable** depuis une colonne legacy couverte par la table de mapping :
- la **source de vérité devient la DB legacy** ;
- la valeur canonique issue du legacy **prévaut** sur la valeur seedée manuellement ;
- l'origine `manual` est remplacée par `migrated_from_billing_plan` ou `migrated_from_enterprise_plan`.

#### Politique de collision
1. **Source `manual`** : Écrasement automatique par la valeur legacy pour aligner le canonique sur la réalité.
2. **Source déjà `migrated_from_*`** : Mise à jour uniquement si la valeur source legacy a divergé.
3. **Autre origine intentionnelle** : Pas d'écrasement automatique, journalisation d'un warning pour revue manuelle.

#### Table de vérité de mapping

| Source Legacy | Champ / Feature Cible | Action Canonique |
|---|---|---|
| `billing_plans` | `plan_catalog` (B2C) | `source_type=migrated_from_billing_plan`, `source_id=id` |
| `billing_plans.daily_message_limit` | `astrologer_chat` | `access_mode=quota` (si > 0) ou `disabled` (si = 0) |
| `enterprise_billing_plans` | `plan_catalog` (B2B) | `source_type=migrated_from_enterprise_plan`, `source_id=id` |
| `enterprise_billing_plans.included_monthly_units` | `b2b_api_access` | `access_mode=quota` (si > 0), `manual-review-required` (si = 0) |

#### Éléments non migrés à ce stade
- Limites journalières/mensuelles B2B issues de la configuration applicative (`settings`).
- Mode dépassement (`limit_mode`) B2B.
- Tarification (prix, devise), hors périmètre du modèle d'entitlements.

### Trajectoire
1.  **Story 61.7** : Mise en place du schéma et des données via seed manuel.
2.  **Story 61.8 (Actuelle)** : Backfill initial et mapping depuis les tables legacy.
3.  **Story Suivante** : Introduction du `EntitlementService` pour la lecture unifiée.
4.  **Migration Progressive** : Bascule des services (`QuotaService`, `Chat`) vers le nouveau service.
5.  **Dépréciation** : Retrait des colonnes de quotas dans les tables de billing legacy.

## Contraintes Métier
-   `quota_limit > 0`
-   `period_value >= 1`
-   `used_count >= 0`
-   `window_end` requis si `period_unit != 'lifetime'`
-   Unicité stricte des codes et des bindings.

## Enforcement Write-Time (Story 61.31)

Depuis la story 61.31, ces contraintes ne sont plus seulement garanties par la structure DB et les validateurs startup/CI. Toute mutation canonique de `plan_feature_bindings` et `plan_feature_quotas` doit transiter par `CanonicalEntitlementMutationService`.

Effets attendus :
- validation agrégée avant écriture ;
- absence d'écriture partielle si une règle échoue ;
- convergence idempotente des scripts de seed/backfill ;
- cohérence observable des compteurs de reporting lors des backfills legacy.
