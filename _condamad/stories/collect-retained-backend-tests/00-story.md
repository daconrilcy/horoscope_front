# Story collect-retained-backend-tests: Collect every retained backend test in the standard pytest command

Status: ready-for-dev

## 1. Objective

Faire en sorte que la commande standard pytest lancee depuis ackend/ collecte tous les tests backend conserves.
Les suites volontairement optionnelles doivent etre documentees avec une justification explicite.
La story corrige le risque principal de l'audit: 64 fichiers et 304 fonctions statiques hors 	estpaths.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-tests/2026-04-28-1600`
- Reason for change: F-001 indique que des tests backend actifs restent invisibles pour la collecte pytest par defaut.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/pyproject.toml` and backend pytest discovery
- In scope:
  - Corriger `tool.pytest.ini_options.testpaths` pour couvrir les tests retenus.
  - Ecarter l'entree inexistante `app/ai_engine/tests` ou recreer une suite intentionnelle seulement si elle contient des tests.
  - Ajouter une garde deterministe qui compare l'inventaire statique `test_*.py` avec la collecte standard.
  - Persister la preuve avant/apres de l'inventaire des fichiers collectes et non collectes.
- Out of scope:
  - Renommer en masse les tests story-numbered.
  - Reorganiser la topologie complete des tests au-dela du strict necessaire pour la collecte.
  - Modifier les fixtures DB ou les assertions metier des tests.
- Explicit non-goals:
  - Ne pas Ecarter un test pour faire baisser le nombre de fichiers non collectes.
  - Ne pas contourner RG-001..RG-009 en excluant les guards No Legacy ou API.
  - Ne pas ajouter de dossier racine sous `backend/`.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: test-guard-hardening
- Archetype reason: la story durcit la garde de collecte pytest sans changer le comportement applicatif.
- Behavior change allowed: constrained
- Behavior change constraints:
  - La collecte standard doit augmenter ou rester equivalente; aucune suite conservee ne doit devenir silencieusement opt-out.
  - Les suites optionnelles doivent etre nommees, justifiees et exclues par regle explicite.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: CI utilise une commande custom qui ne doit pas s'aligner sur `pytest` depuis `backend/`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La source effective est la collecte pytest, pas seulement les fichiers presents. |
| Baseline Snapshot | yes | Le delta avant/apres des fichiers collectes doit etre persiste. |
| Ownership Routing | no | Cette story ne decide pas encore la topologie canonique des racines. |
| Allowlist Exception | yes | Les suites opt-in, si elles existent, doivent etre listees exactement. |
| Contract Shape | no | Aucun contrat API, DTO ou schema public n'est modifie. |
| Batch Migration | no | La correction doit etre atomique sur la configuration de collecte. |
| Reintroduction Guard | yes | Une garde doit echouer si un test conserve sort de la collecte standard. |
| Persistent Evidence | yes | Les inventaires avant/apres doivent rester dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:`n  - AST guard and loaded config evidence for this story.`n  - `pytest --collect-only -q --ignore=.tmp-pytest` execute depuis `backend/`.
  - `backend/pyproject.toml` pour les `testpaths` pytest effectifs.
- Secondary evidence:
  - `rg --files backend -g test_*.py -g *_test.py -g !backend/.tmp-pytest/**`.
- Static scans alone are not sufficient for this story because:
  - un fichier peut exister mais ne pas etre importable ou collectable par pytest.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/collect-retained-backend-tests/pytest-collection-before.md`
  - `_condamad/stories/collect-retained-backend-tests/static-test-inventory-before.md`
- Comparison after implementation:
  - `_condamad/stories/collect-retained-backend-tests/pytest-collection-after.md`
  - `_condamad/stories/collect-retained-backend-tests/static-test-inventory-after.md`
  - `_condamad/stories/collect-retained-backend-tests/uncollected-tests-after.md`
- Expected invariant:
  - Tout fichier `test_*.py` ou `*_test.py` conserve est collecte par la commande standard ou liste comme opt-in.
- Allowed differences:
  - Ajout de racines `testpaths`; ecartement de l'entree inexistante `app/ai_engine/tests`.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: la topologie canonique est traitee par `converge-backend-test-topology`; cette story ne fait que rendre la collecte exhaustive.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `uncollected-tests-after.md` | `none by default` | Opt-in requires CI reason. | Exit: empty or approved rows. |
## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API payload, DTO, status code, generated client type, or frontend type changes.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: une seule surface est corrigee, la configuration de collecte pytest.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline collecte | `_condamad/stories/collect-retained-backend-tests/pytest-collection-before.md` | Prouver l'etat initial. |
| Inventaire statique avant | `_condamad/stories/collect-retained-backend-tests/static-test-inventory-before.md` | Lister les fichiers candidats. |
| Collecte apres | `_condamad/stories/collect-retained-backend-tests/pytest-collection-after.md` | Prouver la collecte finale. |
| Inventaire non collecte | `_condamad/stories/collect-retained-backend-tests/uncollected-tests-after.md` | Prouver zero oubli ou exceptions exactes. |

## 4i. Reintroduction Guard

The implementation must add or update deterministic guards that fail if:

- un fichier `test_*.py` ou `*_test.py` sous `backend/` reste hors collecte sans exception explicite;
- `backend/pyproject.toml` reference une racine de test inexistante;
- une future racine de tests backend apparait sans etre couverte par la collecte standard ou l'allowlist opt-in.

Guard evidence:

- `pytest --collect-only -q --ignore=.tmp-pytest`
- test ou script de garde dedie sous `backend/app/tests/unit` ou `backend/tests/unit`.

Required architecture guard: pytest -q app/tests/unit/test_backend_architecture_guard.py with AST guard evidence.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md` - E-002 collecte 3164 tests, E-004 identifie 64 fichiers et 304 fonctions hors `testpaths`.
- Evidence 2: `backend/pyproject.toml` - `testpaths = ["app/tests", "app/ai_engine/tests", "tests/evaluation", "tests/integration"]`; `app/ai_engine/tests` est absent.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants RG-001..RG-009 consultes avant cadrage.

## 6. Target State

- `pytest --collect-only -q --ignore=.tmp-pytest` collecte tous les tests backend retenus.
- Aucune racine pytest configuree n'est inexistante.
- Les suites opt-in, s'il y en a, ont un registre exact et une raison explicite.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-001` - les guards de facades supprimees ne doivent pas etre exclus de la collecte.
  - `RG-002` - les tests d'architecture routeurs doivent rester collectes.
  - `RG-003` - les guards de montage runtime doivent rester collectes.
  - `RG-004` - les tests d'erreurs API doivent rester collectes.
  - `RG-005` - les guards frontiere API/services doivent rester collectes.
  - `RG-006` - les guards adaptateur API doivent rester collectes.
  - `RG-007` - les guards observability LLM doivent rester collectes.
  - `RG-008` - les guards d'exceptions API/SQL doivent rester collectes.
  - `RG-009` - le guard anti-retour de `app.api.v1.schemas` doit rester collecte.
- Non-applicable invariants:
  - none; cette story touche la couverture de collecte des guards backend.
- Required regression evidence:
  - Collecte pytest complete et inventaire statique compare.
- Allowed differences:
  - Augmentation du nombre de tests collectes; aucune ecartement silencieuse.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La commande standard collecte tous les tests retenus. | Evidence profile: `runtime_openapi_contract`; `pytest --collect-only -q --ignore=.tmp-pytest`. |
| AC2 | Aucune racine `testpaths` inexistante ne reste configuree. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_backend_pytest_collection.py`. |
| AC3 | Toute suite opt-in est explicite. | Evidence profile: `allowlist_register_validated`; `rg -n "opt-in|exception" ../_condamad/stories`. |
| AC4 | Une garde bloque les tests hors collecte. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_backend_pytest_collection.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer la baseline de collecte (AC: AC1, AC2)
- [x] Task 2 - Corriger `backend/pyproject.toml` ou deplacer les fichiers strictement necessaires (AC: AC1, AC2)
- [x] Task 3 - Ajouter la garde d'inventaire collecte vs fichiers (AC: AC1, AC3, AC4)
- [x] Task 4 - Persister les preuves apres changement (AC: AC1, AC3)
- [x] Task 5 - Executer lint et tests dans le venv (AC: AC1, AC4)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/pyproject.toml` comme source unique de configuration pytest.
  - Pytest collect-only comme preuve runtime.
- Do not recreate:
  - Une deuxieme configuration de test hors pyproject.
  - Un script CI parallele qui masque `pytest` standard.
- Shared abstraction allowed only if:
  - Elle sert aussi a la garde de topologie de `converge-backend-test-topology`.

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

- `app/ai_engine/tests` dans `testpaths` si le dossier reste absent.
- Exclusion permanente des racines auditees hors `testpaths` sans decision documentee.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

- Canonical ownership: not applicable

## 14. Delete-Only Rule

- Delete-Only Rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 17. Files to Inspect First

- `_condamad/audits/backend-tests/2026-04-28-1600/00-audit-report.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/02-finding-register.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/pyproject.toml`

## 18. Expected Files to Modify

Likely files:

- `backend/pyproject.toml` - aligner `testpaths`.
- `backend/app/tests/unit/test_backend_pytest_collection.py` or `backend/tests/unit/test_backend_pytest_collection.py` - garde de collecte.
- `_condamad/stories/collect-retained-backend-tests/*.md` - preuves persistantes.

Likely tests:

- `backend/app/tests/unit/test_backend_pytest_collection.py` or `backend/tests/unit/test_backend_pytest_collection.py`.

Files not expected to change:

- `frontend/src` - aucun contrat front.
- `backend/app/infra` - aucune logique DB.
- `requirements.txt` - must not be created.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest --collect-only -q --ignore=.tmp-pytest
pytest -q app/tests/unit/test_backend_pytest_collection.py
pytest -q
rg --files . -g test_*.py -g *_test.py -g !.tmp-pytest/**
```

Story validation:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/collect-retained-backend-tests/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/collect-retained-backend-tests/00-story.md
```

## 21. Regression Risks

- Risk: une suite LLM ou architecture reste invisible.
  - Guardrail: comparaison statique vs collecte runtime.
- Risk: une exception opt-in devient une poubelle durable.
  - Guardrail: registre exact, sans wildcard, avec raison.

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

- `_condamad/audits/backend-tests/2026-04-28-1600/00-audit-report.md` - synthese de la collecte actuelle.
- `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md` - preuves E-002, E-003, E-004.
- `_condamad/audits/backend-tests/2026-04-28-1600/02-finding-register.md` - finding F-001.
- `_condamad/audits/backend-tests/2026-04-28-1600/03-story-candidates.md` - candidat SC-001.
- `_condamad/stories/regression-guardrails.md` - invariants a ne pas exclure.









