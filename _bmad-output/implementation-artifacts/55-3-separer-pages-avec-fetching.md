# Story 55.3: Séparer les pages-composants qui font du fetching (AstrologersPage, ConsultationsPage)

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux que les pages qui mélangent fetching et rendu soient séparées en hook de données et composant de page présentationnel,
afin de respecter le pattern container/presenter de manière cohérente sur toutes les pages.

## Acceptance Criteria

1. `AstrologersPage.tsx` ne contient plus de `useQuery`/`useMutation` directs — il reçoit ses données via props ou utilise des hooks dédiés déjà extraits.
2. `ConsultationsPage.tsx` suit le même pattern.
3. Les hooks extraits (`useAstrologers.ts`, `useConsultations.ts`) sont dans `frontend/src/hooks/`.
4. Le rendu visuel est identique avant/après.
5. Les tests existants passent sans modification.

## Tasks / Subtasks

- [ ] Tâche 1 : Analyser `AstrologersPage.tsx` (AC: 1)
  - [ ] Lire le fichier
  - [ ] Identifier les appels `useQuery`, `useMutation`, `useEffect` avec fetch
  - [ ] Vérifier si un hook existe déjà (`useAstrologers.ts` ?)

- [ ] Tâche 2 : Extraire `useAstrologers.ts` (AC: 1, 3)
  - [ ] Si le hook n'existe pas, le créer dans `frontend/src/hooks/`
  - [ ] Retourner `{ astrologers, isLoading, error }`

- [ ] Tâche 3 : Refactoriser `AstrologersPage.tsx` (AC: 1)
  - [ ] Utiliser `useAstrologers()` au lieu de `useQuery` direct
  - [ ] La page reste le point d'assemblage (pas besoin de container séparé pour les pages)

- [ ] Tâche 4 : Analyser et refactoriser `ConsultationsPage.tsx` (AC: 2, 3)
  - [ ] Même processus que pour AstrologersPage
  - [ ] Vérifier si `useConsultations.ts` existe déjà

- [ ] Tâche 5 : Validation (AC: 4, 5)
  - [ ] Naviguer vers les pages concernées et vérifier le rendu
  - [ ] `npm run test`

## Dev Notes

### Contexte technique

**Prérequis** : Stories 55.1 et 55.2 `done`.

**Nuance pour les pages** : Les pages React Router n'ont pas forcément besoin d'un container séparé — contrairement aux composants réutilisables. La page elle-même peut appeler le hook et passer les données aux composants enfants. L'objectif est d'isoler le fetching dans des hooks nommés, pas forcément de créer des containers.

```tsx
// AstrologersPage.tsx — après refacto
export function AstrologersPage() {
  const { astrologers, isLoading, error } = useAstrologers()

  if (isLoading) return <PageSkeleton />
  if (error) return <ErrorState error={error} />

  return (
    <PageLayout title="Astrologues">
      <AstrologersList astrologers={astrologers} />
    </PageLayout>
  )
}
```

**Hooks existants à vérifier** : Le projet a des hooks dans `frontend/src/hooks/` et potentiellement dans les dossiers des composants. Vérifier avant d'en créer de nouveaux.

**Cas particulier ConsultationsPage** : Cette page a probablement un wizard et une logique complexe. Si la séparation complète est trop risquée, au minimum extraire le fetching initial dans un hook et laisser la logique d'état local dans la page.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Lire/modifier | `frontend/src/pages/AstrologersPage.tsx` |
| Lire/modifier | `frontend/src/pages/ConsultationsPage.tsx` |
| Créer si besoin | `frontend/src/hooks/useAstrologers.ts` |
| Créer si besoin | `frontend/src/hooks/useConsultations.ts` |

### References

- [Source: frontend/src/pages/AstrologersPage.tsx] (à lire)
- [Source: frontend/src/pages/ConsultationsPage.tsx] (à lire)
- [Source: _bmad-output/planning-artifacts/epic-55-separation-logique-presentation.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
