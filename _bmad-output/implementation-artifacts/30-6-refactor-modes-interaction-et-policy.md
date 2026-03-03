# Story 30-6 : Refactor des Modes d'Interaction et Policies

**Status:** done

## 1. Contexte et Objectifs
Standardisation du Gateway pour supporter trois modes d'interaction distincts (A, B, C) et sécuriser la transmission des questions utilisateurs via des politiques strictes.

## 2. Modifications Réalisées

### 2.1 Refactor Architecture Gateway
- **Composition de Messages** : Extraction de la logique de composition dans `compose_chat_messages` et `compose_structured_messages`.
- **User Payload Centralisé** : Implémentation de `build_user_payload` pour construire dynamiquement le bloc de données utilisateur (Layer 4) en fonction des variables disponibles (natal summary, technical data, situation).
- **Redundancy Protection** : Le gateway détecte si `chart_json` est déjà présent dans le prompt `developer` pour éviter de le renvoyer inutilement dans le message `user`.

### 2.2 Modes d'Interaction & Policies
- **Validation Runtime** : Ajout de contrôles sur `interaction_mode` (`structured`, `chat`) et `user_question_policy` (`none`, `optional`, `required`).
- **Enforcement Policy** : Le gateway lève une `InputValidationError` si une question est requise mais absente, et ignore silencieusement les questions pour les modes purement descriptifs.

### 2.3 Configuration & Seeds
- **Seeds Canoniques** : Mise à jour de `use_cases_seed.py` pour définir les contrats de tous les use cases (ex: `natal_interpretation` -> mode `structured`, policy `none`).
- **Stubs de Secours** : Alignement des `USE_CASE_STUBS` in-code avec les contrats de la base de données.

## 3. Fichiers Modifiés
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/models.py`
- `backend/app/llm_orchestration/seeds/use_cases_seed.py`
- `backend/app/tests/unit/test_gateway_modes.py`

## 4. Validation
- [x] Test des modes d'interaction : 6/6 passent.
- [x] Validation de la politique de question : confirmée par tests unitaires.
- [x] Intégrité des seeds DB : validée par inspection.
