# Story 30.13: Chat Navigation: ouverture par conversationId + démarrage par personaId (get-or-create) sans doublons

Status: done

## Senior Developer Review (AI)

- **AC1 (Deep Linking)**: [PASS] Verified in `frontend/src/app/routes.tsx` and `frontend/src/pages/ChatPage.tsx`.
- **AC2 (Redirection by personaId)**: [FIXED] Added `isRedirecting` state with a loading overlay/spinner to prevent "flash of empty state" while API is thinking. Fixed `hasRedirectedByPersona` logic to allow switching between different `personaId`s in the same session without page reload.
- **AC3 (Auto-redirect)**: [PASS] Works as intended when navigating to `/chat` without ID.
- **AC4 (Error Handling)**: [FIXED] Added `console.error` and proper redirection to `/astrologers` when `personaId` is unknown. (Note: Toast skipped as project lacks a toast provider, standard redirection preferred).
- **AC5 (Empty State)**: [FIXED] Added "Démarrer ma première discussion" CTA button in `ChatWindow` empty state that focuses the composer input, making the empty state more actionable.
- **Code Quality**: Improved the robustness of redirection effects by using refs to track the "current" redirection target instead of a simple boolean.

## Story

As an utilisateur,
I want retrouver automatiquement ma discussion existante quand je re-sélectionne un astrologue,
so that je ne crée pas de doublons et je garde mon historique de manière fluide et déterministe.

## Acceptance Criteria

1. **AC1: Support Deep Linking** : L'URL `/chat/:conversationId` est supportée. Si un `conversationId` est présent, le front charge et affiche immédiatement cette conversation dans la fenêtre de chat.
2. **AC2: Redirection Intelligente via personaId** : Si l'URL contient un paramètre `personaId` (ex: `/chat?personaId=luna`), le front :
   - Appelle l'endpoint `POST /v1/chat/conversations/by-persona/{personaId}` (Story 30.11).
   - Redirige automatiquement vers `/chat/{new_conversation_id}`.
   - Assure que l'historique est préservé si la conversation existait déjà (idempotence de l'API).
3. **AC3: Nettoyage de l'état générique** : La navigation vers `/chat` sans ID charge la dernière conversation active par défaut (si elle existe) ou affiche l'empty state, évitant un état "entre-deux".
4. **AC4: Gestion des erreurs de navigation** :
   - Si un `conversationId` est invalide ou 404, afficher un message d'erreur et proposer de retourner à la liste.
   - Si un `personaId` est inconnu, rediriger vers `/astrologers` avec un toast d'erreur.
5. **AC5: État "Nouveau Fil"** : Si une conversation est créée mais n'a pas encore de messages, la fenêtre de chat affiche un état vide accueillant avec le profil de l'astrologue et un CTA pour envoyer le premier message.

## Tasks / Subtasks

- [x] **Routing Refactor** (AC: 1, 3)
  - [x] Mettre à jour la définition des routes dans `App.tsx` (ou le fichier central de routes) pour supporter `:conversationId`.
  - [x] Adapter `ChatPage.tsx` pour lire `conversationId` depuis `useParams`.
- [x] **Redirection Logic** (AC: 2)
  - [x] Implémenter l'effet de redirection dans `ChatPage.tsx` quand `personaId` est détecté en `searchParams`.
  - [x] Utiliser `useNavigate` avec `{ replace: true }` pour garder un historique de navigation propre.
- [x] **Data Fetching & Error Handling** (AC: 4)
  - [x] Gérer les erreurs 404 lors de la récupération d'une conversation spécifique.
  - [x] Ajouter des gardes pour les IDs malformés.
- [x] **Empty Chat State** (AC: 5)
  - [x] Améliorer `ChatWindow.tsx` pour distinguer "chargement", "erreur", "conversation vide" et "historique chargé".
  - [x] Afficher les détails du persona même si la liste des messages est vide.

## Dev Notes

- **Fichiers impactés** :
  - `frontend/src/pages/ChatPage.tsx`
  - `frontend/src/App.tsx` (ou `frontend/src/routes.tsx`)
  - `frontend/src/features/chat/components/ChatWindow.tsx`
- **UX** : La redirection de `?personaId=...` vers `/:conversationId` doit être quasi-instantanée (avec un spinner discret si l'appel réseau est lent).
- **Rétrocompatibilité** : Déprécier l'ancien paramètre `astrologerId` s'il est encore utilisé, au profit de `personaId`.

### Project Structure Notes

- Utiliser `react-router-dom` v6 patterns.
- Garder la logique de redirection dans le composant de page (`ChatPage`).

### References

- [Source: frontend/src/pages/ChatPage.tsx]
- [Source: Story 30.11: Chat API Enrichment]
- [Source: Story 30.12: Chat UI Messenger Identity]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

Aucune erreur bloquante. Les tests `NatalChartPage.test.tsx` et `ChatComponents.test.tsx` qui échouaient étaient des régressions préexistantes (confirmé par git stash avant/après).

### Completion Notes List

- **AC1 (Deep Linking)** : Les routes `/chat` et `/chat/:conversationId` étaient déjà définies dans `routes.tsx`. `ChatPage.tsx` lisait déjà `conversationId` via `useParams`. Confirmé fonctionnel.
- **AC2 (Redirection par personaId)** : Ajout de la lecture de `personaId` depuis `searchParams`. Ajout d'un `useEffect` qui appelle `createConversationByPersona` puis navigue vers `/chat/:id` avec `{replace: true}`. En cas d'erreur API (persona inconnu), redirige vers `/astrologers`.
- **AC3 (Navigation sans ID)** : Ajout d'un `useEffect` qui redirige automatiquement vers la dernière conversation (`conversations[0]`) quand on navigue vers `/chat` sans ID et que des conversations existent.
- **AC4 (Gestion des erreurs)** : Enrichissement de `isInvalidConversationUrl` pour inclure les erreurs 404 de l'API d'historique (`history.error instanceof ChatApiError && history.error.status === 404`). Guard NaN déjà présent.
- **AC5 (Empty Chat State)** : Extraction de `selectedConversationSummary` depuis la liste des conversations. Passage de `personaName` et `personaAvatarUrl` à `ChatWindow`. Dans `ChatWindow`, affichage conditionnel de l'avatar et du nom du persona dans l'état vide.
- **Tests** : 21/21 tests passent dans `ChatPage.test.tsx`. 7 nouveaux tests ajoutés (AC2 ×2, AC3 ×3, AC5 ×1, plus mise à jour du test "navigates to new conversation").

### File List

- `frontend/src/pages/ChatPage.tsx` (modifié)
- `frontend/src/features/chat/components/ChatWindow.tsx` (modifié)
- `frontend/src/tests/ChatPage.test.tsx` (modifié)
- `frontend/src/App.css` (modifié)

## Change Log

- 2026-03-06: Implémentation story 30-13 — navigation chat par conversationId et redirection par personaId (claude-sonnet-4-6)
