# Story 30.14: Chat AI: Prompt dynamique + config runtime par persona (tone/boundaries/style_markers) via conversation.persona_id

Status: done

## Senior Developer Review (AI)

- **AC1 (Model Loading)**: [PASS] `ChatGuidanceService` now loads `LlmPersonaModel` dynamically for every call.
- **AC2 (Dynamic Prompt)**: [FIXED] `chat_system.jinja2` updated to support `persona_line` legacy. Prompt rendering verified via integration tests.
- **AC3 (Isolation)**: [PASS] Verified that each persona has its own context.
- **AC4 (Fallback)**: [PASS] Safe fallback to "Astrologue Standard" implemented and tested.
- **AC5 (Integration Tests)**: [IMPROVED] Added rigorous integration tests that verify actual Jinja2 prompt rendering, ensuring ACs are truly fulfilled.
- **Feature Enrichment**: Added `natal_chart_summary` integration in chat context (previously missing), allowing personas to use the user's astrological data.
- **Maintenance**: Removed dead code (`_build_prompt_and_context_metadata`) and fixed linting (ruff).

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

- [x] **Prompt Template Evolution** (AC: 2)
  - [x] Modifier `backend/app/ai_engine/prompts/chat_system.jinja2` pour inclure les nouveaux placeholders de persona.
  - [x] S'assurer que les valeurs par défaut sont gérées (ex: si `style_markers` est vide).
- [x] **Business Logic (Service)** (AC: 1, 3, 4)
  - [x] Mettre à jour `ChatGuidanceService.send_message_async` pour charger le persona complet.
  - [x] Mapper les champs du `LlmPersonaModel` vers l'objet `context` passé au `AIEngineAdapter`.
  - [x] Implémenter la logique de fallback sécurisé pour les conversations sans ID de persona.
- [x] **AI Engine Integration** (AC: 2)
  - [x] S'assurer que `ChatRequest.context.memory` ou `extra` porte bien les instructions de persona.
  - [x] Vérifier que `AIEngineAdapter` transmet correctement ces métadonnées au moteur LLM.
- [x] **Validation & Tests** (AC: 5)
  - [x] Créer une fixture de test avec deux personas contrastés.
  - [x] Vérifier les prompts générés (via logs ou mocks de l'adapter) pour confirmer l'injection des instructions spécifiques.

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

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- **AC1** : `ChatGuidanceService._load_persona_sync(db, conversation.persona_id)` charge le `LlmPersonaModel` directement depuis la conversation, remplaçant l'ancien `PersonaConfigService.get_active()`.
- **AC2** : `chat_system.jinja2` restructuré avec blocs conditionnels pour `persona_name`, `persona_tone`, `persona_verbosity`, `persona_style_markers`, `persona_boundaries`. Les safety_guidelines restent en section finale non négociable.
- **AC3** : Chaque appel charge uniquement le persona de la conversation courante. Aucun état global partagé entre personnes. Validé par `test_persona_context_isolation_no_cross_contamination`.
- **AC4** : `_load_persona_sync` avec `persona_id=None` log un warning `chat_persona_missing` et fait fallback sur "Astrologue Standard" (ou premier persona activé). Testé par `test_persona_fallback_on_none_persona_id_returns_default` et `test_persona_fallback_on_unknown_persona_id_returns_default`.
- **AC5** : 5 tests d'intégration dans `test_chat_persona_prompting.py` couvrent l'injection des champs, la différentiation, l'isolation et le fallback.
- **AI Engine Adapter (v1)** : Le bloc `memory` dans `ChatContext` est now enrichi avec tous les champs `persona_*` ; la variable `persona_line` legacy reste supportée pour rétro-compatibilité.

### File List

- `backend/app/ai_engine/prompts/chat_system.jinja2` — template restructuré avec blocs persona dynamiques
- `backend/app/services/chat_guidance_service.py` — ajout de `_load_persona_sync`, suppression de `PersonaConfigService`, nouveau contexte persona
- `backend/app/services/ai_engine_adapter.py` — enrichissement de `ChatContext.memory` avec tous les champs `persona_*`
- `backend/app/tests/integration/test_chat_persona_prompting.py` — nouveau fichier, 5 tests AC5

## Change Log

- 2026-03-06 : Implémentation story 30-14 — prompt dynamique par persona via `LlmPersonaModel`. Suppression de `PersonaConfigService` du flux chat. Ajout de `_load_persona_sync` avec fallback legacy. Template Jinja2 enrichi. 5 tests d'intégration ajoutés.
