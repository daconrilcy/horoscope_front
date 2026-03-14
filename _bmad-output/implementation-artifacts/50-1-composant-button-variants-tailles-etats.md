# Story 50.1: Créer le composant <Button> avec variants, tailles et états

Status: done

## Story

En tant que développeur frontend,
je veux un composant `<Button>` partagé avec des variants, tailles et états standardisés,
afin que tous les boutons du produit soient visuellement cohérents et modifiables depuis un seul fichier.

## Acceptance Criteria

1. Le composant `frontend/src/components/ui/Button/Button.tsx` existe et est exporté via `frontend/src/components/ui/index.ts`.
2. Les variants `primary`, `secondary`, `ghost`, `danger` sont supportés via une prop `variant`.
3. Les tailles `sm`, `md`, `lg` sont supportées via une prop `size`.
4. L'état `loading` affiche un spinner inline et désactive l'interaction (prop `loading?: boolean`).
5. L'état `disabled` est géré nativement via l'attribut HTML + styles visuels dédiés.
6. Les props `leftIcon` et `rightIcon` acceptent un `ReactNode` et positionnent l'icône correctement.
7. La prop `fullWidth` (boolean) étend le bouton à 100% de la largeur du conteneur.
8. Le composant est accessible : `type="button"` par défaut, support `aria-label`, `aria-busy` en état loading.
9. Tous les styles utilisent exclusivement les tokens CSS de `design-tokens.css` (Epic 49).
10. Un fichier de tests `Button.test.tsx` couvre le rendu des variants, l'état loading et le disabled.

## Tasks / Subtasks

- [x] Tâche 1 : Créer la structure de fichiers (AC: 1)
  - [x] `frontend/src/components/ui/Button/Button.tsx`
  - [x] `frontend/src/components/ui/Button/Button.css`
  - [x] `frontend/src/components/ui/Button/Button.test.tsx`
  - [x] `frontend/src/components/ui/Button/index.ts` (re-export)
  - [x] Créer `frontend/src/components/ui/index.ts` avec export `export * from './Button'`

- [x] Tâche 2 : Implémenter le composant (AC: 2, 3, 4, 5, 6, 7, 8)
  - [x] Interface TypeScript `ButtonProps`
  - [x] Variante `primary` : fond gradient `--color-cta-left` → `--color-cta-right`, texte `--color-btn-text`
  - [x] Variante `secondary` : fond `--color-glass-bg`, bordure `--color-glass-border`, texte `--color-text-primary`
  - [x] Variante `ghost` : fond transparent, texte `--color-text-primary`, hover léger
  - [x] Variante `danger` : fond `--color-danger`, texte blanc
  - [x] Tailles via padding et font-size depuis les tokens
  - [x] Spinner SVG ou CSS animé pour l'état `loading`
  - [x] `aria-busy="true"` quand `loading`, `aria-disabled="true"` quand `disabled`

- [x] Tâche 3 : Créer `Button.css` (AC: 9)
  - [x] Base `.btn` : display flex, align-center, border-radius `--radius-full`, transition, cursor
  - [x] `.btn--primary`, `.btn--secondary`, `.btn--ghost`, `.btn--danger`
  - [x] `.btn--sm`, `.btn--md`, `.btn--lg`
  - [x] `.btn--loading` : opacity réduite, pointer-events none
  - [x] `.btn--full-width` : width 100%
  - [x] `.btn:disabled` : opacity 0.5, cursor not-allowed
  - [x] `.btn__spinner` : animation rotation

- [x] Tâche 4 : Écrire les tests (AC: 10)
  - [x] Rendu de chaque variant sans crash
  - [x] État loading : spinner présent, `aria-busy="true"`, bouton non cliquable
  - [x] État disabled : `aria-disabled="true"`, onClick non déclenché
  - [x] Props leftIcon/rightIcon renduées

## Dev Notes

### Contexte technique

**Stack** : React 19 + TypeScript + Vitest + Testing Library. Pas de CSS-in-JS.

**Prérequis** : Epic 49 (stories 49.1 et 49.2) doit être `done` — les tokens CSS doivent exister.

### Interface TypeScript

```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  fullWidth?: boolean
}
```

Étendre `React.ButtonHTMLAttributes<HTMLButtonElement>` pour passer-through `onClick`, `type`, `aria-label`, `form`, etc.

### Correspondance visuelle avec les boutons existants

| Bouton existant | Nouveau composant |
|-----------------|-------------------|
| `.hero-card__cta` (gradient, 48px) | `<Button variant="primary" size="lg">` |
| `button-ghost` dans App.css | `<Button variant="ghost">` |
| Bouton submit dans SignInForm | `<Button variant="primary" loading={isLoading}>` |
| Bouton "Se déconnecter" dans Header | `<Button variant="ghost" size="sm">` |
| Bouton de suppression dans DeleteAccountModal | `<Button variant="danger">` |

### Spinner

Ne pas utiliser une dépendance externe. Implémenter avec un simple SVG circulaire CSS animé ou une `border-animation` CSS :

```css
.btn__spinner {
  width: 1em;
  height: 1em;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: btn-spin var(--duration-normal, 250ms) linear infinite;
}
@keyframes btn-spin { to { transform: rotate(360deg); } }
```

### Tokens CSS utilisés

```css
/* Variant primary */
background: linear-gradient(135deg, var(--color-cta-left), var(--color-cta-right));
color: var(--color-btn-text);
box-shadow: var(--shadow-cta);

/* Variant secondary */
background: var(--color-glass-bg);
border: 1px solid var(--color-glass-border);
color: var(--color-text-primary);

/* Variant ghost */
background: transparent;
color: var(--color-text-primary);

/* Variant danger */
background: var(--color-danger);
color: white;

/* Tailles */
--btn-sm-padding: var(--space-2) var(--space-4);
--btn-md-padding: var(--space-3) var(--space-6);
--btn-lg-padding: var(--space-4) var(--space-8);
```

### Gestion de `type` par défaut

Par défaut, les boutons HTML dans un `<form>` ont `type="submit"`. Définir `type="button"` par défaut dans le composant pour éviter les soumissions accidentelles :

```typescript
function Button({ type = 'button', ...props }: ButtonProps) { ... }
```

### Fichiers à créer

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/components/ui/Button/Button.tsx` |
| Créer | `frontend/src/components/ui/Button/Button.css` |
| Créer | `frontend/src/components/ui/Button/Button.test.tsx` |
| Créer | `frontend/src/components/ui/Button/index.ts` |
| Créer | `frontend/src/components/ui/index.ts` |

### Project Structure Notes

- Le dossier `frontend/src/components/ui/` est **nouveau** — ne pas confondre avec `frontend/src/ui/` (qui contient `icons.tsx` et `nav.ts`, ce sont des utilitaires, pas des composants)
- Convention : 1 dossier par composant, PascalCase
- Importer `Button.css` dans `Button.tsx` via `import './Button.css'`
- Ne pas importer `Button.css` dans `main.tsx` — les CSS de composants sont importés localement

### Tests

Framework de test : Vitest + `@testing-library/react`. Voir les tests existants dans `frontend/src/tests/` pour les patterns utilisés dans ce projet.

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

test('renders primary button', () => {
  render(<Button variant="primary">Click me</Button>)
  expect(screen.getByRole('button')).toBeInTheDocument()
})

test('shows spinner when loading', () => {
  render(<Button loading>Click me</Button>)
  expect(screen.getByRole('button')).toHaveAttribute('aria-busy', 'true')
})
```

### References

- [Source: frontend/src/components/SignInForm.tsx] (usage actuel de bouton submit)
- [Source: frontend/src/components/HeroHoroscopeCard.tsx] (`.hero-card__cta`)
- [Source: frontend/src/App.css] (`.button-ghost` si existe)
- [Source: frontend/src/components/settings/DeleteAccountModal.tsx] (bouton danger)
- [Source: frontend/src/styles/design-tokens.css] (Epic 49)
- [Source: frontend/src/tests/] (patterns de tests existants)
- [Source: _bmad-output/planning-artifacts/epic-50-bibliotheque-composants-ui-primitifs.md]

## Dev Agent Record

### Agent Model Used

claude-opus-4-6

### Debug Log References

- Corrigé un problème de cleanup entre tests dans `setup.ts` (ajout de `cleanup()` après chaque test via `afterEach`) — le test "does not render icons when loading" échouait car le DOM du test précédent n'était pas nettoyé.

### Completion Notes List

- Composant `<Button>` implémenté avec `React.forwardRef`, 4 variants (primary/secondary/ghost/danger), 3 tailles (sm/md/lg), états loading/disabled, props leftIcon/rightIcon, fullWidth
- Spinner CSS pur avec animation `btn-spin` et `border-top-color: transparent`
- Tous les styles utilisent les tokens de `design-tokens.css` (Epic 49)
- `type="button"` par défaut pour éviter les soumissions accidentelles
- 16 tests unitaires couvrant variants, tailles, états, icônes et props passthrough
- Correction du setup de test global (`setup.ts`) pour ajouter le cleanup automatique entre tests
- Suite complète : 72 fichiers de tests, 1042 tests, 0 régression

### Change Log

- 2026-03-14 : Implémentation complète du composant Button et correction du setup de test global

### File List

| Action | Fichier |
|--------|---------|
| Créé | `frontend/src/components/ui/Button/Button.tsx` |
| Créé | `frontend/src/components/ui/Button/Button.css` |
| Créé | `frontend/src/components/ui/Button/Button.test.tsx` |
| Créé | `frontend/src/components/ui/Button/index.ts` |
| Créé | `frontend/src/components/ui/index.ts` |
| Modifié | `frontend/src/tests/setup.ts` (ajout cleanup afterEach) |
