# Story 47.5: Construire le dossier de consultation et le routing LLM versionné

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend consultation architect,
I want introduire un `ConsultationDossier` et un routeur de génération consultation dédiés,
so that la feature `/consultations` cesse d'orchestrer sa logique métier côté frontend et dispose d'un contrat backend versionné, testable et compatible avec l'infrastructure LLM existante.

## Acceptance Criteria

1. Le backend définit un schéma `ConsultationDossier` v1 couvrant au minimum le type de consultation, la question, l'horizon, la qualité de profil, le `precision_level`, le `fallback_mode`, les éventuelles données tiers et les métadonnées utiles à la restitution.
2. Un endpoint de génération consultation dédié, par exemple `POST /v1/consultations/generate`, reçoit un input consultation et renvoie un payload consultation stable, sans laisser le frontend assembler lui-même la logique de route ou les métadonnées métier.
3. Le backend calcule un `route_key` déterministe à partir du dossier et versionne explicitement cette résolution.
4. Le routage consultation réutilise l'infrastructure existante (`GuidanceService`, `AIEngineAdapter`, `llm_orchestration`) au lieu de créer un second pipeline LLM parallèle.
5. Les logs consultation incluent au minimum `consultation_type`, `route_key`, `precision_level`, `fallback_mode`, `request_id` et le statut final.
6. Le resolver documente et teste au minimum une matrice MVP de résolution couvrant `period/full`, `period/no_birth_time`, `relation/full+full`, `relation/full+other_no_time`, `relation/user_only`, `timing/full`, `timing/degraded`.
7. Le routage consultation intègre la décision de safeguards issue de 47.4 et distingue explicitement route générative, refus et recadrage.
8. La liste exacte des `route_key` MVP partagées est figée et documentée dans cette story.
9. Les tests couvrent la construction du dossier, la résolution de route et la cohérence du contrat API de génération.

## Tasks / Subtasks

- [ ] Task 1: Définir le contrat métier `ConsultationDossier` (AC: 1)
  - [ ] Créer les schémas Pydantic consultation d'entrée et intermédiaires
  - [ ] Y porter explicitement qualité, précision, fallback, question et métadonnées
  - [ ] Prévoir la compatibilité future mono-profil / relation / timing

- [ ] Task 2: Implémenter le resolver `route_key` consultation (AC: 2, 3, 4, 6, 7, 8)
  - [ ] Définir une matrice minimale nominale / dégradée pour le MVP epic 47
  - [ ] Formaliser explicitement les résolutions attendues `period/full`, `period/no_birth_time`, `relation/full+full`, `relation/full+other_no_time`, `relation/user_only`, `timing/full`, `timing/degraded`
  - [ ] Conserver `guidance_contextual` comme brique interne possible, pas comme API frontend
  - [ ] Propager la décision safeguards `generate / refuse / reframe` dans la résolution
  - [ ] Rendre la résolution traçable et testable

- [ ] Task 3: Ajouter le service / routeur de génération consultation (AC: 2, 4, 5)
  - [ ] Introduire un service consultation dédié orchestrant précheck, fallback, dossier et appel LLM
  - [ ] Retourner un payload consultation structuré et stable
  - [ ] Journaliser le run consultation avec `request_id`

- [ ] Task 4: Préparer l'alignement prompt / use-case sans refonte globale du moteur LLM (AC: 3, 4, 7)
  - [ ] Définir si les nouvelles routes consultation pointent vers des use cases dédiés ou vers une composition contrôlée autour de `guidance_contextual`
  - [ ] Documenter pour chaque `route_key` MVP le use case / prompt attendu et les garde-fous associés
  - [ ] Éviter toute modification hors scope des flows chat et natal
  - [ ] Documenter clairement les placeholders et versions nécessaires

- [ ] Task 5: Tester dossier, routeur et contrat (AC: 6)
  - [ ] Ajouter des tests unitaires du dossier et du route resolver
  - [ ] Ajouter des tests d'intégration du routeur `/v1/consultations/generate`
  - [ ] Vérifier que les erreurs conservent les conventions API du projet

## Dev Notes

- Le point faible du flux actuel est l'orchestration distribuée entre le frontend et `guidance_contextual`. Le `ConsultationDossier` est le pivot qui manque.
- Il ne faut pas réécrire tout le moteur LLM. La bonne stratégie est d'encapsuler le chemin consultation dans un service dédié qui réutilise la pile existante.
- Cette story doit éviter l'explosion combinatoire: commencer par les routes MVP strictement nécessaires aux stories 47.3 et 47.4.
- Le `route_key` ne doit pas rester une abstraction technique vide. Il doit correspondre à une matrice métier compréhensible par les prompts, les tests et l'observabilité, avec un jeu MVP explicitement documenté.

### Locked MVP `route_key` Enum

- `period_full`
- `period_no_birth_time`
- `work_full`
- `work_no_birth_time`
- `orientation_full`
- `orientation_no_birth_time`
- `relation_full_full`
- `relation_full_other_no_time`
- `relation_user_only`
- `timing_full`
- `timing_degraded`

Notes de contrat:

- `route_key` vaut `null` quand la décision safeguards finale est `refuse` ou `reframe`.
- Les routes `work_*` et `orientation_*` suivent le même régime de précision que `period_*` au MVP.

### Canonical JSON Example: `POST /v1/consultations/generate`

Request:

```json
{
  "consultation_type": "timing",
  "question": "Quel est le meilleur moment pour lancer cette discussion importante ?",
  "horizon": "next_30_days",
  "precheck": {
    "precision_level": "medium",
    "fallback_mode": "timing_degraded",
    "safeguard_issue": null
  }
}
```

Response:

```json
{
  "data": {
    "consultation_id": "consult_47_demo_001",
    "contract_version": "consultation-generate.v1",
    "consultation_type": "timing",
    "status": "degraded",
    "precision_level": "medium",
    "fallback_mode": "timing_degraded",
    "safeguard_issue": null,
    "route_key": "timing_degraded",
    "summary": "Une fenetre favorable se dessine, mais sans heure de naissance la granularite reste large.",
    "sections": [
      {
        "id": "timing_window",
        "title": "Fenetre utile",
        "content": "Visez plutot la deuxieme quinzaine du mois pour une discussion structurante."
      },
      {
        "id": "limitations",
        "title": "Limites de precision",
        "content": "L'analyse reste journaliere et non horaire faute d'heure de naissance exploitable."
      }
    ],
    "chat_prefill": "Je veux prolonger cette consultation timing en tenant compte du mode degrade et de ses limites.",
    "metadata": {
      "request_id": "req_consult_generate_123"
    }
  },
  "meta": {
    "request_id": "req_consult_generate_123",
    "contract_version": "consultation-generate.v1"
  }
}
```

### Previous Story Intelligence

- Les stories 47.2 et 47.4 fournissent déjà `precision_level` et `fallback_mode`; ce sont des entrées du dossier, pas des sorties décoratives.
- Le backend possède déjà une couche `GuidanceService` et `AIEngineAdapter` qui gère retry, off-scope et erreurs transport.
- La story 46.1 a montré qu'un simple branchement direct du frontend sur `/v1/guidance/contextual` est trop limité pour la consultation complète.

### Project Structure Notes

- Backend probable:
  - `backend/app/api/v1/routers/consultations.py`
  - `backend/app/services/consultation_precheck_service.py`
  - `backend/app/services/consultation_generation_service.py`
  - `backend/app/services/guidance_service.py`
  - `backend/app/services/ai_engine_adapter.py`
  - `backend/app/llm_orchestration/seeds/use_cases_seed.py`
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`

### Technical Requirements

- Le frontend ne doit plus choisir implicitement la route métier.
- `route_key` doit être un identifiant stable, journalisable et testable.
- Le contrat de sortie doit déjà être pensé pour la page résultat 47.6.
- La résolution doit pouvoir court-circuiter la génération pour un refus ou un recadrage issu des safeguards.
- Les `route_key` listées ci-dessus deviennent la référence unique backend/frontend/tests pour le MVP Epic 47.

### Architecture Compliance

- Respecter le layering `router -> consultation service -> services existants`.
- Réutiliser l'orchestration LLM déjà en place.
- Ne pas modifier le comportement des use cases chat/natal hors besoins consultation explicitement documentés.

### Testing Requirements

- Tester la détermination du `route_key`.
- Tester la construction de `ConsultationDossier`.
- Tester la réponse API consultation complète sur plusieurs modes.

### References

- [Source: docs/backlog_epics_consultation_complete.md#9-epic-cc-05-routing-des-prompts-et-orchestration-llm]
- [Source: docs/backlog_epics_consultation_complete.md#10-epic-cc-06-dossier-de-consultation-contrats-backend-et-payload-metier]
- [Source: _bmad-output/planning-artifacts/epic-47-consultation-complete-depuis-consultations.md]
- [Source: backend/app/api/v1/routers/guidance.py]
- [Source: backend/app/services/guidance_service.py]
- [Source: backend/app/services/ai_engine_adapter.py]
- [Source: backend/app/llm_orchestration/seeds/use_cases_seed.py]
- [Source: backend/app/llm_orchestration/policies/hard_policy.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 47 et du backlog consultation complète.

### Completion Notes List

- Artefact créé uniquement; aucun code applicatif n'a été modifié.
- La story encadre explicitement le réemploi de `guidance_contextual` pour éviter une régression ou un deuxième pipeline LLM.

### File List

- TBD pendant `dev-story`
