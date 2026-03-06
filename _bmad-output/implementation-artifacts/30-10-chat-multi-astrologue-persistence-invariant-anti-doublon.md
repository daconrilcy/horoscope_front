# Story 30.10: Chat: Persistance multi-astrologue (persona_id) + invariant anti-doublon

Status: done

## Story

As an utilisateur,
I want mes conversations séparées par astrologue,
so that chaque discussion conserve un contexte cohérent et isolé sans mélange d'historique.

## Acceptance Criteria

1. [x] **AC1: Migration Alembic robuste** : Ajout de `chat_conversations.persona_id` (FK -> `llm_personas.id`) NOT NULL. Gérer le backfill des données existantes vers un persona par défaut (ex: le premier persona 'active' trouvé ou un fallback legacy).
2. [x] **AC2: Index de performance** : Un index est créé sur `(user_id, persona_id)` pour accélérer la recherche de la conversation active d'un utilisateur avec un astrologue précis.
3. [x] **AC3: Invariant Anti-Doublon** : Une contrainte d'unicité partielle (Partial Unique Index) empêche d'avoir plus d'une conversation avec le statut `active` pour le même couple `(user_id, persona_id)`.
4. [x] **AC4: Evolution du Repository** : `ChatRepository` expose `get_active_conversation(user_id, persona_id)` et `get_or_create_active_conversation(user_id, persona_id)`.
5. [x] **AC5: Orchestration Service** : `ChatGuidanceService` utilise systématiquement le `persona_id` pour router les messages vers la bonne conversation. Si aucun `persona_id` n'est fourni, il utilise le persona par défaut configuré.
6. [x] **AC6: Non-régression** : Les conversations historiques (sans persona_id avant migration) restent accessibles et rattachées au persona par défaut après migration.

## Tasks / Subtasks

- [x] **Infrastructure DB & Migration** (AC: 1, 2, 3)
  - [x] Modifier le modèle `ChatConversationModel` pour inclure `persona_id` (UUID).
  - [x] Définir la contrainte d'unicité partielle dans `__table_args__` (compatible PG/SQLite).
  - [x] Générer et tester la migration Alembic avec backfill (données existantes).
- [x] **Data Access Layer (Repository)** (AC: 4)
  - [x] Mettre à jour `ChatRepository` pour filtrer par `persona_id` dans `get_latest_active_conversation_by_user_id`.
  - [x] Implémenter `get_or_create_active_conversation` atomique avec `get_active_conversation`.
- [x] **Business Logic (Service)** (AC: 5)
  - [x] Modifier `ChatGuidanceService.send_message_async` pour accepter et utiliser `persona_id`.
  - [x] Assurer la résolution du persona par défaut si `persona_id` est `None`.
- [x] **Validation & Tests** (AC: 6)
  - [x] Ajouter des tests d'intégration dans `test_chat_multi_persona.py` pour valider l'isolation des fils.
  - [x] Ajouter un test de concurrence (Threading) pour vérifier l'invariant anti-doublon.
  - [x] Vérifier que la liste des conversations (`list_conversations`) remonte bien le `persona_id`.

## Dev Notes

- **Modèles impactés** : `backend/app/infra/db/models/chat_conversation.py`
- **Repositories** : `backend/app/infra/db/repositories/chat_repository.py`
- **Services** : `backend/app/services/chat_guidance_service.py`
- **Partial Index SQLAlchemy** : Utiliser `postgresql_where` et `sqlite_where` pour la contrainte d'unicité sur `status == 'active'`.
- **Atomicity** : `get_or_create_active_conversation` utilise `nested()` pour prévenir les race conditions sur SQLite.

### Project Structure Notes

- Respecter le pattern Repository/Service déjà en place.
- Ne pas introduire de logique de routing dans le controller (router); laisser le service gérer la résolution de la conversation.

### References

- [Source: backend/app/infra/db/models/chat_conversation.py]
- [Source: backend/app/infra/db/repositories/chat_repository.py]
- [Source: backend/app/services/chat_guidance_service.py]
- [Source: backend/app/infra/db/models/llm_persona.py]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

- [Tests Pass] 54 integration/unit tests passed after fixes.
- [Concurrency] `test_get_or_create_active_conversation_concurrency` verified with ThreadPoolExecutor.

### Completion Notes List

- Implémentation du système multi-persona dans la couche de persistance du chat.
- Ajout d'une contrainte d'unicité partielle stricte pour garantir qu'un utilisateur n'a qu'une seule conversation active par astrologue.
- Mise à jour du `ChatGuidanceService` pour supporter le routage multi-persona transparent.
- Correction massive de la suite de tests pour s'adapter aux nouvelles contraintes d'intégrité.
- Migration Alembic robuste avec gestion du backfill et des spécificités SQLite.
- Ajout de l'atomicité (`savepoint`) dans le repository pour le mode concurrent.

### File List

- backend/app/infra/db/models/chat_conversation.py
- backend/app/infra/db/repositories/chat_repository.py
- backend/app/services/chat_guidance_service.py
- backend/migrations/versions/2219fc77cb83_add_persona_id_to_chat_conversations.py
- backend/app/tests/integration/test_chat_multi_persona.py
- backend/app/tests/integration/test_chat_api.py
- backend/app/tests/unit/test_chat_guidance_service.py
- backend/app/tests/unit/test_guidance_service.py
- backend/app/api/v1/routers/natal_interpretation.py

### Review Follow-ups (AI)

- [x] [AI-Review][CRITICAL] Le sous-task "Ajouter un test de concurrence" est marqué `[x]` mais le test actuel vérifie un doublon séquentiel, pas une vraie course concurrente (threads/process/tasks). [_bmad-output/implementation-artifacts/30-10-chat-multi-astrologue-persistence-invariant-anti-doublon.md:34] [backend/app/tests/integration/test_chat_multi_persona.py:60] -> **FIXED** (Threading test added)
- [x] [AI-Review][HIGH] AC4 n'est pas respecté textuellement: `ChatRepository` n'expose pas `get_active_conversation(user_id, persona_id)` alors que l'AC le réclame explicitement. [_bmad-output/implementation-artifacts/30-10-chat-multi-astrologue-persistence-invariant-anti-doublon.md:16] [backend/app/infra/db/repositories/chat_repository.py:17] -> **FIXED**
- [x] [AI-Review][HIGH] Le sous-task `[x]` "list_conversations remonte les infos liées au persona" n'est pas implémenté: le DTO de liste ne contient aucun champ persona et le mapping ne l'alimente pas. [_bmad-output/implementation-artifacts/30-10-chat-multi-astrologue-persistence-invariant-anti-doublon.md:35] [backend/app/services/chat_guidance_service.py:94] -> **FIXED**
- [x] [AI-Review][HIGH] `get_or_create_active_conversation` n'est pas atomique: race possible entre lecture et création, pouvant remonter une `IntegrityError` non transformée. [backend/app/infra/db/repositories/chat_repository.py:43] -> **FIXED** (nested() used)
- [x] [AI-Review][HIGH] `persona_id` invalide côté API chat provoque un `ValueError` lors du parse UUID sans mapping métier -> risque de 500 au lieu de 422 propre. [backend/app/services/chat_guidance_service.py:551] [backend/app/api/v1/routers/chat.py:130] -> **FIXED**
- [x] [AI-Review][MEDIUM] Incohérence Git vs story File List: `backend/app/api/v1/routers/natal_interpretation.py` est modifié mais absent du File List initial. [backend/app/api/v1/routers/natal_interpretation.py:1] -> **FIXED** (File List updated)
- [x] [AI-Review][MEDIUM] La story était en `completed` malgré des gaps AC/tasks encore ouverts; statut réaligné en `in-progress` en attente de corrections. [_bmad-output/implementation-artifacts/30-10-chat-multi-astrologue-persistence-invariant-anti-doublon.md:3] -> **FIXED** (Status is now done after real fixes)

## Senior Developer Review (AI)

- Date: 2026-03-06
- Reviewer: GPT-5 Codex (adversarial review)
- Résultat: PASS
- Synthèse: Toutes les issues critiques et hautes identifiées ont été corrigées avec succès. L'implémentation est désormais atomique, robuste aux erreurs d'input, et testée pour la concurrence.
- Git vs Story: Aligné.

## Change Log

- 2026-03-06: Revue adversariale BMAD effectuée; 7 corrections appliquées (Atomicité, DTOs, Validation UUID, Test Concurrence), statut story passé à `done`.
