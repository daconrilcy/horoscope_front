# Story 29.2: N2 — NatalInterpretationServiceV2 + Endpoint

Status: done

## Story

As a utilisateur,
I want demander une interprétation natale (SIMPLE ou COMPLETE) via un nouvel endpoint,
so that je bénéficie de l'orchestration LLMGateway avec gestion des personas et fallbacks.

## Acceptance Criteria

1. L'endpoint `POST /v1/natal/interpretation` est implémenté et protégé par authentification.
2. Le service supporte deux niveaux : `short` (SIMPLE/gratuit) et `complete` (COMPLETE/payant).
3. Pour le mode COMPLETE, le `persona_name` est résolu en base de données à partir de `persona_id` avant l'appel au Gateway.
4. Le service injecte systématiquement le `chart_json` en double format :
   - `user_input.chart_json` (dict) pour la validation par le JSON Schema.
   - `context.chart_json` (string JSON) pour le rendu du prompt Jinja2.
5. Les résultats structurés (`AstroResponse_v1`) du Gateway sont retournés au client.
6. La réponse inclut systématiquement un objet `interpretation_meta` enrichi :
   - `level` (short|complete), `use_case_key`, `persona_id`, `persona_name`, `prompt_version_id`, `was_fallback`, `latency_ms`.
7. La gestion des erreurs du Gateway (UnknownUseCase, InputValidation, UpstreamError, etc.) est mappée sur des codes HTTP appropriés.
7. Le flag `llm_orchestration_v2` contrôle l'accès à cette nouvelle logique (retourne 501 si désactivé).

## Tasks / Subtasks

- [x] Créer les schémas Pydantic dans `backend/app/api/v1/schemas/natal_interpretation.py`
  - [x] Définir `NatalInterpretationRequest`, `InterpretationMeta`, `NatalInterpretationData` et `NatalInterpretationResponse`
- [x] Créer `backend/app/services/natal_interpretation_service_v2.py`
  - [x] Implémenter `NatalInterpretationServiceV2.interpret`
  - [x] Intégrer l'appel à `LLMGateway.execute()`
  - [x] Gérer la résolution de la persona et la construction du contexte
- [x] Créer le router API dans `backend/app/api/v1/routers/natal_interpretation.py`
  - [x] Implémenter l'endpoint `POST /interpretation`
  - [x] Récupérer le dernier thème natal de l'utilisateur via `UserNatalChartService`
- [x] Enregistrer le nouveau router dans `backend/app/main.py`
- [x] Créer les tests d'intégration dans `backend/app/tests/integration/test_natal_interpretation_endpoint.py`
  - [x] Mocker le Gateway pour tester les succès et les échecs (404, 500, 502, 503)

## Dev Notes

- Le service V2 est une nouvelle classe pour éviter de casser l'existant.
- Utiliser `LLMGateway` de `app.llm_orchestration.gateway`.
- Le `chart_json` doit être passé deux fois : en dict pour la validation de schéma et en string pour le rendu du prompt.
- L'interprétation structurée doit respecter le contrat `AstroResponse_v1`.

### Technical Requirements

- Backend: FastAPI/Python 3.13
- Database: SQLAlchemy (pour charger les personas et les charts)
- Gateway integration: LLMGateway V2

### File Structure Requirements

- `backend/app/api/v1/schemas/natal_interpretation.py`
- `backend/app/services/natal_interpretation_service_v2.py`
- `backend/app/api/v1/routers/natal_interpretation.py`
- `backend/app/tests/integration/test_natal_interpretation_endpoint.py`

### Testing Requirements

- Tests d'intégration avec `httpx.AsyncClient`.
- Mocks asynchrones du Gateway.

### References

- Epic/Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 29, Story 29.2)
- Context documentation: `docs/agent/story-29-N2-natal-interpretation-gateway.md`

## Addendum Run/Prod (2026-03-04)

### Incident

- Erreurs intermittentes `500 internal_error` sur `POST /v1/natal/interpretation`.
- Trace backend: `sqlalchemy.exc.MultipleResultsFound: Multiple rows were found when one or none was required`.

### Root Cause

- La lecture du cache d'interprétation utilisait `scalar_one_or_none()` sur une clé supposée unique.
- Des doublons historiques existaient dans `user_natal_interpretations` pour une même clé logique (`user_id`, `chart_id`, `level`, `persona_id` nullable).

### Correctifs appliqués

- Service:
  - `backend/app/services/natal_interpretation_service_v2.py`
  - fallback robuste en cas de doublons: récupération du record le plus récent (`created_at DESC, id DESC`) au lieu de crash.
- Base de données:
  - migration `backend/migrations/versions/20260304_0028_dedupe_and_unique_user_natal_interpretations.py`
  - nettoyage des doublons + création de contraintes d'unicité partielles (cas `persona_id IS NULL` et `persona_id IS NOT NULL`).
- Modèle ORM:
  - `backend/app/infra/db/models/user_natal_interpretation.py` aligné avec les index uniques partiels.
- Exploitation:
  - script `backend/scripts/diagnose_natal_interpretation_duplicates.py` pour audit pré-migration sur staging/prod.

### Validation

- Test unitaire ajouté pour couvrir le scénario doublons/cache.
- Vérification manuelle post-fix: endpoint ne renvoie plus d'erreur 500 sur retries/reconnexion.
