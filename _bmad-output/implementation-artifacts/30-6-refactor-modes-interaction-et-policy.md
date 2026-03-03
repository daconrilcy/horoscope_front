# Story 30-6 : Refactor des Modes d'Usage (Phase 1)

**Status:** done

## 1. Contexte et Objectifs
Refactoriser le Gateway et la base de données pour supporter trois modes d'interaction distincts : (A) structuré sans question, (B) structuré avec question, et (C) chat libre.

## 2. Modifications Réalisées

### 2.1 Modèle de Données (DB & SQLAlchemy)
Mise à jour de `LlmUseCaseConfigModel` dans `llm_prompt.py` :
- `interaction_mode` : `structured` (par défaut) ou `chat`.
- `user_question_policy` : `none` (par défaut), `optional` ou `required`.
- Migration Alembic générée et appliquée.

### 2.2 Refactor LLM Gateway (`gateway.py`)
- **Extraction `build_user_payload`** : Centralise la construction du message utilisateur et valide la présence de la question selon la `policy`.
- **Sous-fonctions de composition** :
    - `compose_structured_messages` : Pour les réponses JSON validées.
    - `compose_chat_messages` : Pour les conversations fluides avec injection d'historique.
- **Routage Dynamique** : Le Gateway choisit automatiquement le mode de composition et d'exécution (`response_format` activé ou non) selon la configuration du use-case.
- **Validation enum** : Vérification des valeurs `interaction_mode` et `user_question_policy` avant routage.

### 2.3 Client Providers (`responses_client.py`)
- Support générique des appels sans schéma JSON pour le mode chat (via `response_format=None`).

### 2.4 Seeds (`use_cases_seed.py`)
- 7 use-cases canoniques seedés avec `interaction_mode` et `user_question_policy`.

## 3. Dev Agent Record

### File List
- `backend/app/infra/db/models/llm_prompt.py` — ajout `interaction_mode`, `user_question_policy`
- `backend/app/llm_orchestration/gateway.py` — refactoring compose + build_user_payload + validation enum + history guard
- `backend/app/llm_orchestration/models.py` — ajout champs `interaction_mode`, `user_question_policy` dans `UseCaseConfig`
- `backend/app/llm_orchestration/seeds/use_cases_seed.py` — 7 use-cases canoniques avec modes
- `backend/migrations/versions/ee2645ed1a1c_add_interaction_modes_to_use_case.py` — migration Alembic
- `backend/app/tests/unit/test_gateway_modes.py` — tests 3 politiques + mode chat + schéma
- `backend/app/tests/unit/test_gateway_3_roles.py` — test chart_json dans message user

## 4. Validation
- [x] Tests unitaires couvrant les 3 politiques de question (`none`, `optional`, `required`).
- [x] Tests unitaires vérifiant l'injection de l'historique en mode `chat`.
- [x] Validation de la non-régression du mode structuré.

## 5. Senior Developer Review (AI) — 2026-03-02

**Outcome : APPROVED avec corrections appliquées**

Issues trouvés et corrigés automatiquement :

### 🔴 HIGH (corrigés)
- **H1** `ee2645ed1a1c` : colonnes NOT NULL sans `server_default` → fail PostgreSQL prod si table non vide. **Fix** : ajout `server_default='structured'` / `server_default='none'`.
- **H2** `test_gateway_3_roles.py` : `settings.llm_orchestration_v2` non patché → le gateway ignorait la DB et levait `UnknownUseCaseError`. **Fix** : ajout `monkeypatch` + helper `_make_result()`.
- **H3** `build_user_payload` : champ `user_input["message"]` (utilisé par `chat_astrologer`) ignoré → message perdu silencieusement. **Fix** : ajout `or user_input.get("message") or context.get("last_user_msg")`.

### 🟡 MEDIUM (corrigés)
- **M1** Aucune validation des valeurs enum `interaction_mode`/`user_question_policy`. **Fix** : guards `_VALID_INTERACTION_MODES` / `_VALID_QUESTION_POLICIES` + `GatewayConfigError` avant routage.
- **M2** History injectée sans validation du format → erreur 400 opaque côté OpenAI. **Fix** : skip des messages malformés avec warning dans `compose_chat_messages`.
- **M3** Migration `ee2645ed1a1c` contenait des `alter_column` NUMERIC→UUID parasites (artefacts Alembic/SQLite sur 6 tables). **Fix** : migration réécrite pour ne contenir que les 2 `add_column` de la story 30-6, avec commentaire explicatif.
- **M4** `build_user_payload` ignorait `context["last_user_msg"]`. **Fix** inclus dans H3.

### 🟢 LOW (corrigés)
- **L1** Unicode échappé (`\u00e8`) → réécrit en UTF-8 natif.
- **L2** Signature de `build_user_payload` sur une ligne trop longue → reformatée.

## 6. Change Log
- 2026-03-02 : Implémentation initiale (dev agent)
- 2026-03-02 : Code review AI — 3 HIGH, 4 MEDIUM, 3 LOW identifiés et corrigés (reviewer AI)
