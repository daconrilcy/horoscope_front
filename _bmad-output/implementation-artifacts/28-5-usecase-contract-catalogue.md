# Story 28.5: UseCase Contract — catalogue officiel, input/output/persona/safety par use_case

Status: review

## Story

As a backend platform engineer,
I want un catalogue de "UseCase Contracts" formalisés et persistés, définissant pour chaque use_case ses schémas d'entrée, de sortie, sa stratégie persona, ses règles lint spécifiques et son profil de sécurité,
so that tous les services métier (natal, chat, tirage, guidance) disposent d'un contrat stable qui empêche la dérive silencieuse et permet la validation en amont de chaque modification.

## Acceptance Criteria

1. **Given** la liste officielle des use_cases **When** le projet est déployé **Then** les 7 use_cases canoniques sont présents dans la DB (`LlmUseCaseConfig`) avec leur contrat complet : `input_schema`, `output_schema_id`, `persona_strategy`, `safety_profile`, `fallback_use_case_key`, `required_prompt_placeholders`.
2. **Given** un use_case avec `persona_strategy=required` **When** aucun persona actif n'est résolu **Then** le gateway lève une `GatewayConfigError` (pas de dégradation silencieuse).
3. **Given** un use_case avec `persona_strategy=optional` **When** aucun persona n'est résolu **Then** la couche 3 est omise (comportement 28.3 AC3 conservé).
4. **Given** un admin qui publie un prompt **When** le use_case a des `required_prompt_placeholders` configurés **Then** le lint 28.2 vérifie leur présence (en plus de `{{locale}}` et `{{use_case}}`) et bloque la sauvegarde si l'un est absent.
5. **Given** un appel avec `context.persona_id` fourni par le front **When** le gateway résout le use_case **Then** il vérifie que le persona_id est dans `allowed_persona_ids` du use_case ; si non autorisé il tombe sur le persona `default_safe` du use_case (ou aucun si absent), et logue un warning `persona_override_rejected`.
6. **Given** un use_case `chat_astrologer` **When** il est configuré **Then** son `output_schema_id` pointe sur `ChatResponse_v1` (défini dans cette story) et la validation 28.4 s'applique.
7. **Given** l'endpoint `GET /v1/admin/llm/use-cases/{key}/contract` **When** un admin le consulte **Then** il reçoit le contrat complet du use_case : input_schema, output_schema, persona_strategy, safety_profile, required_prompt_placeholders, fallback_use_case_key, use_cases_allowed_personas.
8. **Given** un appel gateway avec un `input` qui viole l'`input_schema` du use_case **When** la validation est effectuée **Then** une `InputValidationError` (HTTP 400) est retournée avant tout appel LLM.

## Tasks / Subtasks

- [x] Task 1 (AC: 1)
  - [x] Étendre `LlmUseCaseConfig` (Story 28.2) avec les colonnes manquantes :
    - `input_schema` (JSON, nullable) — JSON Schema décrivant le `user_input` attendu.
    - `persona_strategy` (enum : `required` / `optional` / `forbidden`).
    - `safety_profile` (enum : `astrology` / `transactional` / `support`).
    - `required_prompt_placeholders` (JSON list, ex: `["{{chart_json}}", "{{persona_name}}"]`).
  - [x] Migration Alembic.

- [x] Task 2 (AC: 1, 6)
  - [x] Définir et insérer le schéma de sortie `ChatResponse_v1` dans `LlmOutputSchema`

- [x] Task 3 (AC: 1)
  - [x] Seed DB : insérer les 7 use_cases canoniques avec leur contrat complet.
  - [x] Script de seed idempotent.
  - [x] Validation pré-seed : `persona_strategy=required` exige `allowed_persona_ids` non-vide.

- [x] Task 4 (AC: 2, 3, 5)
  - [x] Mettre à jour `LLMGateway.execute()` (Story 28.1) :
    - [x] Lecture de `persona_strategy` depuis la config use_case.
    - [x] Si `required` et aucun persona résolu → lever `GatewayConfigError`.
    - [x] Si `context.persona_id` fourni → vérifier autorisation dans `allowed_persona_ids` ; si rejeté → `default_safe` persona ou omission + warning `persona_override_rejected`.

- [x] Task 5 (AC: 4)
  - [x] Mettre à jour `prompt_lint.py` (Story 28.2) :
    - Accepter une liste `use_case_required_placeholders` en entrée.
    - Vérifier leur présence en plus des placeholders globaux.
    - Erreur bloquante si l'un est absent.

- [x] Task 6 (AC: 8)
  - [x] Créer `backend/app/llm_orchestration/services/input_validator.py` : `validate_input(user_input: dict, input_schema: dict) -> ValidationResult`.
  - [x] Intégrer dans `LLMGateway.execute()` : valider `user_input` contre `input_schema` avant composition des messages.

- [x] Task 7 (AC: 7)
  - [x] Ajouter `GET /v1/admin/llm/use-cases/{key}/contract` dans `admin_llm.py`.
  - [x] Réponse : contrat complet (input_schema, output_schema résolu, persona_strategy, safety_profile, required_prompt_placeholders, fallback_use_case_key, allowed_personas résumés).

- [x] Task 8 (AC: 1-8)
  - [x] Tests unitaires : persona_strategy required/optional/forbidden, persona_override_rejected, lint use_case-specific placeholders, input_validator.
  - [x] Tests d'intégration : seed use_cases, `GET /contract`, InputValidationError avant appel LLM.

## Dev Notes

### Catalogue officiel des use_cases (seed initial)

| key | output_schema | persona_strategy | safety_profile | fallback_use_case_key | required_placeholders |
|---|---|---|---|---|---|
| `natal_interpretation` | `AstroResponse_v1` | required | astrology | `natal_interpretation_short` | `{{chart_json}}`, `{{persona_name}}` |
| `natal_interpretation_short` | `AstroResponse_v1` | optional | astrology | _(aucun)_ | `{{chart_json}}` |
| `chat_astrologer` | `ChatResponse_v1` | required | astrology | _(aucun)_ | `{{persona_name}}` |
| `tarot_reading` | `AstroResponse_v1` | optional | astrology | `natal_interpretation_short` | `{{cards_json}}` |
| `event_guidance` | `AstroResponse_v1` | optional | astrology | `natal_interpretation_short` | `{{chart_json}}`, `{{event_description}}` |
| `astrologer_selection_help` | `ChatResponse_v1` | forbidden | support | _(aucun)_ | _(aucun)_ |
| `account_support` | _(texte libre)_ | forbidden | support | _(aucun)_ | _(aucun)_ |

**Légende persona_strategy :**
- `required` : le gateway refuse d'appeler le LLM sans persona actif.
- `optional` : la couche 3 est omise si aucun persona résolu (comportement gracieux).
- `forbidden` : aucune persona injectée, quelle que soit la config (use_cases de support).

**Légende safety_profile :**
- `astrology` : Hard Policy complète (non-fatalisme, pas de diagnostic, conditionnel).
- `transactional` : Hard Policy réduite (pas de diagnostic médical, données exactes obligatoires).
- `support` : Hard Policy minimale (pas de promesse contractuelle, redirection vers équipe humaine si escalade).

### ChatResponse_v1 — justification

Le schéma `ChatResponse_v1` permet :
- Afficher des quick replies côté front sans parsing heuristique.
- Router vers un outil (tirage, guidance) via le champ `intent`.
- Garder le chat stable et testable au fil des versions de prompt.

En AC8 de 28.4, `chat_astrologer` était en texte libre. Cette story le fait passer en `ChatResponse_v1` — changement rétrocompatible car `message` contient le texte exact précédemment retourné.

### Persona override depuis le front

Flux complet :
```
Front envoie context.persona_id = "luna_v2"
   ↓
Gateway charge use_case.allowed_persona_ids = ["luna_v2", "orion_v1"]
   ↓
"luna_v2" ∈ allowed ? OUI → compose_persona_block(luna_v2)
   ↓
"luna_v2" ∈ allowed ? NON → fallback default_safe (premier persona enabled de allowed_persona_ids)
                             + log WARNING persona_override_rejected{use_case, requested=..., applied=...}
```

`default_safe` = premier persona `enabled=true` dans `allowed_persona_ids`, ou omission si liste vide.

### Extension du lint (Story 28.2 → mise à jour)

`prompt_lint.py` doit recevoir un paramètre optionnel `use_case_required_placeholders: list[str]` (fourni par le gateway lors de la validation avant publication). Le lint global (`{{locale}}`, `{{use_case}}`) reste inchangé.

### Input schema — exemples

```json
// natal_interpretation
{
  "type": "object",
  "required": ["question", "chart_json"],
  "properties": {
    "question":   { "type": "string", "maxLength": 500 },
    "chart_json": { "type": "object" },
    "locale":     { "type": "string", "pattern": "^[a-z]{2}-[A-Z]{2}$" }
  }
}

// chat_astrologer
{
  "type": "object",
  "required": ["message"],
  "properties": {
    "message":         { "type": "string", "maxLength": 1000 },
    "conversation_id": { "type": "string" },
    "persona_id":      { "type": "string", "nullable": true }
  }
}
```

### Scope

- Extension `LlmUseCaseConfig` (colonnes + migration).
- Schéma `ChatResponse_v1` en DB.
- Seed des 7 use_cases.
- `input_validator.py`.
- Mise à jour lint use_case-specific dans `prompt_lint.py`.
- Mise à jour `LLMGateway.execute()` (persona_strategy + persona override + input validation).
- Endpoint `GET /contract`.

### Out of Scope

- Tool calling / function calling (story future post-28).
- Modification des use_case contracts via l'admin (lecture + seed uniquement en v1 — évolution via déploiement).
- Interface graphique admin pour le catalogue.

### Technical Notes

- `input_schema` nullable : si null, pas de validation input (comportement 28.1).
- `persona_strategy=forbidden` doit court-circuiter la résolution persona entièrement, même si `context.persona_id` est fourni.
- Le seed est idempotent : `INSERT ... ON CONFLICT (key) DO UPDATE` sur les champs non-verrouillés.
- Les use_cases `account_support` et `astrologer_selection_help` ont `output_schema_id=null` (texte libre) et `persona_strategy=forbidden` : cas de dégradation où le LLM est utilisé hors astrologie.
- **Invariant à maintenir en prod** : si un admin désactive tous les personas d'un use_case `required`, l'admin endpoint doit retourner un warning `use_case_persona_coverage_broken` (non bloquant, mais visible dans le dashboard 28.6). La désactivation reste possible — c'est une alerte, pas un refus.

### Tests

- `test_usecase_catalogue.py` : les 7 use_cases sont présents après seed, contrats conformes au tableau.
- `test_persona_strategy.py` : required + aucun persona → GatewayConfigError ; optional + aucun persona → OK ; forbidden + persona_id fourni → persona ignoré + warning.
- `test_persona_override.py` : persona autorisé → utilisé ; persona non autorisé → default_safe + warning loggué.
- `test_lint_usecase_placeholders.py` : `{{chart_json}}` absent → lint error ; présent → lint pass.
- `test_input_validator.py` : input conforme → pass ; input invalide → InputValidationError avant appel LLM.
- `test_contract_endpoint.py` : contrat complet retourné, RBAC admin.

### Rollout / Feature Flag

- Dépend du flag `LLM_ORCHESTRATION_V2` de Story 28.1.
- Le seed peut être exécuté indépendamment du flag (les données DB ne sont utilisées que si le flag est actif).
- Peut être développé en parallèle de 28.3 et 28.4.

### Observability

- Warning `persona_override_rejected` : structuré avec `use_case`, `requested_persona_id`, `applied_persona_id`.
- Error `GatewayConfigError` : inclut `use_case`, `persona_strategy`, raison.
- Metric : `llm_input_validation_errors_total{use_case}`.
- Metric : `llm_persona_override_rejected_total{use_case}`.

### Dependencies

- 28.1 (LLM Gateway) : intégration des vérifications persona_strategy + input validation.
- 28.2 (Prompt Registry v2) : extension `LlmUseCaseConfig` + mise à jour lint.
- 28.3 (Persona System) : logique `allowed_persona_ids` + `compose_persona_block`.
- 28.4 (Structured Outputs) : schéma `AstroResponse_v1` déjà défini, `ChatResponse_v1` ajouté ici.

### Project Structure Notes

- Extension modèle : `backend/app/models/llm_use_case.py` (colonnes supplémentaires).
- Nouveau fichier : `backend/app/llm_orchestration/services/input_validator.py`.
- Seed : `backend/app/llm_orchestration/seeds/use_cases_seed.py`.
- Migration Alembic : `backend/alembic/versions/`.
- Endpoint : `backend/app/api/v1/routers/admin_llm.py`.
- Story artifact : `_bmad-output/implementation-artifacts/`.
- Planning source : `_bmad-output/planning-artifacts/epic-28-llm-orchestration-layer.md`.

### References

- [Source: _bmad-output/planning-artifacts/epic-28-llm-orchestration-layer.md]
- [Source: _bmad-output/implementation-artifacts/28-1-llm-gateway-point-entree-unique.md]
- [Source: _bmad-output/implementation-artifacts/28-2-prompt-registry-v2-versioning-db-admin.md]
- [Source: _bmad-output/implementation-artifacts/28-3-persona-system-profils-parametriques.md]
- [Source: _bmad-output/implementation-artifacts/28-4-structured-outputs-hard-policy.md]

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- Fixed `NameError: name 'Field' is not defined` by importing it from `pydantic`.
- Fixed `AttributeError: 'UseCaseConfig' object has no attribute 'input_schema'` by adding it to the Pydantic model.
- Handled seed idempotency and placeholder formatting.

### Implementation Plan

1. Extend `LlmUseCaseConfigModel` with `input_schema` and `required_prompt_placeholders`.
2. Implement `InputValidator` service.
3. Update `PromptLint` to enforce use-case specific placeholders.
4. Finalize `LLMGateway` logic: persona strategy, persona override authorization, and input validation.
5. Seed database with 7 canonical use cases and `ChatResponse_v1`.
6. Add `GET /v1/admin/llm/use-cases/{key}/contract` endpoint.
7. Verify with unit and integration tests.

### Completion Notes List

- All 8 criteria of acceptance are met.
- Use Case Catalogue is fully functional and persisted in DB.
- Strict input validation enforced before LLM calls.
- Persona overrides are authorized against `allowed_persona_ids`.
- Admin API provides complete contract visibility.
- Canonical use cases are seeded with their official schemas and safety profiles.

### File List

- `backend/app/infra/db/models/llm_prompt.py` (Extended LlmUseCaseConfigModel)
- `backend/app/llm_orchestration/models.py` (Updated UseCaseConfig)
- `backend/app/llm_orchestration/admin_models.py` (Updated LlmUseCaseConfigBase)
- `backend/app/llm_orchestration/services/input_validator.py` (New)
- `backend/app/llm_orchestration/services/prompt_lint.py` (Updated)
- `backend/app/llm_orchestration/seeds/use_cases_seed.py` (New Seed Script)
- `backend/app/llm_orchestration/gateway.py` (Finalized logic)
- `backend/app/api/v1/routers/admin_llm.py` (New endpoints)
- `backend/migrations/versions/12216bc815ed_extend_use_case_config_contract.py` (Migration)
- `backend/app/tests/unit/test_use_case_contract.py` (New)
- `backend/app/tests/integration/test_contract_api.py` (New)

## Change Log

- 2026-03-01: Story créée (Epic 28, LLM Orchestration Layer).
- 2026-03-01: Implementation complète: Catalogue, Input Validation, Persona Strategy, Admin Contract API.
