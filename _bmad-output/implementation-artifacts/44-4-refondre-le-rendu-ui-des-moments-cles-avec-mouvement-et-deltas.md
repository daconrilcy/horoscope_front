# Story 44.4: Refondre le rendu UI des moments clés avec mouvement et deltas

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur consultant le daily,
I want voir pour chaque bascule quelles forces montent, reculent ou se redistribuent,
so that je comprenne visuellement pourquoi le moment mérite mon attention.

## Acceptance Criteria

1. Chaque carte `Moment clé` peut afficher un bloc `Mouvement` ou `Évolution` basé sur `movement` et `category_deltas`.
2. Le rendu met en avant au maximum les 2 ou 3 variations les plus utiles, avec une hiérarchie claire et sans surcharge mobile.
3. Les catégories ajoutées, retirées ou stabilisées sont distinguées visuellement.
4. Le composant conserve un fallback lisible quand les nouveaux champs ne sont pas présents.
5. Le rendu reste cohérent avec les sections existantes `Pourquoi`, `Transition`, `Implication` et `Impacts`.

## Tasks / Subtasks

- [ ] Task 1: Concevoir la hiérarchie visuelle du bloc de mouvement (AC: 1, 2, 5)
  - [ ] Ajouter une zone dédiée sous la transition existante
  - [ ] Mettre en avant le mouvement global avant les variations locales
  - [ ] Limiter l'encombrement sur mobile

- [ ] Task 2: Rendre les deltas de catégories lisibles (AC: 2, 3)
  - [ ] Afficher les catégories qui montent, reculent ou restent dominantes
  - [ ] Utiliser une iconographie ou un marquage simple pour le sens de variation
  - [ ] Afficher au plus 2 ou 3 lignes de variation

- [ ] Task 3: Préserver les fallbacks et la cohérence produit (AC: 4, 5)
  - [ ] Conserver le rendu actuel si `movement` est absent
  - [ ] Éviter de dupliquer l'information entre `Transition`, `Mouvement` et `Impacts`
  - [ ] Vérifier la cohérence avec l'agenda du jour et les autres blocs du daily

## Dev Notes

- Cette story porte sur la présentation UI des nouvelles valeurs.
- Le rendu doit rester sobre et scannable; l'objectif n'est pas de créer un panneau expert.
- Il faudra probablement utiliser une formulation qualitative en priorité et réserver les chiffres détaillés à un second niveau.

### Project Structure Notes

- Frontend principal:
  - `frontend/src/components/prediction/TurningPointsList.tsx`
  - `frontend/src/pages/TodayPage.tsx`
  - `frontend/src/utils/dailyAstrology.ts`
  - `frontend/src/types/dailyPrediction.ts`

### Technical Requirements

- Le composant doit supporter les payloads enrichis et legacy.
- Les valeurs ne doivent pas casser le layout mobile.
- Les variations visibles doivent être limitées et triées.

### Architecture Compliance

- Les composants UI consomment les helpers i18n et les types structurés.
- La logique de détection métier des variations reste côté backend.

### Testing Requirements

- Ajouter des tests de rendu pour les cas enrichis avec montée, baisse et redistribution.
- Vérifier le fallback sans `movement`.
- Vérifier l'absence de surcharge visuelle ou de duplication textuelle.

### Previous Story Intelligence

- Epic 43 a déjà introduit les sections `Pourquoi`, `Transition`, `Implication`, `Impacts`.
- Les bugs récents ont montré que les transitions deviennent vite incohérentes si le composant tronque trop de catégories ou recompose mal le diff.

### Git Intelligence Summary

- Les composants des moments clés ont déjà été corrigés plusieurs fois pour supprimer les faux pivots et les transitions trompeuses.
- Cette story doit enrichir sans casser cette sobriété retrouvée.

### References

- [Source: frontend/src/components/prediction/TurningPointsList.tsx]
- [Source: frontend/src/pages/TodayPage.tsx]
- [Source: frontend/src/utils/dailyAstrology.ts]
- [Source: _bmad-output/implementation-artifacts/43-3-refaire-le-rendu-ui-des-moments-cles.md]
- [Source: user request 2026-03-12 — “Travail monte nettement / Argent se retire / Santé reste dominante”]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
