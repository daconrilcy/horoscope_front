# Story 30-6 : Refactor des Modes d'Interaction et Policies

**Status:** done

## 1. Contexte et Objectifs
Standardisation du Gateway pour supporter les modes `structured` et `chat`, et sécuriser la transmission des messages via des politiques de question strictes.

## 2. Modifications Réalisées

### 2.1 Refactor Architecture Gateway
- **Composition de Messages** : Extraction de la logique dans `compose_chat_messages` et `compose_structured_messages`.
- **User Payload Centralisé** : Implémentation de `build_user_payload` pour centraliser Layer 4 (Données utilisateur).
- **Protection Redondance** : Détection intelligente de `chart_json` dans le rôle `developer`.

### 2.2 Modes d'Interaction
- **Validation Runtime** : Contrôles sur `interaction_mode` et `user_question_policy`.
- **Chat Messenger** : Support de l'historique complet rejoué au gateway via le champ `history` dans le contexte.

## 3. Fichiers Modifiés
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/seeds/use_cases_seed.py`
- `backend/app/services/ai_engine_adapter.py`

## 4. Validation
- [x] Test des modes d'interaction : 6/6 passent.
- [x] Validation de l'historique chat : confirmée par tests d'intégration.
