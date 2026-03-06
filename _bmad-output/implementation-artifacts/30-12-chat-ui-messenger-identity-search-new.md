# Story 30.12: Chat UI Messenger: Liste conversations (identité), recherche, bouton Nouvelle discussion, empty state

Status: done

## Story

As an utilisateur,
I want une liste de discussions claire et actionnable,
so that je retrouve instantanément la bonne conversation et je peux en démarrer une nouvelle avec l'astrologue de mon choix.

## Acceptance Criteria

1. **AC1: Identité des conversations** : Chaque item de la liste (`ConversationItem`) affiche désormais :
   - L'avatar de l'astrologue (ou un placeholder généré si absent).
   - Le nom de l'astrologue (`persona_name`).
   - L'aperçu du dernier message (`last_message_preview`).
   - La date relative ou absolue du dernier message (`last_message_at`).
2. **AC2: Recherche performante** : La barre de recherche dans `ConversationList` filtre en temps réel sur le `persona_name`.
3. **AC3: Flux "Nouvelle discussion"** :
   - Un bouton "Nouvelle discussion" (ou icône "+" stylisée) est présent en haut de la liste.
   - Son clic ouvre une modal (ou un volet) listant les astrologues disponibles (via `useAstrologers`).
   - Sélectionner un astrologue appelle l'endpoint de création (Story 30.11) et redirige vers la conversation.
4. **AC4: Empty State engageant** : Si aucune conversation n'existe :
   - Un message d'accueil bienveillant est affiché à la place de la liste.
   - Un bouton d'action principal (CTA) "Démarrer ma première discussion" est mis en évidence.
5. **AC5: Intégrité du Layout** : Les changements respectent le layout 3 colonnes (Story 16.3) et assurent une bonne lisibilité sur mobile (liste escamotable ou prioritaire).
6. **AC6: Skeletons & Loading** : Affichage de Skeletons (ou d'un état de chargement propre) pendant la récupération de la liste.

## Tasks / Subtasks

- [x] **UI Components Evolution** (AC: 1, 2)
  - [x] Mettre à jour `ConversationItem.tsx` pour inclure l'avatar et le nom du persona.
  - [x] Améliorer le style CSS/Tailwind de `ConversationItem` (typographie, espacement).
  - [x] Modifier la logique de filtrage dans `ConversationList.tsx` pour inclure le nom de l'astrologue.
- [x] **New Discussion Flow** (AC: 3)
  - [x] Créer un composant `AstrologerPickerModal` (ou réutiliser un composant de catalogue).
  - [x] Ajouter le bouton de création dans le header de `ConversationList`.
  - [x] Implémenter le hook/mutation pour appeler `POST /v1/chat/conversations/by-persona/{persona_id}`.
- [x] **Experience & States** (AC: 4, 6)
  - [x] Créer un composant `ChatEmptyState` visuellement riche (icône, texte, CTA).
  - [x] Implémenter des Skeletons pour `ConversationItem` pendant le chargement initial.
- [x] **Navigation & Integration** (AC: 5)
  - [x] Assurer la synchronisation entre la création d'une nouvelle conversation et la sélection dans `ChatPage`.
  - [x] Vérifier le comportement responsive (mobile drawer si applicable).

## Dev Notes

- **Fichiers impactés** :
  - `frontend/src/features/chat/components/ConversationList.tsx`
  - `frontend/src/features/chat/components/ConversationItem.tsx`
  - `frontend/src/pages/ChatPage.tsx`
- **Identity Assets** : Si `avatar_url` est une URL relative, s'assurer de la résolution correcte. Sinon, utiliser un fallback (ex: `https://ui-avatars.com/api/?name={name}`).
- **Concurrence** : Gérer le cas où l'utilisateur clique plusieurs fois sur "Créer" (l'API 30.11 est idempotente, mais l'UI doit gérer l'état de chargement).

### Project Structure Notes

- Respecter les conventions de design existantes (Glassmorphism, Tokens Lucide).
- Utiliser `lucide-react` pour les icônes (Plus, Search, MessageCircle).

### References

- [Source: frontend/src/features/chat/components/ConversationList.tsx]
- [Source: frontend/src/features/chat/components/ConversationItem.tsx]
- [Source: Story 30.11: Chat API Enrichment]

## Senior Developer Review (AI)

**🔥 CODE REVIEW FINDINGS!**

**Story:** 30-12-chat-ui-messenger-identity-search-new.md
**Git vs Story Discrepancies:** 0 found
**Issues Found:** 1 High, 2 Medium, 2 Low

### 🔴 HIGH ISSUES
- **UX/Layout Break (FIXED)**: In `ChatPage.tsx`, the global empty state was replacing the entire page content, bypassing `ChatLayout` and breaking visual consistency. Fixed by rendering `ChatEmptyState` within the `ChatLayout` center panel.

### 🟡 MEDIUM ISSUES
- **Fragile DOM Selection (FIXED)**: `ConversationItem.tsx` was using `nextElementSibling` for avatar fallback, which is fragile. Fixed by implementing a robust React state (`imageError`).
- **Hardcoded String (FIXED)**: `ChatLayout.tsx` contained a hardcoded "Reprendre la conversation" button for mobile. Fixed by adding i18n key `chat_resume_conversation`.

### 🟢 LOW ISSUES
- **Inconsistent Search State (FIXED)**: Added a container class `.conversation-list-empty-wrap` for search results empty state to ensure better alignment/styling.
- **Date Robustness (FIXED)**: Added validation for `dateSource` in `ConversationItem.tsx` to prevent "Invalid Date" display.

**Outcome:** Approved (with automatic fixes applied)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

Aucun blocage rencontré. Build TypeScript et Vite réussis du premier coup.

### Completion Notes List

- **`ChatConversationSummary`** : Étendu avec `persona_name?`, `avatar_url?`, `last_message_at?` pour consommer les champs enrichis de l'API 30.11.
- **`createConversationByPersona` + `useCreateConversationByPersona`** : Ajouté dans `chat.ts` — appelle `POST /v1/chat/conversations/by-persona/{persona_id}`, retourne `CreateConversationByPersonaResponse`.
- **`ConversationItem.tsx`** : Refactored avec layout flex (avatar 40px + body). Avatar avec fallback dicebear (`bottts/svg?seed={name}`) et fallback initiale si l'image échoue. Date prioritaire sur `last_message_at` vs `updated_at`.
- **`ConversationItemSkeleton`** : Composant skeleton animé (shimmer) pour l'état de chargement (3 squelettes affichés).
- **`ConversationList.tsx`** : Filtrage étendu sur `persona_name` + `last_message_preview`. Bouton "+" (lucide `Plus`) dans la barre de titre. Props `onNewConversation` ajouté. Skeletons pendant `isLoading`.
- **`AstrologerPickerModal.tsx`** : Modal glassmorphism avec liste d'astrologues (avatar + nom + bio_short), Escape/click-overlay pour fermer, état `isCreating` désactive les boutons.
- **`ChatEmptyState.tsx`** : Empty state visuel avec icône `MessageCircle` dans un cercle glassmorphism, titre bienveillant, description, bouton CTA principal.
- **`ChatPage.tsx`** : Intègre `useAstrologers`, `useCreateConversationByPersona`, `showAstrologerPicker` state. Empty state global remplacé par `ChatEmptyState` + modal. Bouton "+" dans `ConversationList` ouvre le même modal.
- **i18n** : 5 nouvelles clés ajoutées (`new_conversation`, `chat_empty_state_title`, `chat_empty_state_description`, `chat_empty_state_cta`, `close`) en FR/EN/ES.
- **CSS** : Refactored styles `conversation-item` (flex avec avatar), ajout `.conversation-list-title-row`, `.conversation-list-new-btn`, `.conversation-item-avatar*`, `.conversation-item-body`, `.skeleton-*`, `.chat-empty-state-icon-wrap`, `.astrologer-picker-*`.
- **Exports** : `features/chat/index.ts` mis à jour avec `ConversationItemSkeleton`, `AstrologerPickerModal`, `ChatEmptyState`.

### File List

- `frontend/src/api/chat.ts`
- `frontend/src/features/chat/components/ConversationItem.tsx`
- `frontend/src/features/chat/components/ConversationList.tsx`
- `frontend/src/features/chat/components/AstrologerPickerModal.tsx`
- `frontend/src/features/chat/components/ChatEmptyState.tsx`
- `frontend/src/features/chat/index.ts`
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/i18n/astrologers.ts`
- `frontend/src/App.css`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/30-12-chat-ui-messenger-identity-search-new.md`

## Change Log

- 2026-03-06: Implémentation complète story 30-12 — liste enrichie avec avatar/persona_name, recherche sur persona_name, bouton "+" + AstrologerPickerModal, ChatEmptyState visuel, skeletons, CSS glassmorphism, 5 clés i18n.
