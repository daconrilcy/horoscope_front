# Story CS-007 extraire-dependances-infra-hors-prediction: Extraire les dependances infra hors prediction

Status: done

## 1. Objective

Deplacer le chargement de contexte DB et la persistence des sorties prediction hors du package `backend/app/prediction`.
Le domaine prediction doit consommer des ports ou contrats purs, tandis que SQLAlchemy et les repositories restent sous `infra` ou sous un service applicatif explicite.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-002`
- Reason for change: le finding `F-002` montre des imports SQLAlchemy, repositories, settings et LLM dans prediction.

## 3. Domain Boundary

- Domain: `backend/app/services/prediction`
- In scope:
  - Extraction du chargement contexte DB depuis `backend/app/prediction/context_loader.py`.
  - Extraction de la persistence depuis `backend/app/prediction/persistence_service.py`.
  - Interfaces minimales pour le moteur ou service de calcul prediction.
  - Migration des imports consommateurs directs.
- Out of scope:
  - Refonte du payload public V4.
  - Refonte de la narration LLM horoscope.
  - Creation d'un nouveau dossier racine sous `backend/`.
  - Changement du schema DB.
- Explicit non-goals:
  - Ne pas contourner `RG-011` sur les fixtures DB de tests.
  - Ne pas modifier les invariants LLM `RG-016` a `RG-019`.
  - Ne pas garder `app.prediction.context_loader` comme facade importable.

## 4. Operation Contract

- Operation type: move
- Primary archetype: service-boundary-refactor
- Archetype reason: la story deplace des responsabilites DB hors d'un package metier vers service et infra.
- Behavior change allowed: no
- Behavior change constraints:
  - Les snapshots persistes et les tests e2e prediction doivent rester equivalentes.
  - Les changements autorises portent sur les imports et owners.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: le nom canonique du service de contexte ou de persistence ne peut pas etre deduit des owners existants.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La persistence DB doit etre prouvee par tests avec session effective. |
| Baseline Snapshot | yes | Le refactor doit comparer les imports et comportements avant apres. |
| Ownership Routing | yes | DB et repositories doivent etre routes vers infra ou service. |
| Allowlist Exception | no | Aucune exception large n'est admise. |
| Contract Shape | no | Le schema public ne doit pas changer. |
| Batch Migration | no | La story porte sur deux modules lies. |
| Reintroduction Guard | yes | SQLAlchemy ne doit pas revenir dans le futur domaine pur. |
| Persistent Evidence | yes | Les scans avant apres doivent etre conserves. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - DB schema verifie par `inspect()` et tests de persistence avec session SQLAlchemy effective.
- Secondary evidence:
  - Scans imports `sqlalchemy`, `Session`, repositories et `app.infra` sous `backend/app/prediction`.
- Static scans alone are not sufficient for this story because:
  - Une importation propre ne prouve pas que les donnees sont chargees et sauvegardees avec la meme semantique.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, API contract changes, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/CS-007-extraire-dependances-infra-hors-prediction/infra-dependency-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-007-extraire-dependances-infra-hors-prediction/infra-dependency-after.md`
- Expected invariant:
  - Les tests `test_context_loader.py`, `test_prediction_persistence.py` et `test_engine_persistence_e2e.py` restent passants.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Application use case | `services/**` | `api/**` |
| HTTP-only adapter | `api/v1/**` | `services/**` |
| Pure cross-cutting helper | `core/**` | `api/**` |
| Persistence detail | `infra/**` | `api/**` |
| Domain invariant | `domain/**` | `api/**` |
| Prediction context loading use case | `backend/app/services/prediction` | `backend/app/prediction` |
| Prediction DB implementation | `backend/app/infra/**` | `backend/app/prediction` |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| dependency baseline | `_condamad/stories/CS-007-extraire-dependances-infra-hors-prediction/infra-dependency-before.md` | Capturer imports infra actuels. |
| dependency after | `_condamad/stories/CS-007-extraire-dependances-infra-hors-prediction/infra-dependency-after.md` | Prouver l'absence d'import infra interdit. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route, field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- `from sqlalchemy`
- `Session`
- `DailyPredictionRepository`
- `PredictionReferenceRepository`
- `PredictionRulesetRepository`
- `from app.infra`

Guard evidence:

- Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` checks forbidden imports.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - `E-005` montre `PredictionContextLoader` couple a SQLAlchemy et repositories.
- Evidence 2: `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - `E-006` montre `PredictionPersistenceService` couple aux models et repositories infra.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage, notamment `RG-011`, `RG-016` a `RG-019`.

## 6. Target State

- Les acces DB prediction passent par un owner infra ou service explicite.
- `backend/app/prediction` ne contient plus SQLAlchemy ni repositories DB.
- Les tests de persistence existants continuent de verifier le comportement.
- Une garde AST bloque le retour de dependances infra dans le domaine pur.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-011` - les tests DB doivent passer par les helpers ou fixtures canoniques.
  - `RG-026` - la convergence du namespace prediction ne doit pas etre contournee.
  - `RG-027` - SQLAlchemy et repositories ne doivent pas redevenir dependances du domaine prediction pur.
- Non-applicable invariants:
  - `RG-025` - Stripe n'est pas touche.
- Required regression evidence:
  - Tests de persistence, tests daily prediction, scans imports infra et garde AST.
- Allowed differences:
  - Chemins d'import internes vers les nouveaux owners.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le contexte n'importe plus SQLAlchemy depuis prediction. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |
| AC2 | La persistence prediction reste fonctionnelle. | Evidence profile: `baseline_before_after_diff`; `pytest -q app/tests/unit/test_context_loader.py`. |
| AC3 | Les consumers utilisent le service canonique. | Evidence profile: `repo_wide_negative_scan`; `rg -n "app\\.prediction\\.context_loader" app tests`. |
| AC4 | Pas de racine `backend/prediction`. | Evidence profile: `targeted_forbidden_symbol_scan`; `python -c "import os; assert not os.path.exists('prediction')"`. |
| AC5 | Les preuves avant apres sont persistees. | Evidence profile: `baseline_before_after_diff`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer les imports infra actuels (AC: AC1, AC5)
- [x] Task 2 - Definir les ports minimaux contexte et persistence (AC: AC2, AC3)
- [x] Task 3 - Deplacer les implementations DB vers owner canonique (AC: AC1, AC2)
- [x] Task 4 - Migrer les consumers sans facade (AC: AC3)
- [x] Task 5 - Ajouter la garde AST (AC: AC1, AC4)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/services/prediction` pour les use cases existants.
  - Repositories existants sous `backend/app/infra`.
  - Helpers DB de test documentes par `RG-011`.
- Do not recreate:
  - Un second repository prediction.
  - Un wrapper DB dans `app.prediction`.
  - Une facade importable pour les anciens modules.
- Shared abstraction allowed only if:
  - Elle remplace les chemins DB dupliques entre chargement contexte et persistence.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- `backend/app/prediction/context_loader.py` comme facade.
- `backend/app/prediction/persistence_service.py` comme facade.
- `from app.prediction.context_loader import`
- `from app.prediction.persistence_service import`
- `from sqlalchemy` dans `backend/app/prediction`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Chargement contexte prediction | `backend/app/services/prediction` plus adapter infra | `backend/app/prediction/context_loader.py` |
| Persistence prediction | `backend/app/infra/**` ou `backend/app/services/prediction` | `backend/app/prediction/persistence_service.py` |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- preserving a wrapper
- adding a compatibility alias
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop and record the exact external evidence.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `backend/app/prediction/context_loader.py`
- `backend/app/prediction/persistence_service.py`
- `backend/app/services/prediction/compute_runner.py`
- `backend/app/services/prediction/service.py`
- `backend/tests/integration/app_db.py`
- `backend/app/tests/unit/test_context_loader.py`
- `backend/app/tests/unit/test_daily_prediction_service.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/services/prediction` - ports et use cases de contexte ou persistence.
- `backend/app/infra` - implementation DB canonique si un adapter manque.
- `backend/app/prediction/context_loader.py` - suppression ou migration.
- `backend/app/prediction/persistence_service.py` - suppression ou migration.

Likely tests:

- `backend/app/tests/unit/test_context_loader.py` - nouveau owner contexte.
- `backend/app/tests/integration/test_prediction_persistence.py` - persistence inchangee.
- `backend/app/tests/unit/test_daily_prediction_guardrails.py` - garde imports infra.

Files not expected to change:

- `frontend/src` - aucune integration frontend.
- `backend/app/api/v1/routers/public/predictions.py` - API hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check app tests
pytest -q app/tests/unit/test_context_loader.py app/tests/unit/test_daily_prediction_service.py app/tests/unit/test_daily_prediction_guardrails.py
pytest -q app/tests/integration/test_prediction_persistence.py app/tests/integration/test_engine_persistence_e2e.py
rg -n "sqlalchemy|Session|DailyPredictionRepository|PredictionReferenceRepository|PredictionRulesetRepository|from app\\.infra" app/prediction -g "*.py"
rg -n "app\\.prediction\\.context_loader|app\\.prediction\\.persistence_service" app tests
python -c "import os; assert not os.path.exists('prediction')"
```

## 22. Regression Risks

- Risk: la persistence sauvegarde un bundle incomplet apres migration.
  - Guardrail: `AC2` impose les tests de persistence existants.
- Risk: le domaine pur recupere une dependance SQLAlchemy.
  - Guardrail: `AC1` impose garde AST et scan cible.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 24. References

- `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - preuves `E-002`, `E-005`, `E-006`.
- `_condamad/audits/prediction/2026-05-03-2214/02-finding-register.md#F-002` - finding source.
- `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-002` - candidate d'origine.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
