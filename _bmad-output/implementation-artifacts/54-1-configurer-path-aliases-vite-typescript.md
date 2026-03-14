# Story 54.1: Configurer les path aliases dans vite.config.ts et tsconfig.json

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux configurer des path aliases `@ui`, `@components`, `@api`, `@hooks`, `@i18n`, `@styles`, `@state` dans Vite et TypeScript,
afin que les imports longs en chemins relatifs puissent être remplacés par des aliases courts dans la story suivante.

## Acceptance Criteria

1. `vite.config.ts` contient un bloc `resolve.alias` avec tous les aliases définis.
2. `tsconfig.json` contient un bloc `compilerOptions.paths` cohérent avec les aliases Vite.
3. `npm run build` passe sans erreur avec les nouveaux aliases.
4. `npm run test` passe sans erreur.
5. Au moins un import de test utilisant un alias est présent pour valider la configuration (peut être dans un fichier de test temporaire ou dans un composant existant).

## Tasks / Subtasks

- [ ] Tâche 1 : Lire les fichiers existants (AC: 1, 2)
  - [ ] Lire `frontend/vite.config.ts`
  - [ ] Lire `frontend/tsconfig.json`
  - [ ] Lire `frontend/tsconfig.app.json` s'il existe

- [ ] Tâche 2 : Configurer les aliases dans `vite.config.ts` (AC: 1)
  - [ ] Importer `path` from `'node:path'`
  - [ ] Ajouter `resolve: { alias: { '@ui': ..., '@components': ..., '@api': ..., '@hooks': ..., '@i18n': ..., '@styles': ..., '@state': ... } }`
  - [ ] Utiliser `path.resolve(__dirname, 'src/...')` pour chaque alias

- [ ] Tâche 3 : Configurer les paths dans `tsconfig.json` (AC: 2)
  - [ ] Ajouter `"paths"` dans `compilerOptions`
  - [ ] Chaque alias : `"@ui/*": ["src/components/ui/*"]`, etc.
  - [ ] Vérifier que `baseUrl` est défini sur `"."`

- [ ] Tâche 4 : Vérifier la build et les tests (AC: 3, 4)
  - [ ] `npm run build`
  - [ ] `npm run test`

- [ ] Tâche 5 : Import de validation (AC: 5)
  - [ ] Modifier un import existant dans un composant test pour utiliser un alias
  - [ ] Vérifier que le composant compile et s'affiche correctement

## Dev Notes

### Contexte technique

**Stack** : React 19 + Vite 7 + TypeScript. Le projet est dans `frontend/` — tous les chemins sont relatifs à ce dossier.

**Aliases à configurer** :

| Alias | Chemin réel |
|-------|-------------|
| `@ui` | `src/components/ui` |
| `@components` | `src/components` |
| `@api` | `src/api` |
| `@hooks` | `src/hooks` |
| `@i18n` | `src/i18n` |
| `@styles` | `src/styles` |
| `@state` | `src/state` |
| `@pages` | `src/pages` |

**Pattern vite.config.ts** :
```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@ui': path.resolve(__dirname, 'src/components/ui'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@api': path.resolve(__dirname, 'src/api'),
      '@hooks': path.resolve(__dirname, 'src/hooks'),
      '@i18n': path.resolve(__dirname, 'src/i18n'),
      '@styles': path.resolve(__dirname, 'src/styles'),
      '@state': path.resolve(__dirname, 'src/state'),
      '@pages': path.resolve(__dirname, 'src/pages'),
    }
  }
})
```

**Pattern tsconfig.json** :
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@ui/*": ["src/components/ui/*"],
      "@components/*": ["src/components/*"],
      "@api/*": ["src/api/*"],
      "@hooks/*": ["src/hooks/*"],
      "@i18n/*": ["src/i18n/*"],
      "@styles/*": ["src/styles/*"],
      "@state/*": ["src/state/*"],
      "@pages/*": ["src/pages/*"]
    }
  }
}
```

**Attention** : Si le projet utilise `tsconfig.app.json` séparé du `tsconfig.json` racine, les `paths` doivent être dans le fichier que `tsc` utilise effectivement pour la compilation (souvent `tsconfig.app.json`).

### References

- [Source: frontend/vite.config.ts]
- [Source: frontend/tsconfig.json]
- [Source: _bmad-output/planning-artifacts/epic-54-path-aliases-barrel-exports.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
