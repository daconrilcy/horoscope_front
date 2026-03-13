# Story 46.6: Verrouiller QA, cohérence BMAD et non-régression de la refonte

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a QA and product consistency owner,
I want verrouiller la refonte consultations sans tirage par des tests, des gates et un réalignement documentaire BMAD,
so that le périmètre astrologique soit cohérent dans le produit, dans le code et dans les artefacts de référence.

## Acceptance Criteria

1. Une matrice de non-régression explicite couvre au minimum:
   - navigation `/dashboard` -> `/consultations`
   - création d'une consultation `dating`
   - création d'une consultation `pro`
   - création d'une consultation `event`
   - création d'une consultation `free`
   - ouverture d'une consultation sauvegardée
   - ouverture dans le chat
2. Les tests frontend et backend nécessaires aux stories 46.1 à 46.5 sont en place et reflètent le nouveau périmètre sans tirage.
3. Une vérification ciblée confirme qu'aucune chaîne UI visible ne contient encore `tirage`, `tarot`, `runes` ou `cartes` dans le parcours consultations/dashboard/navigation.
4. Les artefacts BMAD affectés par le changement sont revus et réalignés, au minimum:
   - `11-2-modules-tarot-runes-derriere-feature-flags.md`
   - `16-5-consultations-pages.md`
   - `17-1-fondations-ui-tokens-typo-lucide.md`
   - `17-5-raccourcis-shortcut-card.md`
   - `45-2-creer-la-landing-dashboard-avec-resume-et-hub-d-activites.md`
5. La documentation résultante explique clairement que `/consultations` reste une route stable mais que le périmètre produit a été recentré sur la guidance astrologique ciblée.
6. Un gate final de vérification liste les risques restants, les limites éventuelles et les validations manuelles à exécuter avant clôture de l'epic.

## Tasks / Subtasks

- [ ] Task 1: Formaliser la matrice de QA de l'epic 46 (AC: 1, 2, 6)
  - [ ] Lister les scénarios critiques front/back et leurs dépendances par story
  - [ ] Identifier ce qui relève des tests automatisés versus smoke manuel
  - [ ] Intégrer les cas de migration localStorage et de deep links

- [ ] Task 2: Verrouiller les suites frontend et backend finales (AC: 1, 2, 3)
  - [ ] Vérifier les tests du wizard, du résultat, du nav, du dashboard et du chat prefill
  - [ ] Vérifier les tests du backend guidance et du retrait tarot/runes
  - [ ] Ajouter si nécessaire une recherche automatisée ou un test de présence résiduelle des termes interdits sur les surfaces critiques

- [ ] Task 3: Réaligner les artefacts BMAD existants (AC: 4, 5)
  - [ ] Mettre à jour la story 16.5 pour refléter le nouveau périmètre consultations sans tirage
  - [ ] Marquer la story 11.2 comme fonctionnalité retirée ou dépassée par l'epic 46
  - [ ] Corriger les docs 17.1, 17.5 et 45.2 pour retirer `Tirages` et `Tirage du jour`
  - [ ] Vérifier les liens croisés et les références depuis les nouveaux story docs 46.x

- [ ] Task 4: Produire un gate final de clôture de l'epic (AC: 6)
  - [ ] Résumer les validations automatiques passées
  - [ ] Résumer les validations manuelles restantes
  - [ ] Lister explicitement les risques résiduels si certains éléments restent hors scope
  - [ ] Préparer la base de rétro si une retrospective epic est lancée ensuite

## Dev Notes

- Cette story ne doit pas être traitée comme un simple lot de tests. Elle ferme la boucle produit/technique/documentaire de l'epic.
- Le réalignement BMAD est important ici car plusieurs artefacts existants documentent encore positivement le tirage comme une fonctionnalité valide.
- La vérification de termes résiduels doit être ciblée sur les surfaces utilisateur et les docs de référence, sans exiger de purger tout l'historique du repository.

### Previous Story Intelligence

- Story 43.4 et 45.4 montrent le format attendu pour verrouiller QA, cohérence multilingue et navigation.
- Story 16.5 contient une documentation très détaillée du parcours consultations d'origine; elle devra être amendée plutôt que laissée contradictoire.
- Story 11.2 documente l'introduction des modules tarot/runes; l'epic 46 doit clarifier qu'ils sont désormais retirés du périmètre produit.

### Project Structure Notes

- Artefacts BMAD à réviser:
  - `_bmad-output/implementation-artifacts/11-2-modules-tarot-runes-derriere-feature-flags.md`
  - `_bmad-output/implementation-artifacts/16-5-consultations-pages.md`
  - `_bmad-output/implementation-artifacts/17-1-fondations-ui-tokens-typo-lucide.md`
  - `_bmad-output/implementation-artifacts/17-5-raccourcis-shortcut-card.md`
  - `_bmad-output/implementation-artifacts/45-2-creer-la-landing-dashboard-avec-resume-et-hub-d-activites.md`
- Tests front/back dépendront des stories précédentes et devront être évalués globalement.

### Technical Requirements

- Le gate final doit être lisible et actionnable.
- Les docs mises à jour doivent rester compatibles avec l'historique du projet et expliciter le changement de périmètre.
- Les validations manuelles doivent couvrir les scénarios les plus risqués, notamment historique legacy et ouverture dans le chat.

### Architecture Compliance

- Le périmètre final documenté doit rester 100% astrologie pour les consultations.
- Les routes stables et le découplage frontend/backend doivent être rappelés dans les docs.
- Les BMAD artifacts doivent converger vers la même sémantique produit.

### Testing Requirements

- Réutiliser les suites existantes plutôt que créer des tests redondants.
- Ajouter seulement les tests de verrouillage manquants, notamment sur présence textuelle résiduelle et parcours critiques.
- Prévoir un smoke manuel final documenté.

### References

- [Source: _bmad-output/implementation-artifacts/43-4-verrouiller-qa-et-coherence-multilingue-des-moments-cles.md]
- [Source: _bmad-output/implementation-artifacts/45-4-verrouiller-qa-accessibilite-et-coherence-i18n-du-parcours-dashboard.md]
- [Source: _bmad-output/implementation-artifacts/11-2-modules-tarot-runes-derriere-feature-flags.md]
- [Source: _bmad-output/implementation-artifacts/16-5-consultations-pages.md]
- [Source: _bmad-output/implementation-artifacts/17-1-fondations-ui-tokens-typo-lucide.md]
- [Source: _bmad-output/implementation-artifacts/17-5-raccourcis-shortcut-card.md]
- [Source: _bmad-output/implementation-artifacts/45-2-creer-la-landing-dashboard-avec-resume-et-hub-d-activites.md]
- [Source: _bmad-output/planning-artifacts/epic-46-consultations-astrologiques-sans-tirage.md]

## Dev Agent Record

### Agent Model Used

TBD

### Debug Log References

### Completion Notes List

### File List
