# Story 30.16: Chat — Idempotence POST /v1/chat/messages via client_message_id

Status: reviewed
Review: _bmad-output/test-artifacts/review-30-16.md

## Story

As a utilisateur du chat,
I want que l'envoi d'un message reste idempotent même en cas de timeout réseau ou de double-clic,
so that je ne me retrouve pas avec des messages dupliqués dans ma conversation si le frontend retente automatiquement une requête dont la réponse a été perdue.

## Contexte du problème

Le endpoint `POST /v1/chat/messages` ne disposait d'aucun mécanisme d'idempotence :

1. **Côté backend** : `send_message_async` crée systématiquement un nouveau message utilisateur dans la DB sans vérifier si ce message a déjà été traité → un double-POST (timeout puis retry) produit deux paires (user_message + assistant_message) dans la conversation.
2. **Côté frontend** : `handleSendMessage` dans `ChatPage.tsx` n'envoyait aucune clé d'idempotence, rendant impossible côté serveur la détection des doublons.
3. **Impact observé** : conversations avec des messages en double, même réponse "bonjour" reçue deux fois dans des scénarios de lenteur réseau.

## Acceptance Criteria

1. [x] **AC1 — Clé d'idempotence frontend** : Le frontend génère un UUID (`crypto.randomUUID()`) par tentative d'envoi et le transmet en tant que `client_message_id` dans le payload `POST /v1/chat/messages`.
2. [x] **AC2 — Schéma request étendu** : `ChatMessageRequest` accepte un champ optionnel `client_message_id: str | None`.
3. [x] **AC3 — Colonne DB** : La table `chat_messages` dispose d'un champ `client_message_id VARCHAR(36) NULLABLE` avec un index unique partiel sur `(conversation_id, client_message_id) WHERE client_message_id IS NOT NULL`.
4. [x] **AC4 — Détection idempotente** : Si `client_message_id` est fourni et qu'un message utilisateur avec cet ID existe déjà dans la conversation ET que le message assistant suivant existe aussi → la paire existante est retournée directement sans appel LLM (log `chat_idempotent_hit`).
5. [x] **AC5 — Race condition gérée** : Si le message utilisateur existe mais pas encore le message assistant (premier appel toujours en cours), le service skip la création du message utilisateur doublon et relance uniquement l'appel LLM.
6. [x] **AC6 — Rétrocompatibilité** : `client_message_id` est optionnel. Les requêtes sans ce champ fonctionnent exactement comme avant.

## Tasks / Subtasks

- [x] **T1 — Migration Alembic** (AC3)
  - [x] Créer `backend/migrations/versions/20260306_0029_add_client_message_id_to_chat_messages.py`
  - [x] Ajouter colonne `client_message_id VARCHAR(36) NULLABLE`
  - [x] Créer index unique partiel `uq_chat_messages_conversation_client_id` sur `(conversation_id, client_message_id) WHERE client_message_id IS NOT NULL`
  - [x] Implémenter `downgrade()` (drop index + drop column)

- [x] **T2 — Modèle SQLAlchemy** (AC3)
  - [x] Ajouter `client_message_id: Mapped[str | None]` à `ChatMessageModel`

- [x] **T3 — Repository** (AC4, AC5)
  - [x] Étendre `create_message()` pour accepter `client_message_id: str | None = None`
  - [x] Ajouter `get_message_by_client_id(conversation_id, client_message_id)`
  - [x] Ajouter `get_next_assistant_message(conversation_id, after_id)`

- [x] **T4 — Service** (AC4, AC5, AC6)
  - [x] Ajouter `client_message_id: str | None = None` à `send_message()` et `send_message_async()`
  - [x] Implémenter la logique d'idempotence avant la création du message utilisateur :
    - Si message user+assistant existants → retour immédiat de la paire en cache
    - Si message user existant sans assistant → réutiliser le message user, relancer LLM
    - Sinon → créer le message user avec `client_message_id`

- [x] **T5 — Router API** (AC2, AC6)
  - [x] Ajouter `client_message_id: str | None = None` à `ChatMessageRequest`
  - [x] Transmettre `client_message_id` à `ChatGuidanceService.send_message()`

- [x] **T6 — Frontend** (AC1)
  - [x] Ajouter `client_message_id?: string` à `SendChatPayload` dans `frontend/src/api/chat.ts`
  - [x] Générer `crypto.randomUUID()` dans `handleSendMessage` de `ChatPage.tsx` et le passer dans le payload

## Dev Notes

### Architecture de l'idempotence

La clé d'idempotence est générée **côté client** (UUID v4 via `crypto.randomUUID()`). Le serveur est responsable de la détection et du retour de la réponse en cache.

Séquence normale (premier envoi) :
```
Frontend → POST /v1/chat/messages { message, client_message_id: "uuid-abc" }
Backend  → create user_message(client_message_id="uuid-abc") → LLM → create assistant_message
         ← { user_message, assistant_message }
```

Séquence idempotente (retry après timeout) :
```
Frontend → POST /v1/chat/messages { message, client_message_id: "uuid-abc" }
Backend  → get_message_by_client_id("uuid-abc") → found!
         → get_next_assistant_message(after=user_msg.id) → found!
         → log "chat_idempotent_hit"
         ← { user_message (cached), assistant_message (cached) }  // pas d'appel LLM
```

### Index partiel : pourquoi WHERE IS NOT NULL

Les lignes sans `client_message_id` (anciennes conversations, ou appels sans clé) ne participent pas à la contrainte d'unicité → pas de collision entre les requêtes legacy et les nouvelles.

### Rétrocompatibilité garantie

`client_message_id` est optionnel à tous les niveaux :
- `ChatMessageRequest.client_message_id: str | None = None`
- `send_message(client_message_id=None)` → branche `else` → comportement identique à avant
- `ChatMessageModel.client_message_id` nullable

### Fichiers modifiés

| Fichier | Type | Action |
|---------|------|---------|
| `backend/migrations/versions/20260306_0029_add_client_message_id_to_chat_messages.py` | Migration | CRÉÉ |
| `backend/app/infra/db/models/chat_message.py` | Modèle | Ajout champ `client_message_id` |
| `backend/app/infra/db/repositories/chat_repository.py` | Repository | Ajout méthodes idempotence |
| `backend/app/services/chat_guidance_service.py` | Service | Logique idempotence |
| `backend/app/api/v1/routers/chat.py` | Router | Ajout champ `ChatMessageRequest` |
| `frontend/src/api/chat.ts` | API types | Ajout `client_message_id` à `SendChatPayload` |
| `frontend/src/pages/ChatPage.tsx` | Page | Génération UUID par envoi |

### Commande de migration

```bash
cd backend && alembic upgrade head
```

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Completion Notes List

- Migration Alembic `20260306_0029` créée avec index unique partiel (compatible PostgreSQL et SQLite).
- `ChatMessageModel` étendu avec `client_message_id: Mapped[str | None]`.
- `ChatRepository` : `create_message()` étendu + 2 nouvelles méthodes (`get_message_by_client_id`, `get_next_assistant_message`).
- `ChatGuidanceService.send_message_async` : logique d'idempotence complète avec gestion race condition.
- `ChatMessageRequest` : champ optionnel `client_message_id` ajouté, transmis au service.
- Frontend : `crypto.randomUUID()` généré par `handleSendMessage`, `SendChatPayload` étendu.
- Réaudit frontend du 2026-03-08: les assertions de `ChatPage.test.tsx` ont été réalignées sur le contrat réel d'idempotence en vérifiant `client_message_id` via `expect.objectContaining(...)` au lieu d'un payload figé.

## Change Log

- 2026-03-08: Validation corrective frontend — contrat `client_message_id` revalidé dans `ChatPage.test.tsx`, sans régression sur l'optimistic update.

### File List

- `backend/migrations/versions/20260306_0029_add_client_message_id_to_chat_messages.py`
- `backend/app/infra/db/models/chat_message.py`
- `backend/app/infra/db/repositories/chat_repository.py`
- `backend/app/services/chat_guidance_service.py`
- `backend/app/api/v1/routers/chat.py`
- `frontend/src/api/chat.ts`
- `frontend/src/pages/ChatPage.tsx`
