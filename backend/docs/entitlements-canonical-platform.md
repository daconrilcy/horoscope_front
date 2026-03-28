# Architecture des Entitlements : Plateforme Canonique

Ce document définit la source de vérité pour les droits d'accès (entitlements) aux fonctionnalités B2C de la plateforme.

## Source de Vérité Canonique

Depuis la story 61.16, la source de vérité unique pour les fonctionnalités B2C migrées est le système **Feature Usage Counters** (`feature_usage_counters`).

Le système legacy basé sur les quotas journaliers (`user_daily_quota_usages`) est officiellement déprécié pour ces flux.

## État de Migration des Fonctionnalités

| Fonctionnalité | Story de Migration | État | Fallback Legacy |
|----------------|-------------------|------|-----------------|
| `astrologer_chat` | 61.11 | 100% Canonique | Supprimé (61.15/61.16) |
| `natal_chart_long` | 61.13 | 100% Canonique | Aucun (Natif) |
| `thematic_consultation` | 61.12 | 100% Canonique | Aucun (Natif) |

## Breaking Changes (Story 61.17)

- **Endpoint Supprimé** : `GET /v1/billing/quota` a été décommissionné. Il retourne désormais HTTP 404.
- **Module Supprimé** : `backend/app/services/quota_service.py` (`QuotaService`) a été supprimé. Tout nouveau code doit utiliser `QuotaUsageService` et le système canonique d'entitlements.
- **Refactor Frontend** : Les helpers frontend (`useBillingQuota`, `fetchQuotaStatus`) ont été renommés en `useChatEntitlementUsage`, `fetchChatEntitlementUsage` pour refléter leur usage réel de `GET /v1/entitlements/me`.

## Inventaire des Usages Résiduels (Legacy)

Bien que déprécié et ses services supprimés, certains artefacts subsistent :

### Backend
- **Audit et RGPD** : `privacy_service.py` inclut toujours `user_daily_quota_usages` dans l'export des données personnelles (obligation légale tant que les données existent).
- **Migration** : Le script `migrate_legacy_quota_to_canonical.py` reste archivé pour référence historique.

### Frontend
- (Aucun usage legacy actif identifié après 61.17)

## Trajectoire de Décommission

1. **Audit Final** : (Terminé en 61.17) ✓
2. **Nettoyage Code** : (Terminé en 61.17) ✓
3. **Migration RGPD** : Retirer la table de `privacy_service.py` une fois que les données sont archivées ou supprimées.
4. **Suppression Physique** : Migration Alembic `DROP TABLE user_daily_quota_usages`.

## Contraintes de Sécurité

**NE PAS DROP TABLE** `user_daily_quota_usages` sans avoir validé les étapes ci-dessus. La table sert de filet de sécurité pour les audits (obligation légale RGPD).

## Support B2B (Story 61.18, 61.25)

Depuis la story 61.18, le système d'entitlements canonique s'étend au segment B2B. En story 61.25, le stockage a été découplé pour utiliser une table native B2B.

### Séparation Canonique B2C / B2B

| Segment | Table | Index Primaire | Service |
|---------|-------|----------------|---------|
| **B2C** | `feature_usage_counters` | `user_id` | `QuotaUsageService` |
| **B2B** | `enterprise_feature_usage_counters` | `enterprise_account_id` | `EnterpriseQuotaUsageService` |

### Identifiant de Compteur B2B (Story 61.25)

Le compromis transitoire consistant à utiliser `admin_user_id` comme clé de quota a été supprimé. Les consommations B2B sont désormais indexées directement par `enterprise_account_id` dans la table native `enterprise_feature_usage_counters`.

- **Indépendance** : La consommation quota ne dépend plus de l'existence ou du changement d'un administrateur particulier.
- **Source de Vérité** : `EnterpriseQuotaUsageService` est l'unique service gérant le cycle de vie de ces compteurs.

### Décommissionnement B2B Legacy (Story 61.24)

- **Suppression Physique** : La table `enterprise_daily_usages` a été supprimée via une migration Alembic destructive (`9d73f7af0bf4`).
- **Services Migrés** : `B2BBillingService`, `B2BReconciliationService`, `B2BApiEntitlementGate` et `B2BAuditService` utilisent désormais la table native B2B.

### Outils ops B2B — Alignement post-61.26

Depuis la story 61.26, l'écosystème ops B2B est entièrement aligné sur la table native `enterprise_feature_usage_counters`.

- **Audit Ops** : `GET /v1/ops/b2b/entitlements/audit` lit exclusivement `enterprise_feature_usage_counters`. L'absence d'`admin_user_id` n'est plus un motif de blocage ou d'audit "settings_fallback".
- **Repair Ops** : Les blockers `"set_admin_user"` ont été supprimés. L'outil `POST /repair/set-admin-user` est désormais documenté comme un outil de gestion d'**ownership/authentification**, sans impact sur le quota.
- **admin_user_id** : Ce champ dans `enterprise_accounts` définit l'administrateur du compte (ownership) uniquement. Plus aucun chemin de décision quota/usage B2B n'en dépend.
- **Nettoyage Historique** : Les compteurs legacy B2B dans `feature_usage_counters` ont été purgés après vérification via `verify_b2b_usage_migration.py`.

### Invariants du Système (Post-61.26)

| Flux | Table Source | Identifiant Pivot |
|------|--------------|-------------------|
| **Usage B2C** | `feature_usage_counters` | `user_id` |
| **Usage B2B** | `enterprise_feature_usage_counters` | `enterprise_account_id` |
| **Audit B2B** | `enterprise_feature_usage_counters` | `enterprise_account_id` |
| **Ownership B2B** | `enterprise_accounts` | `admin_user_id` |

### Métadonnées de Quota

Les réponses API B2B incluent désormais un objet `quota_info` dans le body JSON :

- `source: "canonical"` : Consommation via le moteur canonique (champs `limit`, `remaining`, `window_end` présents).
- `source: "canonical_unlimited"` : Accès illimité via le moteur canonique.

