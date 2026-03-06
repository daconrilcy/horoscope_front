# Story 30.11: Chat API: Conversations list enrichie + endpoint get-or-create par astrologue

Status: ready-for-dev

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

- [ ] **Data Access Layer (Repository)** (AC: 1, 2, 3)
  - [ ] Étendre `list_conversations_with_last_preview_by_user_id` pour inclure les jointures avec `LlmPersonaModel`.
  - [ ] Inclure `last_message_at` (created_at du dernier message) via subquery.
  - [ ] Implémenter `get_or_create_conversation_by_persona(user_id, persona_id)`.
- [ ] **Schemas & DTOs** (AC: 1)
  - [ ] Mettre à jour `ChatConversationSummaryData` dans `backend/app/services/chat_guidance_service.py` ou `schemas.py`.
- [ ] **API Router** (AC: 1, 3)
  - [ ] Mettre à jour `GET /v1/chat/conversations` pour utiliser le repo enrichi.
  - [ ] Ajouter `POST /v1/chat/conversations/by-persona/{persona_id}`.
- [ ] **Business Logic (Service)** (AC: 1, 3)
  - [ ] Adapter `ChatGuidanceService` pour orchestrer ces appels et fournir les métadonnées de persona.
- [ ] **Validation & Tests** (AC: 5)
  - [ ] Mettre à jour `backend/app/ai_engine/tests/test_chat_endpoint.py`.
  - [ ] Vérifier les performances de la subquery (éviter le N+1).

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

gemini-2.0-flash-exp

### Debug Log References

### Completion Notes List

### File List
