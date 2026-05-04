# Story CS-016 reclasser-dto-persisted-prediction-hors-namespace-legacy: Reclasser les DTO persisted prediction hors du namespace legacy

Status: done

## 1. Objective

Donner un owner stable aux read models persisted prediction utilises par l'infra DB, puis migrer les imports hors `app.prediction` sans double implementation active.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prediction/2026-05-04-1130/03-story-candidates.md#SC-003`
- Reason for change: le finding `F-003` montre que les repositories DB importent encore des DTO situes dans le namespace legacy.

## 3. Domain Boundary

- Domain: `backend/app/infra/db/repositories`
- In scope:
  - Classification de chaque type persisted en `domain-pure` ou `infra-read-model`.
  - Migration des imports repositories, services et tests vers l'owner retenu.
  - Suppression des imports `app.prediction.persisted_*` et `app.prediction.context` dans l'infra DB.
  - Audit persistant des decisions par type.
- Out of scope:
  - Suppression complete de `backend/app/prediction`.
  - Migration du moteur pur.
  - Changement de schema SQL ou migration Alembic.
  - Changement de contrat API.
- Explicit non-goals:
  - Ne pas affaiblir `RG-027` ni `RG-032`.
  - Ne pas creer deux DTO actifs pour un meme contrat.
  - Ne pas importer l'infra depuis le domaine pur.

## 4. Operation Contract

- Operation type: move
- Primary archetype: service-boundary-refactor
- Archetype reason: la story corrige la direction de dependance entre infra DB et types prediction.
- Behavior change allowed: no
- Behavior change constraints:
  - Les chemins d'import changent, pas les donnees persistees.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un type ne peut pas etre classe sans arbitrage entre contrat domaine pur et read model infra.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests persistence et repositories DB sont la source executable du contrat. |
| Baseline Snapshot | yes | Les imports et types doivent etre compares avant/apres. |
| Ownership Routing | yes | Chaque DTO persisted doit avoir un owner canonique. |
| Allowlist Exception | no | Aucune exception `app.prediction.persisted_*` n'est autorisee. |
| Contract Shape | no | Le shape serialise ne doit pas changer. |
| Batch Migration | no | La migration est bornee aux DTO persisted et consommateurs directs. |
| Reintroduction Guard | yes | Les imports legacy doivent etre bloques. |
| Persistent Evidence | yes | La classification par type doit rester auditable. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - DB schema inspect() et mapping repository existants.
  - Tests persistence sous `backend/app/tests/integration`.
  - Repositories DB sous `backend/app/infra/db/repositories`.
- Secondary evidence:
  - Scans `rg` des imports `app.prediction.persisted` et `app.prediction.context`.
- Static scans alone are not sufficient for this story because:
  - Les imports peuvent etre corriges alors que la persistence regresse.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/persisted-dto-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/persisted-dto-after.md`
- Expected invariant:
  - Les repositories DB ne consomment plus `app.prediction.persisted_*` ni `app.prediction.context`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Read model DB persisted | `backend/app/infra/db/repositories` ou package infra dedie | `backend/app/prediction` |
| Type metier pur partage | `backend/app/domain/prediction` | `backend/app/infra` si le domaine doit l'importer |
| Service application prediction | `backend/app/services/prediction` | `backend/app/infra/db/repositories` pour logique metier |
| Repository SQLAlchemy | `backend/app/infra/db/repositories` | `backend/app/domain/prediction` |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: aucun import legacy persisted ne doit rester apres migration.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: la story ne migre pas le namespace complet, seulement les DTO persisted et leurs consommateurs directs.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Classification DTO | `persisted-dto-classification.md` | Decider owner par type. |
| Inventaire apres | `persisted-dto-after.md` | Prouver imports canoniques et absence de doublon. |

## 4i. Reintroduction Guard

- Guard target:
  - Aucun import `app.prediction.persisted` ou `app.prediction.context` depuis `backend/app/infra/db/repositories`.
  - Aucun DTO persisted duplique entre owner canonique et `app.prediction`.
- The implementation must add or update an architecture guard against reintroduction of those imports.
- Guard evidence:
  - Evidence profile: `targeted_forbidden_symbol_scan`; scan `rg` des imports interdits.
  - Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prediction/2026-05-04-1130/01-evidence-log.md` - `E-009` cite les imports repositories vers `app.prediction`.
- Evidence 2: `_condamad/audits/prediction/2026-05-04-1130/02-finding-register.md` - `F-003` decrit la violation de direction.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Chaque type persisted a un owner documente.
- Les repositories DB importent uniquement des types canoniques.
- Les services et tests consomment le meme owner, sans shim.
- Les tests persistence, scoring relatif et API daily restent passants.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-027` - l'infra ne doit pas contaminer le domaine pur.
  - `RG-032` - aucun nouveau fichier legacy sous `app.prediction`.
  - `RG-036` - invariant cree par cette story pour les DTO persisted.
- Non-applicable invariants:
  - `RG-030` - la resolution astro_foundation n'est pas touchee directement.
- Required regression evidence:
  - Classification persistante, tests persistence, scans imports.
- Allowed differences:
  - Changement de chemin d'import des DTO persisted.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Chaque DTO persisted est classe avec un owner canonique. | Evidence profile: `baseline_before_after_diff`; `pytest -q app/tests/integration/test_v3_persistence.py`. |
| AC2 | Les repositories DB n'importent plus les DTO legacy. | Evidence profile: `python_import_absence`; `pytest -q app/tests/integration/test_v3_persistence.py` et scan `rg`. |
| AC3 | Aucun shim ou double DTO actif ne remplace la migration. | Evidence profile: `no_legacy_contract`; `rg -n "app\\.prediction\\.persisted" app tests -g "*.py"`. |
| AC4 | Les tests persistence restent passants. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/integration/test_v3_persistence.py`. |
| AC5 | L'API daily reste compatible avec les snapshots persisted. | Evidence profile: `runtime_openapi_contract`; `pytest -q app/tests/integration/test_daily_prediction_api.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Classer les DTO persisted et persister la decision (AC: AC1)
- [x] Task 2 - Migrer les imports repositories vers l'owner canonique (AC: AC2)
- [x] Task 3 - Migrer services, tests et fixtures consommateurs (AC: AC3, AC4)
- [x] Task 4 - Verifier l'API daily et les scans anti-shim (AC: AC3, AC5)
- [x] Task 5 - Mettre a jour les guards de frontiere lies aux imports persisted (AC: AC2, AC3)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Les DTO existants comme source de migration.
  - Les tests persistence existants.
- Do not recreate:
  - `PersistedPredictionSnapshot` sous deux packages actifs.
  - `CalibrationData` avec deux definitions divergentes.
- Shared abstraction allowed only if:
  - Elle devient l'unique owner d'un contrat partage documente.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- `from app.prediction.persisted_snapshot`
- `from app.prediction.persisted_relative_score`
- `from app.prediction.persisted_baseline`
- `from app.prediction.context import CalibrationData`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Snapshots persisted DB | Decision `persisted-dto-classification.md` | `backend/app/prediction/persisted_snapshot.py` |
| Scores relatifs persisted | Decision `persisted-dto-classification.md` | `backend/app/prediction/persisted_relative_score.py` |
| Baseline utilisateur | Decision `persisted-dto-classification.md` | `backend/app/prediction/persisted_baseline.py` |
| CalibrationData | Decision `persisted-dto-classification.md` | `backend/app/prediction/context.py` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `backend/app/infra/db/repositories/daily_prediction_repository.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/infra/db/repositories/user_prediction_baseline_repository.py`
- `backend/app/prediction/persisted_snapshot.py`
- `backend/app/prediction/persisted_relative_score.py`
- `backend/app/prediction/persisted_baseline.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/infra/db/repositories/daily_prediction_repository.py` - imports DTO canoniques.
- `backend/app/infra/db/repositories/prediction_schemas.py` - import `CalibrationData`.
- `_condamad/stories/CS-016-reclasser-dto-persisted-prediction-hors-namespace-legacy/persisted-dto-classification.md` - decisions.

Likely tests:

- `backend/app/tests/integration/test_v3_persistence.py` - persistence.
- `backend/app/tests/integration/test_relative_scoring_service.py` - scoring relatif.
- `backend/app/tests/integration/test_daily_prediction_api.py` - API daily.

Files not expected to change:

- `backend/alembic` - pas de migration DB attendue.
- `frontend/src` - aucun impact frontend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/integration/test_v3_persistence.py app/tests/integration/test_relative_scoring_service.py
pytest -q app/tests/integration/test_daily_prediction_api.py
rg -n "app\.prediction\.persisted|app\.prediction\.context" app/infra/db/repositories -g "*.py"
rg -n "from app\.prediction\.persisted|from app\.prediction\.context" app tests -g "*.py"
ruff check app/infra/db/repositories app/tests
```

## 22. Regression Risks

- Risk: classification incorrecte entre domaine pur et infra read model.
  - Guardrail: `AC1` bloque sans decision par type.
- Risk: duplication silencieuse des DTO.
  - Guardrail: `AC3` impose scan anti-shim et anti-doublon.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 24. References

- `_condamad/audits/prediction/2026-05-04-1130/03-story-candidates.md#SC-003` - candidate source.
- `_condamad/audits/prediction/2026-05-04-1130/02-finding-register.md#F-003` - finding source.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
