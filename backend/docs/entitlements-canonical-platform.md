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

## Inventaire des Usages Résiduels (Legacy)

Bien que déprécié, le système legacy (`QuotaService` et table `user_daily_quota_usages`) subsiste pour les raisons suivantes :

### Backend
- **Audit et RGPD** : `privacy_service.py` inclut toujours `user_daily_quota_usages` dans l'export des données personnelles (obligation légale tant que les données existent).
- **API Billing** : L'endpoint `GET /v1/billing/quota` expose toujours `QuotaService.get_quota_status` pour compatibilité descendante.
- **Maintenance** : `test_quota_service.py` et le script `migrate_legacy_quota_to_canonical.py` utilisent ces artefacts.

### Frontend
- **API Client** : `fetchQuotaStatus` dans `frontend/src/api/billing.ts` est conservé avec un tag LEGACY (dead code, non importé).

## Trajectoire de Décommission

1. **Audit Final** : Valider que plus aucun client (web, mobile, partenaire) n'appelle `GET /v1/billing/quota`.
2. **Nettoyage Code** : Supprimer `QuotaService`, `test_quota_service.py` et l'endpoint backend.
3. **Migration RGPD** : Retirer la table de `privacy_service.py` une fois que les données sont archivées ou supprimées.
4. **Suppression Physique** : Migration Alembic `DROP TABLE user_daily_quota_usages`.

## Contraintes de Sécurité

**NE PAS DROP TABLE** `user_daily_quota_usages` sans avoir validé les étapes ci-dessus. La table sert de filet de sécurité pour les audits et les rollbacks potentiels des stories de migration.
