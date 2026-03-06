# Story 30.11: Chat API: Conversations list enrichie + endpoint get-or-create par astrologue

Status: done

## Story

As an utilisateur,
I want voir mes discussions clairement identifiées (nom, avatar) et pouvoir ouvrir directement la discussion d'un astrologue,
so that l'expérience ressemble à WhatsApp.

## Acceptance Criteria

1. **AC1: Liste des conversations enrichie** : L'endpoint `GET /v1/chat/conversations` renvoie pour chaque conversation :
   - `conversation_id`, `persona_id`, `persona_name`, `avatar_url`.
   - `last_message_preview` (tronqué à 120 caractères).
   - `last_message_at` (date du dernier message).
   - `updated_at` (date de mise à jour de la conversation).
2. **AC2: Tri intelligent** : La liste est triée par `last_message_at` DESC (ou `updated_at` si aucun message) pour que les conversations les plus récentes remontent en haut.
3. **AC3: Endpoint Get-or-Create stable** : Ajout de `POST /v1/chat/conversations/by-persona/{persona_id}` qui :
   - Retourne la conversation active existante pour le couple (user, persona).
   - Ou en crée une nouvelle si aucune n'existe.
   - Retourne l'ID de la conversation.
4. **AC4: Isolation des contextes** : L'API garantit qu'on ne peut pas mélanger les messages de deux personas différents dans un même fil (déjà assuré par story 30.10).
5. **AC5: Tests d'intégration** : Validation du format de réponse enrichi et du comportement get-or-create sous concurrence (via tests existants adaptés).

## Tasks / Subtasks

- [x] **Data Access Layer (Repository)** (AC: 1, 2, 3)
  - [x] Étendre `list_conversations_with_last_preview_by_user_id` pour inclure les jointures avec `LlmPersonaModel`.
  - [x] Inclure `last_message_at` (created_at du dernier message) via subquery.
  - [x] Implémenter `get_or_create_conversation_by_persona(user_id, persona_id)`.
- [x] **Schemas & DTOs** (AC: 1)
  - [x] Mettre à jour `ChatConversationSummaryData` dans `backend/app/services/chat_guidance_service.py` ou `schemas.py`.
- [x] **API Router** (AC: 1, 3)
  - [x] Mettre à jour `GET /v1/chat/conversations` pour utiliser le repo enrichi.
  - [x] Ajouter `POST /v1/chat/conversations/by-persona/{persona_id}`.
- [x] **Business Logic (Service)** (AC: 1, 3)
  - [x] Adapter `ChatGuidanceService` pour orchestrer ces appels et fournir les métadonnées de persona.
- [x] **Validation & Tests** (AC: 5)
  - [x] Mettre à jour `backend/app/tests/integration/test_chat_api.py`.
  - [x] Vérifier les performances de la subquery (éviter le N+1).

## Dev Notes

- **Fichiers impactés** :
  - `backend/app/api/v1/routers/chat.py`
  - `backend/app/services/chat_guidance_service.py`
  - `backend/app/infra/db/repositories/chat_repository.py`
- **Performance** : Utiliser `scalar_subquery()` pour récupérer le contenu ET la date du dernier message efficacement dans une seule requête SQL.
- **Avatar URL** : Comme `LlmPersonaModel` n'a pas encore de champ `avatar_url`, utiliser un mapping temporaire ou le nom du persona pour générer une URL d'avatar par défaut (ex: `https://api.dicebear.com/7.x/bottts/svg?seed={name}`).

### Project Structure Notes

- Respecter le pattern DTO (BaseModel) pour les réponses API.
- S'assurer que le tri par date est robuste aux valeurs nulles (si une conversation est vide).

### References

- [Source: backend/app/infra/db/repositories/chat_repository.py#list_conversations_with_last_preview_by_user_id]
- [Source: backend/app/api/v1/routers/chat.py]
- [Source: backend/app/services/chat_guidance_service.py]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

Aucun blocage rencontré.

### Completion Notes List

- **Repository**: Étendu `list_conversations_with_last_preview_by_user_id` avec jointure INNER JOIN sur `LlmPersonaModel` et deux scalar_subqueries pour `last_message_preview` et `last_message_at`. Tri par `COALESCE(last_message_at, updated_at) DESC` pour respecter AC2. Ajout de `get_or_create_conversation_by_persona` (wrapper sur `get_or_create_active_conversation`).
- **DTO**: `ChatConversationSummaryData` enrichi avec `persona_name: str | None`, `avatar_url: str | None`, `last_message_at: datetime | None`.
- **Service**: `list_conversations` mis à jour pour déstructurer le tuple étendu (4 éléments) et construire l'`avatar_url` via dicebear. Nouvelle méthode statique `get_or_create_conversation_by_persona` ajoutée.
- **Router**: Import `uuid` déplacé en position standard. Nouveaux modèles `GetOrCreateConversationData` et `GetOrCreateConversationApiResponse`. Endpoint `POST /v1/chat/conversations/by-persona/{persona_id}` ajouté.
- **Tests**: 7 nouveaux tests d'intégration couvrant AC1 (champs enrichis), AC2 (tri par `last_message_at`), AC3 (create, idempotence, auth, rôle, request_id). Concurrence couverte par `test_chat_multi_persona.py`.
- **Résultats**: 61 tests passent (37 intégration + 21 unitaires + 3 multi-persona). Aucune régression.

### File List

- `backend/app/infra/db/repositories/chat_repository.py`
- `backend/app/services/chat_guidance_service.py`
- `backend/app/api/v1/routers/chat.py`
- `backend/app/tests/integration/test_chat_api.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/30-11-chat-api-enrichment-get-or-create.md`

## Change Log

- 2026-03-05: Implémentation complète story 30-11 — liste enrichie (persona_name/avatar_url/last_message_at), tri COALESCE, endpoint POST get-or-create par persona, 7 nouveaux tests d'intégration.
