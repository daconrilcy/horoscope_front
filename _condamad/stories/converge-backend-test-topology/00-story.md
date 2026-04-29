# Story converge-backend-test-topology: Converge backend test roots into a documented topology

Status: ready-for-dev

## 1. Objective

Definir et faire respecter une topologie canonique des tests backend.
Les racines unit, integration, regression, evaluation et opt-in doivent etre explicites.
La story reduit l'ambiguite F-002 sans traiter la migration des fixtures DB.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-tests/2026-04-28-1600`
- Reason for change: F-002 montre que les tests actifs vivent dans `backend/app/tests`, `backend/tests` et `backend/app/domain/llm/prompting/tests` sans modele de propriete unique.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: backend test topology and ownership
- In scope:
  - Documenter les racines autorisees pour les tests backend.
  - Migrer ou reclasser les tests hors topologie canonique, avec preuve avant/apres.
  - Ajouter une garde qui echoue si une nouvelle racine non approuvee apparait.
  - Aligner la documentation et la configuration pytest avec la topologie choisie.
- Out of scope:
  - Modifier les assertions metier des tests.
  - Resoudre les imports `SessionLocal` directs.
  - Renommer les `test_story_*.py` sauf deplacement strictement necessaire pour la topologie.
- Explicit non-goals:
  - Ne pas creer de compatibilite par re-export de tests.
  - Ne pas ajouter de dossier racine sous `backend/`.
  - Ne pas ecarter les guards RG-001..RG-009 de la suite standard.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: ownership-routing-refactor
- Archetype reason: la story route chaque categorie de test vers un proprietaire canonique et interdit les racines concurrentes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les tests deplaces doivent conserver leurs assertions.
  - Toute suite opt-in doit etre explicitement nommee et documentee.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: la topologie cible n'est pas `backend/app/tests` plus racines support explicitement documentees sous `backend/tests`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La topologie doit etre verifiee par loaded config, AST guard et collecte pytest. |
| Baseline Snapshot | yes | L'inventaire des racines avant/apres est la preuve principale. |
| Ownership Routing | yes | Chaque categorie de test doit avoir un proprietaire canonique. |
| Allowlist Exception | yes | Les racines support ou opt-in exigent une exception exacte. |
| Contract Shape | no | Aucun contrat API n'est modifie. |
| Batch Migration | yes | Les fichiers peuvent etre deplaces par lots limites et verifies. |
| Reintroduction Guard | yes | Une garde doit empecher de nouvelles racines non approuvees. |
| Persistent Evidence | yes | Les inventaires et decisions de topologie doivent etre conserves. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard over the backend test tree and loaded config from `backend/pyproject.toml`.
  - `pytest --collect-only -q --ignore=.tmp-pytest` for effective collection.
- Secondary evidence:
  - `rg --files backend -g test_*.py -g *_test.py -g !backend/.tmp-pytest/**` grouped by parent directory.
- Static scans alone are not sufficient for this story because:
  - pytest collection and loaded config can diverge from file layout.
## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/converge-backend-test-topology/test-root-inventory-before.md`
- Comparison after implementation:
  - `_condamad/stories/converge-backend-test-topology/test-root-inventory-after.md`
  - `_condamad/stories/converge-backend-test-topology/test-root-diff.md`
- Expected invariant:
  - Chaque fichier de test backend appartient a une racine approuvee ou a une suite opt-in documentee.
- Allowed differences:
  - Deplacements de fichiers sans changement d'assertions; mise a jour des import paths des fichiers deplaces.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Unit tests backend applicatifs | `backend/app/tests/unit` or approved documented successor | Embedded domain package tests without topology approval |
| Integration tests applicatifs | `backend/app/tests/integration` or approved documented successor | Arbitrary `backend/tests/*` folders |
| Regression guards applicatifs | `backend/app/tests/regression` or approved documented successor | Story-numbered roots without durable category |
| Evaluation/support suites | `backend/tests/evaluation` and approved support roots | Undocumented folders |
| LLM orchestration suite | Decision required: standard root or documented opt-in root | Hidden exclusion from pytest defaults |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/pyproject.toml` | `tests/evaluation` | Suite support deja configuree par pytest. | Permanent after topology document includes it. |
| `backend/pyproject.toml` | `tests/integration` | Suite support existante configuree par pytest. | Must be classified canonical or migrated. |
| `backend/tests/llm_orchestration` | `test root` | 39 fichiers actifs hors `testpaths` selon audit. | Must be canonical or explicitly opt-in; no silent exclusion. |
| `backend/app/domain/llm/prompting/tests` | `embedded test root` | Test embarque dans domaine. | Must be migrated or approved with expiry. |
## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API payload, DTO, status code, generated client type, or frontend type changes.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 - Inventory | All current roots | Topology register | None | Topology guard | Exact root list | Unknown root owner |
| 2 - Embedded domain test | embedded domain root | Approved test root | Imports updated for moved files | Targeted collect | Old root absent or allowlisted | Import break |
| 3 - Support roots | `backend/tests/*` | Approved roots or opt-in | Pytest config | Collect-only | No undocumented roots | CI command conflict |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Root baseline | `_condamad/stories/converge-backend-test-topology/test-root-inventory-before.md` | Capturer les 13 racines actuelles. |
| Root after | `_condamad/stories/converge-backend-test-topology/test-root-inventory-after.md` | Prouver la topologie finale. |
| Topology decision | `_condamad/stories/converge-backend-test-topology/backend-test-topology.md` | Documenter les racines autorisees. |

## 4i. Reintroduction Guard

The implementation must add or update deterministic guards that fail if:

- un fichier de test backend apparait sous une racine non documentee;
- un dossier `tests` est cree dans un package domaine sans exception;
- `backend/pyproject.toml` et la documentation de topologie divergent.

Required architecture guard: pytest -q app/tests/unit/test_backend_architecture_guard.py with AST guard evidence.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-tests/2026-04-28-1600/00-audit-report.md` - l audit liste les racines backend actives.
- Evidence 2: `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md` - E-001 trouve 425 fichiers sur 13 dossiers.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Une documentation ou un registre local indique les racines backend autorisees.
- La configuration pytest et les chemins de tests respectent cette topologie.
- Une garde echoue sur toute nouvelle racine non approuvee.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-001` through `RG-009` - les tests qui protegent ces invariants peuvent etre deplaces mais pas retires ou rendus invisibles.
- Non-applicable invariants:
  - none for retained backend test ownership.
- Required regression evidence:
  - Inventaire de racines avant/apres, collecte pytest, scan zero racine non approuvee.
- Allowed differences:
  - Changements de chemins de tests avec assertions preservees.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les racines autorisees sont documentees. | Evidence profile: `allowlist_register_validated`; `pytest -q app/tests/unit/test_backend_test_topology.py`. |
| AC2 | Aucun test backend ne reste dans une racine non approuvee. | Evidence profile: `repo_wide_negative_scan`; `rg --files backend -g test_*.py -g *_test.py`. |
| AC3 | Pytest collecte les racines canoniques ou opt-in documentees. | Evidence profile: `runtime_openapi_contract`; `pytest --collect-only -q --ignore=.tmp-pytest`. |
| AC4 | Une garde empeche la reapparition de racines non documentees. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_backend_architecture_guard.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Inventorier et classifier chaque racine actuelle (AC: AC1, AC2)
- [x] Task 2 - Documenter la topologie canonique (AC: AC1)
- [x] Task 3 - Migrer ou enregistrer les racines hors topologie (AC: AC2, AC3)
- [x] Task 4 - Ajouter une garde de topologie (AC: AC4)
- [x] Task 5 - Executer collecte, tests cibles et lint (AC: AC3, AC4)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/pyproject.toml` pour la configuration pytest.
  - L'inventaire statique de tests deja recommande par l'audit.
- Do not recreate:
  - Des registres de topologie concurrents.
  - Des copies de helpers de tests lors des deplacements.
- Shared abstraction allowed only if:
  - Elle sert aux guards de collecte et de topologie.

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

- Nouveau `backend/app/**/tests` embarque sans exception.
- Nouvelle racine `backend/tests/new_root` non documentee.
- Exclusion silencieuse de `backend/tests/llm_orchestration`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Backend test topology | `backend-test-topology.md` plus pytest config | Implicit folder convention |
| Root enforcement | Dedicated topology guard test | Manual review only |

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
- `_condamad/stories/regression-guardrails.md`
- `backend/pyproject.toml`
- `backend/app/tests`
- `backend/tests`
- `backend/app/domain/llm/prompting/tests`

## 18. Expected Files to Modify

Likely files:

- `backend/pyproject.toml` - aligner les racines avec la topologie.
- `backend/app/tests/unit/test_backend_test_topology.py` or `backend/tests/unit/test_backend_test_topology.py` - garde de topologie.
- `_condamad/stories/converge-backend-test-topology/backend-test-topology.md` - decision persistante.

Likely tests:`n`n- `backend/app/tests/unit/test_backend_test_topology.py` - garde de topologie.

Files not expected to change:

- `backend/app/infra` - pas de changement DB.
- `frontend/src` - pas de surface front.
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
pytest -q app/tests/unit/test_backend_test_topology.py
pytest --collect-only -q --ignore=.tmp-pytest
pytest -q
rg --files . -g test_*.py -g *_test.py -g !.tmp-pytest/**
```

Story validation:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/converge-backend-test-topology/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/converge-backend-test-topology/00-story.md
```

## 21. Regression Risks

- Risk: un deplacement casse les imports de tests.
  - Guardrail: collecte pytest et tests cibles apres chaque lot.
- Risk: la topologie exclut des guards historiques utiles.
  - Guardrail: RG-001..RG-009 cites comme non-goals et collecte complete.

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

- `_condamad/audits/backend-tests/2026-04-28-1600/00-audit-report.md` - etat courant des racines.
- `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md` - preuve E-001.
- `_condamad/audits/backend-tests/2026-04-28-1600/02-finding-register.md` - finding F-002.
- `_condamad/audits/backend-tests/2026-04-28-1600/03-story-candidates.md` - candidat SC-002.
- `_condamad/stories/regression-guardrails.md` - invariants a preserver.











