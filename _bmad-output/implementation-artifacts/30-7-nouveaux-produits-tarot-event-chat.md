# Story 30-7 : Nouveaux Produits et Observabilité

**Status**: done

## 1. Contexte et Objectifs
Lancement des produits Tarot/Event, durcissement de l'observabilité et verrouillage de la qualité via une parité totale des schémas.

## 2. Modifications Réalisées

### 2.1 Services & Observabilité
- **GatewayMeta Enhancement** : Ajout du champ `schema_version` (v1, v2) directement dans les métadonnées gateway pour une traçabilité complète.
- **Strict-by-default** : Activation automatique de `validation_strict=True` dans le gateway pour tous les use cases dans `PAID_USE_CASES`.
- **Refactor Reasoning** : Unification de l'auto-ajustement des tokens/timeout pour les modèles de type `o1`/`gpt-5` via `_adjust_reasoning_config`.

### 2.2 Architecture Chat Premium
- **Chat V2** : Création de `ChatResponseV2` (Message 4000 chars, 8 suggestions max) avec maintien de l'énumération des intentions pour garantir la robustesse fonctionnelle.
- **Parité Totale (Astro & Chat)** : Alignement final de toutes les limites DB (items max, longueurs des items de liste, minItems) avec les modèles Pydantic via des types `Annotated` partagés.

## 3. Fichiers Modifiés
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/models.py`
- `backend/app/llm_orchestration/schemas.py`
- `backend/scripts/fix_schemas_strict.py`

## 4. Validation
- [x] Test de population de `schema_version` en Meta : validé.
- [x] Test de parité totale Pydantic/DB : 42/42 tests unitaires au vert.
- [x] Intégration ChatMessenger : historique et extraction message validés.
