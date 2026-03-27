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

## Support B2B (Story 61.18)

Depuis la story 61.18, le système d'entitlements canonique s'étend au segment B2B.

### Priorité de Résolution B2B

1. **Système Canonique (Source Unique)** : Depuis la story 61.23, le système d'entitlements canonique est l'unique source de vérité pour le segment B2B. Le fallback legacy via `B2BUsageService` a été définitivement supprimé.
   - Si un binding `b2b_api_access` existe pour le plan enterprise lié au compte, il définit les droits d'accès.
   - Si aucun binding n'est trouvé, l'accès est refusé par défaut (politique sécurisée).

### Identifiant de Compteur B2B

En raison de la contrainte technique sur la table `feature_usage_counters`, les consommations B2B sont enregistrées sous le `user_id` correspondant à l'`admin_user_id` de l'EnterpriseAccountModel.

> **Dette technique** : Ce mapping est transitoire. Une future évolution devra découpler les compteurs B2B de la table `users`.

### Métadonnées de Quota

Les réponses API B2B incluent désormais un objet `quota_info` dans le body JSON :

- `source: "canonical"` : Consommation via le moteur canonique (champs `limit`, `remaining`, `window_end` présents).
- `source: "canonical_unlimited"` : Accès illimité via le moteur canonique.

