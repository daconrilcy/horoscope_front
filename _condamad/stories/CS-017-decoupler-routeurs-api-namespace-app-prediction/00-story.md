# Story CS-017 decoupler-routeurs-api-namespace-app-prediction: Decoupler les routeurs API du namespace app.prediction

Status: done

## 1. Objective

Faire consommer aux routeurs API prediction uniquement les services et contrats canoniques.
Les chemins et erreurs OpenAPI existants doivent rester preserves.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prediction/2026-05-04-1130/03-story-candidates.md#SC-004`
- Reason for change: le finding `F-004` montre que les routeurs `public/predictions.py` et `internal/llm/qa.py` importent encore `app.prediction`.

## 3. Domain Boundary

- Domain: `backend/app/api/v1/routers`
- In scope:
  - Remplacement des imports directs `app.prediction` dans les routeurs API.
  - Consommation via `backend/app/services/prediction` ou contrats API canoniques.
  - Preservation des chemins, status codes et enveloppes d'erreur existants.
  - Scan zero import `app.prediction` sous `backend/app/api`.
- Out of scope:
  - Migration du moteur pur.
  - Reclassification des DTO persisted hors besoins des routeurs.
  - Changement volontaire de contrat OpenAPI.
  - Modification frontend.
- Explicit non-goals:
  - Ne pas affaiblir `RG-006`, `RG-029` ou `RG-033`.
  - Ne pas deplacer de logique metier dans les routeurs.
  - Ne pas creer de wrapper API autour de `app.prediction`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: api-adapter-boundary-convergence
- Archetype reason: la story restaure la frontiere adaptateur API vers services et contrats canoniques.
- Behavior change allowed: no
- Behavior change constraints:
  - Les imports changent, pas les routes, payloads ni erreurs.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: la projection publique n'a pas d'owner canonique disponible apres inspection.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les routes FastAPI et OpenAPI doivent rester equivalentes. |
| Baseline Snapshot | yes | Les chemins et schemas exposes doivent etre compares avant/apres. |
| Ownership Routing | yes | Les routeurs doivent rester adaptateurs HTTP. |
| Allowlist Exception | yes | Les imports directs actuels sont des exceptions temporaires a eliminer. |
| Contract Shape | no | Aucun shape API ne doit changer. |
| Batch Migration | no | La story est limitee aux routeurs API cites. |
| Reintroduction Guard | yes | Les imports `app.prediction` sous API doivent etre bloques. |
| Persistent Evidence | yes | Le diff OpenAPI et l'audit imports doivent etre conserves. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `app.openapi()` pour les chemins publics et schemas touches.
- Secondary evidence:
  - Tests API daily et narration horoscope.
- Static scans alone are not sufficient for this story because:
  - Les imports peuvent changer tout en cassant un contrat HTTP expose.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/openapi-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/openapi-after.json`
- Expected invariant:
  - Aucun changement OpenAPI non documente pour les routes prediction.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Adaptation HTTP | `backend/app/api/v1/routers` | `backend/app/services/prediction` |
| Use case prediction | `backend/app/services/prediction` | `backend/app/api/v1/routers` |
| Contrat de sortie API | Owner canonique API ou `services/api_contracts` | `backend/app/prediction` |
| Projection publique deterministe | Owner confirme par story | `backend/app/api/v1/routers` |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/api/v1/routers/public/predictions.py` | `from app.prediction` | Dette `F-004` a supprimer. | Until AC2 is satisfied in CS-017. |
| `backend/app/api/v1/routers/internal/llm/qa.py` | `from app.prediction` | Dette `F-004` a supprimer. | Until AC2 is satisfied in CS-017. |

Rules:

- no wildcard
- no folder-wide exception
- no implicit exception
- every exception must be validated by test or scan

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is intentionally changed.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: la story concerne deux routeurs API, pas une migration par lots multi-domaines.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| OpenAPI avant | `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/openapi-before.json` | Capturer les routes prediction avant changement. |
| OpenAPI apres | `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/openapi-after.json` | Prouver la preservation runtime. |
| Audit imports API | `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/api-import-audit.md` | Prouver zero import `app.prediction` sous API. |

## 4i. Reintroduction Guard

- Guard target:
  - Aucun import `app.prediction` sous `backend/app/api`.
  - Aucun owner de logique metier ajoute dans les routeurs.
- Guard evidence:
  - Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`.
  - Evidence profile: `runtime_openapi_contract`; tests API avec `app.openapi()`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prediction/2026-05-04-1130/01-evidence-log.md` - `E-008` cite les imports API directs.
- Evidence 2: `_condamad/audits/prediction/2026-05-04-1130/02-finding-register.md` - `F-004` decrit le couplage routeurs vers `app.prediction`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les routeurs API prediction importent des services ou contrats canoniques.
- `rg -n "app.prediction" backend/app/api -g "*.py"` est zero-hit.
- OpenAPI reste equivalent pour les routes prediction.
- Les tests API daily et narration horoscope restent passants.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-006` - `backend/app/api` reste un adaptateur HTTP strict.
  - `RG-029` - la projection publique reste deterministe.
  - `RG-033` - les IDs de correlation viennent du chemin API/service.
  - `RG-037` - invariant cree par cette story pour zero import API vers `app.prediction`.
- Non-applicable invariants:
  - `RG-025` - Stripe n'est pas touche.
- Required regression evidence:
  - Diff OpenAPI, tests API, scan API zero import.
- Allowed differences:
  - Changement de chemins d'import internes uniquement.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les routes prediction conservent leur contrat runtime. | Evidence profile: `runtime_openapi_contract`; `pytest -q app/tests/integration/test_daily_prediction_api.py`. |
| AC2 | Aucun import `app.prediction` ne reste sous API. | Evidence profile: `python_import_absence`; `pytest -q app/tests/integration/test_daily_prediction_api.py`. |
| AC3 | Les routeurs consomment des owners canoniques. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |
| AC4 | La narration horoscope daily reste compatible. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/integration/test_horoscope_daily_variant_narration.py`. |
| AC5 | Les snapshots OpenAPI avant/apres sont persistants. | Evidence profile: `openapi_before_after_snapshot`; `pytest -q app/tests/integration/test_daily_prediction_api.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer l'OpenAPI avant et les imports API actuels (AC: AC1, AC5)
- [x] Task 2 - Identifier l'owner canonique de projection et snapshots (AC: AC3)
- [x] Task 3 - Remplacer les imports directs dans les routeurs cites (AC: AC2, AC3)
- [x] Task 4 - Executer tests API et narration (AC: AC1, AC4)
- [x] Task 5 - Persister OpenAPI apres et audit imports (AC: AC2, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/services/prediction` pour les use cases.
  - Contrats API canoniques existants avant d'en creer un nouveau.
- Do not recreate:
  - `PublicPredictionAssembler` dans un routeur.
  - DTO snapshots dans la couche API.
- Shared abstraction allowed only if:
  - Elle devient le contrat canonique unique consomme par les deux routeurs.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- `from app.prediction` dans `backend/app/api`.
- `PublicPredictionAssembler` importe depuis `app.prediction` dans un routeur.
- `PersistedPredictionSnapshot` importe depuis `app.prediction` dans un routeur.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Route HTTP daily prediction | `backend/app/api/v1/routers/public/predictions.py` | logique metier dans routeur |
| Route HTTP QA LLM interne | `backend/app/api/v1/routers/internal/llm/qa.py` | imports `app.prediction` |
| Projection publique | Owner service ou contrat canonique confirme | `backend/app/prediction/public_projection.py` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

Required generated-contract evidence:

- OpenAPI path presence unchanged for routes prediction.
- Generated client/schema absence of unintended diff when generated clients exist.
- Route manifest absence of unintended owner drift when a route manifest exists.

## 18. Files to Inspect First

- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/api/v1/routers/internal/llm/qa.py`
- `backend/app/services/prediction/public_predictions.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/prediction/persisted_snapshot.py`
- `backend/app/tests/integration/test_daily_prediction_api.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/public/predictions.py` - imports canoniques.
- `backend/app/api/v1/routers/internal/llm/qa.py` - imports canoniques.
- `_condamad/stories/CS-017-decoupler-routeurs-api-namespace-app-prediction/api-import-audit.md` - audit imports.

Likely tests:

- `backend/app/tests/integration/test_daily_prediction_api.py` - contrat public.
- `backend/app/tests/integration/test_horoscope_daily_variant_narration.py` - narration daily.
- `backend/app/tests/unit/test_daily_prediction_guardrails.py` - garde API import.

Files not expected to change:

- `frontend/src` - aucun changement de contrat attendu.
- `backend/alembic` - aucune migration DB.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/integration/test_daily_prediction_api.py
pytest -q app/tests/integration/test_horoscope_daily_variant_narration.py
pytest -q app/tests/unit/test_daily_prediction_guardrails.py
rg -n "app\.prediction" app/api -g "*.py"
ruff check app/api app/services/prediction app/tests
```

## 22. Regression Risks

- Risk: un import est remplace par une logique metier locale dans le routeur.
  - Guardrail: `AC3` impose l'audit d'ownership.
- Risk: OpenAPI change sans intention.
  - Guardrail: `AC1` et `AC5` imposent preuve runtime.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 24. References

- `_condamad/audits/prediction/2026-05-04-1130/03-story-candidates.md#SC-004` - candidate source.
- `_condamad/audits/prediction/2026-05-04-1130/02-finding-register.md#F-004` - finding source.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
