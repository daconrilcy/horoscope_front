# Story 44.2: Calculer et projeter les deltas de mouvement des bascules

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend engineer,
I want calculer des deltas de mouvement fiables autour de chaque turning point,
so that les valeurs projetées justifient réellement le passage d'un état à l'autre sans surinterpréter le bruit.

## Acceptance Criteria

1. Le backend calcule `previous_composite`, `next_composite` et `delta_composite` à partir de l'état juste avant et juste après la bascule.
2. Le backend calcule `category_deltas` à partir des catégories dominantes avant/après, avec une règle explicite de tri et de limitation aux variations les plus utiles.
3. Le backend classe le mouvement au minimum entre `upshift`, `downshift` et `redistribution`, de façon cohérente avec `change_type`.
4. Des seuils empêchent d'exposer des micro-variations non significatives comme des mouvements forts.
5. Les journées calmes ou bascules faibles restent rendues sans contradiction entre `change_type`, `transition` et valeurs de mouvement.

## Tasks / Subtasks

- [ ] Task 1: Définir la source de calcul des deltas autour d'une bascule (AC: 1, 3)
  - [ ] Identifier l'état public ou intermédiaire utilisé juste avant et juste après `occurred_at_local`
  - [ ] Définir le calcul de `delta_composite` et de `direction`
  - [ ] Garantir un comportement stable sur les bords de journée

- [ ] Task 2: Calculer les variations de catégories utiles (AC: 2, 4)
  - [ ] Comparer les catégories dominantes avant/après avec une règle déterministe
  - [ ] Trier les variations par amplitude absolue
  - [ ] Limiter les `category_deltas` aux 2 ou 3 changements les plus utiles

- [ ] Task 3: Introduire les garde-fous de bruit métier (AC: 4, 5)
  - [ ] Définir des seuils minimaux pour masquer les micro-mouvements
  - [ ] Assurer la cohérence entre `change_type`, `direction` et catégories affichées
  - [ ] Prévoir un fallback sobre quand les variations existent mais restent sous seuil

- [ ] Task 4: Projeter les nouvelles valeurs dans le payload public (AC: 1, 2, 3, 5)
  - [ ] Alimenter `movement` et `category_deltas` dans la projection publique
  - [ ] Conserver la compatibilité des turning points enrichis et legacy
  - [ ] Vérifier qu'aucune contradiction visuelle n'est injectée dans les données publiques

## Dev Notes

- Cette story porte sur la logique métier et la projection backend.
- Le calcul doit être explicable et déterministe; pas de heuristique opaque dépendante du frontend.
- Les seuils doivent être documentés pour que la QA puisse verrouiller le bruit en 44.5.

### Project Structure Notes

- Backend principal:
  - `backend/app/prediction/public_projection.py`
  - `backend/app/prediction/daily_prediction_evidence_builder.py`
  - `backend/app/prediction/schemas.py`
  - éventuellement les helpers de turning points déjà introduits en Epic 43

### Technical Requirements

- `direction` est un enum stable côté backend.
- Les calculs doivent rester cohérents sur des turning points en fin de journée et sur les journées plates.
- Les nouvelles valeurs doivent être calculées sans casser les budgets runtime des projections publiques.

### Architecture Compliance

- La dérivation des valeurs se fait dans la couche de projection publique ou un helper backend dédié.
- Le backend ne produit toujours pas de wording final localisé.

### Testing Requirements

- Ajouter des tests backend couvrant `upshift`, `downshift`, `redistribution`.
- Ajouter des tests de seuil pour les mouvements trop faibles.
- Vérifier la cohérence sur des payloads de journées calmes et de journées actives.

### Previous Story Intelligence

- Epic 43 a déjà montré que les transitions deviennent incohérentes dès que le frontend doit déduire seul le vrai changement.
- Les cas de faux `before == after` apparent doivent être évités dès le calcul backend.

### Git Intelligence Summary

- Les derniers correctifs ont corrigé des truncations frontend qui masquaient l'émergence d'une troisième catégorie.
- Ici, le backend doit livrer assez d'information pour empêcher ce type de faux égalité.

### References

- [Source: backend/app/prediction/public_projection.py]
- [Source: backend/app/prediction/daily_prediction_evidence_builder.py]
- [Source: backend/app/prediction/schemas.py]
- [Source: _bmad-output/implementation-artifacts/43-1-structurer-une-semantique-explicable-des-bascules.md]
- [Source: user request 2026-03-12 — “expliquer non seulement quoi change, mais aussi de combien et dans quel sens”]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
