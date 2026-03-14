# Story 54.2: Créer les barrel exports par domaine et migrer les imports du codebase

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux des fichiers `index.ts` (barrel exports) par domaine et migrer les imports profonds vers les aliases,
afin que tous les imports du projet utilisent `@ui`, `@i18n`, `@api`, etc. à la place de chemins relatifs profonds.

## Acceptance Criteria

1. Chaque domaine (`ui`, `components`, `api`, `hooks`, `i18n`, `state`, `pages`) a un `index.ts` exportant ses membres publics.
2. Les imports `../../components/ui/Button/Button` sont remplacés par `@ui` ou `@ui/Button` dans tout le codebase.
3. Les imports `../../../i18n/auth` sont remplacés par `@i18n/auth`.
4. `npm run build` passe sans erreur.
5. `npm run test` passe sans erreur.
6. Aucun chemin relatif profond (3+ niveaux `../../..`) ne subsiste dans `src/`.

## Tasks / Subtasks

- [ ] Tâche 1 : Vérifier/créer les barrel exports (AC: 1)
  - [ ] Lire `frontend/src/components/ui/index.ts` s'il existe
  - [ ] Créer ou compléter `frontend/src/i18n/index.ts`
  - [ ] Créer ou compléter `frontend/src/api/index.ts`
  - [ ] Créer ou compléter `frontend/src/hooks/index.ts`
  - [ ] Créer ou compléter `frontend/src/state/index.ts`

- [ ] Tâche 2 : Audit des imports profonds (AC: 2, 3, 6)
  - [ ] `grep -r "from '\.\./\.\./\.\." frontend/src/` — lister tous les imports 3+ niveaux
  - [ ] Prioriser les plus fréquents

- [ ] Tâche 3 : Migrer les imports UI (AC: 2)
  - [ ] Remplacer `from '../../components/ui/Button/Button'` → `from '@ui/Button'`
  - [ ] Migrer tous les imports UI dans les pages et composants

- [ ] Tâche 4 : Migrer les imports i18n, api, hooks, state (AC: 3)
  - [ ] `from '../../../i18n/auth'` → `from '@i18n/auth'`
  - [ ] `from '../../api/predictions'` → `from '@api/predictions'`
  - [ ] etc.

- [ ] Tâche 5 : Validation finale (AC: 4, 5, 6)
  - [ ] `npm run build`
  - [ ] `npm run test`
  - [ ] Re-grep pour vérifier l'absence d'imports profonds résiduels

## Dev Notes

### Contexte technique

**Prérequis** : Story 54.1 `done` — les aliases Vite/TS sont configurés.

**Stratégie barrel export** :

Un barrel export est un `index.ts` qui ré-exporte les membres du domaine :
```ts
// frontend/src/components/ui/index.ts
export { Button } from './Button/Button'
export type { ButtonProps } from './Button/Button'
export { Field } from './Field/Field'
// ...
```

**Ne pas créer de barrel pour les composants complexes non-publics** (pages internes, composants très spécifiques) — seulement les membres qui sont effectivement importés depuis l'extérieur du domaine.

**Migration semi-automatique** : On peut utiliser `sed` ou un script simple pour remplacer les patterns les plus fréquents, mais préférer la migration manuelle fichier par fichier pour éviter les erreurs.

**Priorité de migration** :
1. Composants UI (`@ui`) — les plus importés
2. i18n (`@i18n`) — nombreux imports depuis les composants
3. API (`@api`) — imports depuis les hooks
4. Hooks (`@hooks`) — imports depuis les pages/composants
5. State (`@state`) — imports depuis les providers

**Attention aux circular imports** : Un barrel `index.ts` ne doit pas importer d'autres barrels du même domaine.

### References

- [Source: frontend/src/components/ui/index.ts]
- [Source: frontend/src/i18n/index.ts]
- [Source: _bmad-output/implementation-artifacts/54-1-configurer-path-aliases-vite-typescript.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
