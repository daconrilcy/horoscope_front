# Story 30-7 : Nouveaux Produits et Observabilité

**Status**: done

## 1. Contexte et Objectifs
Lancement des nouveaux produits Premium (Tarot, Guidance Événementielle) et mise en place d'une observabilité fine sur les versions de schémas et les performances des modèles de reasoning.

## 2. Modifications Réalisées

### 2.1 Backend - Services & APIs
- **Versioning Schémas (`schema_version`)** : Ajout du champ `schema_version` dans les métadonnées d'interprétation. Ce champ est calculé dynamiquement lors du parse (V2 si succès, sinon V1) et permet au frontend de typer correctement la réponse.
- **Chat Structuré** : `AIEngineAdapter` supporte désormais les réponses structurées (`ChatResponseV1`). Il extrait automatiquement le champ `message` pour le front-end, permettant d'intégrer des `suggested_replies` et des `intents` sans changer le contrat de l'adaptateur.
- **Nouveaux Use Cases** : Intégration de `tarot_reading` et `event_guidance` avec leurs prompts et schémas dédiés.

### 2.2 LLM Gateway - Optimisation & Observabilité
- **Consolidation Reasoning** : Unification de la logique d'ajustement automatique (tokens/timeout) pour les modèles de type `o1`, `o3`, `gpt-5` dans un helper privé `_adjust_reasoning_config`.
- **Métriques Prometheus** : Inclusion systématique du label `mode` (structured/chat) dans les compteurs de requêtes gateway.
- **Observabilité des Erreurs** : Amélioration de la capture des détails d'erreur provider pour faciliter le debug en production.

## 3. Fichiers Modifiés
- `backend/app/api/v1/schemas/natal_interpretation.py`
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/services/natal_interpretation_service_v2.py`
- `backend/app/services/ai_engine_adapter.py`
- `backend/scripts/seed_30_5_new_use_cases.py`
- `backend/app/tests/unit/test_natal_interpretation_service_v2.py`

## 4. Validation
- [x] Test de population de `schema_version` : 2/2 passent.
- [x] Test du reasoning auto-adjust : validé par logs et tests gateway.
- [x] Intégration Tarot/Event : validée via stubs et tests d'intégration.
