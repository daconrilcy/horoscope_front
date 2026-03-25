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

### Trajectoire
1.  **Story 61.7 (Actuelle)** : Mise en place du schéma et des données.
2.  **Story Suivante** : Introduction du `EntitlementService` pour la lecture unifiée.
3.  **Migration Progressive** : Bascule des services (`QuotaService`, `Chat`) vers le nouveau service.
4.  **Dépréciation** : Retrait des colonnes de quotas dans les tables de billing legacy.

## Contraintes Métier
-   `quota_limit > 0`
-   `period_value >= 1`
-   `used_count >= 0`
-   `window_end` requis si `period_unit != 'lifetime'`
-   Unicité stricte des codes et des bindings.
