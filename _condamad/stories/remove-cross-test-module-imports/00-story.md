# Story test-helper-import-convergence: Extract cross-test-module helpers

Status: ready-for-dev

## 1. Objective

Extraire les builders, helpers de nettoyage et fixtures reutilises depuis des modules de tests executables.
Les helpers partages doivent vivre dans des modules dedies, hors fichiers 	est_*.py.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-tests/2026-04-28-1600`
- Reason for change: F-005 trouve 9 imports croises entre modules de tests, ce qui couple l'ordre de suite et rend la propriete des helpers implicite.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: backend tests helpers
- In scope:
  - Identifier les 9 imports croises actuels.
  - Extraire les helpers partages dans des modules non executables (`helpers.py`, package `helpers`, ou fixtures `conftest.py`).
  - Mettre a jour les imports consommateurs.
  - Ajouter une garde zero-hit contre les imports depuis `test_*.py`.
- Out of scope:
  - Changer les assertions des tests.
  - Reorganiser toute la topologie des tests.
  - Refactorer les fixtures DB au-dela des helpers de tests concernes.
- Explicit non-goals:
  - Ne pas dupliquer les helpers dans chaque test.
  - Ne pas creer d'alias de compatibilite depuis les anciens modules `test_*.py`.
  - Ne pas ajouter de dossier racine sous `backend/`.

## 4. Operation Contract

- Operation type: move
- Primary archetype: module-move
- Archetype reason: la story deplace des helpers depuis des modules executables vers des proprietaires helper explicites.
- Behavior change allowed: no
- Behavior change constraints:
  - Les tests concernes doivent conserver les memes donnees, assertions et nettoyage.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un helper est en realite une assertion de test et non une utilite partagee.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | Le changement concerne des imports de tests, pas un runtime applicatif. |
| Baseline Snapshot | yes | Les 9 imports croises doivent etre captures avant/apres. |
| Ownership Routing | yes | Les helpers doivent avoir un proprietaire non executable. |
| Allowlist Exception | no | Aucun import croise depuis un module `test_*.py` ne doit rester. |
| Contract Shape | no | Aucun contrat API n'est modifie. |
| Batch Migration | no | Le lot est borne aux 9 imports actuels. |
| Reintroduction Guard | yes | Une garde doit bloquer les nouveaux imports croises. |
| Persistent Evidence | yes | Le scan avant/apres doit etre persiste. |

## 4b. Runtime Source of Truth

- Runtime source of truth: not applicable
- Reason: no API route, DB schema, generated manifest, or runtime registration is changed.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/remove-cross-test-module-imports/cross-test-imports-before.md`
- Comparison after implementation:
  - `_condamad/stories/remove-cross-test-module-imports/cross-test-imports-after.md`
- Expected invariant:
  - Le scan d'import croise retourne zero hit.
- Allowed differences:
  - Deplacement de helpers vers modules non executables; aucun changement d'assertion.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Billing API reusable helpers | Dedicated helper/fixture module | `test_billing_api.py` imported by another test |
| Ops alert reusable helpers | Dedicated helper/fixture module | `test_ops_review_queue_alerts_retry_api.py` imported by another test |
| Regression engine builders | Regression helper module | `test_engine_non_regression.py` imported by integration test |
| Unit event fixtures | Unit helper module or conftest fixture | Import from another `test_*.py` file |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API payload, DTO, status code, generated client type, or frontend type changes.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: all known cross-test imports are in scope and must be removed together.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Import baseline | `_condamad/stories/remove-cross-test-module-imports/cross-test-imports-before.md` | Capturer les 9 imports. |
| Import after | `_condamad/stories/remove-cross-test-module-imports/cross-test-imports-after.md` | Prouver zero hit. |

## 4i. Reintroduction Guard

The implementation must add or update deterministic guards that fail if:

- un fichier sous `backend/app/tests` ou `backend/tests` importe depuis un module `test_*.py`;
- un helper partage est expose uniquement par un test executable;
- un alias re-export est ajoute dans l'ancien module de test.

Required architecture guard: pytest -q app/tests/unit/test_backend_architecture_guard.py with AST guard evidence.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md` - E-008 rapporte 9 imports croises.
- Evidence 2: scan local - imports depuis les tests billing, ops alert, engine regression et entitlement alerts.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Aucun test backend n'importe un autre module de test executable.
- Les helpers partages vivent dans des modules explicitement non executables.
- Une garde empeche la reintroduction du pattern.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-005` - les helpers de tests ne doivent pas masquer une propriete de couche API/services.
  - `RG-006` - les guards architecture doivent rester lisibles et independants.
- Non-applicable invariants:
  - `RG-001`, `RG-002`, `RG-003`, `RG-004`, `RG-007`, `RG-008`, `RG-009` - aucune surface API ou legacy n'est modifiee directement.
- Required regression evidence:
  - Scan zero-hit, tests cibles des consommateurs, collecte pytest.
- Allowed differences:
  - Imports modifies vers helpers canoniques; assertions inchangees.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les 9 imports croises actuels sont remplaces. | Evidence profile: `repo_wide_negative_scan`; `rg -n "from app.tests.*.test_" app/tests tests`. |
| AC2 | Les helpers extraits ont un proprietaire non executable. | Evidence profile: `ast_architecture_guard`; `rg --files app/tests tests -g helpers.py -g conftest.py`. |
| AC3 | Les tests consommateurs continuent de passer. | Evidence profile: `runtime_openapi_contract`; `pytest -q app/tests/integration/test_billing_api_61_65.py`. |
| AC4 | Une garde bloque de nouveaux imports depuis `test_*.py`. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_backend_architecture_guard.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer le scan des imports croises (AC: AC1)
- [x] Task 2 - Extraire les helpers par groupe de responsabilite (AC: AC2)
- [x] Task 3 - Mettre a jour les consommateurs (AC: AC1, AC3)
- [x] Task 4 - Ajouter la garde anti-import croise (AC: AC4)
- [x] Task 5 - Executer tests cibles, collecte et lint (AC: AC3, AC4)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Helpers existants deja non executables, si disponibles.
  - Fixtures `conftest.py` quand le helper est une fixture pytest.
- Do not recreate:
  - Copies locales des memes builders.
  - Re-exports depuis les anciens fichiers `test_*.py`.
- Shared abstraction allowed only if:
  - Au moins deux tests consomment le helper ou le helper remplace une dependance croisee existante.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `from app.tests.integration.test_`
- `from app.tests.unit.test_`
- `from app.tests.regression.test_`
- `from tests.integration.test_`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Shared test helper | Non-test helper module or pytest fixture | Executable `test_*.py` module |
| Cross-test import guard | Dedicated architecture/naming test | Manual review only |

## 14. Delete-Only Rule

- Delete-Only Rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 17. Files to Inspect First

- `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/02-finding-register.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/tests/integration/test_billing_api_61_65.py`
- `backend/app/tests/integration/test_billing_api_61_66.py`
- `backend/app/tests/unit/test_canonical_entitlement_alert_handling_service_events.py`
- `backend/app/tests/integration/test_engine_persistence_e2e.py`
- `backend/app/tests/integration/test_ops_alert_batch_handle_api.py`
- `backend/app/tests/integration/test_ops_alert_events_batch_retry_api.py`
- `backend/app/tests/integration/test_ops_alert_events_list_api.py`
- `backend/app/tests/integration/test_ops_alert_event_handle_api.py`
- `backend/app/tests/integration/test_ops_alert_event_handling_history_api.py`

## 18. Expected Files to Modify

Likely files:

- Existing test files listed in Files to Inspect First - update imports.
- New or existing helper modules under the same approved backend test roots.
- `backend/app/tests/unit/test_backend_test_helper_imports.py` or `backend/tests/unit/test_backend_test_helper_imports.py`.
- `_condamad/stories/remove-cross-test-module-imports/*.md` - evidence.

Likely tests:

- `backend/app/tests/unit/test_backend_test_helper_imports.py` - garde contre imports croises.

Files not expected to change:

- `backend/app/api` - no production route change.
- `frontend/src` - no frontend change.
- `requirements.txt` - must not be created.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_backend_test_helper_imports.py
pytest -q app/tests/integration/test_billing_api_61_65.py app/tests/integration/test_billing_api_61_66.py
pytest -q app/tests/integration/test_ops_alert_batch_handle_api.py
pytest -q app/tests/integration/test_ops_alert_events_batch_retry_api.py
pytest -q app/tests/integration/test_ops_alert_events_list_api.py
pytest -q app/tests/integration/test_ops_alert_event_handle_api.py
pytest -q app/tests/integration/test_ops_alert_event_handling_history_api.py
pytest --collect-only -q --ignore=.tmp-pytest
pytest -q
rg -n "from app\.tests\.integration\.test_|from app\.tests\.unit\.test_|from app\.tests\.regression\.test_|from tests\.integration\.test_" app/tests tests -g test_*.py
```

Story validation:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/remove-cross-test-module-imports/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/remove-cross-test-module-imports/00-story.md
```

## 21. Regression Risks

- Risk: helper extrait perd un nettoyage implicite.
  - Guardrail: tests consommateurs cibles.
- Risk: deux helpers equivalents sont crees.
  - Guardrail: DRY et proprietaire par responsabilite.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Respecter l'activation du venv avant toute commande Python.
- Ne pas creer de `requirements.txt`.

## 23. References

- `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md` - preuve E-008.
- `_condamad/audits/backend-tests/2026-04-28-1600/02-finding-register.md` - finding F-005.
- `_condamad/audits/backend-tests/2026-04-28-1600/03-story-candidates.md` - candidat SC-005.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.







