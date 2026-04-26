# Audit schémas, erreurs et constantes API v1

## Périmètre

Audit réalisé pour les AC13, AC14 et AC15 de la story `converge-api-v1-route-architecture`.

## Erreurs HTTP

- Le contrat commun est centralisé dans `backend/app/api/v1/schemas/common.py`.
- La fabrique de réponse est centralisée dans `backend/app/api/v1/errors.py`.
- Les modèles `ErrorPayload` et `ErrorEnvelope` ne sont plus redéfinis dans les schémas de routeurs.
- Les helpers `_error_response`, `_create_error_response` et `_audit_unavailable_response` délèguent à `api_error_response`.

## Constantes partagées

- Les constantes partagées de routeurs, schémas et logique API v1 sont centralisées dans `backend/app/api/v1/constants.py`.
- Les constantes sorties des modules spécialisés couvrent notamment les limites de pagination, vues LLM, messages d'erreur, valeurs autorisées et descriptions OpenAPI réutilisées.
- Le garde d'architecture interdit désormais la redéfinition locale des constantes partagées suivies par la story.

## Organisation canonique des schémas

- Les schémas transverses restent dans `backend/app/api/v1/schemas/common.py`.
- Les schémas de routeurs sont rangés sous `backend/app/api/v1/schemas/routers/<surface>/...`.
- Les fichiers plats historiques `admin_*.py`, `consultation.py`, `entitlements.py` et `natal_interpretation.py` ont été déplacés dans leur sous-dossier canonique.

## Gardes automatisés

- `backend/app/tests/unit/test_api_router_architecture.py` vérifie la centralisation des enveloppes d'erreur.
- Le même garde vérifie que les helpers d'erreur délèguent à la fabrique commune.
- Le même garde vérifie que les constantes partagées ne sont plus redéfinies dans les routeurs, schémas ou modules `router_logic`.
- Le même garde vérifie que les schémas API v1 restent sous les racines canoniques.
- `backend/app/tests/unit/test_api_error_contracts.py` vérifie le contrat JSON produit par `api_error_response`.
