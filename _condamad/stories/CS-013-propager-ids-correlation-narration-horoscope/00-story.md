# Story CS-013 propager-ids-correlation-narration-horoscope: Propager les IDs de correlation vers la narration horoscope

Status: ready-to-review

## 1. Objective

Remplacer la generation locale d'UUID dans la projection prediction par la propagation du `request_id` et du `trace_id` issus du chemin API ou service.
La narration horoscope daily doit recevoir les IDs canoniques pour que logs et metriques restent correlables.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-008`
- Reason for change: le finding `F-008` indique que `public_projection.py` genere des UUID locaux avant d'appeler le LLM.

## 3. Domain Boundary

- Domain: `backend/app/services/prediction`
- In scope:
  - Identifier la source canonique de `request_id` et `trace_id`.
  - Propager ces IDs depuis API vers service prediction puis narration horoscope.
  - Supprimer la generation locale dans `public_projection.py`.
  - Ajouter tests de propagation.
- Out of scope:
  - Refonte globale observability.
  - Changement de format logs.
  - Changement du payload public prediction.
  - Migration complete de `public_projection.py`.
- Explicit non-goals:
  - Ne pas recreer un fallback silencieux `uuid.uuid4()` dans la projection.
  - Ne pas modifier les invariants LLM `RG-017` et `RG-019`.
  - Ne pas introduire une nouvelle lib de tracing.

## 4. Operation Contract

- Operation type: update
- Primary archetype: ownership-routing-refactor
- Archetype reason: la story route la responsabilite de correlation vers le chemin API/service canonique.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les IDs transmis au LLM changent pour utiliser la source canonique.
  - Le payload public et les status codes restent inchanges.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: aucun standard backend de request id n'existe.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les IDs doivent etre verifies au runtime dans le chemin API/service. |
| Baseline Snapshot | yes | Le payload public doit rester stable. |
| Ownership Routing | yes | La correlation appartient au chemin request/service. |
| Allowlist Exception | yes | L'absence d'exception `uuid.uuid4()` doit etre explicite. |
| Contract Shape | yes | Le JSON public ne doit pas changer. |
| Batch Migration | no | Un flux de correlation est touche. |
| Reintroduction Guard | yes | `uuid.uuid4()` ne doit pas revenir dans la projection. |
| Persistent Evidence | yes | La source canonique et les preuves doivent etre persistees. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - TestClient ou AST guard injectant `request_id` et `trace_id`, puis espionnant l'appel narration.
- Secondary evidence:
  - Scan exact `uuid.uuid4()` dans `public_projection.py`.
- Static scans alone are not sufficient for this story because:
  - La propagation doit etre prouvee sur le flux d'appel effectif.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, API contract changes, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/correlation-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/correlation-after.md`
- Expected invariant:
  - Le payload public reste stable et les IDs transmis au LLM proviennent de l'appelant.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Application use case | `services/**` | `api/**` |
| HTTP-only adapter | `api/v1/**` | `services/**` |
| Pure cross-cutting helper | `core/**` | `api/**` |
| Persistence detail | `infra/**` | `api/**` |
| Domain invariant | `domain/**` | `api/**` |
| Request correlation source | API dependency or service request context | local UUID in projection |
| Horoscope narration IDs | `services/llm_generation/horoscope_daily` input | generated inside projection |

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/prediction/public_projection.py` | `uuid.uuid4()` | Aucune exception autorisee pour la generation locale. | Permanent prohibition. |

Rules:

- no wildcard
- no folder-wide exception
- no implicit exception
- every exception must be validated by test or scan

## 4f. Contract Shape

Use when the story touches an API, HTTP error, payload, export, DTO, OpenAPI contract, generated client, or frontend type.

- Contract type:
  - Payload public prediction et input interne narration.
- Fields:
  - `request_id`: identifiant de requete transmis au service LLM.
  - `trace_id`: identifiant de trace transmis au service LLM.
- Required fields:
  - Aucun nouveau champ public requis.
- Optional fields:
  - IDs internes selon le standard backend existant.
- Status codes:
  - Aucun changement HTTP.
- Serialization names:
  - Aucun nouveau nom public.
- Frontend type impact:
  - Aucun type frontend.
- Generated contract impact:
  - Aucun changement OpenAPI attendu.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| correlation source | `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/correlation-source.md` | Documenter la source canonique request_id trace_id. |
| before evidence | `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/correlation-before.md` | Capturer la generation locale initiale. |
| after evidence | `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/correlation-after.md` | Prouver la propagation finale. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route, field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- `uuid.uuid4()` dans `backend/app/prediction/public_projection.py`
- generation locale de `request_id` dans projection
- generation locale de `trace_id` dans projection

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` checks forbidden UUID generation.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - `E-007` montre que la projection genere des UUID fallback.
- Evidence 2: `_condamad/audits/prediction/2026-05-03-2214/02-finding-register.md` - `F-008` classe le probleme en observability-gap.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage, notamment `RG-017` et `RG-019`.

## 6. Target State

- La source canonique des IDs est documentee.
- Les IDs sont transmis de l'API ou service vers narration horoscope.
- `public_projection.py` ne genere plus d'UUID locaux.
- Les tests prouvent la correlation sans changer le payload public.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-017` - le runtime LLM reste sur le provider canonique.
  - `RG-019` - l'assembly prompt horoscope daily reste gouvernee.
  - `RG-033` - les IDs de correlation horoscope doivent provenir du chemin API/service.
- Non-applicable invariants:
  - `RG-025` - Stripe n'est pas touche.
- Required regression evidence:
  - Tests de propagation, scan `uuid.uuid4()`, tests narration et API prediction.
- Allowed differences:
  - Les IDs envoyes au LLM ne sont plus aleatoires quand l'appelant fournit des IDs.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La source canonique des IDs est documentee. | Evidence profile: `baseline_before_after_diff`; `pytest -q app/tests/unit/test_request_id.py`. |
| AC2 | Les IDs sont transmis au service narration. | Evidence profile: `runtime_openapi_contract`; `pytest -q app/tests/unit/test_daily_prediction_service.py`. |
| AC3 | La projection ne genere plus d'UUID. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "uuid\\.uuid4\\(" app/prediction/public_projection.py`. |
| AC4 | Le payload public reste stable. | Evidence profile: `json_contract_shape`; `pytest -q app/tests/unit/test_public_projection.py`. |
| AC5 | La garde anti-retour est executable. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Identifier la source canonique (AC: AC1)
- [x] Task 2 - Propager les IDs API vers service (AC: AC2)
- [x] Task 3 - Retirer la generation UUID locale (AC: AC3)
- [x] Task 4 - Verifier le contrat public (AC: AC4)
- [x] Task 5 - Ajouter la garde anti-retour (AC: AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Standard backend existant de `request_id`.
  - `backend/app/api/v1/routers/public/predictions.py` comme adaptateur HTTP.
  - `backend/app/services/llm_generation/horoscope_daily/narration_service.py`.
- Do not recreate:
  - Un nouveau generateur UUID local.
  - Un contexte observability parallele.
  - Une dependance tracing.
- Shared abstraction allowed only if:
  - Elle reutilise une convention request context deja presente.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- `uuid.uuid4()` dans `backend/app/prediction/public_projection.py`
- `request_id = str(uuid.uuid4())`
- `trace_id = str(uuid.uuid4())`
- `LLMNarrator`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| HTTP request id | API dependency or request context | UUID projection local |
| LLM narration trace id | service input from caller | UUID projection local |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/services/prediction/service.py`
- `backend/app/services/prediction/public_predictions.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
- `backend/app/tests/unit/test_request_id.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/public/predictions.py` - passer les IDs au service.
- `backend/app/services/prediction/service.py` - transporter les IDs.
- `backend/app/prediction/public_projection.py` - retirer `uuid.uuid4()`.
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py` - accepter ou propager les IDs.

Likely tests:

- `backend/app/tests/unit/test_daily_prediction_service.py` - propagation service.
- `backend/app/tests/unit/test_request_id.py` - source canonique.
- `backend/app/tests/unit/test_public_projection.py` - contrat public.
- `backend/app/tests/unit/test_daily_prediction_guardrails.py` - garde UUID.

Files not expected to change:

- `frontend/src` - aucun changement de type public.
- `backend/app/domain/llm` - prompt governance hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check app tests
pytest -q app/tests/unit/test_request_id.py app/tests/unit/test_daily_prediction_service.py app/tests/unit/test_ai_engine_adapter.py
pytest -q app/tests/unit/test_public_projection.py app/tests/integration/test_daily_prediction_api.py app/tests/unit/test_daily_prediction_guardrails.py
rg -n "uuid\\.uuid4\\(|request_id = str\\(|trace_id = str\\(" app/prediction/public_projection.py
```

## 22. Regression Risks

- Risk: aucun standard request id n'existe.
  - Guardrail: `AC1` bloque jusqu'a preuve ou decision utilisateur.
- Risk: la correction change le payload public.
  - Guardrail: `AC4` impose tests JSON API.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 24. References

- `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - preuve `E-007`.
- `_condamad/audits/prediction/2026-05-03-2214/02-finding-register.md#F-008` - finding source.
- `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-008` - candidate d'origine.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
