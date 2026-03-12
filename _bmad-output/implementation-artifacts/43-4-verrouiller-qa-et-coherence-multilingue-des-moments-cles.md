# Story 43.4: Verrouiller QA et cohérence multilingue des moments clés

Status: ready-for-dev

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

- [ ] Task 1: Étendre les fixtures et cas QA frontend (AC: 1, 2, 4, 5)
  - [ ] Ajouter des fixtures structurées pour `emergence`, `recomposition`, `attenuation`
  - [ ] Ajouter un cas sans `primary_driver`
  - [ ] Ajouter un cas multilingue FR/EN

- [ ] Task 2: Verrouiller les garde-fous de wording (AC: 2, 3, 6)
  - [ ] Vérifier qu’aucune chaîne backend brute ne s’affiche dans les cartes enrichies
  - [ ] Vérifier les fallbacks legacy
  - [ ] Vérifier la stabilité des textes sur les payloads réduits

- [ ] Task 3: Couvrir les régressions connues (AC: 4, 5)
  - [ ] Verrouiller le non-retour du faux pivot `00:00`
  - [ ] Verrouiller le non-effacement complet des moments clés tardifs
  - [ ] Vérifier que l’agenda du jour reste cohérent avec les moments clés

## Dev Notes

- Cette story clôt l’extension Epic 43.
- Le but n’est pas seulement d’avoir des tests, mais d’éviter:
  - les faux moments
  - les phrases incohérentes entre langues
  - la dépendance à des chaînes backend non localisées
- Les fixtures doivent rester petites, lisibles et proches des vrais payloads daily.

### Project Structure Notes

- Frontend principal:
  - `frontend/src/tests/TodayPage.test.tsx`
  - `frontend/src/utils/dailyAstrology.test.ts`
  - `frontend/src/utils/predictionI18n.ts`
- Backend si nécessaire:
  - `backend/app/tests/integration/test_daily_prediction_api.py`
  - `backend/app/tests/unit/prediction/test_public_projection_evidence.py`

### Technical Requirements

- Les tests doivent pouvoir s’exécuter sans réseau ni dépendance externe supplémentaire.
- Les fixtures FR/EN doivent partager la même structure source.
- Les cas de fallback legacy doivent rester explicitement couverts.

### Architecture Compliance

- La QA doit couvrir toute la chaîne enrichie:
  - contrat public
  - mapping frontend
  - wording i18n
  - rendu utilisateur
- Ne pas créer une suite parallèle de tests si `TodayPage.test.tsx` et les helpers actuels suffisent à porter les invariants.

### Library / Framework Requirements

- Vitest + Testing Library côté frontend.
- Pytest existant côté backend si la projection publique est enrichie.

### File Structure Requirements

- Étendre les suites déjà existantes avant de créer de nouveaux ensembles de tests.
- Garder les fixtures proches des helpers `dailyAstrology` et du contrat `dailyPrediction`.

### Testing Requirements

- Ajouter au minimum:
  - un test FR et EN sur la même structure enrichie
  - un test sans driver
  - un test multi-drivers
  - un test de non-régression `00:00`
  - un test de compatibilité payload legacy

### Previous Story Intelligence

- 41.6 et les correctifs du 2026-03-11 ont déjà montré que les moments clés sont très sensibles aux frontières de ranges et aux blocs neutres; ces régressions doivent rester verrouillées. [Source: _bmad-output/implementation-artifacts/41-6-refactor-dashboard-moments-cles-et-agenda-du-jour.md]

### Git Intelligence Summary

- La récente stabilisation du dashboard a déjà ajouté `dailyAstrology.test.ts`; cette story doit s’appuyer dessus pour ajouter les nouveaux garde-fous, pas repartir de zéro.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.

### References

- [Source: user request 2026-03-12]
- [Source: frontend/src/tests/TodayPage.test.tsx]
- [Source: frontend/src/utils/dailyAstrology.test.ts]
- [Source: frontend/src/utils/predictionI18n.ts]
- [Source: backend/app/tests/integration/test_daily_prediction_api.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de la demande utilisateur du 2026-03-12.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

- `_bmad-output/implementation-artifacts/43-4-verrouiller-qa-et-coherence-multilingue-des-moments-cles.md`
