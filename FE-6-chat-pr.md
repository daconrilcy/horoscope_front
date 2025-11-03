# PR: FE-6 — Chat RAG Feature

Closes #18

## Description

Implémentation du système complet de chat RAG avec ChatService (validation Zod stricte), store de persistance avec caps FIFO, hooks avec guards paywall et optimistic UI, composants UI découplés, et tests complets.

## Type de changement

- [x] Nouvelle fonctionnalité (feature)
- [ ] Correction de bug (bugfix)
- [ ] Refactoring
- [ ] Documentation

## Checklist

- [x] J'ai vérifié que mon code suit les conventions du projet
- [x] J'ai auto-reviewé mon code
- [x] Mes commentaires sont utiles et clairs
- [x] J'ai documenté les changements complexes si nécessaire
- [x] Mes tests passent localement
- [x] J'ai mis à jour la documentation si nécessaire

## Résumé des changements

### Nouveaux fichiers

1. `src/shared/api/chat.service.ts` - Service chat avec schémas Zod stricts
2. `src/shared/api/chat.service.test.ts` - Tests service (11 tests)
3. `src/shared/auth/chatHistory.ts` - Helpers localStorage pour historique chat
4. `src/stores/chatStore.ts` - Store FIFO, cap 50 messages/chart
5. `src/stores/chatStore.test.ts` - Tests store (16 tests)
6. `src/features/chat/hooks/useChat.ts` - Hook mutation avec guards paywall
7. `src/features/chat/hooks/useChat.test.tsx` - Tests hook (13 tests)
8. `src/features/chat/ChatBox.tsx` - Container chat principal
9. `src/features/chat/MessageList.tsx` - Liste messages + auto-scroll
10. `src/features/chat/MessageItem.tsx` - Rendu message individuel
11. `src/features/chat/MessageInput.tsx` - Input avec textarea auto-resize
12. `src/pages/app/chat/index.tsx` - Page chat avec sélection dernier chart
13. `FE-6-chat-issue.md` - Issue GitHub
14. `FE-6-chat-pr.md` - Description PR

### Fichiers modifiés

1. `src/app/router.tsx` - Ajout route `/app/chat` lazy + Suspense

## Endpoints utilisés

- `POST /v1/chat/advise` - Demande de conseil basée sur thème natal
  - Body : `{ chart_id: string (min 8), question: string (trim, 3-1000) }`
  - Réponse : `{ answer: string, generated_at?: string, request_id?: string }`
  - Headers : JWT Bearer + plan "plus" requis

## Fonctionnalités

### 6.1 — ChatService

- ✅ Schémas Zod stricts : `ChartId` (min 8), `Question` (trim 3-1000)
- ✅ `advise` avec validation fail-fast
- ✅ Mapping 402/429 via client HTTP (événements paywall)
- ✅ Max 1 retry sur NetworkError uniquement

### 6.2 — Store Chat

- ✅ Caps FIFO : 50 messages max par chart
- ✅ Persist localStorage clé `CHAT_HISTORY_V1`
- ✅ Tri par timestamp (croissant)
- ✅ hasHydrated pour hydratation contrôlée

### 6.3 — Hook useChat

- ✅ Guards : aucun POST si `!isAllowed` (toast info)
- ✅ Anti double-submit : vérifie `isPending`
- ✅ Optimistic UI : ajoute message user avant appel
- ✅ Erreur 402/429 : user présent, pas d'assistant
- ✅ Expose `retryAfter` depuis usePaywall

### 6.4 — Composants UI

- ✅ PaywallGate uniquement sur input (historique visible)
- ✅ Enter pour envoyer, Shift+Enter pour newline
- ✅ Textarea auto-resize + compteur X/1000
- ✅ Auto-scroll vers bas à chaque nouveau message
- ✅ Skeleton "Assistant écrit..." pendant loading
- ✅ A11y : aria-live, aria-busy, aria-invalid
- ✅ Bouton effacer historique (confirm)

### 6.5 — Page Chat

- ✅ Sélection dernier chart via `recentCharts[0]`
- ✅ Message si pas de chart + lien horoscope
- ✅ Hydratation stores au montage
- ✅ useTitle pour titre page

## Tests

### Service

- ✅ 11 tests : 200, 401, 402, 429, 500, NetworkError, ZodError (answer manquant/vide, generated_at invalide)

### Store

- ✅ 16 tests : hydratation, add (user/assistant), cap FIFO, get (trié), clear, persistance

### Hook

- ✅ 13 tests : guards paywall (plan/quota), optimistic UI, double-submit, erreurs 402/429/500/NetworkError, messages store

**Total** : 247/247 tests (+40 nouveaux)

## Qualité

- ✅ Lint : 0 erreurs (88 warnings préexistants)
- ✅ Format : Prettier OK
- ✅ Typecheck : OK (erreurs préexistantes dans tests)
- ✅ Build : Vite build OK
- ✅ Pre-commit : OK

## Notes techniques

- Historique persisté par chartId dans localStorage
- Caps FIFO strict : 50 messages max par chart
- Optimistic UI pour feedback immédiat
- Guards paywall empêchent les appels inutiles
- PaywallGate gère automatiquement 402/429 via événements

## Commande pour tester localement

```bash
# Installer les dépendances
npm install

# Lancer les tests
npm run test

# Démarrer le serveur dev
npm run dev
```

## Captures d'écran

À ajouter lors de l'intégration visuelle.

## Labels

`feature`, `chat`, `milestone-fe-6`, `rag`
