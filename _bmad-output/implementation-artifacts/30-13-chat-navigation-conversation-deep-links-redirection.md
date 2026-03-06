# Story 30.13: Chat Navigation: ouverture par conversationId + démarrage par personaId (get-or-create) sans doublons

Status: ready-for-dev

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

- [ ] **Routing Refactor** (AC: 1, 3)
  - [ ] Mettre à jour la définition des routes dans `App.tsx` (ou le fichier central de routes) pour supporter `:conversationId`.
  - [ ] Adapter `ChatPage.tsx` pour lire `conversationId` depuis `useParams`.
- [ ] **Redirection Logic** (AC: 2)
  - [ ] Implémenter l'effet de redirection dans `ChatPage.tsx` quand `personaId` est détecté en `searchParams`.
  - [ ] Utiliser `useNavigate` avec `{ replace: true }` pour garder un historique de navigation propre.
- [ ] **Data Fetching & Error Handling** (AC: 4)
  - [ ] Gérer les erreurs 404 lors de la récupération d'une conversation spécifique.
  - [ ] Ajouter des gardes pour les IDs malformés.
- [ ] **Empty Chat State** (AC: 5)
  - [ ] Améliorer `ChatWindow.tsx` pour distinguer "chargement", "erreur", "conversation vide" et "historique chargé".
  - [ ] Afficher les détails du persona même si la liste des messages est vide.

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

gemini-2.0-flash-exp

### Debug Log References

### Completion Notes List

### File List
