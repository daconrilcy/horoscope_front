# Story 47.7: Verrouiller QA, observabilité et non-régression des consultations complètes

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a QA and product consistency owner,
I want verrouiller la nouvelle mouture des consultations complètes par des tests, du tracking et un gate documentaire final,
so that l'epic 47 puisse être implémenté sans régression sur les parcours existants et avec une visibilité claire sur précision, fallbacks et erreurs.

## Acceptance Criteria

1. Une matrice QA explicite couvre au minimum les parcours `period`, `work`, `orientation`, `relation`, `timing`, ainsi que les cas `nominal`, `degraded`, `blocked` et `legacy history`.
2. Les événements et logs métier consultation couvrent au minimum l'entrée dans `/consultations`, le précheck, la sélection du fallback, la génération, l'échec de génération, l'ouverture d'un résultat et l'ouverture dans le chat.
3. Des fixtures de test permettent de rejouer des profils utilisateur complets, sans heure, absents, et des profils tiers partiels.
4. Les tests frontend et backend garantissent la stabilité des routes `/consultations`, `/consultations/new`, `/consultations/result`, de l'historique local et du prefill chat.
5. Les artefacts BMAD de l'epic 47 et le gate final documentent les limites retenues pour éviter toute régression hors scope, notamment l'absence de refonte du chat, du profil et de la persistance DB globale.
6. La QA couvre explicitement la matrice de safeguards consultation et vérifie les issues `fallback`, `refusal` et `reframing` sur les catégories sensibles retenues pour le MVP.
7. Les wording `fallback_mode` critiques sont verrouillés par snapshots UI ciblés, y compris pour `relation` et `timing`, sans imposer de snapshots globaux sur toutes les pages.
8. Un gate final liste les validations automatiques attendues, les validations manuelles à exécuter et les risques résiduels acceptés.

## Tasks / Subtasks

- [ ] Task 1: Formaliser la matrice QA consultation complète (AC: 1, 4)
  - [ ] Lister les scénarios critiques frontend/backend par story 47.x
  - [ ] Couvrir les branches nominales, dégradées, bloquantes et legacy
  - [ ] Inclure explicitement l'historique local et `open in chat`
  - [ ] Ajouter la matrice safeguards et wording contractuel au plan de test

- [ ] Task 2: Instrumenter les événements et logs consultation (AC: 2)
  - [ ] Définir le plan de tracking frontend consultation
  - [ ] Définir les logs backend consultation-centric
  - [ ] Vérifier la corrélation avec `request_id` et les métadonnées `route_key / fallback_mode / precision_level`

- [ ] Task 3: Préparer fixtures et jeux de données (AC: 3)
  - [ ] Ajouter des fixtures utilisateur complet / sans heure / sans profil
  - [ ] Ajouter des fixtures tiers partiel / heure inconnue
  - [ ] Réutiliser les patterns de tests existants au lieu de créer des harness isolés

- [ ] Task 4: Verrouiller les suites de non-régression (AC: 4, 5)
  - [ ] Étendre les tests consultations frontend existants
  - [ ] Ajouter ou étendre les tests backend consultation
  - [ ] Vérifier explicitement la stabilité des routes et du localStorage
  - [ ] Ajouter des tests ciblés sur refus / recadrage et des snapshots UI sur wording de fallback critique

- [ ] Task 5: Produire le gate final epic 47 (AC: 5, 8)
  - [ ] Résumer validations automatiques et manuelles
  - [ ] Lister les limites fonctionnelles assumées
  - [ ] Lister les risques résiduels et les prérequis avant fermeture d'epic

## Dev Notes

- Le backlog consultation complète insiste sur l'observabilité métier et la QA transverse. Cette story doit être traitée comme un verrou final, pas comme un nettoyage cosmétique.
- L'epic 46 a déjà montré l'intérêt d'un closing gate et d'une matrice explicite. Il faut reprendre cette discipline avec les nouvelles branches `precheck / fallback / consultation generate`.
- Les futures implémentations doivent rester confinées au code consultations et à leurs tests associés; le gate doit le rappeler noir sur blanc.

### Previous Story Intelligence

- La story 46.6 a déjà posé un précédent utile: gate final, grep ciblé, vérifications de routes et d'historique.
- Les stories 47.2 à 47.6 ajoutent de nouveaux états métier; cette story doit s'assurer qu'ils sont tous observables et testés.
- Le parcours consultations est déjà bien couvert en frontend; il faut prolonger cette approche plutôt que repartir de zéro.

### Project Structure Notes

- Fichiers et dossiers probables:
  - `frontend/src/tests/*consultation*`
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
  - `frontend/src/utils/analytics.ts`
  - `backend/app/infra/observability/metrics.py`
  - `_bmad-output/test-artifacts/`
  - `_bmad-output/implementation-artifacts/47-*.md`

### Technical Requirements

- Le tracking consultation doit rester parcimonieux et aligné avec les conventions existantes.
- Les logs doivent suffire à comprendre un run sans exposer d'information personnelle inutile.
- Le gate final doit mentionner explicitement les validations venv / lint / tests attendues pendant l'implémentation.
- Décision QA figée: snapshots UI obligatoires uniquement pour les libellés critiques pilotés par `fallback_mode` et `safeguard_issue`; pas de snapshots de page complets si un test plus ciblé couvre mieux l'intention.

### Architecture Compliance

- Réutiliser les patterns de tests et d'observabilité déjà présents dans le repo.
- Garder les événements consultation séparés des autres features.
- Ne pas transformer cette story en refonte globale du monitoring applicatif.

### Testing Requirements

- Frontend: états wizard, precheck, fallback, résultat, historique, chat prefill.
- Backend: précheck, fallback, génération, contrats API.
- Safeguards: refus, recadrage, wording contractuel.
- Snapshots UI: obligatoires sur les wording fallback critiques, facultatifs ailleurs.
- Vérifier dans le venv les commandes Python du backend pendant la mise en oeuvre réelle.

### References

- [Source: docs/backlog_epics_consultation_complete.md#14-epic-cc-10-analytics-qa-observabilite-et-pilotage]
- [Source: docs/backlog_epics_consultation_complete.md#18-criteres-dacceptation-transverses-reutilisables-dans-les-stories]
- [Source: _bmad-output/planning-artifacts/epic-47-consultation-complete-depuis-consultations.md]
- [Source: _bmad-output/implementation-artifacts/46-6-verrouiller-qa-coherence-bmad-et-non-regression-de-la-refonte.md]
- [Source: frontend/src/tests/ConsultationsPage.test.tsx]
- [Source: frontend/src/tests/ConsultationMigration.test.tsx]
- [Source: frontend/src/tests/ConsultationReconnection.test.tsx]
- [Source: backend/app/infra/observability/metrics.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 47 et du backlog consultation complète.

### Completion Notes List

- Artefact créé uniquement; aucun code applicatif n'a été modifié.
- Cette story est le verrou documentaire et QA de l'epic 47, à l'image du closing gate 46 mais adaptée au nouveau périmètre.

### File List

- TBD pendant `dev-story`
