# Story 46.6: Verrouiller QA, cohérence BMAD et non-régression de la refonte

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a QA and product consistency owner,
I want verrouiller la refonte consultations sans tirage par des tests, des gates et un réalignement documentaire BMAD,
so that le périmètre astrologique soit cohérent dans le produit, dans le code et dans les artefacts de référence.

## Acceptance Criteria

- [x] 1. Une matrice de non-régression explicite couvre au minimum:
   - [x] navigation `/dashboard` -> `/consultations`
   - [x] création d'une consultation `dating`
   - [x] création d'une consultation `pro`
   - [x] création d'une consultation `event`
   - [x] création d'une consultation `free`
   - [x] ouverture d'une consultation sauvegardée
   - [x] ouverture dans le chat
- [x] 2. Les tests frontend et backend nécessaires aux stories 46.1 à 46.5 sont en place et reflètent le nouveau périmètre sans tirage.
- [x] 3. Une vérification ciblée confirme qu'aucune chaîne UI visible ne contient encore `tirage`, `tarot`, `runes` ou `cartes` dans le parcours consultations/dashboard/navigation.
- [x] 4. Les artefacts BMAD affectés par le changement sont revus et réalignés, au minimum:
   - [x] `11-2-modules-tarot-runes-derriere-feature-flags.md`
   - [x] `16-5-consultations-pages.md`
   - [x] `17-1-fondations-ui-tokens-typo-lucide.md`
   - [x] `17-5-raccourcis-shortcut-card.md`
   - [x] `45-2-creer-la-landing-dashboard-avec-resume-et-hub-d-activites.md`
- [x] 5. La documentation résultante explique clairement que `/consultations` reste une route stable mais que le périmètre produit a été recentré sur la guidance astrologique ciblée.
- [x] 6. Un gate final de vérification liste les risques restants, les limites éventuelles et les validations manuelles à exécuter avant clôture de l'epic.

## Tasks / Subtasks

- [x] Task 1: Formaliser la matrice de QA de l'epic 46 (AC: 1, 2, 6)
  - [x] Lister les scénarios critiques front/back et leurs dépendances par story
  - [x] Identifier ce qui relève des tests automatisés versus smoke manuel
  - [x] Intégrer les cas de migration localStorage et de deep links

- [x] Task 2: Verrouiller les suites frontend et backend finales (AC: 1, 2, 3)
  - [x] Vérifier les tests du wizard, du résultat, du nav, du dashboard et du chat prefill
  - [x] Vérifier les tests du backend guidance et du retrait tarot/runes
  - [x] Ajouter si nécessaire une recherche automatisée ou un test de présence résiduelle des termes interdits sur les surfaces critiques

- [x] Task 3: Réaligner les artefacts BMAD existants (AC: 4, 5)
  - [x] Mettre à jour la story 16.5 pour refléter le nouveau périmètre consultations sans tirage
  - [x] Marquer la story 11.2 comme fonctionnalité retirée ou dépassée par l'epic 46
  - [x] Corriger les docs 17.1, 17.5 et 45.2 pour retirer `Tirages` et `Tirage du jour`
  - [x] Vérifier les liens croisés et les références depuis les nouveaux story docs 46.x

- [x] Task 4: Produire un gate final de clôture de l'epic (AC: 6)
  - [x] Résumer les validations automatiques passées
  - [x] Résumer les validations manuelles restantes
  - [x] Lister explicitement les risques résiduels si certains éléments restent hors scope
  - [x] Préparer la base de rétro si une retrospective epic est lancée ensuite

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- ConsultationReconnection.test.tsx, ConsultationMigration.test.tsx, ConsultationsPage.test.tsx verified.
- Backend pytest suite verified (1364 tests).
- Grep check for forbidden terms performed.
- epic-46-closing-gate.md created.

### Completion Notes List

- All critical user journeys verified via automated tests.
- Backend orchestration fully cleaned from tarot/runes references.
- Documentation artefacts (11.2, 16.5, 17.1, 17.5, 45.2) updated to reflect the new scope.
- Migration from legacy history items to V2 schema is robust.
- Post-review correction 2026-03-13: la matrice QA a été renforcée sur la saisie d'objectif/horizon, la compatibilité de l'API guidance et le nettoyage backend des derniers reliquats tarot.

### File List

- _bmad-output/test-artifacts/epic-46-closing-gate.md
- _bmad-output/implementation-artifacts/11-2-modules-tarot-runes-derriere-feature-flags.md
- _bmad-output/implementation-artifacts/16-5-consultations-pages.md
- _bmad-output/implementation-artifacts/17-1-fondations-ui-tokens-typo-lucide.md
- _bmad-output/implementation-artifacts/17-5-raccourcis-shortcut-card.md
- _bmad-output/implementation-artifacts/45-2-creer-la-landing-dashboard-avec-resume-et-hub-d-activites.md
- _bmad-output/implementation-artifacts/46-6-verrouiller-qa-coherence-bmad-et-non-regression-de-la-refonte.md
