# Story 50.3: Généraliser TimezoneSelect en composant <Select> searchable réutilisable

Status: done

## Story

En tant que développeur frontend,
je veux un composant `<Select>` searchable et générique,
afin de pouvoir proposer une liste déroulante filtrée pour n'importe quelle donnée (fuseaux horaires, signes astrologiques, pays, etc.) sans recoder ce pattern.

## Acceptance Criteria

1. Le composant `frontend/src/components/ui/Select/Select.tsx` existe et est exporté via `frontend/src/components/ui/index.ts`.
2. Le composant accepte une prop `options: Array<{ value: string; label: string; group?: string }>` générique.
3. La recherche filtre les options en temps réel (client-side, insensible à la casse).
4. La prop `value` / `onChange` suit le pattern contrôlé React standard.
5. Les props `placeholder`, `searchPlaceholder`, `label`, `error`, `disabled` sont supportées.
6. Le regroupement optionnel d'options via `group` est affiché comme en-têtes de section.
7. Le composant est accessible : role `combobox`, `aria-expanded`, `aria-activedescendant`, navigation clavier (flèches, Entrée, Échap).
8. `TimezoneSelect.tsx` est refactorisé pour utiliser `<Select>` en interne (sans changer son API externe).
9. Tous les styles utilisent les tokens CSS de `design-tokens.css`.
10. Un fichier de tests couvre le filtrage, la sélection, la navigation clavier et l'accessibilité.

## Tasks / Subtasks

- [x] Tâche 1 : Analyser `TimezoneSelect.tsx` et `TimezoneSelect.css` (AC: 8)
  - [x] Lire le composant entier et identifier son API (props, état, comportement dropdown)
  - [x] Identifier les patterns réutilisables vs spécifiques aux fuseaux horaires
  - [x] Lister les styles à migrer vers `Select.css`

- [x] Tâche 2 : Créer la structure de fichiers (AC: 1)
  - [x] `frontend/src/components/ui/Select/Select.tsx`
  - [x] `frontend/src/components/ui/Select/Select.css`
  - [x] `frontend/src/components/ui/Select/Select.test.tsx`
  - [x] `frontend/src/components/ui/Select/index.ts`
  - [x] Ajouter `export * from './Select'` dans `frontend/src/components/ui/index.ts`

- [x] Tâche 3 : Implémenter le composant Select générique (AC: 2, 3, 4, 5, 6, 7)
  - [x] Interface TypeScript `SelectOption` et `SelectProps`
  - [x] État interne : `isOpen`, `search`, `activeIndex` pour navigation clavier
  - [x] Filtre insensible à la casse sur `label`
  - [x] Rendu des groupes avec en-têtes si `group` fourni
  - [x] Fermeture au clic extérieur (useEffect + listener)
  - [x] Navigation clavier : ArrowDown/ArrowUp (index actif), Entrée (sélectionner), Échap (fermer)
  - [x] `aria-expanded`, `aria-activedescendant`, `role="listbox"` sur la liste

- [x] Tâche 4 : Refactoriser `TimezoneSelect` pour utiliser `<Select>` (AC: 8)
  - [x] Transformer les données de `data/timezones.ts` en format `SelectOption[]`
  - [x] Remplacer l'implémentation interne par `<Select options={...} />`
  - [x] Conserver exactement la même interface externe (props) de `TimezoneSelect`
  - [x] Vérifier que le comportement est identique à BirthProfilePage

- [x] Tâche 5 : Créer `Select.css` (AC: 9)
  - [x] `.select` : wrapper position relative
  - [x] `.select__trigger` : styles de bouton dropdown (fond, bordure, radius, chevron)
  - [x] `.select__dropdown` : position absolute, z-index, shadow, border-radius, overflow hidden
  - [x] `.select__search` : input de recherche en haut du dropdown
  - [x] `.select__list` : overflow-y auto, max-height
  - [x] `.select__group-header` : label de groupe, font-weight semibold, couleur muted
  - [x] `.select__option` : padding, hover, `.select__option--active`, `.select__option--selected`

- [x] Tâche 6 : Écrire les tests (AC: 10)
  - [x] Options rendues quand ouvert
  - [x] Filtrage par texte de recherche
  - [x] Sélection d'une option → onChange appelé avec la valeur
  - [x] Navigation clavier : ArrowDown → focus option suivante
  - [x] Fermeture avec Échap

## Dev Notes

### Contexte technique

**Prérequis** : Epic 49 `done`.

**TimezoneSelect.tsx** est à `frontend/src/components/TimezoneSelect.tsx`. Son CSS est `frontend/src/components/TimezoneSelect.css`. Les données sont dans `frontend/src/data/timezones.ts`.

### Interface TypeScript

```typescript
export interface SelectOption {
  value: string
  label: string
  group?: string
}

export interface SelectProps {
  options: SelectOption[]
  value: string
  onChange: (value: string) => void
  placeholder?: string
  searchPlaceholder?: string
  label?: string
  error?: string
  disabled?: boolean
  className?: string
}
```

### Refactorisation de TimezoneSelect

**Avant** (implémentation propriétaire) :
```tsx
// TimezoneSelect.tsx - dropdown codé en dur pour les timezones
```

**Après** (wrapper thin autour de Select) :
```tsx
import { Select } from '../ui/Select'
import { timezones } from '../data/timezones'

function TimezoneSelect({ value, onChange, label, error }: TimezoneSelectProps) {
  const options = timezones.map(tz => ({ value: tz.value, label: tz.label, group: tz.region }))
  return <Select options={options} value={value} onChange={onChange} label={label} error={error} />
}
```

L'API externe de `TimezoneSelect` ne change pas — les consommateurs (BirthProfilePage) n'ont pas besoin d'être modifiés.

### Fermeture au clic extérieur

```typescript
useEffect(() => {
  if (!isOpen) return
  const handleClickOutside = (e: MouseEvent) => {
    if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
      setIsOpen(false)
    }
  }
  document.addEventListener('mousedown', handleClickOutside)
  return () => document.removeEventListener('mousedown', handleClickOutside)
}, [isOpen])
```

### Attention — pas de `<select>` HTML natif

Le composant est un custom dropdown (pas `<select>` HTML natif) pour permettre la recherche et le groupement visuel. L'accessibilité ARIA doit donc être gérée manuellement avec `role="combobox"`, `role="listbox"`, `role="option"`.

### Tokens CSS

```css
.select__trigger {
  background: var(--color-bg-surface);
  border: 1px solid var(--color-glass-border);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
}
.select__dropdown {
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-glass-border);
  box-shadow: var(--shadow-card);
  border-radius: var(--radius-md);
}
.select__option--active {
  background: var(--color-glass-bg);
}
.select__option--selected {
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}
```

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/components/ui/Select/Select.tsx` |
| Créer | `frontend/src/components/ui/Select/Select.css` |
| Créer | `frontend/src/components/ui/Select/Select.test.tsx` |
| Créer | `frontend/src/components/ui/Select/index.ts` |
| Modifier | `frontend/src/components/ui/index.ts` |
| Modifier | `frontend/src/components/TimezoneSelect.tsx` (refacto) |
| Conserver | `frontend/src/components/TimezoneSelect.css` → peut être vidé après refacto |

### Project Structure Notes

- `TimezoneSelect` reste à `frontend/src/components/` (pas dans `ui/`) car c'est un composant domaine-spécifique qui wrape `Select`
- Ne pas déplacer `TimezoneSelect` dans `ui/` — il est câblé sur des données métier (fuseaux horaires)
- Les données `timezones.ts` restent dans `frontend/src/data/` — pas de déplacement

### References

- [Source: frontend/src/components/TimezoneSelect.tsx]
- [Source: frontend/src/components/TimezoneSelect.css]
- [Source: frontend/src/data/timezones.ts]
- [Source: frontend/src/pages/BirthProfilePage.tsx] (consommateur de TimezoneSelect)
- [Source: frontend/src/styles/design-tokens.css]
- [Source: _bmad-output/planning-artifacts/epic-50-bibliotheque-composants-ui-primitifs.md]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

### Completion Notes List

- Composant `<Select>` générique implémenté avec recherche intégrée et support des groupes.
- Refactorisation de `TimezoneSelect` pour utiliser `Select` tout en conservant son API.
- Accessibilité ARIA complète (role combobox, listbox, option).
- Navigation clavier fluide (flèches, Entrée, Échap, Tab).
- Styles alignés sur les design tokens et glassmorphism.
- 7 tests unitaires couvrant le filtrage, la sélection et le clavier.

### Change Log

- 2026-03-14 : Implémentation du composant Select et refacto TimezoneSelect.

### File List

| Action | Fichier |
|--------|---------|
| Créé | `frontend/src/components/ui/Select/Select.tsx` |
| Créé | `frontend/src/components/ui/Select/Select.css` |
| Créé | `frontend/src/components/ui/Select/Select.test.tsx` |
| Créé | `frontend/src/components/ui/Select/index.ts` |
| Modifié | `frontend/src/components/ui/index.ts` |
| Modifié | `frontend/src/components/TimezoneSelect.tsx` |
| Modifié | `frontend/src/components/TimezoneSelect.css` |
