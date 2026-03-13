# Story 46.5: Retirer le sous-système tarot/runes du backend et des contrats LLM

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend maintainer,
I want supprimer l'infrastructure tarot/runes devenue hors périmètre,
so that le backend et l'orchestration LLM ne portent plus de fonctionnalités mortes ou contradictoires avec la promesse astrologique du produit.

## Acceptance Criteria

1. Les feature flags `tarot_enabled` et `runes_enabled` ainsi que les mécanismes de disponibilité/exécution de modules dédiés ne sont plus exposés par le backend.
2. Les endpoints backend et clients frontend associés à `/v1/chat/modules/availability` et `/v1/chat/modules/{module}/execute` sont supprimés ou retirés de l'usage produit selon le plan de migration validé.
3. L'orchestration LLM ne référence plus de use case, schéma, policy, prompt ou intent lié à `tarot`, `runes`, `tarot_spread`, `offer_tarot_reading`.
4. Le hard policy `astrology` est réaligné pour ne plus promettre d'interprétation tarot.
5. Les seeds, schémas et validations runtime restent cohérents après suppression et ne cassent pas le démarrage ou les migrations de configuration existantes.
6. Les tests backend et frontend impactés sont mis à jour pour refléter le retrait complet, sans réintroduire de code mort ni laisser de références résiduelles critiques.
7. La suppression backend n'est lancée qu'après les stories 46.1 à 46.4, de sorte qu'aucun parcours utilisateur encore actif ne dépende de ces modules.

## Tasks / Subtasks

- [ ] Task 1: Confirmer le périmètre exact à retirer (AC: 1, 2, 3, 4, 7)
  - [ ] Faire un inventaire `rg` complet sur `tarot`, `runes`, `tirage`, `cards`, `spread`, `offer_tarot_reading`
  - [ ] Séparer les références historiques/documentaires des références runtime critiques
  - [ ] Vérifier qu'aucun parcours frontend encore actif n'utilise ces modules après 46.1 à 46.4

- [ ] Task 2: Retirer le gating et l'exécution modules côté backend (AC: 1, 2, 7)
  - [ ] Nettoyer `backend/app/services/feature_flag_service.py`
  - [ ] Nettoyer les routeurs backend liés aux modules chat si présents
  - [ ] Réviser les clients frontend dans `frontend/src/api/chat.ts`
  - [ ] Supprimer les types de réponse devenus morts

- [ ] Task 3: Nettoyer les contrats LLM et le prompt registry seed (AC: 3, 4, 5)
  - [ ] Retirer `tarot_reading` des use cases seed
  - [ ] Retirer `tarot_spread` des schémas s'il n'a plus de consommateur légitime
  - [ ] Retirer l'intent `offer_tarot_reading`
  - [ ] Mettre à jour le hard policy `astrology`
  - [ ] Supprimer `backend/app/ai_engine/prompts/card_reading_v1.jinja2` si plus aucun flux ne le référence

- [ ] Task 4: Vérifier les dépendances de configuration et d'observabilité (AC: 1, 3, 5)
  - [ ] Revoir les compteurs/metrics taggés `module=tarot` ou `module=runes`
  - [ ] Vérifier les éventuels scripts de seed, fixtures ou migrations qui supposent encore ces modules
  - [ ] Garantir que les démarrages dev/test restent stables sans ces clés

- [ ] Task 5: Mettre à jour les tests et supprimer le code mort (AC: 5, 6)
  - [ ] Réviser les tests backend feature flags/modules
  - [ ] Réviser les tests frontend `useExecuteModule` / availability si encore présents
  - [ ] Supprimer les imports, mocks et fixtures inutiles
  - [ ] Vérifier qu'aucun `TODO` ou compat layer permanent n'est laissé sans justification

## Dev Notes

- Cette story est volontairement tardive dans l'epic. Elle ne doit pas partir en premier sous peine de casser les consultations encore branchées sur les modules.
- Le nettoyage doit être profond mais prudent: il faut retirer les références runtime, pas casser le démarrage des seeds ou l'orchestration.
- Les points les plus sensibles sont:
  - `backend/app/services/feature_flag_service.py`
  - `frontend/src/api/chat.ts`
  - `backend/app/llm_orchestration/gateway.py`
  - `backend/app/llm_orchestration/schemas.py`
  - `backend/app/llm_orchestration/policies/hard_policy.py`
  - `backend/app/llm_orchestration/seeds/use_cases_seed.py`

### Previous Story Intelligence

- Story 11.2 a précisément introduit tarot/runes derrière feature flags. Elle sert ici de checklist inverse de retrait.
- Story 30.7 a étendu le catalogue de nouveaux produits LLM incluant encore des références tarot/event/chat; il faut vérifier cette zone avant suppression finale.
- Story 28.5 et suivantes ont structuré le catalogue de use cases et schémas. Les suppressions doivent rester cohérentes avec cette architecture.

### Project Structure Notes

- Backend principal:
  - `backend/app/services/feature_flag_service.py`
  - `backend/app/llm_orchestration/`
  - `backend/app/ai_engine/prompts/`
- Frontend principal:
  - `frontend/src/api/chat.ts`
  - tests associés

### Technical Requirements

- Ne pas supprimer `guidance_contextual`, `event_guidance` ou d'autres use cases astrologiques légitimes par sur-nettoyage.
- Vérifier les seeds et validations strictes avant suppression d'une clé de schéma ou d'un intent.
- Toute suppression doit être accompagnée d'un passage de tests et d'un scan de références résiduelles.

### Architecture Compliance

- Le backend reste orienté astrologie, support et guidance.
- Les use cases LLM supprimés ne doivent pas laisser d'incohérence dans les enums, JSON schema ou policies.
- Les suppressions frontend doivent rester alignées avec les clients centraux existants.

### Testing Requirements

- Backend: tests de seed/configuration, feature flags/modules, éventuels routeurs modules.
- Frontend: compilation/typecheck/tests sur `api/chat.ts` et parcours consultations.
- Vérification de non-régression sur les parcours chat et guidance encore actifs.

### References

- [Source: backend/app/services/feature_flag_service.py]
- [Source: frontend/src/api/chat.ts]
- [Source: backend/app/llm_orchestration/gateway.py]
- [Source: backend/app/llm_orchestration/schemas.py]
- [Source: backend/app/llm_orchestration/policies/hard_policy.py]
- [Source: backend/app/llm_orchestration/seeds/use_cases_seed.py]
- [Source: backend/app/ai_engine/prompts/card_reading_v1.jinja2]
- [Source: _bmad-output/implementation-artifacts/11-2-modules-tarot-runes-derriere-feature-flags.md]
- [Source: _bmad-output/implementation-artifacts/30-7-nouveaux-produits-tarot-event-chat.md]
- [Source: _bmad-output/implementation-artifacts/46-1-rebrancher-les-consultations-ciblees-sur-la-guidance-contextuelle.md]

## Dev Agent Record

### Agent Model Used

TBD

### Debug Log References

### Completion Notes List

### File List
