# Story 56.2: Créer le composant ErrorState unifié (icône + message + bouton retry)

Status: ready-for-dev

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

- [ ] Tâche 1 : Analyser le pattern `EmptyState` existant (AC: 4)
  - [ ] Lire `frontend/src/components/ui/EmptyState/EmptyState.tsx`
  - [ ] Reproduire la structure de fichiers : `ErrorState/ErrorState.tsx` + `ErrorState.css` + `index.ts`

- [ ] Tâche 2 : Créer `ErrorState.tsx` (AC: 1, 2, 3)
  - [ ] Props : `title?: string`, `message: string`, `onRetry?: () => void`
  - [ ] Icône : `AlertCircle` de `lucide-react`
  - [ ] Couleurs : `var(--danger)` pour l'icône, `var(--color-text-primary)` pour le texte
  - [ ] Bouton retry : utiliser le composant `Button` de l'Epic 50 si disponible

- [ ] Tâche 3 : Créer `ErrorState.css` (AC: 3)
  - [ ] Style centré, padding cohérent avec `EmptyState`
  - [ ] Pas de valeurs codées en dur — utiliser les tokens CSS

- [ ] Tâche 4 : Créer `index.ts` et exporter (AC: 4)
  - [ ] `export { ErrorState } from './ErrorState'`
  - [ ] Ajouter l'export dans `frontend/src/components/ui/index.ts` si ce barrel existe

- [ ] Tâche 5 : Validation (AC: 5)
  - [ ] `npm run test`

## Dev Notes

### Contexte technique

**Icône** : `lucide-react` est déjà installé dans le projet (vérifié dans l'Epic 17).

**Composant `Button`** : Si Epic 50 story 50.1 est `done`, utiliser `<Button variant="ghost" onClick={onRetry}>Réessayer</Button>`. Sinon, utiliser un `<button>` natif avec styles CSS.

**Structure de fichiers** (copier le pattern EmptyState) :
```
frontend/src/components/ui/ErrorState/
  ErrorState.tsx
  ErrorState.css
  index.ts
```

**Props interface** :
```tsx
interface ErrorStateProps {
  title?: string
  message: string
  onRetry?: () => void
  className?: string
}
```

**Rendu** :
```tsx
<div className={`error-state ${className ?? ''}`}>
  <AlertCircle className="error-state__icon" />
  {title && <h3 className="error-state__title">{title}</h3>}
  <p className="error-state__message">{message}</p>
  {onRetry && <Button variant="ghost" onClick={onRetry}>Réessayer</Button>}
</div>
```

**CSS tokens à utiliser** :
- Icône couleur : `var(--danger)` ou `var(--color-status-danger)`
- Texte : `var(--color-text-primary)`, `var(--color-text-secondary)`
- Espacement : `var(--space-4)`, `var(--space-6)` si définis par Epic 49.2, sinon valeurs rem directes

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Lire | `frontend/src/components/ui/EmptyState/EmptyState.tsx` |
| Créer | `frontend/src/components/ui/ErrorState/ErrorState.tsx` |
| Créer | `frontend/src/components/ui/ErrorState/ErrorState.css` |
| Créer | `frontend/src/components/ui/ErrorState/index.ts` |
| Modifier | `frontend/src/components/ui/index.ts` (si existe) |

### References

- [Source: frontend/src/components/ui/EmptyState/EmptyState.tsx]
- [Source: frontend/src/components/ui/]
- [Source: _bmad-output/planning-artifacts/epic-56-error-boundaries-standardises.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
