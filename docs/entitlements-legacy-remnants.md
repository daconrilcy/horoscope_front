# Inventaire des reliquats legacy des droits produit

Inventaire maintenu après la revue de la story 61.50.

## Éléments supprimés

| Fichier / élément | Type | Statut | Commentaire |
|---|---|---|---|
| `backend/app/services/entitlement_service.py` | Service B2C legacy | `à supprimer` | Supprimé en 61.50, remplacé par `EffectiveEntitlementResolverService` |
| `backend/app/tests/unit/test_entitlement_service.py` | Tests legacy | `à supprimer` | Supprimé avec le service correspondant |
| `FeatureEntitlement` dans `backend/app/services/entitlement_types.py` | Dataclass legacy | `à supprimer` | Supprimée, le runtime repose sur `EffectiveFeatureAccess` |

## Éléments conservés intentionnellement

| Fichier / élément | Type | Statut | Commentaire |
|---|---|---|---|
| `backend/app/services/chat_entitlement_gate.py` | Mapping legacy d'erreur | `conservé intentionnellement` | Conserve `reason` en plus de `reason_code` pour compatibilité du flux chat |
| `backend/app/services/natal_chart_long_entitlement_gate.py` | Mapping legacy d'erreur | `conservé intentionnellement` | Compatibilité du contrat d'erreur existant |
| `backend/app/services/thematic_consultation_entitlement_gate.py` | Mapping legacy d'erreur | `conservé intentionnellement` | Compatibilité du contrat d'erreur existant |
| `backend/app/api/v1/routers/chat.py` | Payload d'erreur | `conservé intentionnellement` | Expose encore `details.reason` pour les clients historiques |
| `backend/app/api/v1/routers/consultations.py` | Payload d'erreur | `conservé intentionnellement` | Expose encore `details.reason` pour les clients historiques |
| `backend/app/api/v1/routers/natal_interpretation.py` | Payload d'erreur | `conservé intentionnellement` | Expose encore `details.reason` pour les clients historiques |

## Dette documentée

| Fichier / élément | Type | Statut | Commentaire |
|---|---|---|---|
| `backend/app/tests/integration/test_chat_entitlement.py` | Assertions legacy | `dette documentée` | Continue d'asserter `reason=no_plan` / `disabled_by_plan` |
| `backend/app/tests/integration/test_natal_chart_long_entitlement.py` | Assertions legacy | `dette documentée` | Vérifie encore le vocabulaire legacy côté gate |
| `backend/app/tests/integration/test_thematic_consultation_entitlement.py` | Assertions legacy | `dette documentée` | Vérifie encore `details.reason` pour compatibilité API |
| `backend/app/tests/unit/test_chat_entitlement_gate.py` | Assertions legacy | `dette documentée` | Couvre l'adaptateur legacy des gates |
| `backend/app/tests/unit/test_natal_chart_long_entitlement_gate.py` | Assertions legacy | `dette documentée` | Couvre l'adaptateur legacy des gates |
| `backend/app/tests/unit/test_thematic_consultation_entitlement_gate.py` | Assertions legacy | `dette documentée` | Couvre l'adaptateur legacy des gates |

## Règle de nettoyage

- Ne supprimer un reliquat que si aucune route publique et aucun test de
  compatibilité ne dépendent encore de `details.reason`.
- Toute suppression future doit être accompagnée d'une revue des contrats front
  et des tests d'intégration des gates.
