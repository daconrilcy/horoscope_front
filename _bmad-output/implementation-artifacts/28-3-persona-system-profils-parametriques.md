# Story 28.3: Persona System — profils paramétriques et injection contrôlée

Status: done

## Story

As a product admin,
I want définir des personas d'astrologue virtuel via des champs paramétriques structurés, injectés par le serveur dans le developer message,
so that le ton, le style et les contraintes éditorialess de chaque astrologue sont garantis par le produit et non écrasables par l'utilisateur.

## Acceptance Criteria

1. **Given** un admin authentifié **When** il crée un persona **Then** il renseigne uniquement des champs paramétriques (`tone`, `verbosity`, `style_markers`, `boundaries`, `allowed_topics`, `disallowed_topics`, `formatting`) — pas de bloc texte libre — et le persona est enregistré avec un `persona_id`.
2. **Given** un persona actif `enabled=true` **When** le gateway exécute un use_case qui lui est associé **Then** un bloc `persona_block` est composé depuis ses champs et injecté en couche 3 (developer message), après le `developer_prompt` du use_case.
3. **Given** un use_case sans persona associé **When** le gateway l'exécute **Then** la couche 3 est omise (pas de bloc vide injecté).
4. **Given** l'injection de la persona **When** le message est composé **Then** la persona est toujours dans un message `developer` (jamais `user`), garantissant la priorité hiérarchique sur les instructions utilisateur.
5. **Given** un admin **When** il désactive un persona (`enabled=false`) pour un use_case `persona_strategy=optional` **Then** la couche 3 est omise sans erreur (AC3). **Given** un use_case `persona_strategy=required` **When** tous les personas de sa `allowed_persona_ids` sont désactivés **Then** le gateway lève `GatewayConfigError` (pas de dégradation silencieuse vers une sortie sans persona sur un use_case qui l'exige).
6. **Given** un appel gateway réussi **When** la réponse est retournée **Then** `GatewayResult.meta.persona_id` contient l'identifiant du persona utilisé (ou `null`).
7. **Given** un admin **When** il modifie les champs d'un persona **Then** l'effet est immédiat sur les prochains appels (pas de cache persona, ou TTL ≤ 30s).

## Tasks / Subtasks

- [x] Task 1 (AC: 1, 5)
  - [x] Créer le modèle SQLAlchemy `LlmPersona` : `id` (uuid), `name`, `description`, `tone` (enum : warm/direct/mystical/rational), `verbosity` (enum : short/medium/long), `style_markers` (JSON list de strings), `boundaries` (JSON list), `allowed_topics` (JSON list, vide = tous), `disallowed_topics` (JSON list), `formatting` (JSON : sections bool, bullets bool, emojis bool), `enabled` (bool), `created_at`, `updated_at`.
  - [x] Migration Alembic correspondante.

- [x] Task 2 (AC: 1, 2, 3)
  - [x] Créer `backend/app/llm_orchestration/services/persona_composer.py` : `compose_persona_block(persona: LlmPersona) -> str`.
  - [x] Le bloc généré est un texte structuré lisible par le LLM, composé uniquement depuis les champs (pas de texte libre).
  - [x] Migration Alembic correspondante. (Already checked)

- [x] Task 3 (AC: 2, 3, 4, 6)
  - [x] Intégrer `persona_composer` dans `LLMGateway.execute()` :
    - [x] Résoudre le persona via `use_case.allowed_persona_ids` (prendre le premier actif, ou aucun).
    - [x] Si persona résolu : injecter `compose_persona_block(persona)` en message `developer` (couche 3).
    - [x] Stocker `persona_id` dans `GatewayResult.meta`.

- [x] Task 4 (AC: 1, 5, 7)
  - [x] Créer les endpoints admin (RBAC `admin` requis) :
    - [x] `GET /v1/admin/llm/personas` — liste (avec statut enabled).
    - [x] `POST /v1/admin/llm/personas` — créer.
    - [x] `PATCH /v1/admin/llm/personas/{id}` — modifier (effet immédiat).
    - [x] `DELETE /v1/admin/llm/personas/{id}` — désactiver (soft delete, `enabled=false`).
  - [x] Endpoint pour associer un persona à un use_case :
    - [x] `PATCH /v1/admin/llm/use-cases/{key}/persona` — body `{ "persona_id": "..." | null }`.

- [x] Task 5 (AC: 1-7)
  - [x] Tests unitaires : `compose_persona_block()` pour chaque combinaison de champs (tone × verbosity × formatting).
  - [x] Test : persona disabled → omission couche 3, `meta.persona_id = null`.
  - [x] Test : injection dans developer message (vérifier rôle du message dans `ComposedMessages`).
  - [x] Tests d'intégration : endpoints admin CRUD + association use_case ↔ persona.

## Dev Notes

### Context

Le système de persona actuel (Story 11 et 15) injecte un bloc texte dans les prompts Jinja2 (`chat_system.jinja2`). Cette story remplace ce mécanisme par des profils entièrement paramétriques, modifiables en admin sans déploiement, et toujours injectés dans le `developer` message (jamais `user`).

La contrainte fondamentale : **l'utilisateur ne peut pas écraser la persona**. Cela est garanti par la hiérarchie des rôles de la Responses API (`system > developer > user`).

### Composition du bloc persona (exemple généré)

Pour un persona `tone=warm, verbosity=medium, style_markers=["tutoiement", "métaphores célestes"], boundaries=["jamais de fatalisme", "toujours proposer 2 pistes"], disallowed_topics=["santé", "légal"], formatting={sections: true, bullets: false, emojis: false}` :

```
## Directives de persona : Luna (astrologue bienveillante)
Adopte un ton chaleureux et empathique. Tutoie l'utilisateur.
Longueur de réponse : modérée (3-5 paragraphes).
Style : utilise des métaphores célestes naturellement.
Contraintes éditoriales :
- Ne formule jamais de prédictions fatalistes ; présente toujours des pistes d'évolution.
- Propose systématiquement au moins 2 orientations possibles.
Topics exclus (ne jamais aborder) : santé, conseil légal.
Structure les réponses en sections claires.
```

### Sécurité anti-injection

- Chaque champ est un type contraint (enum ou liste de strings), pas de texte libre.
- Le `compose_persona_block()` échappe les valeurs avant insertion (pas d'interpolation directe).
- Validation Pydantic sur chaque champ à la création/modification.
- Taille max du bloc généré : 1 500 caractères (warning si dépassé, erreur si > 2 000).

### Scope

- Modèle DB `LlmPersona` + migration.
- Service `persona_composer`.
- Intégration dans `LLMGateway`.
- Endpoints admin CRUD + association use_case ↔ persona.
- Tests unitaires et d'intégration.

### Out of Scope

- Interface graphique admin.
- Personas par utilisateur final (feature future).
- A/B testing de personas (feature future).

### Technical Notes

- `allowed_persona_ids` dans `LlmUseCaseConfig` (Story 28.2) : liste ordonnée, le gateway prend le premier `enabled`.
- **Règle prod `required`** : si `persona_strategy=required` et aucun persona `enabled=true` dans `allowed_persona_ids` (liste vide OU tous désactivés) → `GatewayConfigError`. Cela n'est pas une dégradation gracieuse : le use_case est inutilisable sans persona. L'alerte doit remonter via les métriques (28.6).
- **Seed protection** : le seed 28.5 doit valider à l'insertion qu'un use_case `required` a au moins un persona actif dans `allowed_persona_ids`. Pas de use_case `required` avec liste vide au moment du seed.
- Pas de cache persona (TTL ≤ 30s acceptable si cache ajouté, mais simple rechargement DB suffisant en v1).
- Le bloc persona est loggué de façon sanitisée (tronqué à 200 chars dans les logs).

### Tests

- `test_persona_composer.py` : génération du bloc pour toutes les combinaisons d'enum, valeurs vides, taille max.
- `test_persona_injection.py` : vérifier que le bloc est en position 3 (index 2) dans `ComposedMessages.messages`, rôle `developer`.
- `test_persona_disabled.py` : persona disabled → couche 3 absente, `meta.persona_id = null`.
- `test_admin_persona_endpoints.py` : CRUD + association use_case, RBAC.

### Rollout / Feature Flag

- Dépend du flag `LLM_ORCHESTRATION_V2` de Story 28.1.
- Peut être développé en parallèle de Story 28.2.

### Observability

- Audit log : création/modification/désactivation de persona avec `admin_user_id` et `persona_id`.
- `GatewayResult.meta.persona_id` dans chaque log d'appel gateway.
- Metric : `llm_persona_used_total{persona_id, use_case}`.

### Dependencies

- 28.1 (LLM Gateway) : intégration dans `execute()`.
- 28.2 (Prompt Registry v2) : `LlmUseCaseConfig.allowed_persona_ids` défini en 28.2.
- RBAC `admin` existant.

### Project Structure Notes

- Nouveaux fichiers : `backend/app/llm_orchestration/services/persona_composer.py`.
- Modèle DB : `backend/app/models/llm_persona.py`.
- Migration : `backend/alembic/versions/`.
- Endpoints : dans `backend/app/api/v1/routers/admin_llm.py` (créé en 28.2).
- Story artifact : `_bmad-output/implementation-artifacts/`.
- Planning source : `_bmad-output/planning-artifacts/epic-28-llm-orchestration-layer.md`.

### References

- [Source: _bmad-output/planning-artifacts/epic-28-llm-orchestration-layer.md]
- [Source: _bmad-output/implementation-artifacts/11-1-raffinement-multi-persona-astrologue.md]
- [Source: backend/app/ai_engine/prompts/chat_system.jinja2]
- [Source: docs/persona-governance.md]

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- SQLite UUID type quirk handled by removing unnecessary alter_column for UUIDs in migrations.
- Handle both Enum and string types in persona_composer.
- Convert string IDs to UUIDs in LLMGateway for query compatibility.

### Implementation Plan

1. Create LlmPersonaModel and add persona_strategy to LlmUseCaseConfigModel.
2. Generate and clean up migrations.
3. Implement persona_composer service to generate structured blocks.
4. Integrate persona resolution and injection into LLMGateway.
5. Create admin endpoints and Pydantic models.
6. Verify with unit and integration tests.

### Completion Notes List

- All parametric fields (tone, verbosity, etc.) are implemented with enums or strict types.
- Persona block is injected as a developer message (Layer 3) after the developer prompt.
- Use case configuration now supports 'optional' or 'required' persona strategy.
- Admin endpoints (GET, POST, PATCH, DELETE) for personas are fully functional with RBAC.
- Persona-to-use-case association supports immediate effect via DB fetch.

### File List

- `backend/app/infra/db/models/llm_persona.py`
- `backend/app/infra/db/models/llm_prompt.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/llm_orchestration/services/persona_composer.py`
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/models.py`
- `backend/app/llm_orchestration/admin_models.py`
- `backend/app/api/v1/routers/admin_llm.py`
- `backend/migrations/env.py`
- `backend/migrations/versions/4665be3c5a76_add_llm_persona_model.py`
- `backend/migrations/versions/caf87c3d461f_add_persona_strategy_to_use_case.py`
- `backend/app/tests/unit/test_llm_persona_model.py`
- `backend/app/tests/unit/test_persona_composer.py`
- `backend/app/tests/unit/test_persona_injection.py`
- `backend/app/tests/integration/test_admin_persona_endpoints.py`

## Change Log

- 2026-03-01: Story créée (Epic 28, LLM Orchestration Layer).
- 2026-03-01: Implementation complète: LlmPersonaModel, persona_composer, LLMGateway integration, admin endpoints.
