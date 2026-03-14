# Story 56.2: Créer le composant ErrorState unifié (icône + message + bouton retry)

Status: done

## Story

En tant que développeur frontend,
je veux un composant `<ErrorState>` unifié pour afficher les erreurs API dans les pages,
afin de remplacer les affichages d'erreur hétérogènes (`<span className="chat-error">`, messages inline, etc.) par une UI cohérente.

## Acceptance Criteria

1. Le composant `ErrorState` accepte les props : `title` (optionnel), `message` (requis), `onRetry` (optionnel).
2. Il affiche une icône d'erreur (Lucide `AlertCircle` ou similaire), un titre, un message, et un bouton "Réessayer" si `onRetry` est fourni.
3. Il utilise les tokens CSS du système de design pour les couleurs, espacements, etc.
4. Il est exporté depuis `frontend/src/components/ui/ErrorState/`.
5. Les tests existants passent sans modification.

## Tasks / Subtasks

- [x] Tâche 1 : Analyser le pattern `EmptyState` existant (AC: 4)
  - [x] Création du dossier `frontend/src/components/ui/ErrorState/`.

- [x] Tâche 2 : Créer `ErrorState.tsx` (AC: 1, 2, 3)
  - [x] Implémentation du composant avec `AlertCircle` et le composant `Button` existant.
  - [x] Support des props `title`, `message`, `onRetry`.

- [x] Tâche 3 : Créer `ErrorState.css` (AC: 3)
  - [x] Style centré utilisant les variables de design (`--color-text-headline`, `--error`, etc.).

- [x] Tâche 4 : Créer `index.ts` et exporter (AC: 4)
  - [x] Ajout de l'export dans `frontend/src/components/ui/index.ts`.

- [x] Tâche 5 : Validation (AC: 5)
  - [x] `npm run test` — 1079 tests réussis.

## Dev Notes

### Cohérence Visuelle

Le composant `ErrorState` a été conçu pour être visuellement cohérent avec `EmptyState`, en utilisant une structure similaire (icône en haut, titre, description, action). Il centralise les styles d'erreur qui étaient auparavant dispersés.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Création du composant UI `ErrorState`.
- Export via le barrel `@ui`.
- Utilisation du composant `Button` interne pour l'action de retry.
- Validation via 1079 tests réussis.

### File List
- `frontend/src/components/ui/ErrorState/ErrorState.tsx`
- `frontend/src/components/ui/ErrorState/ErrorState.css`
- `frontend/src/components/ui/ErrorState/index.ts`
- `frontend/src/components/ui/index.ts`
