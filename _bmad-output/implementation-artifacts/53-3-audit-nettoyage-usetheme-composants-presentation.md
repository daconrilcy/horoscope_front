# Story 53.3: Audit et nettoyage des useTheme() résiduels dans les composants de présentation

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux supprimer tous les `useTheme()` résiduels dans les composants purement présentationnels,
afin que les composants de présentation n'aient plus aucune dépendance sur le contexte de thème JavaScript.

## Acceptance Criteria

1. Un audit complet de `useTheme()` dans `frontend/src/components/` est documenté dans le Dev Agent Record.
2. Tous les `useTheme()` utilisés uniquement pour des calculs CSS (couleur, fond, border) sont supprimés.
3. Les `useTheme()` légitimes (Canvas/WebGL, API externe nécessitant le thème) sont conservés et documentés.
4. Aucun composant purement présentationnel n'importe `useTheme()`.
5. Le rendu visuel est identique avant/après dans tous les modes.
6. Les tests existants passent sans modification.

## Tasks / Subtasks

- [ ] Tâche 1 : Audit exhaustif (AC: 1)
  - [ ] `grep -r "useTheme" frontend/src/components/` — lister tous les usages
  - [ ] Pour chaque usage, classer : CSS-only (à supprimer) / légitime (à conserver)
  - [ ] Documenter la liste dans Completion Notes

- [ ] Tâche 2 : Supprimer les imports CSS-only (AC: 2, 4)
  - [ ] Pour chaque composant CSS-only : remplacer le calcul inline par la variable CSS appropriée
  - [ ] Supprimer `const { theme } = useTheme()` et l'import `useTheme`
  - [ ] Vérifier qu'aucune autre utilisation de `theme` ne reste dans le fichier

- [ ] Tâche 3 : Documenter les usages légitimes (AC: 3)
  - [ ] Ajouter un commentaire `// useTheme needed: <raison>` au-dessus de chaque import conservé
  - [ ] Cas connus légitimes : `AstroMoodBackground.tsx` (Canvas WebGL), composants avec API tierce

- [ ] Tâche 4 : Validation (AC: 5, 6)
  - [ ] Test visuel light/dark/astro pour chaque composant modifié
  - [ ] `npm run test`

## Dev Notes

### Contexte technique

**Prérequis** : Stories 53.1 et 53.2 `done` — les variables CSS contextuelles sont en place.

**Règle de décision** :
- `useTheme()` pour `color`, `background`, `border` → supprimer, utiliser `var(--token)`
- `useTheme()` pour passer le thème à un Canvas, WebGL, librarie externe → conserver avec commentaire

**Exemple de migration** :
```tsx
// Avant
const { theme } = useTheme()
const color = theme === 'dark' ? '#fff' : '#111'
return <div style={{ color }}>...</div>

// Après
return <div style={{ color: 'var(--color-text-primary)' }}>...</div>
```

**Cas connu légitime** : `AstroMoodBackground.tsx` passe le thème au Canvas pour la palette de couleurs des étoiles — NE PAS TOUCHER.

### Fichiers potentiellement concernés

- `frontend/src/components/prediction/DayPredictionCard.tsx` (déjà traité en 53.1)
- `frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx` (déjà traité en 53.1)
- Autres composants à découvrir lors de l'audit

### References

- [Source: frontend/src/state/ThemeProvider.tsx]
- [Source: _bmad-output/implementation-artifacts/53-1-variables-css-adaptatives-dark-mode.md]
- [Source: _bmad-output/implementation-artifacts/53-2-variables-css-contextuelles-astrotheme.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
