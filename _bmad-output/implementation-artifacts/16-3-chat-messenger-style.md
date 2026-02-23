# Story 16.3: Chat Messenger-Style — Layout 3 colonnes

Status: done

## Story

As a utilisateur du chat astrologue,
I want une interface de chat style messenger avec liste de conversations, fenêtre de chat et détails astrologue,
So that je puisse naviguer facilement entre mes conversations et voir le contexte.

## Contexte

Le `ChatPage` actuel mélange tout : guidance, modules tarot/runes, historique, et chat dans une seule colonne. Cette story refactorise le chat en layout 3 colonnes moderne (type Messenger/WhatsApp Web) :
- Colonne gauche : liste des conversations
- Colonne centrale : fenêtre de chat avec messages et composer
- Colonne droite : panneau détail astrologue/contexte

## Scope

### In-Scope
- Layout 3 colonnes responsive (1 colonne sur mobile)
- Liste des conversations avec search/filtre
- Fenêtre chat avec messages et composer
- Panneau détail astrologue
- Deep link `/chat/:conversationId`
- Auto-scroll intelligent
- État "assistant typing"
- Empty state avec CTA "Choisir un astrologue"

### Out-of-Scope
- Guidance quotidienne/hebdomadaire (reste accessible ailleurs)
- Modules tarot/runes (story séparée ou section consultations)
- Streaming SSE (amélioration future)
- Notifications temps réel

## Acceptance Criteria

### AC1: Layout 3 colonnes desktop
**Given** un utilisateur sur desktop à `/chat`
**When** la page se charge
**Then** il voit 3 colonnes : conversations | chat | détail astrologue

### AC2: Layout 1 colonne mobile
**Given** un utilisateur sur mobile à `/chat`
**When** la page se charge
**Then** il voit la liste des conversations
**And** cliquer sur une conversation affiche le chat
**And** un bouton retour permet de revenir à la liste

### AC3: Sélection conversation
**Given** la liste des conversations affichée
**When** l'utilisateur clique sur une conversation
**Then** les messages se chargent dans la colonne centrale
**And** l'URL change vers `/chat/:conversationId`

### AC4: Envoi de message
**Given** une conversation ouverte
**When** l'utilisateur tape un message et envoie
**Then** le message apparaît immédiatement (optimistic)
**And** un état "en attente de réponse" est affiché
**And** la réponse de l'astrologue apparaît à réception

### AC5: Auto-scroll
**Given** une conversation avec historique
**When** un nouveau message arrive
**Then** le chat scroll automatiquement vers le bas
**Unless** l'utilisateur a scrollé manuellement vers le haut

### AC6: Empty state
**Given** un utilisateur sans conversation
**When** il accède à `/chat`
**Then** il voit "Aucune conversation" avec CTA "Choisir un astrologue"

### AC7: Deep link
**Given** un lien direct `/chat/123`
**When** l'utilisateur l'ouvre
**Then** la conversation 123 est sélectionnée et affichée

## Tasks

- [x] Task 1: Créer composants chat (AC: #1, #4, #5)
  - [x] 1.1 Créer `src/features/chat/components/ConversationList.tsx`
  - [x] 1.2 Créer `src/features/chat/components/ConversationItem.tsx`
  - [x] 1.3 Créer `src/features/chat/components/ChatWindow.tsx`
  - [x] 1.4 Créer `src/features/chat/components/MessageBubble.tsx`
  - [x] 1.5 Créer `src/features/chat/components/ChatComposer.tsx`
  - [x] 1.6 Créer `src/features/chat/components/AstrologerDetailPanel.tsx`
  - [x] 1.7 Créer `src/features/chat/components/TypingIndicator.tsx`

- [x] Task 2: Layout et responsive (AC: #1, #2)
  - [x] 2.1 Créer `src/features/chat/components/ChatLayout.tsx`
  - [x] 2.2 Implémenter grid 3 colonnes desktop
  - [x] 2.3 Implémenter navigation mobile (list ↔ chat)
  - [x] 2.4 Créer hook `useIsMobile()` si non existant

- [x] Task 3: Refactorer ChatPage (AC: #3, #6, #7)
  - [x] 3.1 Simplifier `ChatPage.tsx` pour utiliser ChatLayout
  - [x] 3.2 Retirer guidance/modules du ChatPage (hors scope de cette story, seront dans une page dédiée)
  - [x] 3.3 Ajouter route `/chat/:conversationId`
  - [x] 3.4 Implémenter empty state

- [x] Task 4: Auto-scroll et UX (AC: #4, #5)
  - [x] 4.1 Créer hook `useAutoScroll()`
  - [x] 4.2 Détecter scroll manuel utilisateur
  - [x] 4.3 Implémenter optimistic update sur envoi

- [x] Task 5: Tests (AC: tous)
  - [x] 5.1 Test rendu liste conversations
  - [x] 5.2 Test sélection conversation
  - [x] 5.3 Test envoi message (mock API)
  - [x] 5.4 Test empty state
  - [x] 5.5 Test deep link

## Dev Notes

### Structure de fichiers

```
frontend/src/features/chat/
├── components/
│   ├── ChatLayout.tsx
│   ├── ConversationList.tsx
│   ├── ConversationItem.tsx
│   ├── ChatWindow.tsx
│   ├── MessageBubble.tsx
│   ├── ChatComposer.tsx
│   ├── AstrologerDetailPanel.tsx
│   └── TypingIndicator.tsx
├── hooks/
│   ├── useAutoScroll.ts
│   └── useIsMobile.ts
└── index.ts
```

### Layout CSS (BEM classes)

```tsx
// ChatLayout.tsx - Desktop (CSS vanilla avec classes BEM)
<div className="chat-layout chat-layout--desktop">
  <div className="chat-layout-panel chat-layout-panel--left">{leftPanel}</div>
  <div className="chat-layout-panel chat-layout-panel--center">{centerPanel}</div>
  <div className="chat-layout-panel chat-layout-panel--right">{rightPanel}</div>
</div>

// Mobile - afficher une seule section à la fois
const [mobileView, setMobileView] = useState<"list" | "chat">("list")
```

### useAutoScroll hook

```typescript
function useAutoScroll(containerRef: RefObject<HTMLElement>, triggerValue: unknown) {
  const [userScrolled, setUserScrolled] = useState(false)
  const prevTriggerRef = useRef(triggerValue)

  useEffect(() => {
    if (prevTriggerRef.current !== triggerValue) {
      prevTriggerRef.current = triggerValue
      if (!userScrolled && containerRef.current) {
        containerRef.current.scrollTop = containerRef.current.scrollHeight
      }
    }
  }, [containerRef, userScrolled, triggerValue])
  
  const handleScroll = useCallback(() => {
    const el = containerRef.current
    if (el) {
      const isAtBottom = el.scrollHeight - el.scrollTop <= el.clientHeight + SCROLL_TOLERANCE_PX
      setUserScrolled(!isAtBottom)
    }
  }, [containerRef])
  
  return { handleScroll, resetScroll: useCallback(() => setUserScrolled(false), []) }
}
```

### APIs existantes à réutiliser

- `useChatConversations()` → liste conversations
- `useChatConversationHistory(id)` → messages d'une conversation
- `useSendChatMessage()` → envoi message

### Breakpoint mobile

```typescript
const MOBILE_BREAKPOINT = 768
const DEBOUNCE_MS = 150

function useIsMobile() {
  const [isMobile, setIsMobile] = useState(
    typeof window !== "undefined" ? window.innerWidth < MOBILE_BREAKPOINT : false
  )
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const handleResize = useCallback(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    timeoutRef.current = setTimeout(() => {
      setIsMobile(window.innerWidth < MOBILE_BREAKPOINT)
    }, DEBOUNCE_MS)
  }, [])

  useEffect(() => {
    window.addEventListener("resize", handleResize)
    return () => {
      window.removeEventListener("resize", handleResize)
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [handleResize])

  return isMobile
}
```

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5

### Debug Log References
Aucun problème majeur rencontré.

### Completion Notes List
- Créé une nouvelle architecture de composants chat dans `frontend/src/features/chat/`
- Implémenté layout 3 colonnes responsive avec grid CSS (pas Tailwind car le projet utilise CSS vanilla)
- ChatPage refactorisé pour utiliser les nouveaux composants modulaires
- Guidance/modules tarot/runes retirés de ChatPage (hors scope, story séparée)
- Auto-scroll intelligent avec détection du scroll manuel utilisateur
- Optimistic update sur envoi de message
- Empty state avec CTA vers page astrologers
- Deep link `/chat/:conversationId` fonctionnel
- Navigation mobile avec vue liste/chat
- Tous les tests passent (297 tests, 0 échec)
- Lint TypeScript OK

### File List

**Nouveaux fichiers:**
- frontend/src/features/chat/components/ChatLayout.tsx
- frontend/src/features/chat/components/ConversationList.tsx
- frontend/src/features/chat/components/ConversationItem.tsx
- frontend/src/features/chat/components/ChatWindow.tsx
- frontend/src/features/chat/components/MessageBubble.tsx
- frontend/src/features/chat/components/ChatComposer.tsx
- frontend/src/features/chat/components/AstrologerDetailPanel.tsx
- frontend/src/features/chat/components/TypingIndicator.tsx
- frontend/src/features/chat/hooks/useAutoScroll.ts
- frontend/src/features/chat/hooks/useIsMobile.ts
- frontend/src/features/chat/index.ts
- frontend/src/tests/chat/ChatComponents.test.tsx

**Fichiers modifiés:**
- frontend/src/pages/ChatPage.tsx (refactorisé pour utiliser les nouveaux composants)
- frontend/src/app/routes.tsx (ajout route /chat/:conversationId)
- frontend/src/App.css (ajout styles chat layout 3 colonnes)
- frontend/src/tests/ChatPage.test.tsx (mis à jour pour nouvelle structure)
- frontend/src/tests/router.test.tsx (mis à jour pour nouvelle structure)
- _bmad-output/implementation-artifacts/sprint-status.yaml (status in-progress → review)

## Change Log

- 2026-02-22: Implémentation complète du chat messenger-style avec layout 3 colonnes, composants modulaires, auto-scroll intelligent, et tests
- 2026-02-22: Code review fixes (round 1):
  - Fix: URL parsing sécurisé (NaN handling) dans ChatPage.tsx
  - Fix: useAutoScroll refactorisé pour éviter l'anti-pattern spread deps
  - Fix: useIsMobile avec debounce sur resize (150ms)
  - Fix: HTML valide - Link stylisé au lieu de button imbriqué
  - Fix: Accessibilité emoji avec role="img" et aria-label
  - Fix: Dev Notes corrigés (useChatNavigation.ts → useIsMobile.ts)
  - Ajout: Tests unitaires pour ChatLayout et ChatWindow
- 2026-02-22: Code review fixes (round 2):
  - Fix: Dev Notes mis à jour avec la signature actuelle de useAutoScroll
  - Fix: Constante SCROLL_TOLERANCE_PX au lieu de magic number 50
  - Fix: Gestion des URLs de conversation invalides (404 gracieux)
  - Fix: aria-label ajouté sur le bouton "Reprendre la conversation"
- 2026-02-22: Code review fixes (round 3):
  - Fix: Test ajouté pour la gestion des URLs de conversation invalides
  - Fix: ChatLayout reçoit isMobile en prop (évite double appel useIsMobile)
  - Fix: Dev Notes useIsMobile mis à jour avec version debounced
- 2026-02-22: Code review fixes (round 4):
  - Fix: Dev Notes corrigés - Layout CSS utilise BEM classes (pas Tailwind)
  - Fix: Accessibilité emojis dans ChatPage (empty states) avec role="img" et aria-label
  - Ajout: Tests unitaires pour useIsMobile hook (3 tests: initial values, resize debounce)
- 2026-02-22: Code review fixes (round 5):
  - Fix: Dev Notes useAutoScroll - constante SCROLL_TOLERANCE_PX au lieu de magic number
  - Fix: useAutoScroll - suppression de userScrolled non utilisé du retour
  - Fix: ConversationItem - aria-current="page" au lieu de "true" (meilleure sémantique)
- 2026-02-23: Code review fixes (round 6):
  - Fix: H1 i18n - ConversationList, ConversationItem, MessageBubble, TypingIndicator utilisent maintenant detectLang() + t() (plus de strings French hardcodées)
  - Fix: H1 i18n - 8 clés ajoutées dans astrologers.ts (conversations_title, conversations_search, conversations_error, conversations_no_results, conversation_new, message_you, message_astrologer, typing_label)
  - Fix: H1 i18n - MessageBubble et TypingIndicator utilisent LOCALE_MAP pour la localisation des dates
  - Fix: H2 accessibilité - aria-live="polite" ajouté sur .chat-window-messages dans ChatWindow
  - Fix: H3 ARIA - ConversationItem corrigé aria-current="page" → aria-pressed={isActive}
  - Fix: M1 tests - describe("useAutoScroll") ajouté dans ChatComponents.test.tsx (3 tests)
  - Fix: M2 hooks - containerRef retiré des tableaux de dépendances dans useAutoScroll (useEffect + useCallback)
  - Fix: L1 imports - deux imports react-router-dom fusionnés en un dans ChatPage.tsx
  - Fix: Test corrigé aria-current="page" → aria-pressed="true" dans ChatComponents.test.tsx
