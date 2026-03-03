# Story 30-7 : Nouveaux Produits et Observabilité

**Status**: done

## 1. Contexte et Objectifs
Lancement des produits Tarot/Event, durcissement de l'observabilité sur les versions de schémas, et verrouillage de la qualité pour les produits payants (Natal Complete, Tarot, Event).

## 2. Modifications Réalisées

### 2.1 Services & APIs
- **Versioning Schémas (`schema_version`)** : Intégration du champ dans les métadonnées. Correction de la logique de cache pour que `schema_version` reflète le parse réel (V2 vs fallback V1).
- **Chat Structuré** : `AIEngineAdapter` supporte les réponses structurées (`ChatResponseV1`). Extraction automatique du champ `message` pour le front-end.
- **Strict-by-default** : Activation automatique de `validation_strict=True` dans le gateway pour tous les use cases dans `PAID_USE_CASES` (Tarot, Event, Natal Complete).

### 2.2 LLM Gateway & Schémas
- **Refactor Reasoning** : Unification de l'auto-ajustement des tokens/timeout pour les modèles `o1`/`gpt-5`.
- **Métriques** : Inclusion du label `mode` dans Prometheus.
- **Architecture Chat V2** : Création de `ChatResponseV2` dans `schemas.py` et `fix_schemas_strict.py` avec des limites étendues et maintien de l'énumération des intentions pour une robustesse maximale.
- **Parité Totale (Astro & Chat)** : Alignement final de toutes les limites DB (items max, longueurs des items de liste, énumérations) avec les modèles Pydantic.

## 3. Fichiers Modifiés
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/schemas.py`
- `backend/app/services/natal_interpretation_service_v2.py`
- `backend/app/services/ai_engine_adapter.py`
- `backend/scripts/fix_schemas_strict.py`

## 4. Validation
- [x] Test de population de `schema_version` : 2/2 passent.
- [x] Test strict validation automatique : validé par inspection.
- [x] Intégration Tarot/Event : 100% fonctionnelle via gateway v2 avec validation stricte.
- [x] Parité des types Pydantic (Astro + Chat) : validée par inspection et tests unitaires.
