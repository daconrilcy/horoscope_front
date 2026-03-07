# Story 30.18: Chat — UX header astrologue, layout élargi, suppression markdown

Status: done

## Story

As a utilisateur du chat,
I want que l'interface de conversation soit plus lisible et mieux organisée,
so that je vois clairement avec quel astrologue je parle, je peux démarrer un nouveau chat depuis la fenêtre de conversation, les messages s'affichent sans caractères de formatage parasites, et la conversation démarre naturellement avec un message d'accueil.

## Problèmes résolus

1. **Panneau droit inutile** : la colonne droite affichait le profil de l'astrologue de façon statique et consommait 280px de largeur, réduisant inutilement la zone de lecture des messages.
2. **Absence d'identité visible** : une fois dans une conversation, aucun indicateur ne montrait avec quel astrologue l'utilisateur était en train de discuter (la liste de gauche était la seule référence).
3. **Bouton "nouveau chat" inaccessible depuis la conversation** : le bouton `+` n'était disponible que dans le panneau gauche, invisible une fois en vue mobile ou quand l'attention est sur la conversation.
4. **Asterisques et marqueurs markdown dans les messages** : le LLM produisait parfois `**texte**`, `*italique*` ou `### Titre` qui s'affichaient tels quels dans les bulles de message.
5. **Absence de message d'ouverture** : la conversation démarrait sur un écran vide, forçant l'utilisateur à prendre l'initiative sans signal de l'astrologue.

## Acceptance Criteria

1. [x] **AC1 — Layout 2 colonnes** : Le layout desktop passe de `280px 1fr 280px` à `280px 1fr`. Le panneau droit (`AstrologerDetailPanel`) est supprimé. La zone de messages occupe tout l'espace restant.
2. [x] **AC2 — Chip astrologue dans le header** : Le header de `ChatWindow` affiche en permanence un chip avec l'avatar (ou ✨ fallback) et le nom de l'astrologue actif.
3. [x] **AC3 — Hover card profil** : Au survol du chip, une card en superposition affiche la bio courte et les spécialités de l'astrologue (données issues de la liste `useAstrologers`).
4. [x] **AC4 — Bouton "Nouveau chat" dans le header** : Un bouton `+` (icône Lucide `Plus`) est présent à droite du header de `ChatWindow` et ouvre l'`AstrologerPickerModal` (get-or-create idempotent).
5. [x] **AC5 — Strip markdown** : Les messages `assistant` sont nettoyés avant affichage : `**gras**` → `gras`, `*italique*` → `italique`, `### Titre` → `Titre`. Les messages `user` ne sont pas modifiés.
6. [x] **AC6 — Message d'ouverture** : Quand la conversation est vide (aucun message en DB), une bulle assistant synthétique affiche "Bonjour, que puis-je faire pour vous ?" (i18n fr/en/es). Ce message est purement frontend — pas stocké en DB, pas d'appel LLM.

## Tasks / Subtasks

- [x] **T1 — Layout** (AC1)
  - [x] Modifier `ChatLayout.tsx` : supprimer prop `rightPanel` et div correspondante
  - [x] Modifier `App.css` : `grid-template-columns: 280px 1fr 280px` → `280px 1fr` (desktop + 1024px breakpoint)
  - [x] Modifier `ChatPage.tsx` : supprimer `rightPanel`, `useAstrologer`, `selectedAstrologer`

- [x] **T2 — Chip astrologue + hover card** (AC2, AC3)
  - [x] Modifier `ChatWindow.tsx` : ajouter props `personaBio?`, `personaSpecialties?`, `onNewConversation?`
  - [x] Restructurer le header : toujours rendu, contient chip + bouton `+`
  - [x] Ajouter styles CSS : `.astrologer-chip`, `.astrologer-chip-avatar`, `.astrologer-chip-fallback`, `.astrologer-chip-name`, `.astrologer-chip-card`, `.astrologer-chip-card-bio`, `.astrologer-chip-card-specialties`
  - [x] Hover card : `visibility/opacity` CSS (transition douce, `position: absolute`, `z-index: 100`)

- [x] **T3 — Bouton nouveau chat** (AC4)
  - [x] Modifier `ChatWindow.tsx` : ajouter bouton `.chat-window-new-btn` avec `Plus` icon
  - [x] Ajouter styles CSS : `.chat-window-new-btn`
  - [x] Modifier `ChatPage.tsx` : passer `onNewConversation={() => setShowAstrologerPicker(true)}`

- [x] **T4 — Strip markdown** (AC5)
  - [x] Ajouter `stripMarkdown()` dans `MessageBubble.tsx`
  - [x] Appliquer sur `content` uniquement pour `role === "assistant"`

- [x] **T6 — Message d'ouverture** (AC6)
  - [x] Ajouter `chat_opening_message` dans `frontend/src/i18n/astrologers.ts` (fr/en/es)
  - [x] Modifier `ChatWindow.tsx` : quand `isEmpty && !isTyping`, afficher `<MessageBubble role="assistant" content={t("chat_opening_message", lang)} />` à la place de l'ancien état vide

- [x] **T5 — Wiring données** (AC2, AC3)
  - [x] Modifier `ChatPage.tsx` : `currentAstrologer = astrologers.data?.find(a => a.name === selectedConversationSummary?.persona_name)`
  - [x] Passer `personaBio={currentAstrologer?.bio_short}` et `personaSpecialties={currentAstrologer?.specialties}` à `ChatWindow`

## Dev Notes

### Chip astrologue — données

La correspondance astrologue → bio/spécialités se fait par `name` :
```tsx
const currentAstrologer = astrologers.data?.find(
  (a) => a.name === selectedConversationSummary?.persona_name
)
```
`ChatConversationSummary` ne contient pas de `persona_id`, donc le matching par nom est le seul moyen sans appel API supplémentaire. Si deux astrologues portaient le même nom, le premier match serait retourné (acceptable).

### Hover card — CSS pure (no JS)

Utilise `:hover` / `:focus-within` + `visibility/opacity` pour une transition douce sans état React :
```css
.astrologer-chip-card {
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.15s, visibility 0.15s;
}
.astrologer-chip:hover .astrologer-chip-card,
.astrologer-chip:focus-within .astrologer-chip-card {
  visibility: visible;
  opacity: 1;
}
```

### stripMarkdown — patterns couverts

```ts
function stripMarkdown(text: string): string {
  return text
    .replace(/\*{1,3}([^*\n]+)\*{1,3}/g, "$1")  // *x*, **x**, ***x***
    .replace(/_{1,3}([^_\n]+)_{1,3}/g, "$1")      // _x_, __x__, ___x___
    .replace(/^#{1,6}\s+/gm, "")                   // ### heading
}
```
Les backticks et blocs de code ne sont pas traités (non nécessaires pour le cas d'usage chat astrologue).

### Bouton "Nouvelle discussion" — style final

Itération nécessaire : l'icône seule avec `background: transparent` ou `var(--glass)` était invisible en dark mode car `--glass = rgba(255,255,255,0.08)` se fond dans le panneau. Solution finale : pill avec fond primaire teinté + label texte + bordure primaire.

```css
.chat-window-new-btn {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  border: 1px solid var(--primary);
  background: rgba(102, 230, 255, 0.12);
  color: var(--primary);
  font-size: 0.8rem;
  font-weight: 600;
}
```
Le bouton affiche `<Plus size={14} /> {t("new_conversation", lang)}` — icon + label texte — pour une visibilité maximale quel que soit le thème.

### Fichiers modifiés

| Fichier | Type | Action |
|---------|------|--------|
| `frontend/src/features/chat/components/ChatLayout.tsx` | Composant | Suppression `rightPanel` |
| `frontend/src/features/chat/components/ChatWindow.tsx` | Composant | Header permanent, chip, bouton pill "Nouvelle discussion" |
| `frontend/src/features/chat/components/MessageBubble.tsx` | Composant | `stripMarkdown` sur messages assistant |
| `frontend/src/pages/ChatPage.tsx` | Page | Wiring nouvelles props, suppression `useAstrologer` |
| `frontend/src/App.css` | Styles | Grid 2 cols, styles chip, hover card, bouton pill primaire |

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Completion Notes List

- `ChatLayout` : prop `rightPanel` supprimée, div droite retirée du JSX.
- `App.css` : grid `280px 1fr` (desktop + breakpoint 1024px), styles `.astrologer-chip*` et `.chat-window-new-btn` ajoutés.
- `ChatWindow` : header toujours rendu (non conditionnel), chip astrologue avec hover card CSS, bouton `+` à droite.
- `MessageBubble` : `stripMarkdown()` appliqué sur messages `assistant` uniquement.
- `ChatPage` : `useAstrologer` / `selectedAstrologer` retirés, `currentAstrologer` déduit par matching `persona_name` dans `astrologers.data`, props `personaBio`, `personaSpecialties`, `onNewConversation` passées à `ChatWindow`.
- `ChatWindow` : état vide remplacé par une bulle `MessageBubble role="assistant"` avec `chat_opening_message` (synthétique, frontend uniquement).
- `i18n/astrologers.ts` : clé `chat_opening_message` ajoutée (fr/en/es).

### File List

- `frontend/src/features/chat/components/ChatLayout.tsx`
- `frontend/src/features/chat/components/ChatWindow.tsx`
- `frontend/src/features/chat/components/MessageBubble.tsx`
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/App.css`
- `frontend/src/i18n/astrologers.ts`
