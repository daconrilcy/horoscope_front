# Story 30.14: Chat AI: Prompt dynamique + config runtime par persona (tone/boundaries/style_markers) via conversation.persona_id

Status: ready-for-dev

## Story

As an utilisateur,
I want que chaque astrologue garde son style propre (ton, verbiage, spécialités) et ses limites de comportement,
so that l'expérience est crédible, immersive et cohérente d'une discussion à l'autre.

## Acceptance Criteria

1. **AC1: Chargement dynamique du Persona** : Le `ChatGuidanceService` récupère désormais les données du `LlmPersonaModel` correspondant au `persona_id` de la conversation active.
2. **AC2: Prompting par Persona (Jinja2)** : Le template `chat_system.jinja2` est enrichi pour injecter dynamiquement :
   - `persona_name`, `tone`, `verbosity`, `style_markers`.
   - `boundaries` (garde-fous spécifiques au persona).
   - `safety_guidelines` (limites globales de sécurité).
3. **AC3: Isolation du contexte** : La génération de réponse pour un astrologue A ne contient aucune trace du style ou des instructions de l'astrologue B.
4. **AC4: Fallback de migration** : Si une conversation n'a pas encore de `persona_id` (cas legacy), le service :
   - Log un warning (tracké pour backfill).
   - Utilise le persona par défaut (via `LlmPersonaRepository.get_default()`).
5. **AC5: Tests de différentiation** : Des tests d'intégration valident qu'un astrologue configuré comme "Mystique et verbeux" produit un prompt substantiellement différent d'un astrologue "Analytique et concis".

## Tasks / Subtasks

- [ ] **Prompt Template Evolution** (AC: 2)
  - [ ] Modifier `backend/app/ai_engine/prompts/chat_system.jinja2` pour inclure les nouveaux placeholders de persona.
  - [ ] S'assurer que les valeurs par défaut sont gérées (ex: si `style_markers` est vide).
- [ ] **Business Logic (Service)** (AC: 1, 3, 4)
  - [ ] Mettre à jour `ChatGuidanceService.send_message_async` pour charger le persona complet.
  - [ ] Mapper les champs du `LlmPersonaModel` vers l'objet `context` passé au `AIEngineAdapter`.
  - [ ] Implémenter la logique de fallback sécurisé pour les conversations sans ID de persona.
- [ ] **AI Engine Integration** (AC: 2)
  - [ ] S'assurer que `ChatRequest.context.memory` ou `extra` porte bien les instructions de persona.
  - [ ] Vérifier que `AIEngineAdapter` transmet correctement ces métadonnées au moteur LLM.
- [ ] **Validation & Tests** (AC: 5)
  - [ ] Créer une fixture de test avec deux personas contrastés.
  - [ ] Vérifier les prompts générés (via logs ou mocks de l'adapter) pour confirmer l'injection des instructions spécifiques.

## Dev Notes

- **Fichiers impactés** :
  - `backend/app/services/chat_guidance_service.py`
  - `backend/app/ai_engine/prompts/chat_system.jinja2`
  - `backend/app/services/ai_engine_adapter.py`
- **Priorité des instructions** : Les `safety_guidelines` (ne pas faire de diagnostic médical, etc.) doivent rester prépondérantes sur le style du persona.
- **Performance** : Le chargement du persona peut être mis en cache (stale-while-revalidate ou TTL court) pour éviter un hit DB à chaque message si nécessaire.

### Project Structure Notes

- Ne plus utiliser `PersonaConfigService` pour la logique de chat; ce service est déprécié au profit du système multi-persona `LlmPersonaModel`.
- Garder le moteur de templates Jinja2 centralisé dans l'AI Engine.

### References

- [Source: backend/app/ai_engine/prompts/chat_system.jinja2]
- [Source: backend/app/services/chat_guidance_service.py]
- [Source: backend/app/infra/db/models/llm_persona.py]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

### Completion Notes List

### File List
