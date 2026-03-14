# Story 50.5: Créer le composant <Modal> / <Dialog> générique

Status: done

## Story

En tant que développeur frontend,
je veux un composant `<Modal>` générique avec header, body et footer composables,
afin de ne plus recoder des overlays ad-hoc pour chaque nouvelle modale du produit.

## Acceptance Criteria

1. Le composant `frontend/src/components/ui/Modal/Modal.tsx` existe et est exporté via `frontend/src/components/ui/index.ts`.
2. Le composant accepte les props `isOpen`, `onClose`, `title`, `children`, `footer`, `variant` (`'default' | 'danger' | 'info'`).
3. La fermeture est déclenchée par : le bouton ✕ en en-tête, le clic sur l'overlay, la touche Échap.
4. L'animation d'ouverture/fermeture utilise les tokens `--duration-normal` et `--easing-default`.
5. Le composant bloque le scroll de la page quand ouvert (`overflow: hidden` sur `body`).
6. Le composant est accessible : `role="dialog"`, `aria-modal="true"`, `aria-labelledby` lié au titre, focus piégé dans la modale quand ouverte.
7. `DeleteAccountModal.tsx` est refactorisé pour utiliser `<Modal>` en interne sans changer son API externe.
8. Tous les styles utilisent les tokens CSS de `design-tokens.css`.
9. Un test couvre : ouverture, fermeture (bouton ✕, overlay, Échap), focus trap.

## Tasks / Subtasks

- [x] Tâche 1 : Analyser `DeleteAccountModal.tsx` (AC: 7)
  - [x] Lire le composant pour identifier sa structure HTML et son comportement
  - [x] Identifier les props à préserver pour la rétrocompatibilité
  - [x] Identifier les styles à migrer vers `Modal.css`

- [x] Tâche 2 : Créer la structure de fichiers (AC: 1)
  - [x] `frontend/src/components/ui/Modal/Modal.tsx`
  - [x] `frontend/src/components/ui/Modal/Modal.css`
  - [x] `frontend/src/components/ui/Modal/Modal.test.tsx`
  - [x] `frontend/src/components/ui/Modal/index.ts`
  - [x] Ajouter `export * from './Modal'` dans `frontend/src/components/ui/index.ts`

- [x] Tâche 3 : Implémenter `<Modal>` (AC: 2, 3, 4, 5, 6)
  - [x] Rendu via `ReactDOM.createPortal` dans `document.body`
  - [x] Overlay semi-transparent + contenu centré
  - [x] Bouton ✕ dans le header
  - [x] Fermeture au clic overlay (stopPropagation sur le contenu)
  - [x] Fermeture à Échap via `useEffect` + listener `keydown`
  - [x] `useEffect` pour bloquer/débloquer le scroll body
  - [x] Focus trap : quand modale ouverte, Tab/Shift+Tab reste dans le contenu modal

- [x] Tâche 4 : Créer `Modal.css` (AC: 8)
  - [x] `.modal-overlay` : fixed inset-0, background rgba semi-transparent, z-index élevé, flex center
  - [x] `.modal` : background `--color-bg-elevated`, border-radius `--radius-lg`, shadow `--shadow-hero`, max-width, width
  - [x] `.modal--danger` : couleur accent header variant danger
  - [x] `.modal__header` : padding, flex between, border-bottom
  - [x] `.modal__title` : font-size `--font-size-lg`, font-weight semibold
  - [x] `.modal__close` : bouton ghost icône ✕
  - [x] `.modal__body` : padding `--space-6`
  - [x] `.modal__footer` : padding, flex end, gap `--space-3`, border-top
  - [x] Animation : `@keyframes modal-enter` avec opacity + translateY

- [x] Tâche 5 : Refactoriser `DeleteAccountModal.tsx` (AC: 7)
  - [x] Wrapper thin autour de `<Modal variant="danger">`
  - [x] Conserver exactement les mêmes props externes
  - [x] Les boutons internes utilisent `<Button>` (story 50.1)

- [x] Tâche 6 : Écrire les tests (AC: 9)
  - [x] Modal fermée par défaut
  - [x] Modal ouverte : contenu visible, `role="dialog"` présent
  - [x] Fermeture via bouton ✕
  - [x] Fermeture via touche Échap
  - [x] `aria-modal="true"` et `aria-labelledby` corrects

## Dev Notes

### Contexte technique

**Prérequis** : Story 50.1 (`<Button>`) doit être `done`.

### Portal et rendu hors DOM

Utiliser `ReactDOM.createPortal` pour rendre la modale dans `document.body` et éviter les problèmes de z-index et de stacking context :

```typescript
import { createPortal } from 'react-dom'

function Modal({ isOpen, onClose, title, children, footer }: ModalProps) {
  if (!isOpen) return null
  return createPortal(
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" role="dialog" aria-modal="true" onClick={e => e.stopPropagation()}>
        ...
      </div>
    </div>,
    document.body
  )
}
```

### Focus trap

Implémenter un focus trap simple sans dépendance externe :

```typescript
useEffect(() => {
  if (!isOpen) return
  const modal = modalRef.current
  if (!modal) return
  const focusableElements = modal.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )
  const first = focusableElements[0] as HTMLElement
  const last = focusableElements[focusableElements.length - 1] as HTMLElement
  first?.focus()

  const handleTab = (e: KeyboardEvent) => {
    if (e.key !== 'Tab') return
    if (e.shiftKey) {
      if (document.activeElement === first) { e.preventDefault(); last.focus() }
    } else {
      if (document.activeElement === last) { e.preventDefault(); first.focus() }
    }
  }
  modal.addEventListener('keydown', handleTab)
  return () => modal.removeEventListener('keydown', handleTab)
}, [isOpen])
```

### Scroll lock

```typescript
useEffect(() => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
  return () => { document.body.style.overflow = '' }
}, [isOpen])
```

### Interface TypeScript

```typescript
interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  footer?: React.ReactNode
  variant?: 'default' | 'danger' | 'info'
  className?: string
}
```

### Tokens CSS

```css
.modal-overlay {
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}
.modal {
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-glass-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-hero);
  animation: modal-enter var(--duration-normal) var(--easing-default);
}
@keyframes modal-enter {
  from { opacity: 0; transform: translateY(-8px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
```

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/components/ui/Modal/Modal.tsx` |
| Créer | `frontend/src/components/ui/Modal/Modal.css` |
| Créer | `frontend/src/components/ui/Modal/Modal.test.tsx` |
| Créer | `frontend/src/components/ui/Modal/index.ts` |
| Modifier | `frontend/src/components/ui/index.ts` |
| Modifier | `frontend/src/components/settings/DeleteAccountModal.tsx` |

### Project Structure Notes

- `DeleteAccountModal.tsx` reste dans `frontend/src/components/settings/` — ne pas déplacer
- Le composant `<Modal>` générique va dans `frontend/src/components/ui/Modal/`
- `createPortal` est disponible dans `react-dom` — déjà une dépendance du projet

### References

- [Source: frontend/src/components/settings/DeleteAccountModal.tsx]
- [Source: frontend/src/components/ui/Button/Button.tsx] (story 50.1)
- [Source: frontend/src/styles/design-tokens.css]
- [Source: _bmad-output/planning-artifacts/epic-50-bibliotheque-composants-ui-primitifs.md]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

### Completion Notes List

- Composant `<Modal>` générique implémenté avec `createPortal` pour un rendu propre hors du flux DOM.
- Gestion automatique du scroll lock sur le `body` lors de l'ouverture.
- Accessibilité native : focus trap, support de la touche Échap, rôles ARIA et labels.
- Support des variants (`default`, `danger`, `info`) et des tailles (`sm`, `md`, `lg`).
- Refactorisation réussie de `DeleteAccountModal` utilisant le nouveau composant.
- 6 tests unitaires couvrant l'ouverture, la fermeture, le clic overlay et l'accessibilité.

### Change Log

- 2026-03-14 : Implémentation du composant Modal et refacto DeleteAccountModal.

### File List

| Action | Fichier |
|--------|---------|
| Créé | `frontend/src/components/ui/Modal/Modal.tsx` |
| Créé | `frontend/src/components/ui/Modal/Modal.css` |
| Créé | `frontend/src/components/ui/Modal/Modal.test.tsx` |
| Créé | `frontend/src/components/ui/Modal/index.ts` |
| Modifié | `frontend/src/components/ui/index.ts` |
| Modifié | `frontend/src/components/settings/DeleteAccountModal.tsx` |
| Modifié | `frontend/src/components/settings/DeleteAccountModal.css` |
