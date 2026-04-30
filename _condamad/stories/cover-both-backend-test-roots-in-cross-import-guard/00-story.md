# Story cover-both-backend-test-roots-in-cross-import-guard: Make cross-test import guard cover both backend test roots

Status: ready-for-dev

## 1. Objective

Corriger la garde anti import croise pour scanner les deux racines reelles.
Les racines attendues sont `backend/app/tests` et `backend/tests`.
La garde doit bloquer les imports depuis des modules executables `test_*.py`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md`
- Reason for change: F-103 signale que la garde anti import croise ne scanne pas `backend/tests` a cause d'un calcul de racine incorrect.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: backend tests helper import guard
- In scope:
  - Corriger `BACKEND_ROOT` dans la garde si le calcul exclut `backend/tests`.
  - Affirmer que `TEST_ROOTS` contient `backend/app/tests` et `backend/tests`.
  - Conserver le scan zero-hit sur les imports depuis modules executables `test_*.py`.
- Out of scope:
  - Migrer de nouveaux helpers de tests.
  - Modifier le harnais DB.
  - Changer la topologie pytest.
- Explicit non-goals:
  - Ne pas ajouter d'allowlist pour des imports croises.
  - Ne pas creer d'alias depuis les anciens modules `test_*.py`.
  - Ne pas affaiblir `RG-013`.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: test-guard-hardening
- Archetype reason: la story corrige une garde existante sans changer le comportement applicatif.
- Behavior change allowed: no
- Behavior change constraints:
  - Seule la couverture de scan de la garde change.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un import croise depuis `test_*.py` est encore present et ne peut pas etre remplace par un helper non executable.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La source de verite est l'AST des imports des tests collectables. |
| Baseline Snapshot | yes | Le scan avant/apres doit prouver l'extension de couverture a `backend/tests`. |
| Ownership Routing | no | Aucun helper n'est deplace par cette story. |
| Allowlist Exception | yes | L'archetype impose un registre explicite; il doit rester vide de toute exception active. |
| Contract Shape | no | Aucun contrat API ou DTO n'est modifie. |
| Batch Migration | no | Correction ponctuelle d'une garde. |
| Reintroduction Guard | yes | La garde elle-meme empeche la reintroduction. |
| Persistent Evidence | yes | Le scan avant/apres doit etre conserve. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard import graph lu par `backend/app/tests/unit/test_backend_test_helper_imports.py`.
- Secondary evidence:
  - `rg` cible sur les prefixes `app.tests.*.test_` et `tests.*.test_`.
- Static scans alone are not sufficient for this story because:
  - la garde doit parser les imports Python reels et couvrir les deux racines.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-guard-before.md`
- Comparison after implementation:
  - `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-guard-after.md`
- Expected invariant:
  - La garde scanne `backend/app/tests` et `backend/tests`.
- Allowed differences:
  - Le calcul de racine et les assertions de couverture changent.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-allowlist.md` | none | Aucun import croise autorise. | Permanent zero-entry register. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Guard baseline | `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-guard-before.md` | Montrer la couverture actuelle de la garde. |
| Guard after | `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-guard-after.md` | Prouver que les deux racines sont couvertes. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- AST imports under `backend/app/tests`
- AST imports under `backend/tests`

Required forbidden examples:

- `from app.tests.integration.test_`
- `from app.tests.unit.test_`
- `from tests.integration.test_`
- `from tests.unit.test_`

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_backend_test_helper_imports.py` checks forbidden test-module imports.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md` - F-103 decrit la faille de couverture.
- Evidence 2: `backend/app/tests/unit/test_backend_test_helper_imports.py` - la garde contient `BACKEND_ROOT` et `TEST_ROOTS`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- `TEST_ROOTS` contient explicitement `backend/app/tests` et `backend/tests`.
- La garde echoue si l'une des deux racines est absente.
- Le scan zero-hit des imports croises reste actif.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-013` - la story touche directement la garde anti imports croises.
  - `RG-010` - les racines scannees doivent rester alignées avec la topologie backend.
- Non-applicable invariants:
  - `RG-011` - aucun import DB n'est migre.
  - `RG-014` - aucun test no-op n'est modifie.
- Required regression evidence:
  - `pytest -q app/tests/unit/test_backend_test_helper_imports.py`
  - scan zero-hit `rg` des imports croises.
- Allowed differences:
  - Correction de chemin pour couvrir `backend/tests`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Guard root calculation resolves backend root. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_backend_test_helper_imports.py`. |
| AC2 | Both backend test roots are asserted. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_backend_test_helper_imports.py`. |
| AC3 | Cross-test imports remain absent. | Evidence profile: `repo_wide_negative_scan`; `pytest -q app/tests/unit/test_backend_test_helper_imports.py`. |
| AC4 | Guard evidence is persisted. | Evidence profile: `baseline_before_after_diff`; `pytest -q app/tests/unit/test_backend_test_helper_imports.py`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture the guard coverage baseline (AC: AC4)
- [ ] Task 2 - Correct backend root and test root assertions (AC: AC1, AC2)
- [ ] Task 3 - Run the guard and targeted negative scan (AC: AC3)
- [ ] Task 4 - Persist the after evidence (AC: AC4)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/tests/unit/test_backend_test_helper_imports.py` as the single guard owner.
- Do not recreate:
  - A second cross-test import guard in another file.
  - A regex-only checker that duplicates AST parsing.
- Shared abstraction allowed only if:
  - The same helper is reused by another backend architecture guard.

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
- `from tests.unit.test_`
- `from tests.regression.test_`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

- Canonical ownership: not applicable

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md`
- `_condamad/audits/backend-tests/2026-04-29-1510/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/tests/unit/test_backend_test_helper_imports.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/tests/unit/test_backend_test_helper_imports.py` - correct root calculation and add root assertions.
- `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-guard-before.md` - baseline.
- `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-guard-after.md` - after evidence.

Likely tests:

- `backend/app/tests/unit/test_backend_test_helper_imports.py` - target guard.

Files not expected to change:

- `backend/app/tests/conftest.py` - DB harness belongs to SC-101.
- `backend/pyproject.toml` - topology belongs to SC-102.
- `requirements.txt` - must not be created.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_backend_test_helper_imports.py
rg -n "from app\.tests\.(integration|unit|regression)\.test_|from tests\.(integration|unit|regression)\.test_" app/tests tests -g "test_*.py"
```

## 22. Regression Risks

- Risk: la garde calcule une racine parente incorrecte.
  - Guardrail: assertions explicites sur les deux chemins attendus.
- Risk: le scan manque un import relatif.
  - Guardrail: AST import graph plus prefixes absolus interdits.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respecter l'activation du venv avant toute commande Python.
- Ne pas creer de `requirements.txt`.

## 24. References

- `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md` - finding F-103.
- `_condamad/audits/backend-tests/2026-04-29-1510/03-story-candidates.md` - candidat SC-103.
- `_condamad/stories/regression-guardrails.md` - invariant RG-013.
- `backend/app/tests/unit/test_backend_test_helper_imports.py` - garde a corriger.
