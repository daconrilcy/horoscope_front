# Inventaire des reliquats legacy des droits produit (Entitlements)

Ce document liste les éléments legacy identifiés lors de la clôture du chantier Epic 61.

## Éléments supprimés dans la story 61.50

| Élément | Type | Statut | Commentaire |
|---|---|---|---|
| `backend/app/services/entitlement_service.py` | Service | **Supprimé** | Remplacé par `EffectiveEntitlementResolverService`. |
| `backend/app/tests/unit/test_entitlement_service.py` | Tests | **Supprimé** | Tests du service legacy supprimé. |
| `FeatureEntitlement` | Dataclass | **Supprimé** | Remplacé par `EffectiveFeatureAccess` dans `entitlement_types.py`. |

## Éléments conservés ou dette technique identifiée

| Élément | Type | Statut | Commentaire |
|---|---|---|---|
| `final_access` (tests) | Champ | **Dette** | Présent dans de nombreux tests d'intégration et unitaires comme mock ou assertion. À migrer vers `granted` lors d'un futur refacto global des tests. |
| `BillingPlanModel` | Table DB | **Conservé** | Conservé pour la compatibilité avec Stripe et le `BillingService`. Le modèle canonique lit ces plans. |
| `QuotaService` | Service | **Conservé** | Utilisé pour la migration progressive et certains comportements spécifiques non encore totalement basculés. |

## Guide de nettoyage futur
- Rechercher `final_access` dans `backend/tests/` et remplacer par `granted`.
- Rechercher `reason` dans les tests d'entitlements et remplacer par `reason_code`.
