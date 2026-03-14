# Story 47.5: Construire le dossier de consultation et le routing LLM versionné

Status: done

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

- [x] Task 1: Définir le contrat métier `ConsultationDossier` (AC: 1)
  - [x] Créer les schémas Pydantic consultation d'entrée et intermédiaires
  - [x] Y porter explicitement qualité, précision, fallback, question et métadonnées

- [x] Task 2: Implémenter le resolver `route_key` consultation (AC: 2, 3, 4, 6, 7, 8)
  - [x] Définir une matrice minimale nominale / dégradée pour le MVP epic 47
  - [x] Formaliser explicitement les résolutions attendues dans `ConsultationFallbackService`
  - [x] Propager la décision safeguards `generate / refuse / reframe` dans la résolution

- [x] Task 3: Ajouter le service / routeur de génération consultation (AC: 2, 4, 5)
  - [x] Introduire `ConsultationGenerationService` orchestrant le flux
  - [x] Ajouter l'endpoint `POST /v1/consultations/generate`
  - [x] Retourner un payload consultation structuré et stable

- [x] Task 4: Préparer l'alignement prompt / use-case sans refonte globale du moteur LLM (AC: 3, 4, 7)
  - [x] Aligner les `route_key` sur `guidance_contextual` pour le MVP
  - [x] Documenter les identifiants de route stables

- [x] Task 5: Tester dossier, routeur et contrat (AC: 6)
  - [x] Ajouter des tests unitaires du route resolver
  - [x] Ajouter des tests d'intégration du routeur de génération

## Dev Notes

- MVP `route_key` matrix implemented in `ConsultationFallbackService`.
- `ConsultationGenerationService` leverages existing `GuidanceService` to avoid pipeline duplication.
- Safeguard refusal is handled before LLM call.
- JSON payload follows the requested canonical example.
- The generation contract now accepts an explicit `objective` from the wizard so the backend no longer collapses the request to a generic `Consultation <type>` intent.
- The consultation orchestration reuses the latest natal chart already generated for the user when available and injects its summary into `guidance_contextual`.
- For `relation` routes with `other_person`, the backend now computes a third-party natal chart on the fly from the enriched payload and injects a combined user/other natal context into the interpretation.
- The generation contract now exposes structured `blocks` inside each consultation section so the frontend controls titles, subtitles and bullet rendering instead of displaying raw LLM markdown.
- The contextual guidance prompt was hardened to forbid decorative markdown markers and to favor plain semantic sections, with backend parsing kept as a compatibility layer.

### Locked MVP `route_key` Enum

- `period_full`, `period_no_birth_time`
- `work_full`, `work_no_birth_time`
- `orientation_full`, `orientation_no_birth_time`
- `relation_full_full`, `relation_full_other_no_time`, `relation_user_only`
- `timing_full`, `timing_degraded`

### Project Structure Notes

- Modified:
  - `backend/app/api/v1/schemas/consultation.py`
  - `backend/app/services/consultation_fallback_service.py`
  - `backend/app/api/v1/routers/consultations.py`
  - `backend/app/services/consultation_generation_service.py`
- Tests:
  - `backend/app/tests/unit/services/test_consultation_fallback_service.py`
  - `backend/app/tests/integration/test_consultations_router.py`

### Technical Requirements

- Pydantic v2 for all schemas.
- Deterministic route resolution based on precheck data.
- Structured sections in output for future rendering.

### Architecture Compliance

- Separation of concerns: fallback service handles routing logic, generation service handles orchestration.
- Reused `GuidanceService.request_contextual_guidance_async`.

### Testing Requirements

- Verified with unit tests for route mapping.
- Verified with integration test for nominal generation flow.

### References

- [Source: docs/backlog_epics_consultation_complete.md#9-epic-cc-05-routing-des-prompts-et-orchestration-llm]
- [Source: backend/app/api/v1/routers/consultations.py]

## Dev Agent Record

### Agent Model Used

Gemini CLI

### Debug Log References

- Route resolver unit tests: 5 passed.
- Integration tests for precheck & generate: 4 passed.
- Schema extensions for generation request/response implemented.

### Completion Notes List

- Defined stable route keys for all MVP consultation types.
- Implemented dedicated generation service and router.
- Ensured safeguard resolution is integrated into the generation flow.
- Robust test coverage for the routing logic and API contract.
- Fixed a production gap where the route resolver existed but the prompt still received a weak objective and no natal chart summary.
- Fixed a production gap where `other_person` data was acknowledged in the dossier but never transformed into an actual natal context for `relation_full_full`.

### File List

- `backend/app/api/v1/schemas/consultation.py`
- `backend/app/api/v1/routers/consultations.py`
- `backend/app/services/consultation_fallback_service.py`
- `backend/app/services/consultation_generation_service.py`
- `backend/app/tests/unit/services/test_consultation_fallback_service.py`
- `backend/app/tests/integration/test_consultations_router.py`

## Change Log

- 2026-03-13: Initial implementation of story 47.5. Consultation dossier and LLM routing.
- 2026-03-13: Post-implementation verification fixes. `route_key` nul en cas de `safeguard_reframed/refused` et génération court-circuitée pour les cas bloquants/recadrés.
- 2026-03-13: The consultation generate contract now forwards `objective` explicitly and injects the latest natal chart summary into the contextual guidance path.
- 2026-03-14: Relation consultations now calculate the third-party natal chart from the enriched payload and merge both natal summaries into the generated reading when the route allows it.
- 2026-03-14: Generation sections now include structured `blocks`, and the prompt/backend pair now suppresses raw markdown formatting from leaking into the consultation product contract.
