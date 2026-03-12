# Story 44.5: Verrouiller QA et garde-fous de bruit sur les valeurs de bascule

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a QA engineer,
I want vérifier que les valeurs de mouvement restent vraies, lisibles et non bruitées,
so that les moments clés enrichis ne sur-vendent pas des micro-variations et restent cohérents en plusieurs langues.

## Acceptance Criteria

1. Les tests couvrent au minimum un cas d'augmentation nette, un cas d'atténuation, un cas de redistribution et un cas de mouvement sous seuil non affiché.
2. Les suites backend vérifient les calculs de `movement` et `category_deltas` sur des bascules représentatives.
3. Les suites frontend vérifient les rendus FR et EN avec et sans chiffres détaillés.
4. Les régressions connues restent couvertes: faux pivot de minuit, transition `avant -> après` incohérente, disparition complète des moments clés valides.
5. Les garde-fous empêchent l'affichage de chiffres bruts instables, de décimales inutiles et de messages contradictoires entre `Implication` et `Mouvement`.

## Tasks / Subtasks

- [ ] Task 1: Étendre les cas backend de calcul de mouvement (AC: 1, 2)
  - [ ] Ajouter des cas d'augmentation nette et d'atténuation
  - [ ] Ajouter un cas de redistribution entre catégories
  - [ ] Ajouter un cas sous seuil qui ne doit pas polluer la sortie publique

- [ ] Task 2: Verrouiller le rendu frontend multilingue (AC: 3, 5)
  - [ ] Vérifier FR et EN avec rendu qualitatif
  - [ ] Vérifier FR et EN avec valeurs détaillées si elles sont affichées
  - [ ] Vérifier la stabilité du formatage des nombres et l'absence de décimales bruyantes

- [ ] Task 3: Couvrir les régressions et incohérences produit (AC: 4, 5)
  - [ ] Verrouiller les faux mouvements sur catégories visiblement identiques
  - [ ] Verrouiller la cohérence entre `Transition`, `Mouvement`, `Implication` et `Impacts`
  - [ ] Revalider les cas de pivot tardif et de fin de journée

## Dev Notes

- Cette story doit servir de garde-fou final de l'Epic 44.
- Les seuils décidés en 44.2 doivent être testables et documentés.
- La QA doit rester orientée produit, pas seulement technique.

### Project Structure Notes

- Backend principal:
  - `backend/app/tests/integration/test_daily_prediction_api.py`
  - `backend/app/tests/unit/prediction/`
- Frontend principal:
  - `frontend/src/tests/TurningPointsEnriched.test.tsx`
  - `frontend/src/tests/predictionI18n.test.ts`
  - `frontend/src/tests/TodayPage.test.tsx`

### Technical Requirements

- Les tests doivent séparer les attentes métier backend et les attentes de wording frontend.
- Les nombres affichés publiquement doivent rester bornés et stables.
- Les suites doivent rester assez ciblées pour éviter des tests snapshot trop fragiles.

### Architecture Compliance

- Les garde-fous QA couvrent à la fois le contrat backend, la traduction i18n et le rendu UI.
- Les tests doivent réutiliser les fixtures représentatives déjà construites en Epic 43 quand c'est pertinent.

### Testing Requirements

- Ajouter des tests backend pour le calcul des deltas.
- Ajouter des tests frontend pour les variantes de rendu et les fallbacks.
- Vérifier explicitement le cas “mouvement sous seuil non affiché”.

### Previous Story Intelligence

- Epic 43 a déjà verrouillé les régressions sur faux pivots de minuit, disparition des moments clés, et wording trompeur `before == after`.
- Epic 44 doit préserver ces garde-fous tout en ajoutant des valeurs quantitatives.

### Git Intelligence Summary

- Les derniers correctifs ont montré que les incohérences les plus visibles proviennent souvent du rendu frontend, même si la donnée backend est correcte.
- Les tests doivent donc croiser backend et frontend, pas seulement l'un des deux.

### References

- [Source: frontend/src/tests/TurningPointsEnriched.test.tsx]
- [Source: frontend/src/tests/predictionI18n.test.ts]
- [Source: frontend/src/tests/TodayPage.test.tsx]
- [Source: backend/app/tests/integration/test_daily_prediction_api.py]
- [Source: _bmad-output/implementation-artifacts/43-4-verrouiller-qa-et-coherence-multilingue-des-moments-cles.md]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
