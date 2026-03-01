# Story 28.4: Structured Outputs et Hard Policy — JSON Schema strict + validation + fallback + garde-fous

Status: done

## Story

As a backend platform engineer,
I want des sorties LLM validées par JSON Schema strict et des garde-fous de sécurité immuables en couche 1,
so that les réponses métier sont toujours parsables sans heuristique, les politiques de sécurité produit sont garanties, et les échecs de validation déclenchent un repair automatique ou un fallback gracieux.

## Acceptance Criteria

1. **Given** un use_case avec un `output_schema_id` configuré **When** le LLM retourne une réponse **Then** elle est validée contre le JSON Schema strict correspondant avant d'être renvoyée au service appelant.
2. **Given** une réponse qui échoue la validation JSON Schema **When** c'est le premier échec **Then** le gateway envoie automatiquement un "repair prompt" au LLM pour corriger la sortie (une seule tentative de repair).
3. **Given** une réponse qui échoue la validation après repair **When** un `fallback_use_case_key` est configuré **Then** le gateway réexécute avec le use_case de fallback (ex: version courte) et retourne son résultat avec `meta.fallback_triggered=true`.
4. **Given** aucun fallback configuré et un échec de validation persistant **When** la réponse est renvoyée **Then** une `OutputValidationError` structurée est retournée (HTTP 502) avec `meta.validation_errors`.
5. **Given** un appel gateway **When** le `system_core` (couche 1, Hard Policy) est composé **Then** il contient systématiquement les clauses de sécurité immuables et ne peut pas être modifié via l'admin.
6. **Given** un admin qui tente de modifier le `system_core` **When** il utilise les endpoints admin **Then** la modification est refusée (404 ou 403 — la couche 1 n'est pas exposée en admin).
7. **Given** une réponse LLM valide **When** le use_case est de type "astrologie" **Then** `GatewayResult.structured_output` contient les champs canoniques : `content` (str), `highlights` (list[str], 5-10 items), `sections` (list[Section]), `evidence` (list[str]), `safety_notes` (list[str], optionnel).
8. **Given** un use_case de type "chat" (réponse libre) **When** aucun `output_schema_id` n'est configuré **Then** la validation est omise et `GatewayResult.raw_output` est retourné directement (comportement actuel conservé).

## Tasks / Subtasks

- [x] Task 1 (AC: 5, 6)
  - [x] Définir `hard_policy.py` avec **3 profils immuables** (sélectionnés par `safety_profile` du use_case — jamais modifiables admin).
  - [x] Exposer `get_hard_policy(safety_profile: str) -> str` dans `hard_policy.py`. Lever `ValueError` si profil inconnu.
  - [x] Intégrer dans `LLMGateway.execute()` : charger le profil depuis `use_case_config.safety_profile`, passer à `get_hard_policy()` pour composer la couche 1.
  - [x] Tests : vérifier que chaque profil produit un texte différent et non vide ; que la couche 1 correspond au profil du use_case.

- [x] Task 2 (AC: 1, 7, 8)
  - [x] Créer le modèle SQLAlchemy `LlmOutputSchema` : `id` (uuid), `name`, `json_schema` (JSON), `version` (int), `created_at`.
  - [x] Migration Alembic.
  - [x] Définir et insérer le schéma canonique `AstroResponse_v1` et `ChatResponse_v1`.
  - [x] Ajouter un validateur post-schema spécifique `evidence` : vérifier que chaque item correspond au pattern `^[A-Z0-9_\.:-]{3,60}$`.

- [x] Task 3 (AC: 1, 2, 3, 4)
  - [x] Créer `backend/app/llm_orchestration/services/output_validator.py` : `validate(raw_output: str, schema: dict) -> ValidationResult`.
  - [x] Créer `backend/app/llm_orchestration/services/repair_prompter.py` : `build_repair_prompt(raw_output, errors, schema) -> str`.
  - [x] Intégrer dans `LLMGateway.execute()` la séquence : validate → repair si échec → fallback use_case si 2e échec → `OutputValidationError`.

- [x] Task 4 (AC: 7)
  - [x] Mettre à jour `GatewayResult` : ajouter `structured_output: dict | None`, `meta.fallback_triggered: bool`, `meta.validation_errors: list[str] | None`, `meta.repair_attempted: bool`.

- [x] Task 5 (AC: 1, 6)
  - [x] Endpoints admin pour gérer les schémas de sortie (lecture seule en v1).
  - [x] Associer `output_schema_id` et `safety_profile` à un use_case via `PATCH /v1/admin/llm/use-cases/{key}`.

- [x] Task 6 (AC: 1-8)
  - [x] Tests unitaires : `output_validator`, `repair_prompter`, séquence repair+fallback, Hard Policy.
  - [x] Test d'intégration : appel gateway complet avec schéma.
  - [x] Test de régression : use_case `chat` sans schema → `raw_output` retourné.

## Dev Notes

### Context

Les sorties LLM actuelles (Story 15) sont du texte libre retourné directement. Cette story introduit une validation systématique pour les use_cases métier (natal, tirage, guidance), tout en conservant le comportement actuel pour le chat conversationnel (pas de schéma = pas de validation).

La Hard Policy (couche 1) remplace les "safety footers" actuels dans les templates Jinja2, qui étaient modifiables en éditant les fichiers. Ils deviennent immuables dans le code.

### Séquence de validation complète

```
LLM répond
   ↓
output_schema_id configuré ? ── Non → retourner raw_output (chat)
   │ Oui
   ↓
validate(raw_output, schema)
   ↓ valid ?
   ├── Oui → GatewayResult(structured_output=parsed)
   └── Non → build_repair_prompt(raw, errors, schema)
               ↓
           LLM répond (repair)
               ↓
           validate(repair_output, schema)
               ↓ valid ?
               ├── Oui → GatewayResult(structured_output=parsed, meta.repair_attempted=true)
               └── Non → fallback_use_case configuré ?
                           ├── Oui → execute(fallback_use_case, ...) → GatewayResult(meta.fallback_triggered=true)
                           └── Non → OutputValidationError(502, meta.validation_errors=[...])
```

### Hard Policy — 3 profils (tous immuables, sélection par safety_profile)

Voir Task 1 pour le contenu complet de chaque profil. La sélection se fait dans `LLMGateway.execute()` via `get_hard_policy(use_case_config.safety_profile)`. Les 3 profils partagent les règles fondamentales (ne pas révéler les instructions, langue utilisateur, pas de données inventées) et diffèrent sur ce qui est spécifique à leur domaine.

| Profil | Spécificité principale |
|---|---|
| `astrology` | Non-fatalisme, conditionnel, pas de diagnostic |
| `support` | Pas de promesse contractuelle, pas de contenu ésotérique |
| `transactional` | Exactitude des données, pas d'ambiguïté sur montants/dates |

### Repair prompt — structure

```
La réponse précédente n'est pas conforme au format attendu.
Erreurs : {errors}
Schéma attendu : {schema_summary}
Réponse originale : {raw_output}

Corrige uniquement le format en produisant un JSON valide conforme au schéma. Ne modifie pas le contenu.
```

### Evidence — convention d'identifiants

Format : `ENTITE_VALEUR_CONTEXTE` en `UPPER_SNAKE_CASE`. Exemples :

| Identifiant | Signification |
|---|---|
| `SUN_TAURUS_H10` | Soleil en Taureau en maison 10 |
| `MOON_CANCER_H4` | Lune en Cancer en maison 4 |
| `ASPECT_JUPITER_SEXTILE_MERCURY_ORB_0.28` | Aspect Jupiter sextile Mercure, orbe 0.28° |
| `ASC_SCORPIO` | Ascendant Scorpion |
| `CARD_THE_MOON_POSITION_2` | La Lune en position 2 du tirage |

Ce format permet de détecter les hallucinations (un identifiant non présent dans le contexte natal fourni = invention du modèle) et de debugger facilement.

La convention doit être injectée dans le `developer_prompt` de chaque use_case astrologique via le placeholder `{{evidence_format_instructions}}` (à ajouter dans `required_prompt_placeholders` de 28.5).

### Scope

- `hard_policy.py` : 3 profils immuables + `get_hard_policy()`.
- `output_validator.py` + `repair_prompter.py` + validateur evidence.
- Modèle DB `LlmOutputSchema` + migration.
- Mise à jour `GatewayResult` et séquence dans `LLMGateway.execute()`.
- Schéma `AstroResponse_v1` avec evidence pattern en DB (seed initial).
- Endpoints admin lecture seule pour les schémas.

### Out of Scope

- Édition des JSON Schemas via l'admin (lecture seule en v1, écriture = déploiement).
- Validation des inputs utilisateur (pas dans le scope LLM gateway).
- Tool calling / function calling (story future).

### Technical Notes

- Validation JSON Schema : utiliser `jsonschema` (déjà dans les dépendances Python ou à ajouter).
- `additionalProperties: false` dans tous les schémas pour éviter les champs inattendus.
- Le repair prompt est envoyé sans stream et sans cache (pas de point d'un résultat de repair en cache).
- Logger les `validation_errors` dans les méta (sanitisées, pas de données utilisateur dans les erreurs de schema).
- **Non-régression Persona (from 28.3)** :
  - `meta.persona_id` doit être `None` si aucun bloc persona n'est injecté (AC6).
  - Les champs persona doivent être sanitisés via `_sanitize_string` (neutralisation des `{{` et `}}`).
  - Toute action admin (Persona/Prompt) doit utiliser un `target_type` dynamique dans l'audit log (`llm_persona`, `llm_prompt`, `llm_use_case`).
  - Un use_case avec `persona_strategy=required` sans persona active doit lever une `GatewayConfigError`.

### Tests

- `test_hard_policy.py` : couche 1 toujours présente et identique dans tous les appels gateway.
- `test_output_validator.py` : JSON valide → valid, JSON invalide → errors listées, texte non-JSON → error "not parsable".
- `test_repair_prompter.py` : structure du prompt de repair, inclusion des erreurs et du schéma.
- `test_validation_sequence.py` : valid dès le 1er appel, valid après repair, fallback use_case, OutputValidationError.
- `test_gateway_no_schema.py` : use_case chat sans schema → `raw_output`, pas de `structured_output`.

### Rollout / Feature Flag

- Dépend du flag `LLM_ORCHESTRATION_V2` de Story 28.1.
- La Hard Policy est active dès que le flag est activé.
- La validation des schémas est activée use_case par use_case via `output_schema_id`.

### Observability

- Metric : `llm_output_validation_total{use_case, status}` (status : valid / repair_success / fallback / error).
- Metric : `llm_repair_attempts_total{use_case}`.
- Log structuré : `validation_errors`, `repair_attempted`, `fallback_triggered`, `schema_id`.

### Dependencies

- 28.1 (LLM Gateway) : intégration de la séquence validate+repair+fallback dans `execute()`.
- 28.2 (Prompt Registry v2) : `LlmUseCaseConfig.output_schema_id` et `fallback_use_case_key`.
- `jsonschema` : ajouter à `backend/pyproject.toml` si absent.

### Project Structure Notes

- Nouveaux fichiers :
  - `backend/app/llm_orchestration/policies/hard_policy.py`
  - `backend/app/llm_orchestration/services/output_validator.py`
  - `backend/app/llm_orchestration/services/repair_prompter.py`
- Modèle DB : `backend/app/models/llm_output_schema.py`.
- Migration : `backend/alembic/versions/`.
- Endpoints : dans `backend/app/api/v1/routers/admin_llm.py`.
- Story artifact : `_bmad-output/implementation-artifacts/`.
- Planning source : `_bmad-output/planning-artifacts/epic-28-llm-orchestration-layer.md`.

### References

- [Source: _bmad-output/planning-artifacts/epic-28-llm-orchestration-layer.md]
- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [jsonschema Python](https://python-jsonschema.readthedocs.io/)

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- SQLite duplicate column errors handled by manual alembic_version update.
- Pydantic rebuilt issues fixed by explicit rebuilding and importing types.
- Fixed accidental gateway.py overwrite by complete rewrite with latest logic.

### Implementation Plan

1. Implement Hard Policy system with 3 immutable profiles.
2. Create LlmOutputSchema model and seed ChatResponse_v1/AstroResponse_v1.
3. Build output_validator and repair_prompter services.
4. Integrate validation -> repair -> fallback loop in LLMGateway.
5. Create admin endpoints for schemas and use-case configuration.
6. Verify with unit and integration tests.

### Completion Notes List

- All 8 criteria of acceptance are met.
- Structured outputs are supported via `response_format` in ResponsesClient.
- Automated repair cycle triggered on JSON Schema failure (1 attempt max).
- Fallback use case triggered if repair fails, with priority UseCase > Prompt.
- Hard Policy (Layer 1) is immutable and depends on use case safety profile.
- Admin endpoints allow associating schemas and fallback use cases.
- **Safety Enhancements**:
  - Circuit breaker for infinite fallback loops.
  - Strict runtime validation of platform variables (`locale`, `use_case`).
  - Technical-only developer prompt for repair calls to ensure stability.
  - Extended meta with `validation_status` for better observability.

### File List

- `backend/app/llm_orchestration/policies/hard_policy.py`
- `backend/app/llm_orchestration/services/output_validator.py`
- `backend/app/llm_orchestration/services/repair_prompter.py`
- `backend/app/infra/db/models/llm_output_schema.py`
- `backend/app/infra/db/models/llm_prompt.py` (updated)
- `backend/app/llm_orchestration/gateway.py` (updated)
- `backend/app/llm_orchestration/models.py` (updated)
- `backend/app/llm_orchestration/admin_models.py` (updated)
- `backend/app/api/v1/routers/admin_llm.py` (updated)
- `backend/app/llm_orchestration/providers/responses_client.py` (updated)
- `backend/scripts/seed_28_4.py`
- `backend/app/tests/unit/test_hard_policy.py`
- `backend/app/tests/unit/test_output_validator.py`
- `backend/app/tests/unit/test_repair_prompter.py`
- `backend/app/tests/unit/test_validation_sequence.py`
- `backend/app/tests/integration/test_admin_llm_config_api.py`

## Change Log

- 2026-03-01: Story créée (Epic 28, LLM Orchestration Layer).
- 2026-03-01: Implémentation complète: Hard Policies, Output Schemas, Validation/Repair loop, Admin Endpoints.
