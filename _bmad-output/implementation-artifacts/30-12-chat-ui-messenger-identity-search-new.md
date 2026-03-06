# Story 30.12: Chat UI Messenger: Liste conversations (identité), recherche, bouton Nouvelle discussion, empty state

Status: ready-for-dev

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

- [ ] **UI Components Evolution** (AC: 1, 2)
  - [ ] Mettre à jour `ConversationItem.tsx` pour inclure l'avatar et le nom du persona.
  - [ ] Améliorer le style CSS/Tailwind de `ConversationItem` (typographie, espacement).
  - [ ] Modifier la logique de filtrage dans `ConversationList.tsx` pour inclure le nom de l'astrologue.
- [ ] **New Discussion Flow** (AC: 3)
  - [ ] Créer un composant `AstrologerPickerModal` (ou réutiliser un composant de catalogue).
  - [ ] Ajouter le bouton de création dans le header de `ConversationList`.
  - [ ] Implémenter le hook/mutation pour appeler `POST /v1/chat/conversations/by-persona/{persona_id}`.
- [ ] **Experience & States** (AC: 4, 6)
  - [ ] Créer un composant `ChatEmptyState` visuellement riche (icône, texte, CTA).
  - [ ] Implémenter des Skeletons pour `ConversationItem` pendant le chargement initial.
- [ ] **Navigation & Integration** (AC: 5)
  - [ ] Assurer la synchronisation entre la création d'une nouvelle conversation et la sélection dans `ChatPage`.
  - [ ] Vérifier le comportement responsive (mobile drawer si applicable).

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

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

### Completion Notes List

### File List
