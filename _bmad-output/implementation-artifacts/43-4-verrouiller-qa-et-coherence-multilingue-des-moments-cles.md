# Story 43.4: Verrouiller QA et cohérence multilingue des moments clés

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a QA engineer,
I want valider que les moments clés enrichis restent vrais, lisibles et localisés,
so that le produit ne surinterprète pas les bascules et conserve un wording cohérent en plusieurs langues.

## Acceptance Criteria

1. Les tests couvrent au minimum un cas d’émergence, un cas de recomposition et un cas d’atténuation.
2. Les suites frontend vérifient la production des textes FR et EN à partir de la même structure de données.
3. Aucun wording ne dépend directement de chaînes backend non localisées pour les cartes de moments clés enrichis.
4. Les cas sans driver, avec driver exact et avec plusieurs drivers restent stables et lisibles.
5. Les régressions sur faux pivots de minuit et disparition complète des moments clés restent verrouillées.
6. Le produit continue à rendre un fallback lisible avec un payload daily plus ancien.

## Tasks / Subtasks

- [x] Task 1: Étendre les fixtures et cas QA frontend (AC: 1, 2, 4, 5)
  - [x] Ajouter des fixtures structurées pour `emergence`, `recomposition`, `attenuation`
  - [x] Ajouter un cas sans `primary_driver`
  - [x] Ajouter un cas multilingue FR/EN

- [x] Task 2: Verrouiller les garde-fous de wording (AC: 2, 3, 6)
  - [x] Vérifier qu’aucune chaîne backend brute ne s’affiche dans les cartes enrichies
  - [x] Vérifier les fallbacks legacy
  - [x] Vérifier la stabilité des textes sur les payloads réduits

- [x] Task 3: Couvrir les régressions connues (AC: 4, 5)
  - [x] Verrouiller le non-retour du faux pivot `00:00`
  - [x] Verrouiller le non-effacement complet des moments clés tardifs
  - [x] Vérifier que l’agenda du jour reste cohérent avec les moments clés

## Dev Notes

- Added comprehensive tests in `TurningPointsEnriched.test.tsx`.
- Verified FR and EN rendering for all change types.
- Confirmed legacy fallback works as expected.
- Ensured no technical codes are exposed.

### Project Structure Notes

- Frontend principal:
  - `frontend/src/tests/TurningPointsEnriched.test.tsx`
  - `frontend/src/tests/predictionI18n.test.ts`

### Completion Notes List

- Created `TurningPointsEnriched.test.tsx` with edge cases: emergence, recomposition, attenuation, missing driver, empty next categories.
- Verified multilingual support in helpers and components.
- Validated that midnight pivots remain excluded (backend side logic verified in 43.1).
- Extended `TodayPage` regression coverage to keep impacts labels, humanized summaries, and non-technical fallbacks stable in FR and EN.
- Revalidated frontend targeted suites after post-implementation fixes on fallback normalization and enriched card rendering.
- Added a dedicated regression case to prevent misleading `before == after` wording when the actual movement is an emergence via a third category.
- Added a regression guard to ensure `Agenda du jour` marks slot cells when a displayed key moment falls inside the 2h window, including synthesized fallback moments on `flat_day`.

### File List

- `frontend/src/tests/TurningPointsEnriched.test.tsx`
- `frontend/src/tests/predictionI18n.test.ts`
- `frontend/src/tests/TodayPage.test.tsx`
