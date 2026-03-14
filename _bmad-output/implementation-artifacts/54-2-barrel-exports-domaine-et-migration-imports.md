# Story 54.2: Créer les barrel exports par domaine et migrer les imports du codebase

Status: done

## Story

En tant que développeur frontend,
je veux des fichiers `index.ts` (barrel exports) par domaine (`api`, `components/ui`, `i18n`, `pages`, `state`) et migrer les imports existants,
afin de simplifier la lecture des imports et de tirer profit des path aliases.

## Acceptance Criteria

1. Chaque domaine (`api`, `components/ui`, `i18n`, `pages`, `state`, `layouts`) a un `index.ts` exportant ses membres publics.
2. Les imports dans le codebase utilisent les path aliases (`@api`, `@ui`, etc.) dès que c'est possible (si hors du domaine local).
3. Les imports multiples du même domaine sont groupés sur une seule ligne via le barrel.
4. Aucun import relatif ne remonte plus haut que le dossier `src` (ex: `../../` est toléré si interne au domaine, mais `@` est préféré).
5. `npm run build` passe.
6. Aucun chemin relatif profond (3+ niveaux `../../..`) ne subsiste dans `src/`.
7. Tous les tests existants passent.

## Tasks / Subtasks

- [x] Tâche 1 : Créer les fichiers `index.ts` manquants (AC: 1)
  - [x] `frontend/src/i18n/index.ts`
  - [x] `frontend/src/api/index.ts` (Attention aux conflits de noms comme `ApiError`)
  - [x] `frontend/src/state/index.ts`
  - [x] `frontend/src/pages/index.ts`
  - [x] `frontend/src/layouts/index.ts` (Déjà fait en Story 51.1)

- [x] Tâche 2 : Résoudre les conflits de nommage pour les barrels (AC: 1, 5)
  - [x] Déplacer `ApiError` dans `src/api/client.ts` et le re-exporter une seule fois.
  - [x] Renommer les fonctions `t` génériques en `tConsultations` et `tAstrologers` dans leurs fichiers respectifs.

- [x] Tâche 3 : Migrer les imports du codebase (AC: 2, 3, 4, 6)
  - [x] Utilisation massive de scripts PowerShell pour remplacer `../../../` par les aliases correspondants.
  - [x] Remplacement de `@types` par `@app-types` pour éviter les conflits avec le namespace TypeScript standard.
  - [x] Mise à jour des tests pour utiliser `@api` et garantir que `instanceof ApiError` fonctionne (partage de la même référence de classe).

- [x] Tâche 4 : Validation (AC: 5, 7)
  - [x] `npm run build` (tsc baselines vérifiées).
  - [x] `npm run test` — 1079 tests réussis.

## Dev Notes

### Gestion des conflits Barrels

L'export en étoile (`export *`) a nécessité quelques ajustements :
1. **ApiError** : présent dans 2 fichiers API, il a été centralisé dans `client.ts` pour garantir une instance unique et éviter les erreurs de "duplicate export".
2. **Fonctions t()** : présentes dans plusieurs fichiers i18n, elles ont été renommées de manière spécifique au domaine pour permettre l'export groupé dans `@i18n`.

### Path Aliases additionnels

L'alias `@app-types` a été ajouté pour `src/types` car le nom `@types` entrait en conflit avec la résolution automatique des types de `node_modules` par TypeScript.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Création des barrels pour tous les dossiers racine de `src/`.
- Suppression totale des imports relatifs profonds (`../../../`).
- Centralisation de `ApiError` pour la cohérence du typage et des tests.
- Migration de l'ensemble de la suite de tests (80 fichiers) vers les nouveaux aliases.
- Validation via 1079 tests réussis.

### File List
- `frontend/src/i18n/index.ts`
- `frontend/src/api/index.ts`
- `frontend/src/state/index.ts`
- `frontend/src/pages/index.ts`
- `frontend/src/api/client.ts`
- `frontend/src/api/dailyPrediction.ts`
- `frontend/src/api/natalChart.ts`
- `frontend/src/i18n/consultations.ts`
- `frontend/src/i18n/astrologers.ts`
- (et ~100 fichiers impactés par la migration des imports)
