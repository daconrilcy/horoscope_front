# Story 47.2: Exposer le précheck de complétude et de précision des consultations

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend/frontend integrator,
I want introduire un précheck consultation dédié avant la génération,
so that `/consultations` sache réutiliser le profil natal existant, afficher le niveau réel de précision et annoncer proprement les modes disponibles avant d'engager l'utilisateur.

## Acceptance Criteria

1. Le backend expose un contrat consultation dédié, par exemple `POST /v1/consultations/precheck`, prenant au minimum `consultation_type` et retournant `user_profile_quality`, `precision_level`, `missing_fields`, `available_modes`, `fallback_mode` éventuel et `blocking_reasons`.
2. Le calcul du précheck réutilise les sources de vérité existantes (`/v1/users/me/birth-data`, `UserBirthProfileService`, `UserAstroProfileService`, éventuelle présence du thème natal) au lieu de dupliquer les règles côté frontend.
3. Le précheck distingue explicitement les situations `nominal`, `degraded` et `blocked`, y compris le cas `birth_profile_not_found` et le cas `birth_time` manquant.
4. Le contrat de réponse respecte les conventions API existantes du projet (`data` + `meta.request_id`, erreurs normalisées).
5. Le frontend consultations consomme ce contrat via un client API centralisé et peut afficher un état de préparation sans interprétation métier locale supplémentaire.
6. Les enums partagées consultation sont figées dès cette story pour éviter toute dérive entre backend, frontend et tests.
7. Les tests backend et frontend couvrent au minimum les cas `profil complet`, `profil sans heure`, `profil absent` et `cas bloquant`.

## Tasks / Subtasks

- [ ] Task 1: Définir le modèle de données du précheck consultation (AC: 1, 3, 4, 6)
  - [ ] Créer les schémas Pydantic consultation pour le précheck
  - [ ] Définir des enums ou constantes stables pour `user_profile_quality`, `precision_level`, `available_modes`, `fallback_mode`, `safeguard_issue`
  - [ ] Prévoir un champ de version ou un contrat explicitement versionnable
  - [ ] Ajouter un exemple JSON canonique de requête / réponse `POST /v1/consultations/precheck`

- [ ] Task 2: Implémenter un service backend consultation-precheck réutilisant les services existants (AC: 1, 2, 3)
  - [ ] Ajouter une couche `services/consultation_*` dédiée au lieu d'enfouir la logique dans le routeur
  - [ ] Réutiliser `UserBirthProfileService` et `UserAstroProfileService`
  - [ ] Gérer proprement les cas sans profil, sans heure et sans données minimales
  - [ ] Journaliser la résolution du précheck avec `request_id`

- [ ] Task 3: Exposer le routeur API consultation et un client frontend centralisé (AC: 4, 5)
  - [ ] Ajouter le routeur `/v1/consultations/*` dans `backend/app/api/v1/routers/`
  - [ ] Créer `frontend/src/api/consultations.ts` pour le précheck
  - [ ] Mapper uniformément les erreurs backend vers des messages exploitables par l'UI consultations

- [ ] Task 4: Intégrer l'affichage consultation-ready dans le parcours (AC: 5)
  - [ ] Préparer les états `loading`, `error`, `ready`, `degraded`, `blocked` côté consultations
  - [ ] Éviter de calculer des règles métier dupliquées dans `ConsultationWizardPage`
  - [ ] Laisser la collecte conditionnelle détaillée à la story suivante

- [ ] Task 5: Tester le contrat et les cas limites (AC: 6)
  - [ ] Ajouter des tests backend de contrat et de règles
  - [ ] Ajouter des tests frontend pour la consommation du précheck
  - [ ] Vérifier la cohérence `404/422` existante avec les nouveaux cas consultation

## Dev Notes

- Le précheck est la pièce manquante la plus critique entre le backlog de référence et le code actuel: aujourd'hui la génération échoue tardivement si le profil natal manque.
- Le projet possède déjà des signaux réutilisables (`birth_time` nullable, `astro_profile.missing_birth_time`) qu'il faut agréger dans une couche consultation unique.
- Cette story doit rester consultation-centric: elle n'a pas vocation à refondre les endpoints `/users/me/birth-data`.

### Shared Enums Locked For Epic 47

- `precision_level`: `high`, `medium`, `limited`, `blocked`
- `fallback_mode`: `user_no_birth_time`, `other_no_birth_time`, `relation_user_only`, `timing_degraded`, `blocking_missing_data`, `safeguard_reframed`, `safeguard_refused`
- `safeguard_issue`: `health`, `emotional_distress`, `obsessive_relation`, `pregnancy`, `death`, `legal_finance`, `third_party_manipulation`

Notes de contrat:

- En mode nominal, `fallback_mode` et `safeguard_issue` valent `null`.
- `precision_level` reste générique et portable; la cause précise de dégradation est portée par `fallback_mode`.

### Canonical JSON Example: `POST /v1/consultations/precheck`

Request:

```json
{
  "consultation_type": "relation",
  "question": "Est-ce que cette relation a un potentiel durable ?",
  "horizon": "next_6_months",
  "other_person": {
    "birth_date": "1992-07-11",
    "birth_time_known": false,
    "birth_place": "Lyon, France"
  }
}
```

Response:

```json
{
  "data": {
    "consultation_type": "relation",
    "user_profile_quality": "complete",
    "precision_level": "medium",
    "status": "degraded",
    "missing_fields": [],
    "available_modes": [
      "relation_full_other_no_time",
      "relation_user_only"
    ],
    "fallback_mode": "other_no_birth_time",
    "safeguard_issue": null,
    "blocking_reasons": []
  },
  "meta": {
    "request_id": "req_consult_precheck_123",
    "contract_version": "consultation-precheck.v1"
  }
}
```

### Previous Story Intelligence

- L'epic 46 a laissé la responsabilité du cadrage métier côté frontend. Cette dette doit être inversée ici.
- Le client `frontend/src/api/guidance.ts` montre déjà le pattern attendu pour un client API centralisé avec erreur normalisée.
- `BirthProfilePage` et `birthProfile.ts` prouvent qu'on peut relire le profil natal sans toucher au reste de l'app.

### Project Structure Notes

- Backend probable:
  - `backend/app/api/v1/routers/consultations.py`
  - `backend/app/services/consultation_precheck_service.py`
  - `backend/app/services/user_birth_profile_service.py`
  - `backend/app/services/user_astro_profile_service.py`
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Frontend probable:
  - `frontend/src/api/consultations.ts`
  - `frontend/src/pages/ConsultationWizardPage.tsx`
  - `frontend/src/state/consultationStore.tsx`
  - `frontend/src/tests/`

### Technical Requirements

- Le frontend ne doit pas réencoder les règles `full / no_birth_time / blocking`.
- Le service backend doit être déterministe et facilement testable.
- Les noms d'états et de champs doivent être stables dès cette story, car ils alimenteront fallback, dossier et résultat.
- Les enums ci-dessus deviennent la source de vérité contractuelle pour l'epic 47 et doivent être réutilisées à l'identique côté frontend, backend et fixtures.

### Architecture Compliance

- Respecter la séparation `router -> service -> service existant`.
- Réutiliser les conventions API du monorepo (`data`, `meta`, `error`).
- Ne pas introduire de dépendance cross-feature côté dashboard, chat ou profil.

### Testing Requirements

- Backend: tests unitaires du resolver + tests d'intégration du routeur.
- Frontend: tests du client API et de l'affichage de statut.
- Vérifier dans le venv: `ruff check .` et suites ciblées frontend/backend pendant l'implémentation.

### References

- [Source: docs/backlog_epics_consultation_complete.md#6-epic-cc-02-precheck-de-completude-profil-et-eligibilite-consultation]
- [Source: docs/backlog_epics_consultation_complete.md#18-criteres-dacceptation-transverses-reutilisables-dans-les-stories]
- [Source: _bmad-output/planning-artifacts/epic-47-consultation-complete-depuis-consultations.md]
- [Source: frontend/src/api/birthProfile.ts]
- [Source: frontend/src/api/guidance.ts]
- [Source: backend/app/api/v1/routers/users.py]
- [Source: backend/app/services/user_birth_profile_service.py]
- [Source: backend/app/services/user_astro_profile_service.py]
- [Source: backend/app/api/v1/routers/guidance.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 47 et du backlog consultation complète.

### Completion Notes List

- Artefact créé uniquement; aucun code applicatif n'a été modifié.
- Le routeur consultation dédié devient ici la base des stories 47.4 à 47.6.

### File List

- TBD pendant `dev-story`
