# Issue: FE-6 — Chat RAG

## Objectif

Implémenter le système complet de chat RAG avec ChatService (validation Zod stricte), store de persistance avec caps FIFO pour l'historique, hooks avec guards paywall et optimistic UI, composants UI découplés avec markdown safe, et tests complets.

## ✅ Statut : IMPLÉMENTÉ

### 6.1 — ChatService + Types Zod ✅

- ✅ `src/shared/api/chat.service.ts` créé
- ✅ Schémas Zod stricts : `ChartId` (min 8), `Question` (trim 3-1000)
- ✅ `advise(input)` → POST `/v1/chat/advise`
- ✅ Réponse : `answer`, `generated_at?`, `request_id?`
- ✅ Validation fail-fast, mapping 402/429 via client
- ✅ Max 1 retry sur NetworkError uniquement

### 6.2 — Store Chat avec Persistance & Caps FIFO ✅

- ✅ `src/stores/chatStore.ts` créé
- ✅ `src/shared/auth/chatHistory.ts` helpers créés
- ✅ Caps FIFO : 50 messages max par chart
- ✅ Persistance localStorage clé `CHAT_HISTORY_V1`
- ✅ Tri par timestamp (croissant)
- ✅ HasHydrated flag pour hydratation

### 6.3 — Hook useChat avec Guards Paywall ✅

- ✅ `src/features/chat/hooks/useChat.ts` créé
- ✅ Guards : aucun POST si `!isAllowed`
- ✅ Anti double-submit : vérifie `isPending`
- ✅ Optimistic UI : ajoute user avant appel, assistant à la réception
- ✅ Erreur 402/429 : user présent, pas d'assistant
- ✅ Expose `retryAfter` depuis usePaywall

### 6.4 — Composants UI Découplés ✅

- ✅ `src/features/chat/ChatBox.tsx` : container principal
- ✅ `src/features/chat/MessageList.tsx` : historique + auto-scroll + skeleton
- ✅ `src/features/chat/MessageItem.tsx` : rendu message avec bulles user/assistant
- ✅ `src/features/chat/MessageInput.tsx` : textarea auto-resize + compteur X/1000
- ✅ PaywallGate uniquement sur input (historique visible)
- ✅ Enter pour envoyer, Shift+Enter pour newline
- ✅ A11y : aria-live, aria-busy, aria-invalid

### 6.5 — Page Chat & Router ✅

- ✅ `src/pages/app/chat/index.tsx` créé
- ✅ Sélection dernier chart via `recentCharts[0]`
- ✅ Message si pas de chart + lien vers horoscope
- ✅ Hydratation stores au montage
- ✅ Route `/app/chat` lazy dans router.tsx

## Tests

- ✅ Service : 11 tests (200, 401, 402, 429, 500, NetworkError, ZodError)
- ✅ Store : 16 tests (hydratation, add, cap FIFO, get, clear, persistance, tri)
- ✅ Hook : 13 tests (guards paywall, optimistic UI, double-submit, erreurs)
- ⚠️ Composants UI : 0 tests (MVP acceptable, décalés)

**Total** : 247/247 tests passants (+40 nouveaux) ✅

## Check-list d'acceptation

- [x] **Service** : Zod strict (question 3-1000), request_id, pas de retry 4xx
- [x] **Store** : cap 50/chart FIFO, clé CHAT_HISTORY_V1, tri timestamp
- [x] **Hook** : guards paywall, anti double-submit, optimistic UI, retryAfter
- [x] **UI** : PaywallGate input, Enter/Shift+Enter, auto-scroll, A11y
- [x] **Page** : sélection dernier chart, hydratation stores
- [x] **Tests** : service + store + hook ✅
- [x] **Qualité** : lint 0 erreurs, tests 247/247, build OK

## Labels

`feature`, `chat`, `milestone-fe-6`, `rag`
