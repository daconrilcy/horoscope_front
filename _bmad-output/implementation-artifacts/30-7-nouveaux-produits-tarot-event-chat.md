# Story 30-7 : Nouveaux Produits et Observabilité

**Status**: done

## 1. Contexte et Objectifs
Lancement des produits Tarot/Event et durcissement de l'observabilité sur les versions de schémas. Verrouillage de la qualité pour les produits payants.

## 2. Modifications Réalisées

### 2.1 Services & APIs
- **Versioning Schémas (`schema_version`)** : Intégration du champ dans les métadonnées. Correction de la logique de cache pour que `schema_version` reflète le parse réel (V2 vs fallback V1).
- **Chat Structuré** : Extraction du champ `message` par `AIEngineAdapter` lorsque le gateway renvoie du JSON.
- **Strict-by-default** : Activation automatique de `validation_strict=True` dans le gateway pour tous les use cases dans `PAID_USE_CASES` (Tarot, Event, Natal Complete).

### 2.2 LLM Gateway & Schémas
- **Refactor Reasoning** : Unification de l'auto-ajustement des tokens/timeout pour les modèles `o1`/`gpt-5`.
- **Métriques** : Inclusion du label `mode` dans Prometheus.
- **Parité 100% (V1/V2)** : Alignement final de `schemas.py` et `fix_schemas_strict.py` sur les limites Premium V2 et Standard V1 (ex: disclaimers max 200 en V1, 300 en V2).

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
