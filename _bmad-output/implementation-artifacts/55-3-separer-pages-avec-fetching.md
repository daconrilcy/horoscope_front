# Story 55.3: Séparer les pages-composants qui font du fetching (AstrologersPage, ConsultationsPage)

Status: done

## Story

En tant que développeur frontend,
je veux que les pages qui mélangent fetching et rendu soient séparées en hook de données et composant de page présentationnel,
afin de respecter le pattern container/presenter de manière cohérente sur toutes les pages.

## Acceptance Criteria

1. `AstrologersPage.tsx` ne contient plus de `useQuery`/`useMutation` directs — il utilise le hook dédié `useAstrologers`.
2. `ConsultationsPage.tsx` suit le même pattern via `useConsultations`.
3. Les hooks extraits (`useAstrologers.ts`, `useConsultations.ts`) sont dans `frontend/src/hooks/`.
4. Le rendu visuel est identique avant/après.
5. Les tests existants passent sans modification.

## Tasks / Subtasks

- [x] Tâche 1 : Analyser `AstrologersPage.tsx` (AC: 1)
  - [x] Identifier l'utilisation de `useAstrologers` (API).

- [x] Tâche 2 : Extraire `useAstrologers.ts` (AC: 1, 3)
  - [x] Créer `frontend/src/hooks/useAstrologers.ts` encapsulant l'appel API et la transformation des données.

- [x] Tâche 3 : Refactoriser `AstrologersPage.tsx` (AC: 1)
  - [x] Utiliser le nouveau hook et mettre à jour les imports (utilisation de `@hooks` et `@api`).

- [x] Tâche 4 : Analyser et refactoriser `ConsultationsPage.tsx` (AC: 2, 3)
  - [x] Créer `frontend/src/hooks/useConsultations.ts` encapsulant l'accès au store de consultations.
  - [x] Utiliser le nouveau hook dans `ConsultationsPage.tsx`.

- [x] Tâche 5 : Validation (AC: 4, 5)
  - [x] `npm run test` — 1079 tests réussis.
  - [x] Vérification visuelle des pages Astrologues et Consultations.

## Dev Notes

### Standardisation des hooks de page

L'extraction des hooks dans `src/hooks/` permet de clarifier la responsabilité des composants de page. Ils ne s'occupent plus de savoir d'où viennent les données (API vs Store), mais seulement de la manière dont elles sont assemblées et présentées.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Création du hook `useAstrologers`.
- Création du hook `useConsultations`.
- Migration des pages `AstrologersPage` et `ConsultationsPage` vers ces hooks.
- Nettoyage des imports via path aliases.
- Validation via 1079 tests réussis.

### File List
- `frontend/src/hooks/useAstrologers.ts`
- `frontend/src/hooks/useConsultations.ts`
- `frontend/src/pages/AstrologersPage.tsx`
- `frontend/src/pages/ConsultationsPage.tsx`
